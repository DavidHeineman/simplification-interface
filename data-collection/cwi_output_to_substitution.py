import argparse
import csv
import json
from lexi.core.util import util
from lexi.core.simplification.lexical_en import MounicaGeneratorPhrasal, MounicaSelectorPhrasal
from nltk.tokenize import word_tokenize 

def main(args):
    substitution_data = []
    
    print("Loading Generator & Selector models... ", end = '')
    generator = MounicaGeneratorPhrasal()
    selector = MounicaSelectorPhrasal(2)
    print("Done!")
    
    # LOAD CWI JSON FILE
    with open(args.cwi_data, encoding='utf-8') as f:
        cwi_data = json.load(f)
    
    for pg_num in range(0, args.length):
        print("Processing text set {}".format(pg_num))
        
        # PARSE CWI INPUT .BIN FILE
        text, count, feedback, complex_words = openCWI(args.path + "/pg_" + str(pg_num) + "_output.bin")
        
        # GENERATE SUBSTITUTES W/ PHRASAL-MOUNICA-GENERATOR
        candidate_list, lost_words = [], []
        for sb, se, wb, we in complex_words:
            sent = text[sb:se].lower()
            candidates = generator.getSubstitutions(sent, wb, we)
            if candidates:
                candidate_list.append((sb, se, wb, we, candidates))
            else:
                lost_words.append(sent[wb:we])
        print("[" + str(pg_num) + "] " + "Generated no substitutions for {} of {} words".format(len(lost_words), len(complex_words)))

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
        
        # APPEND TO SUBSTITUTION LIST
        sub_out = []
        for sb, se, wb, we, cands in candidate_list:
            sub_out.append([sb, se, wb, we, cands])

        # COMPILE INTO WORD ENTRY
        word = {}
        word['ID'] = pg_num
        word['Title'] = cwi_data[pg_num]['Title']
        word['URL'] = cwi_data[pg_num]['URL']
        word['Text'] = cwi_data[pg_num]['Text']
        word['Large Paragraph Index'] = cwi_data[pg_num]['Large Paragraph Index']
        word['Source'] = cwi_data[pg_num]['Source']
        word['Substitutes'] = sub_out
        substitution_data.append(word)
        
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