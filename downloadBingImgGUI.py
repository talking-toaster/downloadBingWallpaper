import requests
import re
import os
from threading import Thread, Lock, Event
import threading
import time
import random
import tkinter as tk
import tkinter.filedialog


baseUrl = 'https://bing.ioliu.cn/'
global x
x=0
global imgBasePath 
imgBasePath = ''
global totalImgNum 
totalImgNum = 0
threadNum = 1
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
                if self.pointer < totalImgNum-1:
                    if self.pointer != 0:
                        textLog.delete(0.0,'end')
                    textLog.insert('end',f'下载进度  {(self.pointer+1)/totalImgNum}%\n')
                else:
                    textLog.delete(0.0,'end')
                    textLog.insert('end',f'下载进度  100%\n')
    
def choseDir():
    filename = tkinter.filedialog.askdirectory()
    if filename != '':
        global imgBasePath
        imgBasePath = filename
        lbDir.config(text = "您选择的文件夹是："+filename)
    else:
        lbDir.config(text = "您没有选择任何文件夹")

def initDownload():
    if enImgNum.get() == '':
        textLog.insert('end','未选择下载数量\n')
        return False
    else:
        try:
            global totalImgNum
            totalImgNum = int(enImgNum.get())
        except ValueError:
            textLog.insert('end','下载数量输入框存在非数字字符\n')
        if imgBasePath == '':
            textLog.insert('end','未选择下载位置\n')
            return False
        else:
            return True 
def downloadMain():
    if initDownload():
        imgInfo = getImgInfo(baseUrl,totalImgNum)
        imgBaseUrl,imgName = imgInfo['imgBaseUrl'],imgInfo['imgName']
        try:
            for threadId in range(threadNum):
                locals()['Thread-'+str(threadId + 1)] = downloadImgThread('1','Thread-'+str(threadId + 1), imgBaseUrl, imgName)
            for threadId in range(threadNum):
                locals()['Thread-'+str(threadId + 1)].start()
        except:
            textLog.insert('end','开启下载线程失败\n')
        finally:
            #exit()
            pass
    else:
        textLog.insert('end','下载初始化失败\n')


window = tk.Tk()
window.title('下载Bing主页壁纸多线程爬虫工具')
window.geometry('1000x500')

lbDescribe = tk.Label(window,text=
'''
这是一个从Bing主页下载壁纸的工具
使用方法：
1.选择下载壁纸数量
2.选择下载路径
3.开始下载
'''
,font=('Arial', 15))
lbDescribe.pack()
e=tk.StringVar()
enImgNum = tk.Entry(window,textvariable= e,font=('Arial', 15))
e.set('下载数量')
enImgNum.pack()
lbDir = tk.Label(window,text = '',font=('Arial', 15))
lbDir.pack()
btnDir = tk.Button(window,text="选择文件夹",command=choseDir,font=('Arial', 12))
btnDir.pack()
btnDownload1 = tk.Button(window,text="开始下载",command=downloadMain,font=('Arial', 12))
btnDownload1.pack()
textLog = tk.Text(window,height=3,font=('Arial', 15))
textLog.pack()
#downloadMain()
window.mainloop()
