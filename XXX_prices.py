
# coding: utf-8

# In[21]:


from feed_parser import FeedParser
from VseSoki import VseSoki
from HealthTehnika import HealthTehnika
from MadeInDream import MadeInDream
import pandas as pd
import re
import sys
import datetime
import pymorphy2
morph=pymorphy2.MorphAnalyzer()

import pygsheets
#in case of time out
#pygsheets.client.GOOGLE_SHEET_CELL_UPDATES_LIMIT=5000

gc = pygsheets.authorize()


# In[31]:


def prepareName(name):
    name_pr = re.sub(r"[-(),_+/'`]", " ", name)
    name_pr = name_pr.replace(" для ", " ")
    names = name_pr.lower().split()
    
    
    return(names)

def distance(words1, words2):
    w1_set = set(words1)
    w2_set = set(words2)
    intersection = len(w1_set.intersection(w2_set))
    union = len(w1_set.union(w2_set))
    
    if(intersection == 1):
        return(0)
    
    return(1.0*intersection/union)

def bestBidirectionalHit(query, reference):
    listQueryBestHit = {}
    listRefBestHit = {}
    bestBidirectionalHit = []
    
    for i in range(query.shape[0]):
        words1 = query.iloc[i,0]
        name1 = query.iloc[i,1]
        listQueryBestHit[name1] = ["",0]
        for j in range(reference.shape[0]):
            words2 = reference.iloc[j,0]
            name2 = reference.iloc[j,1]
            if name2 not in listRefBestHit:
                listRefBestHit[name2] = ["",0]            
            
            dist = distance(words1, words2)
            if listQueryBestHit[name1][1] < dist:
                listQueryBestHit[name1] = [name2, dist]
            if listRefBestHit[name2][1] < dist:
                listRefBestHit[name2] = [name1, dist]
            
    
    for name1 in query.name:
        
        name2 = listQueryBestHit[name1][0]
        if name2 == '':
            name3 = ''
        else:
            name3 = listRefBestHit[name2][0]
        if  name1 == name3:
            bestBidirectionalHit.append(name2)
        else:
            bestBidirectionalHit.append(None)
    return(bestBidirectionalHit)

def bestBidirectionalHitDataFrame(gt_df, df):
    name = bestBidirectionalHit(gt_df.loc[:,("words","name")], df.loc[:,("words","name")])
    bbh = pd.DataFrame({"name":name})
    bbh = bbh.merge(df, how='left', on="name")
    bbh = bbh[["name", "price"]]
    return(bbh)

def printToExcel(gt_df_res, vs_df, ht_df, md_df, writer):
    gt_df_res.to_excel(writer,'XXX_to_all', index = False)

    vs_df.to_excel(writer,'VseSoki', index = False)
    ht_df.to_excel(writer,'HealthTehnika', index = False)
    md_df.sort_values("name").to_excel(writer,'MadeInDream', index = False)

    workbook  = writer.book
    worksheet = writer.sheets['XXX_to_all']

    text_format = workbook.add_format({'text_wrap': True})
    worksheet.set_column('A:A', 50, text_format)
    worksheet.set_column('C:C', 50, text_format)
    worksheet.set_column('E:E', 50, text_format)
    worksheet.set_column('G:G', 50, text_format)

    money_format = workbook.add_format({'num_format': '0'})
    worksheet.set_column('B:B', 15, money_format)
    worksheet.set_column('D:D', 15, money_format)
    worksheet.set_column('F:F', 15, money_format)
    worksheet.set_column('H:H', 15, money_format)

    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'align': 'center',
        'fg_color': '#D7E4BC',
        'border': 1})
    for col_num, value in enumerate(gt_df_res.columns.values):
        worksheet.write(0, col_num, value, header_format)


    worksheet = writer.sheets['VseSoki']
    worksheet.set_column('A:A', 50, text_format)
    worksheet.set_column('B:B', 15, money_format)

    for col_num, value in enumerate(vs_df[["name", "price"]].columns.values):
        worksheet.write(0, col_num, value, header_format)


    worksheet = writer.sheets['HealthTehnika']
    worksheet.set_column('A:A', 50, text_format)
    worksheet.set_column('B:B', 15, money_format)

    for col_num, value in enumerate(ht_df[["name", "price"]].columns.values):
        worksheet.write(0, col_num, value, header_format)


    worksheet = writer.sheets['MadeInDream']
    worksheet.set_column('A:A', 50, text_format)
    worksheet.set_column('B:B', 15, money_format)

    for col_num, value in enumerate(md_df[["name", "price"]].columns.values):
        worksheet.write(0, col_num, value, header_format)


    writer.save()
    writer.close()
    
