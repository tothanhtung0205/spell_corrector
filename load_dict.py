import numpy as np
from underthesea import word_tokenize
from io import open
import os
from glob import glob

# acr_dict = np.load('dict1.npy').item()
# print(acr_dict)

MIN_PROB = 0.5

def count_gram(sent,uni_gram_dict,di_gram_dict):
    words = word_tokenize(sent)
    for i in range(len(words)):
        words[i] = words[i].lower()
    for word in words:
        if word not in uni_gram_dict:
            uni_gram_dict[word] = 1
        else:
            uni_gram_dict[word] += 1

    words.insert(0,'bos')
    words.append('eos')
    for i,word in enumerate(words):          
        if i == len(words)-1:
            continue
        else:
            di_gram = words[i] + " " + words[i+1]
            if di_gram not in di_gram_dict:
                di_gram_dict[di_gram] = 1
            else:
                di_gram_dict[di_gram]+=1

def get_gram_dict(path_name):
    uni_dict = {}
    di_dict = {}
    files = glob(path_name+"/*")
    for file in files:
        with open(file,encoding='utf-8') as f:
            sent = f.read()
            count_gram(sent,uni_dict,di_dict)
            print("Priocess " + file)
    return uni_dict,di_dict

def get_prob(dict,token):
    try:
        p = dict[token]
    except:
        p = MIN_PROB
    return p

def replace_acronym(acr,uni_dict,di_dict,acr_dict):
    temp_un_acr = acr_dict[acr[0]]
    max = 0
    true_acr = ""
    for un_acr in temp_un_acr:
        w_front = acr[1]    #w-1
        w_behind = acr[2]   #w+1
                
        # p_w_front = get_prob(uni_dict,w_front)
        # p_w_behind = get_prob(uni_dict,w_behind)
        w = un_acr  
        p_w = get_prob(uni_dict,w)

        di_gram_front = w_front+" "+w
        di_gram_behind = w + " " + w_behind

        p_w1w2 = get_prob(di_dict,di_gram_front)
        p_w2w3 = get_prob(di_dict,di_gram_behind)

        score = p_w1w2*p_w2w3/p_w

        print("Word %s : Score %f" %(w,score))
        if score > max:
            true_acr = w
    return true_acr    

def detect_acronym(sent):
    acr_list = []
    words = word_tokenize(sent)
    for i,word in enumerate(words):
        if word.isupper() and 1<len(word)<4:
            print("Acronym : " + word)

            w = word.lower()
            if i==0:
                w_front = "bos"
                w_behind = word[i+1].lower()
            elif i==len(words) - 1:
                w_front = words[i-1].lower()
                w_behind = "eos"
            else:
                w_front = words[i-1].lower()
                w_behind = words[i+1].lower()

            acr = [w,w_front,w_behind]
            acr_list.append(acr)
    return acr_list

def process_acronym(sent,uni_dict,di_dict,acr_dict):
    acr_list = detect_acronym(sent)
    for acr in acr_list:
        true_acr = replace_acronym(acr,uni_dict,di_dict,acr_dict)
        print(true_acr)
        sent = sent.replace(acr[0].upper(),true_acr,1)
    return sent

if __name__ == "__main__":
    acr_dict = np.load('dict.npy').item()
    
    uni_dict,di_dict = get_gram_dict('dataset/dataset/news_mongo')

    np.save('uni_dict',uni_dict)
    np.save('di_dict',di_dict)
    
    test_sent = "Tôi là người VN máu đỏ da vàng"
    sent = process_acronym(test_sent,uni_dict,di_dict,acr_dict)
    print(sent)