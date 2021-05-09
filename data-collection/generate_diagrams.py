from nltk.tokenize import word_tokenize 
from matplotlib import colors
from lexi.config import *
from lexi.core.util import util
from lexi.core.simplification.lexical_en import MounicaCWI
from lexi.core.en_nrr.features.feature_extractor_fast import FeatureExtractorFast
import argparse
import textstat
import statistics
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main(args):
    df = pd.read_csv('selected_data.csv')

    ## Sentence Counts
    data = [
        sent_count_list(df[df['Source'] == 'wikipedia']['Text']),
        sent_count_list(df[df['Source'] == 'wikinews']['Text']),
        sent_count_list(df[df['Source'] == 'reddit']['Text']),
        sent_count_list(df[df['Source'] == 'arxiv']['Text'])
    ]
    xaxes = ['# Sent.','# Sent.','# Sent.','# Sent.']
    yaxes = ['# Pgs','# Pgs','# Pgs','# Pgs']
    titles = ['Wikipedia','Wikinews','Reddit','arXiv Abstracts'] 

    f,a = plt.subplots(2,2, sharex=True, sharey=True)
    a = a.ravel()
    for idx,ax in enumerate(a):
        ax.hist(data[idx])
        ax.set_title(titles[idx])
        # ax.set(xlim=(2, 15), ylim=(0, 6))
    #plt.xlabel('# Sent.')
    #plt.ylabel('# Pgs')
    f.text(0.5, -0.02, '# Sentences', ha='center', va='center', fontsize="large")
    f.text(-0.02, 0.45, '# Paragraphs', ha='center', va='center', rotation='vertical', fontsize="large")
    plt.tight_layout()
    plt.suptitle('Number of Paragraphs by Length', fontsize="x-large")
    plt.subplots_adjust(top=0.83)
    plt.savefig("plt-sent-counts.svg")

    ## Avg. Words per Sentence
    counts = [
        word_sent_ratio(df[df['Source'] == 'wikipedia']['Text']),
        word_sent_ratio(df[df['Source'] == 'wikinews']['Text']),
        word_sent_ratio(df[df['Source'] == 'reddit']['Text']),
        word_sent_ratio(df[df['Source'] == 'arxiv']['Text'])
    ]
    x = ['Wikipedia','Wikinews','Reddit','arXiv Abstracts'] 
    plt.bar(x, counts, align='center')
    plt.ylabel('Words per Sentence')
    plt.title('Average Sentence Length by Dataset')
    plt.savefig("plt-avg-sent-length.svg")

    ## Text Complexity - Average Kincaid
    counts = [
        kincaid(df[df['Source'] == 'wikipedia']['Text']),
        kincaid(df[df['Source'] == 'wikinews']['Text']),
        kincaid(df[df['Source'] == 'reddit']['Text']),
        kincaid(df[df['Source'] == 'arxiv']['Text'])
    ]
    x = ['Wikipedia','Wikinews','Reddit','arXiv Abstracts'] 
    plt.bar(x, counts, align='center')
    plt.ylabel('Flesch-Kincaid Score per Sentence')
    plt.title('Average Sentence Flesch-Kincaid Readability Score By Dataset')
    plt.savefig("plt-avg-flesch-kincaid.svg")

    ## Text Complexity - Median Kincaid
    counts = [
        kincaid_median(df[df['Source'] == 'wikipedia']['Text']),
        kincaid_median(df[df['Source'] == 'wikinews']['Text']),
        kincaid_median(df[df['Source'] == 'reddit']['Text']),
        kincaid_median(df[df['Source'] == 'arxiv']['Text'])
    ]
    x = ['Wikipedia','Wikinews','Reddit','arXiv Abstracts'] 
    plt.bar(x, counts, align='center')
    plt.ylabel('Flesch-Kincaid Score')
    plt.title('Median Sentence Flesch-Kincaid Readability Score By Dataset')
    plt.savefig("plt-median-flesch-kincaid.svg")

    ## Text Complexity - Kincaid per type
    data = [
        kincaid_list(df[df['Source'] == 'wikipedia']['Text']),
        kincaid_list(df[df['Source'] == 'wikinews']['Text']),
        kincaid_list(df[df['Source'] == 'reddit']['Text']),
        kincaid_list(df[df['Source'] == 'arxiv']['Text'])
    ]
    xaxes = ['Readability Score','Readability Score','Readability Score','Readability Score']
    yaxes = ['# Sent','# Sent','# Sent','# Sent']
    titles = ['Wikipedia','Wikinews','Reddit','arXiv Abstracts'] 

    f,a = plt.subplots(2,2)
    a = a.ravel()
    for idx,ax in enumerate(a):
        ax.hist(data[idx])
        ax.set_title(titles[idx])
        ax.set_xlabel(xaxes[idx])
        ax.set_ylabel(yaxes[idx])
    plt.tight_layout()
    plt.savefig("plt-histogram-flesch-kincaid.svg")

    ## % Complex Words defined by Mounica CWI
    cwi = MounicaCWI.staticload(CWI_PATH_TEMPLATE.format("default"))
    counts = [
        complex_word_ratio(cwi, df[df['Source'] == 'wikipedia']['Text']),
        complex_word_ratio(cwi, df[df['Source'] == 'wikinews']['Text']),
        complex_word_ratio(cwi, df[df['Source'] == 'reddit']['Text']),
        complex_word_ratio(cwi, df[df['Source'] == 'arxiv']['Text'])
    ]
    x = ['Wikipedia','Wikinews','Reddit','arXiv Abstracts'] 
    plt.bar(x, counts, align='center')
    plt.ylabel('Average Word to Complex Word Ratio')
    plt.title('Average % Complex Words by Dataset')
    plt.savefig("plt-percent-complex-words.svg")

    ## Example Sentence w/ Complex Word Labels
    arx = df[df['Source'] == 'arxiv']['Text'][49]
    wiki = df[df['Source'] == 'wikipedia']['Text'][8]
    print(visualize_cwi(cwi, wiki))

    c = [0] * 25
    for entry in df[df['Source'] == 'wikipedia']['Text']:
        c[entry.count('\n') + 1] += 1
    for entry in df[df['Source'] == 'wikinews']['Text']:
        c[entry.count('\n') + 1] += 1
        if entry.count('\n') > 10:
            print(entry)

    ## Paragraphs per Wikipedia / Wikinews Text
    x = np.arange(len(c))
    plt.bar(x, c, align='center')
    plt.ylabel('# Paragraphs')
    plt.title('# Paragraphs per Wikipedia or Wikinews Text')
    plt.savefig("plt-paragrpahs-per-text.svg")

    ## Count of the amount of sentences removed for substitution selection
    # Get number of sentences in all paragraphs
    # Get number of sentences in target paragraph
    # Subtract the first two to get the thrown out sentences
    rem = 0
    keep = 0
    for i in range(0, len(df[df['Source'] == 'wikipedia'])):
        rem += sent_count(df[df['Source'] == 'wikipedia']['Text'][i]) - \
        sent_count(df[df['Source'] == 'wikipedia']['Text'][i].splitlines()[df[df['Source'] == 'wikipedia']['Large Paragraph Index'][i]])
        
        keep += sent_count(df[df['Source'] == 'wikipedia']['Text'][i])
    for i in range(15, 15+len(df[df['Source'] == 'wikinews'])):
        rem += sent_count(df[df['Source'] == 'wikinews']['Text'][i]) - \
        sent_count(df[df['Source'] == 'wikinews']['Text'][i].splitlines()[df[df['Source'] == 'wikinews']['Large Paragraph Index'][i]])
        
        keep += sent_count(df[df['Source'] == 'wikinews']['Text'][i])
    print("{} of {} sentences are removed for substitution selection".format(rem, keep))

