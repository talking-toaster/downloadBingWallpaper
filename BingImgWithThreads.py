import requests
import re
import os
from threading import Thread, Lock, Event
import threading
import time
import random

#全局变量，用于指示当前下载数量
global x     
x=0
#保存位置
imgBasePath = 'D:\\spider\\test\\'   
#要下载的图片数量
totalImgNum = 46     
#下载使用线程数，由于GIL的存在，虽然不是真正多线程，但是对加速下载有效
threadNum = 20     

#线程锁，防止多个线程同时访问x
lock = threading.Lock()

def getImgInfo(baseUrl, totalImgNum):
    pageNum = totalImgNum // 12
    restImgNum = totalImgNum % 12
    imgBaseUrl = []
    imgName = []
    imgInfo = {'imgBaseUrl':imgBaseUrl,'imgName':imgName}
    for page in range(pageNum+1):
        if page == 0:
            url = baseUrl
        else :
            url = nextPageUrl
        response = requests.get(url)
        response.encoding = 'utf-8'
        baseHtml = response.text
        #homeConUrl = re.findall(r'<li class="active"><a href="(.*?)"><i class="icon icon-home">',baseHtml)[0]
        #rankConUrl = re.findall(r'<li><a href="(.*?)"><i class="icon icon-ranking">',baseHtml)[0]
        imgBaseUrl = re.findall(r'data-progressive="(.*?)"',baseHtml)
        imgName = re.findall(r'<h3>(.*?)</h3>',baseHtml)
        for i in range(len(imgName)):
            imgName[i] = imgName[i].replace('/','')
            imgName[i] = imgName[i].replace('©','')
            imgName[i] = imgName[i].replace('，','')
        curPageNum = re.findall(r'</a><span>(.*?)/',baseHtml)[0]
        curPageNum = int(curPageNum)
        maxPageNum = re.findall(r' / (\d+)</span><a href="',baseHtml)[0]
        maxPageNum = int(maxPageNum)
        nextPageUrl = baseUrl + re.findall(r'</span><a href="(.*)">下一页',baseHtml)[0]
        if page == pageNum:
            imgNumOnCurPage = restImgNum
        else:
            imgNumOnCurPage = len(imgBaseUrl)
        for i in range(imgNumOnCurPage):
            imgInfo['imgBaseUrl'].append(imgBaseUrl[i])
            imgInfo['imgName'].append(imgName[i])
    return(imgInfo)

def downloadOneImg( imgDir, imgUrl, imgName):
    response = requests.get(imgUrl)
    with open(f'{imgDir}/{imgName}.jpg','wb') as f:
        f.write(response.content)
class downloadImgThread(Thread):
    
    def __init__(self, threadID, threadName, imgUrlList, imgNameList):
        super().__init__()
        self.threadID = threadID
        self.threadName = threadName
        self.imgUrlList = imgUrlList
        self.imgNameList = imgNameList
        self.exit = Event()
        self.pointer = -1
    def run( self ):
        while not self.exit.is_set():
            lock.acquire()
            global x
            if x < totalImgNum:
                self.pointer = x
                x += 1
                print(f'{self.getName()} {x}')
            else:
                self.exit.set()
            lock.release()
            if not self.exit.is_set():
                oneImgBaseUrl = self.imgUrlList[self.pointer]
                oneImgName = self.imgNameList[self.pointer]
                downloadOneImg( imgBasePath, oneImgBaseUrl, oneImgName)

def main():
    
    baseUrl = 'https://bing.ioliu.cn/'
    
   
    imgInfo = getImgInfo(baseUrl,totalImgNum)
    imgBaseUrl,imgName = imgInfo['imgBaseUrl'],imgInfo['imgName']
    
    try:
        for threadId in range(threadNum):
            locals()['Thread-'+str(threadId + 1)] = downloadImgThread('1','Thread-'+str(threadId + 1), imgBaseUrl, imgName)
        for threadId in range(threadNum):
            locals()['Thread-'+str(threadId + 1)].start()
    except:
        print('get error')
    finally:
        print('global:'+ str(x) )
        exit()

if __name__ == "__main__":
    main()