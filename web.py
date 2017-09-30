# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import pprint

app = Flask(__name__)

@app.route("/")
def hello():
  return render_template('index.html')

@app.route('/getInfo', methods=['POST'])
def get_info():
  print request.form['youtube_id']

  from crawler import Crawler
  c = Crawler()
  data = c.get_infos(request.form['youtube_id'])
  data[u'day'], data[u'shaerCount'], data[u'viewTime'], data[u'aveViewTime'], data[u'reason'] = c.get_num_share(request.form['youtube_id'])

  if data[u'reason'] == '':
    data[u'reason'] = data[u'day']
  
  data[u'viewTime'] = data[u'viewTime'].decode("utf-8")

  return render_template('result.html', data=data)

if __name__ == "__main__":
  app.run()
