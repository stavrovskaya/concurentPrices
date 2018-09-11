
# coding: utf-8

# In[6]:


import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import pandas as pd
import datetime
import re

class HealthTehnika():
    mainRef = "https://health-tehnika.ru"    
    
    @staticmethod
    def getPrices(ref):
        responce = requests.get(ref).text
        html = bs(responce, "lxml")

        tags = html.find_all("div", class_="product_preview-form_container row")
        prices = {}
        for tag in tags:
            subtag = tag.find("div", class_="product_preview-title")
            name = subtag.find("a").getText().strip()

            name = name.replace(u'\u2010',"-")
            price = tag.find("div", class_="prices-current").getText().strip("отр \n\r\t")

            price = price.replace("\xa0","")

            if price == 'Предзаказ':
                continue


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
            prices = HealthTehnika.getPrices(pageRef)
            allPrices.update(prices)
        return(allPrices)
    @staticmethod
    def printToFile(allPrices, fname):

        data = pd.DataFrame(list(allPrices.items()))
        data.columns = ["name","price"]

        data.sort_values("name").to_csv(fname, index = False, sep = ";", encoding='cp1251')
    @staticmethod
    def getAll(ref):

        refs = HealthTehnika.getPageRefs(ref)

        allPrices = HealthTehnika.getAllPrices(refs)

        return(allPrices)
    @staticmethod
    def getCatalogRefs(ref):
        refs = set()

        responce = requests.get(ref).text
        html = bs(responce, "lxml")

        megaCat = html.find("ul", class_="menu menu--main menu--main_lvl_1 menu--horizontal")

        colBlockTags = megaCat.findAll("li", class_="menu-node menu-node--main_lvl_1 js-menu-wrapper")
        for tag in colBlockTags:
            atag = tag.find("a")
            name = atag.getText().strip()

            if (name == "Акции") | (name == "Подарочные сертификаты") | (name == "Бренды"):
                continue

            refs.add(ref + atag['href'])

        return(refs)
    @staticmethod
    def parseSite():
        catRefs = HealthTehnika.getCatalogRefs(HealthTehnika.mainRef)


        allPrices = {}

        for ref in catRefs:

            print(ref)
            allPrices.update(HealthTehnika.getAll(ref))
        return(allPrices)
    
if __name__ == '__main__':    
    now = datetime.datetime.now()
    fname = "HealthTehnika_" + now.strftime("%d-%m-%Y") + ".csv"
    
    allPrices = HealthTehnika.parseSite()
    
    HealthTehnika.printToFile(allPrices, fname)


# In[89]:



    
    


# In[ ]:




