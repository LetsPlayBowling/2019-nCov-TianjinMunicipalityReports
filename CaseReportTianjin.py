# -*- coding: utf-8 -*-
"""
Created on Sun Feb 9  2020

Tianjin（天津）municipality reported 2019-nCoV Cases

Information source: 
Tianjin（天津）municipality people's government, official website: (最新疫情通报) latest cases reports 
    http://www.tj.gov.cn/xw/ztzl/tjsyqfk/yqtb/index.html
    
manual:
    to get latest reports, you can run this script everyday. 
    the reports will be saved in the current folder as txt files.
    after the first run, you should comment the OPTIONAL line in the main function.
    (在第一次跑完此代码获取历史数据之后，请将main函数里OPITIONAL的那一行前加#，注释掉。)
    
@author: RAY 

"""

import requests
import re
import datetime
import os

def getTodayDate():    
    # get date as a string, like "20200203"
    today = datetime.date.today() 
    if today.month < 10:
        strTodayMonth = '0'+ str(today.month)
    else:
        strTodayMonth = str(today.month)   
    if today.day < 10:
        strTodayDay = '0'+ str(today.day)
    else:
        strTodayDay = str(today.day)
    strTodayDate = str(today.year) + strTodayMonth + strTodayDay
    return strTodayDate

def getAllNewsUrls():
    # get webpage news titles and urls from the "最新疫情通报" webpage
    # including news titles and their urls
    print(">>>> Requesting the website...")
    url = 'http://www.tj.gov.cn/xw/ztzl/tjsyqfk/yqtb/index.html' # '首页/新闻/天津市肺炎疫情防控专题/最新疫情通报' address
    print(">>>> Requesting the website: " + url + " ...")
    try:
        res = requests.get(url)
    except IOError:
        print(">>>> Connection Error ")
    else:
        res.encoding = 'utf-8'
        totalPageNumber = int(re.search('(countPage =)(.*?)(//共多少页)',
                            res.text, re.S).group(2)) # get webpage numbers
        print('>>>> totalPageNumber = ' + str(totalPageNumber))
        PageNewsTxt = ''
        for i in range(totalPageNumber): 
            if i == 0:
               temp_url = url; # webpage indices are  index; index_1; index_2,...
            else:
               temp_url = ('http://www.tj.gov.cn/xw/ztzl/tjsyqfk/yqtb/index_' +  
                   str(i) + '.html')
            # print(temp_url)           
            temp_res = requests.get(temp_url)   
            temp_res.encoding = 'utf-8'
            PageNewsTxt = PageNewsTxt + re.search('(<ul class="sub_list">)(.*?)(</ul>)',
                            temp_res.text, re.S).group(2)
            # print(PageNewsTxt)
            
        strTodayDate = getTodayDate()
    
        # save this page valid content in a record text file 
        file = open('RawPage_'+ strTodayDate + '.txt','w')
        file.write(PageNewsTxt)
        file.close()
        # sort:
        file1 = open(('RawPage_'+ strTodayDate + '.txt'), 'r') # 要去掉空行的文件 
        file2 = open(('疫情通报_items_'+ strTodayDate + '.txt'), 'w') # 生成没有空行的文件
        try:
            for line in file1.readlines():
                if not (re.search('[.*]',line) is None): # 包含任何字符
                    date = re.search('(<span class="date">)(.*?)(</span>)',line).group(2)
                    title = re.search('(target="_blank">)(.*?)(</a></li>)',line).group(2)
                    url = re.search('(href=")(.*?)(" target="_blank")',line).group(2)
                    if not ('..' in url):
                        temp_url = re.search(r'(./)(.*?)(.html)',url)
                        temp_url = temp_url[2]
                        latest_page_url = ('http://www.tj.gov.cn/xw/ztzl/tjsyqfk/yqtb/' + 
                          temp_url + '.html')
                    else:
                        temp_url = re.search(r'(/bdyw/)(.*?)(.html)',url)
                        temp_url = 'bdyw/'+ temp_url[2]
                        latest_page_url = ('http://www.tj.gov.cn/xw/' + 
                          temp_url + '.html')
                    file2.write(date+'\t' + title + '\t' + latest_page_url + '\n')
                    
                    
        finally:
            file1.close()
            file2.close()
        os.remove('RawPage_'+ strTodayDate + '.txt') 


  
