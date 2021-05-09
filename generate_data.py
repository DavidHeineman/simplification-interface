from newsplease import NewsPlease
from lexi.core.util import util
from random import randint
from bs4 import BeautifulSoup
from random import randint
from langdetect import detect
import argparse
import urllib.request
import requests
import re
import pickle as pkl
import pandas as pd
import csv
import matplotlib.pyplot as plt
import numpy as np

def main(args):
    # WIKIPEDIA EXTRACTION
    url = "https://en.wikipedia.org/wiki/Wikipedia:Multiyear_ranking_of_most_viewed_pages"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for link in soup.findAll('a'):
        curr = link.get('href')
        if curr is not None and len(curr) > 0:
            if curr[0] != '#':
                if curr[:5] == '/wiki':
                    curr = 'http://en.wikipedia.org' + curr
                links.append(curr)
    linksnew = []
    for link in links:
        if link[:7] == 'http://':
            linksnew.append(link)
    print('Links extracted {}'.format(len(linksnew)))

    articles = get_wikipedia_articles(linksnew)
    articles_filtered = filter_wikipedia_pages(articles)
    articles_neighbors = paragraph_neighboring_selection(articles_filtered, 'wikipedia')
    wikipedia = []
    for a, b, paragraph, d, e in articles_neighbors:
        wikipedia.append((a, b, remove_citations(paragraph), d, e))

    # REDDIT EXTRACTION
    # Extracts the top 20% longest top English Reddit posts
    reddit = []
    for i in range(1, 15):
        with open('top_reddit/{}.csv'.format(i), newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
                for pg in row['selftext'].splitlines():
                    sents = list(util.span_tokenize_sents(pg))
                    if len(sents) > 4 and 'http://' not in pg and 'edit' not in pg and detect(pg)=='en':
                        reddit.append((row['title'], row['url'], pg, 0, 'reddit'))
    reddit.sort(key=lambda row: len(row[2]))
    reddit = reddit[(int) (4 * (len(reddit) / 5)):]

    # WIKINEWS EXTRACTION
    url = "https://en.wikinews.org/wiki/Wikinews:Featured_articles"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for listitem in soup.findAll('div', {'class': 'mw-parser-output'})[0].findAll('li')[6:]:
        links.append('https://en.wikinews.org' + listitem.findAll('a')[0].get('href'))
    print('Links extracted {}'.format(len(links)))

    articles = get_wikipedia_articles(links)
    wikinews = paragraph_neighboring_selection(articles, 'wikinews')

    # ARXIV ABSTRACTS EXTRACTION
    ## LOAD ARXIV CSV DATA COPY-PASTED FROM RECENT JOURNAL ARTICLES
    temp = []
    with open('arxiv.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            temp.append(row)
    arxiv = []
    for entry in temp:
        arxiv.append((entry[0], entry[1], entry[2], 0, 'arxiv'))

    # CREATE FINAL DATAFRAME
    all_data = []
    all_data.extend(wikipedia)
    all_data.extend(wikinews)
    all_data.extend(reddit)
    all_data.extend(arxiv)
    df = pd.DataFrame(all_data, columns=['Title', 'URL', 'Text', 'Large Paragraph Index', 'Source'])
    print(df.head())    

    ## SAVE FULL DATASET
    df.to_csv('all_data.csv')

    ## SAVE RANDOM SUBSET OF N PARAGRAPHS OF EACH TYPE
    types = ['wikipedia', 'wikinews', 'reddit', 'arxiv']
    df_new = pd.DataFrame(columns=['Title', 'URL', 'Text', 'Large Paragraph Index', 'Source'])
    for type_ in types:
        df_new = df_new.append(df[df['Source'] == type_].sample(n=args.number_of_paragraphs))
    df_new.to_csv('selected_data.csv')

# Given a wikipedia page, extracts all the links on the page
def get_wikipedia_articles(links):
    articles = []
    count = 0
    for link in links:
        count += 1
        try:
            news = NewsPlease.from_url(link)
        except Exception:
            print('Tried to get article at {} but ran into exception: {}'.format(link, str(Exception)))
        if count % 50 == 0:
            print('Processed {} articles'.format(count))
        articles.append(news)
    return articles

# Given a set of wikipedia articles, filters out non-article wikipedia pages
def filter_wikipedia_pages(articles):
    temp = []
    titles = []
    for article in articles:
        if article.source_domain == 'en.wikipedia.org' and article.title[:9] != 'Wikipedia' and article.title[:6] != 'Portal' and article.title != 'Recent changes' and article.title[:4] != 'User' and article.title[:9] != 'Category:' and article.title[:4] != 'Help' and article.title != 'Related changes' and article.title != 'Special pages' and article.title != 'Pages that link to "Wikipedia:Multiyear ranking of most viewed pages"' and article.title not in titles and article.maintext is not None:
            titles.append(article.title)
            temp.append(article)
    return temp

# Returns the number of sentences using NLTK's sentence tokenizer
def sent_count(paragraph):
    return len(list(util.span_tokenize_sents(paragraph)))

# Identifies a long paragraph and gets neighboring paragraphs such that 
# the text will be at or around 15 sentences
def paragraph_neighboring_selection(articles, label):
    output = []
    for article in articles:
        pgs = article.maintext.splitlines()
        for i in range(0, len(pgs)):
            output_pg = ""
            if pgs[i] not in output and sent_count(pgs[i]) > 4:
                output_pg += pgs[i]
                j = i
                k = i
                pg_loc = 0
                while sent_count(output_pg) < 15:
                    j -= 1
                    if j >= 0:
                        if sent_count(pgs[j]) + sent_count(output_pg) < 15: 
                            pg_loc += 1
                            output_pg = pgs[j] + "\n" + output_pg
                        else:
                            break
                    k += 1
                    if k < len(pgs):
                        if sent_count(pgs[k]) + sent_count(output_pg) < 15: 
                            output_pg = output_pg + "\n" + pgs[k]
                        else:
                            break
                    if j < 0 and k >= len(pgs):
                        break
                if sent_count(output_pg) < 25:
                    output.append((article.title, article.url, output_pg, pg_loc, label))
    return output

# Removes the citations from wikipedia articles
def remove_citations(paragraph):
    op = False
    temp = 0
    char = 0
    while char < len(paragraph):
        if paragraph[char] == '[':
            op = True
            temp = char
        if paragraph[char] == ']':
            op = False
            paragraph = paragraph[:temp] + paragraph[char + 1:]
        char += 1
    return paragraph

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts the CWI annotation output .bin files \n'
                                                 'to a substitutes to be used in the ranker annotations.\n'
                                                 'MUST have lexi installed to work.')
    parser.add_argument('--cwi_input', help='Input data (.json) to CWI annotation page', dest='cwi_data', type=str)
    parser.add_argument('--cwi_outputs', help='Path to a folder of cwi_[num]_output.bin files generated \n'
                                              'by the CWI annotation interface.', dest='path', type=str)
    parser.add_argument('--length', help='The number of CWI annotation output files.',
                        dest='length', type=int, default=60)

    parser.add_argument('--npgs', help='The number of paragraphs to select from each input type.',
                    dest='number_of_paragraphs', typee=int, default=15)
    args = parser.parse_args()
    main(args)