# -*- coding=utf-8 -*-
__author__ = 'tungtt'

from flask import Flask, request
from spell_corrector import detect_wrong_spell
from io import open
from sklearn.externals import joblib

app = Flask('crf')

words_dict = joblib.load('model/words_dict.pkl')
uni_dict = joblib.load("model/count_uni.pkl")
print("Loading bi_dict....")
bi_dict = joblib.load("model/count_bi.pkl")

with open('crf.html', 'r', encoding='utf-8') as f:
	data = f.read()

@app.route('/',methods = ['GET'])
def homepage():
	return data


@app.route('/crf', methods=['POST'])
def process_request():
    data = request.get_data()
    data = unicode(data, "utf-8")
    true_sent = detect_wrong_spell(data,bi_dict,uni_dict,words_dict)
    return true_sent

if __name__ == '__main__':
    app.run(port=12345)