
# coding: utf-8

# In[3]:


import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import pandas as pd
import datetime
import re

class MadeInDream():
    mainRef = "https://madeindream.com"
    @staticmethod
    def getPrices(ref):
        responce = requests.get(ref).text
        html = bs(responce, "lxml")

        tags = html.find_all("div", class_="product-thumb clearfix grid_3")
        prices = {}
        for tag in tags:
            nameTag = tag.find("div", class_="name")
            name = nameTag.find("a").getText().strip()
            name = name.replace(u'\u2010',"-")
            price = tag.find("div", class_="price").getText().strip("₽ \n\r")
            res = re.search(r"(\d+)₽\n\d+",price)
            if(res):
                price = res.group(1)

            if (int(price) != 0):
                prices[name] = price
        return(prices)
    @staticmethod
    def getPageRefs(ref):
        responce = requests.get(ref).text
        html = bs(responce, "lxml")

        pageNumTags = html.find("div", class_="results")

        if pageNumTags == None:
            return([ref])

        res = re.search(r"Показано с \d+ по \d+ из \d+ \(всего (\d+) страниц\)", pageNumTags.getText())


        lastPageNum = int(res.group(1))

        refs = [ref + "?page=" + str(x) for x in range(2,lastPageNum + 1)]
        refs = [ref] + refs
        return(refs)
    @staticmethod
    def getAllPrices(refs):
        allPrices = {}

        for pageRef in refs:
            prices = MadeInDream.getPrices(pageRef)
            allPrices.update(prices)
        return(allPrices)
    @staticmethod
    def printToFile(allPrices, fname):

        data = pd.DataFrame(list(allPrices.items()))
        data.columns = ["name","price"]

        data.sort_values("name").to_csv(fname, index = False, sep = ";", encoding='cp1251')
    @staticmethod
    def getAll(ref):

        refs = MadeInDream.getPageRefs(ref)

        allPrices = MadeInDream.getAllPrices(refs)

        return(allPrices)
    @staticmethod
    def getCatalogRefs(ref):
        refs = set()

        responce = requests.get(ref).text
        html = bs(responce, "lxml")

        megaCat = html.find("ul", class_="mega-category")

        colBlockTags = megaCat.findAll("li")
        for tag in colBlockTags:
            atag = tag.find("a")

            if atag['href'].find("?filter_tag=")>0:
                continue
            result = re.search(r'(.*/)[^/]+/$', atag['href'])
            cat = result.group(1)

            if cat in refs:
                continue

            refs.add(atag['href'])

        return(refs)
    @staticmethod
    def parseSite():
        catRefs = MadeInDream.getCatalogRefs(MadeInDream.mainRef)
    
        allPrices = {}

        for ref in catRefs:

            print(ref)
            allPrices.update(MadeInDream.getAll(ref))

        return(allPrices)
    
if __name__ == '__main__':    
    now = datetime.datetime.now()
    fname = "MadeInDream_" + now.strftime("%d-%m-%Y") + ".csv"
    
    allPrices = MadeInDream.parseSite()
    
    MadeInDream.printToFile(allPrices, fname)    