def removeNull(df):
    dfNoNull = df.apply(lambda x: x.astype("object"),1)

    dfNoNull[pd.isnull(dfNoNull)]=''
    
    return(dfNoNull)

def printToGoogleSpreadsheets(gt_df_res, vs_df, ht_df, md_df, gsprshtBook):
    now = datetime.datetime.now()
    sht0 = gsprshtBook.worksheet_by_title("Дата обновления")
    sht0.update_cell('A1', now.strftime("%d-%m-%Y %H:%M:%S"))
    
    sht1 = gsprshtBook.worksheet_by_title("XXX_to_all")
    sht1.clear()
    sht1.set_dataframe(removeNull(gt_df_res),(1,1))

    sht2 = gsprshtBook.worksheet_by_title("VseSoki")
    sht2.clear()
    sht2.set_dataframe(vs_df,(1,1))

    sht3 = gsprshtBook.worksheet_by_title("HealthTehnika")
    sht3.clear()
    sht3.set_dataframe(ht_df,(1,1))

    sht4 = gsprshtBook.worksheet_by_title("MadeInDream")
    sht4.clear()
    sht4.set_dataframe(md_df,(1,1))   


# In[3]:




feedUrl = "XXX" 


if __name__ == '__main__':
    feedParser = FeedParser(feedUrl)
    print(feedParser.get_offer_count())
    gt_df = feedParser.url_offer_df.loc[feedParser.url_offer_df.available,["name","price"]]
    gt_df = gt_df.reset_index(drop=True)
    gt_df["name"] = [x.replace(u'\u2069'," ") for x in gt_df.name] 
    
    vs_dict = VseSoki.parseSite()

    vs_df = pd.DataFrame(list(vs_dict.items()))
    vs_df.columns = ["name","price"]
    
    ht_dict = HealthTehnika.parseSite()

    ht_df = pd.DataFrame(list(ht_dict.items()))
    ht_df.columns = ["name","price"]
    md_dict = MadeInDream.parseSite()

    md_df = pd.DataFrame(list(md_dict.items()))
    md_df.columns = ["name","price"]
    vs_df["words"] = vs_df.name.astype(str).apply(prepareName)

    ht_df["words"] = ht_df.name.astype(str).apply(prepareName)

    md_df["words"] = md_df.name.astype(str).apply(prepareName)

    gt_df["words"] = gt_df.name.astype(str).apply(prepareName)

    vs_bbh = bestBidirectionalHitDataFrame(gt_df, vs_df)
    ht_bbh = bestBidirectionalHitDataFrame(gt_df, ht_df)
    md_bbh = bestBidirectionalHitDataFrame(gt_df, md_df)

    gt_df_res = gt_df[["name", "price"]]
    gt_df_res[["VseSoki name", "VseSoki price"]] = vs_bbh

    gt_df_res[["HealthTehnika name", "HealthTehnika price"]] = ht_bbh
    gt_df_res[["MadeInDream name", "MadeInDream price"]] = md_bbh


    gt_df_res = gt_df_res.sort_values("name")
    vs_df = vs_df[["name", "price"]].sort_values("name")
    ht_df = ht_df[["name", "price"]].sort_values("name")
    md_df = md_df[["name", "price"]].sort_values("name")


#     now = datetime.datetime.now()
#     writer = pd.ExcelWriter('XXX_prices' + now.strftime("%d-%m-%Y") + '.xlsx')
#     printToExcel(gt_df_res, vs_df, ht_df, md_df, writer)

    googleSpreadsheets = 'XXX'
    googleSpreadsheetsBook = gc.open_by_key(googleSpreadsheets)
    printToGoogleSpreadsheets(gt_df_res, vs_df, ht_df, md_df, googleSpreadsheetsBook)


# In[32]:


printToGoogleSpreadsheets(gt_df_res, vs_df, ht_df, md_df, googleSpreadsheetsBook)


# In[27]:


sht1 = googleSpreadsheetsBook.worksheet_by_title("XXX_to_all")
sht1.clear()
cleaned = removeNull(gt_df_res)
sht1.set_dataframe(cleaned,(1,1))