def visualize_cwi(cwi, text):
    b = 0
    for sb, se, wb, we in complex_words_single(cwi, text):
        text = text[:sb+wb + b] + "\\textbf{" + text[sb+wb + b:]
        text = text[:sb+we + b + 8] + "}" + text[sb+we + b + 8:]
        b += 9
    return text

def sent_count(paragraph):
    return len(list(util.span_tokenize_sents(paragraph)))

def sent_count_list(df):
    output = []
    for text in df:
        output.append(sent_count(text))
    return output

def word_sent_ratio(series):
    wc = 0
    sc = 0
    for text in series:
        wc += len(word_tokenize(text))
        sc += len(list(util.span_tokenize_sents(text)))
    return wc / sc

def kincaid(series):
    return sum(kincaid_list(series)) / sum(sent_count_list(series))

def kincaid_median(series):
    return statistics.median(kincaid_list(series))

def kincaid_list(series):
    ks = []
    for text in series:
        ks.append(textstat.flesch_kincaid_grade(text))
    return ks

def complex_words_single(cwi, text):
    offset2html, text = util.filter_html(text)
    sent_offsets = list(util.span_tokenize_sents(text))
    startOffset = 0
    endOffset = len(text)
    offsets = util.span_tokenize_words(text)

    # COMPLEX WORD IDENTIFICATION
    complex_words = []
    for sb, se in sent_offsets:
        if se < startOffset or sb > endOffset:
            continue
        sent = text[sb:se]
        token_offsets = util.span_tokenize_words(sent)
        for wb, we in token_offsets:
            global_word_offset_start = sb + wb
            global_word_offset_end = sb + we
            if global_word_offset_start < startOffset or \
                    global_word_offset_end > endOffset:
                continue
            complex_word = True
            if cwi:
                complex_word = cwi.is_complex(sent, wb, we)
            if complex_word:
                complex_words.append((sb, se, wb, we))
    return complex_words

def complex_words(cwi, series):
    output = []
    for text in series:
        output.append(complex_words_single(cwi, text))
    return output

def complex_word_list(cwi, series):
    out = []
    for x in complex_words(cwi, series):
        out.append(len(x))
    return out

def complex_word_ratio(cwi, series):
    wc = 0
    for text in series:
        wc += len(word_tokenize(text))
    return sum(complex_word_list(cwi, series)) / wc

def visualize_cwi(cwi, text):
    b = 0
    for sb, se, wb, we in complex_words_single(cwi, text):
        text = text[:sb+wb + 4*b] + "**" + text[sb+wb + 4*b:]
        text = text[:sb+we + 4*b + 2] + "**" + text[sb+we + 4*b + 2:]
        b += 1
    return text

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