import argparse
import csv
import json
from lexi.core.util import util
from lexi.core.simplification.lexical_en import MounicaGenerator, MounicaSelector
from nltk.tokenize import word_tokenize 

def main(args):
    substitution_data = []
    
    print("Loading Generator & Selector models... ", end = '')
    generator = MounicaGenerator()
    selector = MounicaSelector(2)
    print("Done!")
    
    # LOAD PHRASAL PPDB++ CORPUS FILE
    # DELETE ALL PHRASAL PPDB STUFF, IT'S NOT CURRENTLY USED FOR GENERATION / SELECTION
    print("Loading SimplePPDB++ Corpus... ", end = '')
    ppdb_file = 'simpleppdbpp-phrasal.txt'
    corpus = {}
    NUM_REPLACEMENTS = 10
    for line in open(ppdb_file, encoding='utf-8'):
        tokens = [t.strip() for t in line.strip().split('\t')]
        if float(tokens[2]) > 0:
            if tokens[0] not in corpus:
                replacements = {}
            else:
                replacements = corpus[tokens[0]]
            if tokens[0] not in corpus or len(corpus[tokens[0]]) < NUM_REPLACEMENTS:
                replacements[tokens[1]] = float(tokens[2])
                corpus[tokens[0]] = replacements

    for key in corpus.keys():
        corpus[key] = dict(sorted(corpus[key].items(), key=lambda item: item[1], reverse=True))
    print("Done!")
    
    # LOAD CWI JSON FILE
    with open(args.cwi_data, encoding='utf-8') as f:
        cwi_data = json.load(f)
    
    for pg_num in range(0, args.length):
        print("Processing text set {}".format(pg_num))
        
        # PARSE CWI INPUT .BIN FILE
        text, count, feedback, complex_words = openCWI(args.path + "/pg_" + str(pg_num) + "_output.bin")
        
        # GENERATE SUBSTITUTES W/ MOUNICA-GENERATOR
        candidate_list = []
        lost_words = []
        for sb, se, wb, we in complex_words:
            sent = text[sb:se].lower()
            candidates = generator.getSubstitutions(sent[wb:we])
            if candidates:
                candidate_list.append((sb, se, wb, we, candidates))
            else:
                lost_words.append(sent[wb:we])
        print("[" + str(pg_num) + "] " + "Generated no substitutions for {} words".format(len(lost_words)))
        
        # SELECT SUBSTITUTES W/ MOUNICA-SELECTOR
        selected_list = []
        notSelected = 0
        for sb, se, wb, we, candidates in candidate_list:
            sent = text[sb:se]
            selected = selector.select(sent, wb, we, candidates)
            if len(selected) == 0:
                selected = candidates
                notSelected += 1
            selected_list.append((sb, se, wb, we, selected))
        print("[" + str(pg_num) + "] " + 'No selected substitutions for {} words'.format(notSelected))
        
        # GENERATE PHRASAL SUBSTITUTIONS
        candidate_list = []
        lost_words = []
        for sb, se, wb, we in complex_words:
            sent = text[sb:se].lower()
            candidates = getSubstitutionsPhrasal(corpus, sent, wb, we)
            if candidates:
                candidate_list.append((sb, se, wb, we, candidates))
            else:
                lost_words.append(sent[wb:we])
        print("[" + str(pg_num) + "] " + "Generated no substitutions for {} of {} words".format(len(lost_words), len(complex_words)))
        
        # APPEND TO SUBSTITUTION LIST
        sub_out = []
        for sb, se, wb, we, cands in candidate_list:
            sub_out.append([sb, se, wb, we, cands])
        out = {}
        out['ID'] = pg_num
        out['Title'] = cwi_data[pg_num]['Title']
        out['URL'] = cwi_data[pg_num]['URL']
        out['Text'] = cwi_data[pg_num]['Text']
        out['Large Paragraph Index'] = cwi_data[pg_num]['Large Paragraph Index']
        out['Source'] = cwi_data[pg_num]['Source']
        out['Substitutes'] = sub_out
        substitution_data.append(out)
        
    print("Saved generated substitutes to data_RANKER.json!")
    with open("data_RANKER.json", "w") as f:
        json.dump(substitution_data, f)
    
def openCWI(path):
    text = ""
    count = 0
    feedback = []
    complex_words = []
    
    # Parses feedback into array
    with open(path, newline='\n', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for item in f:
            listitem = []
            char = 0
            while char < len(item):
                if (item[char] == '\t'):
                    listitem.append(item[:char])
                    listitem.append(item[char+1])
                char += 1
            feedback.append(listitem)

    # Parses array back into text, counts complex words
    for item in feedback:
        text += item[0] + " "
        if item[1] != '0':
            count += 1
    # print("{}...\t {:.2f}% identified as complex".format(text[:32], 100*(count / (len(feedback)))))
    
    # Realigns sentence offsets to location within text
    sent_offsets = list(util.span_tokenize_sents(text))
    global_offset = 0
    i = 0
    j = 0
    for word, difficulty in feedback:
        try:
            while global_offset >= sent_offsets[i][1]:
                i += 1
                j = 0
            offset = (0,0)
            for temp in util.span_tokenize_words(word):
                if (temp[1] - temp[0]) > (offset[1] - offset[0]):
                    offset = temp
            wb, we = offset[0] + j, offset[1] + j
            if int(difficulty) > 0:
                complex_words.append((sent_offsets[i][0], sent_offsets[i][1], wb, we))
        except IndexError:
            print("Couldn't get word at sent_offset = {}".format(global_offset))
        global_offset += len(word) + 1
        j += len(word) + 1
    
    return text, count, feedback, complex_words

def getSubstitutionsPhrasal(corpus, sent, so, eo):
    t_b = word_tokenize(sent[:so])
    t_a = word_tokenize(sent[eo:])
    t_b = ['<S>'] + t_b
    t_a = t_a + ['</S>']

    ngrams = []
    for i in range(0,8):
        for j in range(0,8):
            out = sent[so:eo]
            if (i != 0):
                for word in t_b[::-1][:i]:
                    out = word + " " + out
            if (j != 0):
                for word in t_a[:j]:
                    out = out + " " + word
            if (len(word_tokenize(out)) < 8 and out not in ngrams):
                ngrams.append(out)
    
    phrases = []
    for phrase in ngrams:
        if phrase in corpus:
            phrases.append((phrase, list(corpus[phrase].keys())))
        # else:
            # phrases.append((phrase, None))
    return phrases

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts the CWI annotation output .bin files \n'
                                                 'to a substitutes to be used in the ranker annotations.\n'
                                                 'MUST have lexi installed to work.')
    parser.add_argument('--cwi_input', help='Input data (.json) to CWI annotation page', dest='cwi_data', type=str)
    parser.add_argument('--cwi_outputs', help='Path to a folder of cwi_[num]_output.bin files generated \n'
                                              'by the CWI annotation interface.', dest='path', type=str)
    parser.add_argument('--length', help='The number of CWI annotation output files.',
                        dest='length', type=int, default=60)
    args = parser.parse_args()
    main(args)