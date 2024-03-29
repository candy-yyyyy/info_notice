#!usr/bin/python
# -*- coding: utf-8 -*-
import requests
import SendEmail
import sched
import time
import redis
from bs4 import BeautifulSoup

waterUrl = 'http://www.cqzls.com'  # 停水
gasUrl = 'http://www.cqgas.cn/portal/article/page?cateId=1082&pageNo=1'  # 燃气
gasContentUrl = 'http://www.cqgas.cn/portal/article/content?contentId='
user_list = ['545496535@qq.com']
list_1 = []  # 停水爬虫记录集合
list_2 = []  # 停气爬虫记录集合
# 初始化sched模块的scheduler类
# 第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。
schedule = sched.scheduler(time.time, time.sleep)
# 启用redis 存放扫描过的记录 decode_responses=True 解决redis返回结果带有‘b’ byte 如果不需要使用到redis请屏蔽 redis注释区间内的代码
pool = redis.ConnectionPool(host='XXX.XXX.XXX.XXX', port=1111,db=1,password='XXX',decode_responses=True)
r = redis.Redis(connection_pool=pool)
# redis

def getWaterCutOffInfoList(waterUrl, inc):
    html = requests.get(waterUrl + '/html/tstz/')
    html.encoding = 'GBK'
    htmlObj = BeautifulSoup(html.text, 'html.parser')
    list = htmlObj.find_all('a')
    # redis 获取缓存集合数据 ==》》0,-1 所有数据
    list_1 = r.lrange('cutOffWaterRecord',0,-1)
    if list_1 is None:
        list_1 = []
    # redis
    for i in list:
        if '停水' in i.text and '北碚' in i.text:
            newsDetail = requests.get(waterUrl + i.get('href'))
            if waterUrl + i.get('href') not in list_1:
                getWaterCutOffInfo(newsDetail, waterUrl + i.get('href'))

    schedule.enter(inc, 0, getWaterCutOffInfoList, (waterUrl, inc))


def getWaterCutOffInfo(newDetail, url):
    newDetail.encoding = 'GBK'
    newDetailObj = BeautifulSoup(newDetail.text, 'html.parser')
    content = newDetailObj.find(id='showcontent').div
    sendContent = content.text
    SendEmail.send_mail(user_list, '停水通知', sendContent)
    list_1.append(url)
    # redis
    r.rpush('cutOffWaterRecord',url)
    # redis


def getGasCutOff(gasUrl, inc):
    html = requests.get(gasUrl)
    htmlObj = BeautifulSoup(html.text, 'html.parser')
    list = htmlObj.find(class_='news_list').find_all('a')
    # redis 获取缓存集合数据 ==》》0,-1 所有数据
    list_2 = r.lrange('cutOffGasRecord',0,-1)
    if list_2 is None:
        list_2 = []
    # redis
    for i in list:
        contentHtml = requests.get(gasContentUrl + i['contentid'])
        contentObj = BeautifulSoup(contentHtml.text, 'html.parser')
        if '北碚' in contentObj.text and i['contentid'] not in list_2:
            SendEmail.send_mail(user_list, '停气通知', contentObj.find('div').text)
            list_2.append(i['contentid'])
            # redis
            r.rpush('cutOffGasRecord',i['contentid'])
            # redis

    schedule.enter(inc, 0, getGasCutOff, (gasUrl, inc))

# enter四个参数分别为：间隔事件、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数，
# 给该触发函数的参数（tuple形式）
if __name__ == '__main__':
    schedule.enter(0, 0, getWaterCutOffInfoList, (waterUrl,60)) # 60秒
    schedule.enter(0, 0, getGasCutOff, (gasUrl, 60))  # 60秒
    while True:
        try:
            schedule.run()
        except Exception as e:
            SendEmail.send_mail(user_list, '通知程序异常', "Error {0}".format(str(e.args[0])).encode("utf-8"))

