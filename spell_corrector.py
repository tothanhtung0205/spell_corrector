# -*- coding=utf-8 -*-
# author = "tungtt"

from Levenshtein import distance
from sklearn.externals import joblib
import math
MIN_PROB = math.log(1e-50)

def get_ed_score(wrong_word,can):
    if can == 'bos':
        can = u'bos'
    ed = distance(wrong_word, can)
    return 10*math.log(1.0/ed)


def get_markov_chain_score(words,bi_dict,uni_dict):

        previous_word = words[0]
        prob = 0.0
        '''
        p(w1w2w3w4) = p(w1).p(w2|w1).p(p3|w2).p(w4|w3)
        p(w2|w1) = p(w1w2)/p(w1)
        where w1 and w4 are constant so p(w1) is constant
        '''

        for i in xrange(1, len(words)):
            current_word = words[i]
            try:
                c = current_word[0]
                stastistic = bi_dict[c][current_word][previous_word]
                cc = previous_word[0]
                total = uni_dict[cc][previous_word]
                prob += math.log(float(stastistic) / float(total))
            except:
                prob += MIN_PROB
            previous_word = current_word
        
        return prob


def detect_wrong_spell(sent,bi_dict,uni_dict, words_dict):
    words = sent.lower().split()
    words.insert(0, u"bos")
    #words.insert(0,u'bbos')
    contexts = []
    for i in xrange(1, len(words)-1):
        curr = words[i]
        if curr not in words_dict:
            print("Wrong token not in dict : " + curr)
            prev = words[i-1]
            nex = words[i+1]
            context = [prev, curr, nex]
            true_can = process_corrector(context,bi_dict,uni_dict)
            words[i] = true_can

    for i in xrange(1, len(words)-1):
        curr = words[i]
        prev = words[i-1]
        nex = words[i+1]

        if prev not in bi_dict[curr[0]][curr] and curr not in bi_dict[nex[0]][nex]:
            print("Wrong token usage: " + curr)
            context = [prev, curr, nex]
            true_can = process_corrector(context,bi_dict,uni_dict)
            words[i] = true_can

    sent = u" ".join(words[1:])
    return sent

def process_corrector(context, bi_dict,uni_dict):
    print(u"Generate candidate for [%s] " %(' '.join(context)))
    prev = context[0]
    wrong_word = context[1]
    next = context[2]
    count = 0
    true_can = ""
    curs = bi_dict[next[0]][next]    # dict of words preceed next
    max_score = -100

    for cur in curs:
        prev_candidate = bi_dict[cur[0]][cur]
        for prev_can in prev_candidate:
            if prev == prev_can:
                can_ctx = [prev, cur, next]
                
                ed_score = get_ed_score(wrong_word,cur)

                if ed_score < 10*math.log(1.0/3.0):
                    break

                mkov_score = get_markov_chain_score(can_ctx, bi_dict, uni_dict)
                print("\nCandidate: %s" %cur)
                print("Markov score : %f" %mkov_score)
                print("ED score : %f" %ed_score)
                score = mkov_score
                print("Total score : %f" %score)
                if score>max_score:
                    max_score = score
                    true_can = cur
                count += 1
    print("\n %d candidates" %count)
    print(" True candidate" + true_can)

    return true_can


if __name__ == "__main__":

    words_dict = joblib.load('model/words_dict.pkl')
    uni_dict = joblib.load("model/count_uni.pkl")
    print("Loading bi_dict....")
    bi_dict = joblib.load("model/count_bi.pkl")
    sent = ""
    while (sent != 'q'):
        sent = raw_input("Enter sent : ")
        sent = unicode(sent, "utf-8")
        correct_sent = detect_wrong_spell(sent,bi_dict,uni_dict,words_dict)
        print(correct_sent)