def getLatestReport():
    # (1) get latest report url 
    strTodayDate = getTodayDate()
    file = open('疫情通报_items_'+ strTodayDate + '.txt','r')
    lines = file.readlines()
    firstLine = lines[0] # the first line is for today
    temp_url = re.search(r'(http.*.html)',firstLine)
    temp_url = temp_url[0]
    
    # (2) record the webpage 
    print(">>>> Requesting the website: " + temp_url + '...')
    try:
        res = requests.get(temp_url)    
    except IOError:
        print(">>>> Connection Error ")
    else:
        res.encoding = 'utf-8'
        ReportPageTxt = re.search(r'(<div class=TRS_Editor>)(.*?)(</div></div>)',
                           res.text,re.S).group(2)
        ReportPageTxt = re.sub("<.*?>", "", ReportPageTxt)
        ReportPageTxt = re.sub("&nbsp;", "", ReportPageTxt)
        ReportPageTime = re.search(r'(<meta name="PubDate" content=")(.*?)(" />)',
                           res.text,re.S).group(2)
        ReportPageTime = re.sub("[\:\-]", "", ReportPageTime) # year+month+day+hour+min        
        # print(ReportPageTxt + ' ' + ReportPageTime)
        # save in txt file
        file_1 = open('Raw_Report_content_'+ ReportPageTime + '.txt','w')
        file_1.write(ReportPageTxt)
        file_1.close()
        with open('Raw_Report_content_'+ ReportPageTime + '.txt','r') as fr,open('Report_content_'+ ReportPageTime + '.txt','w') as fw:
            for line in fr.readlines():
                fw.write(line.lstrip())
        fr.close()
        fw.close()
        os.remove('Raw_Report_content_'+ ReportPageTime + '.txt')
    file.close
        
def getHistoryReports():
    '''
    since this code is written in 20200209, 
    the history reports need to be collected 
    ''' 
    strTodayDate = getTodayDate()
    file = open('疫情通报_items_'+ strTodayDate + '.txt','r')
    lines = file.readlines()
    for line in lines:
        temp_url = re.search(r'http.*html',line)
        temp_page_url = temp_url[0]
        print(">>>> Requesting the website: " + temp_page_url + '...')
    
        try:
            res = requests.get(temp_page_url)    
        except IOError:
                print(">>>> Connection Error ")
        else:
            res.encoding = 'utf-8'
            ReportPageTxt = re.search(r'(<div class=TRS_Editor>)(.*?)(</div></div>)',
                                      res.text,re.S).group(2)
            ReportPageTxt = re.sub("<.*?>", "", ReportPageTxt)
            ReportPageTxt = re.sub("&nbsp;", "", ReportPageTxt)
            ReportPageTime = re.search(r'(<meta name="PubDate" content=")(.*?)(" />)',res.text,re.S).group(2)
            ReportPageTime = re.sub("[\:\-]", "", ReportPageTime) # year+month+day+hour+min        
            # print(ReportPageTxt + ' ' + ReportPageTime)
            # save in txt file
            file_1 = open('Raw_Report_content_'+ ReportPageTime + '.txt','w')
            file_1.write(ReportPageTxt)
            file_1.close()
            with open('Raw_Report_content_'+ ReportPageTime + '.txt','r') as fr,open('Report_content_'+ ReportPageTime + '.txt','w') as fw:
                for line in fr.readlines():
                    fw.write(line.lstrip())
                fr.close()
                fw.close()
            os.remove('Raw_Report_content_'+ ReportPageTime + '.txt')
       
    file.close()
    

    
def main():
    
    # (1) get all news titles in the news release pages
    getAllNewsUrls()
    
    # OPTIONAL： get history reports (for the first-time run) 
    getHistoryReports()
    
    # (2) get latest report 
    getLatestReport()
    
    

if __name__ == "__main__":
    main()
