
# coding: utf-8

# In[3]:


import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import pandas as pd
import datetime

class VseSoki():
    mainRef = "http://vsesoki.ru"

    @staticmethod
    def getPrices(ref):
        responce = requests.get(ref).text
        html = bs(responce, "lxml")

        tags = html.find_all("div", class_="prod-block")
        prices = {}
        for tag in tags:
            name = tag.find("p", class_="title").getText().strip()
            price = tag.find("p", class_="price").getText().strip(" руб.")
            if (int(price) != 0):
                prices[name] = price
        return(prices)
    @staticmethod
    def getPageRefs(ref):
        responce = requests.get(ref).text
        html = bs(responce, "lxml")

        pageNumTags = html.find("div", class_="pagination fr")
        if pageNumTags == None:
            return([ref])

        pageNums = pageNumTags.getText().split()
        lastPageNum = int(pageNums[-1])

        refs = [ref + "?page=" + str(x) for x in range(2,lastPageNum + 1)]
        refs = [ref] + refs
        return(refs)
    @staticmethod
    def getAllPrices(refs):
        allPrices = {}

        for pageRef in refs:
            prices = VseSoki.getPrices(pageRef)
            allPrices.update(prices)
        return(allPrices)
    @staticmethod
    def printToFile(allPrices, fname):

        data = pd.DataFrame(list(allPrices.items()))
        data.columns = ["name","price"]

        data.sort_values("name").to_csv(fname, index = False, sep = ";", encoding='cp1251')

    @staticmethod
    def getAll(ref):

        refs = VseSoki.getPageRefs(ref)

        allPrices = VseSoki.getAllPrices(refs)

        return(allPrices)
    @staticmethod
    def getCatalogRefs(ref):
        refs = []

        responce = requests.get(ref).text
        html = bs(responce, "lxml")

        colBlockTags = html.findAll("div", class_="col-block")
        for tag in colBlockTags:
            ptag = tag.find("p")
            atag = ptag.find("a")
            refs.append(ref + atag['href'])

        return(refs)
    @staticmethod
    def parseSite():
        catRefs = VseSoki.getCatalogRefs(VseSoki.mainRef)
    
        allPrices = {}

        for ref in catRefs:

            print(ref)
            allPrices.update(VseSoki.getAll(ref))

        return(allPrices)
    
    
if __name__ == '__main__':    
    now = datetime.datetime.now()
    fname = "VseSoki_" + now.strftime("%d-%m-%Y") + ".csv"
    
    allPrices = VseSoki.parseSite()

    VseSoki.printToFile(allPrices, fname)
    
    

