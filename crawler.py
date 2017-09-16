# -*- coding: utf-8 -*-
from urllib2 import Request, build_opener, HTTPCookieProcessor, HTTPHandler, urlopen
import urllib
import time
import re
import cookielib
import json
import pprint
from lib.xmlparser import parseString

class Crawler(object):

  def __init__(self):
    self._cookie = ''
    self._session_token = ''

  def set_infos(self):
    cookie_jar = cookielib.CookieJar()
    opener = build_opener(HTTPCookieProcessor(cookie_jar), HTTPHandler())
    request_object = Request("https://www.youtube.com")
    src = opener.open(request_object).read()  

    cookiename = ['YSC', 'PREF', 'VISITOR_INFO1_LIVE']

    for cookie in cookie_jar:
      if cookie.name in cookiename:
        self._cookie += '%s=%s;' % (cookie.name, cookie.value)

    re_st = re.compile('\'XSRF_TOKEN\'\: \"([^\"]+)\"\,')
    self._session_token = re_st.findall(src)[0]
    
  def get_headers(self, k):
    headers = {}
    headers['Accept'] = '*/*'
    headers['Accept-Language'] = 'ko-KR,ko;q=0.8,en-US;q=0.6,en;q=0.4'
    headers['Content-Length'] = '280'
    headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    headers['Cookie'] = self._cookie
    headers['Referer'] = 'https://www.youtube.com/watch?v=' + k
    headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
    
    return headers
    
  def get_num_share(self, key):
    self.set_infos()
    
    day_st = re.compile('stats-sub-header\">([^<까]*)')
    share_count_st = re.compile('<span class=\"metric-label\">공유<\/span>\n*\s*<div class=\"bragbar-metric\">(.*)<\/div>')
    view_time_st = re.compile('<span class=\"metric-label\">시청 시간<\/span>\n*\s*<div class=\"bragbar-metric\">(.*)<\/div>')
    ave_view_time_st = re.compile('<span class=\"metric-label\">평균 시청 지속시간<\/span>\n*\s*<span class=\"menu-metric-value\">([^<]*)')

    url = 'https://www.youtube.com/insight_ajax?action_get_statistics_and_data=1&v=' + key
    data = urllib.urlencode({'session_token': self._session_token})
    headers = self.get_headers(key)

    request = Request(url, data, headers=headers)
    txt = urlopen(request).read()
    
    if "통계 공개가 사용 중지되었습니다." in txt: 
        return '', '', '', ''

    day = day_st.findall(txt)[0].replace(',', '')
    share_count = share_count_st.findall(txt)[0].replace(',', '')
    view_time = self.cleanhtml(view_time_st.findall(txt)[0].replace(',', ''))
    ave_view_time = ave_view_time_st.findall(txt)[0].replace(',', '')

    return day, share_count, view_time, ave_view_time
    
  
  def get_infos(self, key):
    url = 'https://www.googleapis.com/youtube/v3/videos?part=contentDetails,statistics&key=AIzaSyB-jMLhP0BKle6xlwRIEXuxZ1Sr08JduUA&id=' + key
    request = Request(url)
    txt = urlopen(request).read()

    data = json.loads(txt)
    return data['items'][0]['statistics']

  def cleanhtml(self, raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext
    
