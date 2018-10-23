# -*- coding: utf-8 -*-
import bs4
import requests
import json
import asyncio

from cachetools import cached, TTLCache
cache = TTLCache(maxsize=100, ttl=300)

from flask import Flask, request
app = Flask(__name__)

class WordCount():
    def __init__(self, urlList, word):
        self.urlList = urlList
        self.word = word

    @cached(cache)
    def getWebContent(self, url):
        if (url.startswith('https://') or url.startswith('http://')):
            try:
                response = requests.get(url)
                return bs4.BeautifulSoup(response.text, 'html.parser').get_text()
            except Exception as e:
                return url
        else:
            return url

    @cached(cache)
    def getWordCount(self, url, word):
        data = {}
        count = ''
        content = self.getWebContent(url)

        if (content != url):
            count = content.lower().count(word)
        else:
            count = url
        
        if(type(count)==int):
            data['url'] = url
            data['word'] = word
            data['count'] = count
            data['response'] = 200
        else:
            data['url'] = url
            data['word'] = word
            data['message'] = 'Nao foi possivel realizar o count na url enviada!'
            data['response'] = 400
        return json.dumps(data)


    def runWordCount(self, *args):
        responseData = []
        for url in self.urlList.split(','):
            responseData.append(self.getWordCount(url, self.word))

        return json.dumps(responseData)


@app.route("/", methods=['GET'])
def home():
    listaUrl = request.args.get('listaUrl')
    word = request.args.get('word')

    if (listaUrl != None and word != None):
        wordCount = WordCount(listaUrl, word)
        return wordCount.runWordCount(wordCount)
    else:
        return json.dumps({'message' : 'Checar parametros. listaUrl e word sao obrigatorios', 'response' : 404})

if __name__ == '__main__':
    app.run(debug=True)

# https://app.swaggerhub.com/apis/maurojosedmjr/api-word-count/1.0.0#/developers