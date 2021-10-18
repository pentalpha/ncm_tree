# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 16:58:09 2021

@author: pitagoras
"""

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
import requests
import pandas as pd
from bs4 import BeautifulSoup 
initial_cest = "https://www.confaz.fazenda.gov.br/legislacao/convenios/2015/CV092_15"
last_cest = "https://www.confaz.fazenda.gov.br/legislacao/convenios/2018/CV142_18"

#%%
class CestTable():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    months = {"JANEIRO": 1, "FEVEREIRO": 2, "MARÇO": 3,
            "ABRIL": 4, "MAIO": 5, "JUNHO": 6, "JULHO": 7,
            "AGOSTO": 8, "SETEMBRO": 9, "OUTUBRO": 10, 
            "NOVEMBRO": 11, "DEZEMBRO": 12}
    def __init__(self, icms_conv_url):
        self.url = icms_conv_url
        page = requests.get(self.url, verify=False, 
                            headers=CestTable.headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        self.rows = CestTable.rows_from_soup(soup)
        paragraphs = soup.find_all('p')
        paragraphs = [p.text for p in paragraphs 
                      if "CONVÊNIO ICMS " in p.text and ", DE " in p.text]
        print(paragraphs)
        if len(paragraphs) > 0:
            title_p = paragraphs[0]
            self.date = CestTable.ptbr_date_to_datetime(
                title_p.split(", DE ")[-1])
        else:
            self.date = []
        self.soup = soup
        
        self.write_table()
    
    def write_table(self, d="."):
        fname = "cest-table_"+"-".join(self.date)+".tsv"
        fpath = d+"/"+fname
        print("Writing to", fpath)
        with open(fpath,'w') as stream:
            stream.write("CEST\tNCM_LIST\tDESCRIPTION\n")
            for cest, ncms, descript, index in self.rows:
                row = ['"'+cest+'"', '"'+str(ncms)+'"', 
                       '"'+(descript.replace('"', ''))+'"']
                stream.write("\t".join(row)+"\n")
            
    def ptbr_date_to_datetime(date_txt):
        parts = date_txt.replace(" DE ", " ").split()
        month = CestTable.months[parts[1]]
        day = parts[0]
        year = parts[2]
        
        return [str(year), str(month), str(day)]
    
    def rows_from_soup(soup):
        rows = soup.find_all('tr')
        cest_rows = [CestTable.parse_cest_row(row) for row in rows]
        cest_rows = [x for x in cest_rows if x]
        cest_rows = [cest_rows[i] + [i] for i in range(len(cest_rows))]
        
        decimal_houses = len(str(cest_rows[-1][-1]))
        cest_rows.sort(key=(lambda row: 
                            float(row[0])
                            + row[-1]*pow(0.1, decimal_houses)
                        ))
        repetitions = 0
        i = 0
        max_i = len(cest_rows)-1
        while i < max_i:
            if cest_rows[i][0] == cest_rows[i+1][0]:
                print("Solving repetition of",
                      cest_rows[i][0],"in indexes",i,i+1)
                cest_before = cest_rows[i][0]
                len_before = len(cest_rows)
                print("\t",len_before, "total rows")
                before = []
                if i > 0:
                    before = cest_rows[:i]
                print("\t",len(before), "rows before")
                after = cest_rows[i+1:]
                print("\t",len(after), "rows after")
                cest_rows = before + after
                print("\t",len(cest_rows), "rows after solving")
                assert len(cest_rows) == len_before-1
                assert cest_rows[i][0] == cest_before
                repetitions += 1
                max_i = len(cest_rows)-1
            i += 1
        print(repetitions, "solved repetitions of CESTs")
        return cest_rows
        
    def is_ncm(txt):
        no_dots = txt.replace(".","")
        is_ncm = (len(no_dots) >= 2 and len(no_dots) <= 8 
                  and no_dots.isdigit())
        return (is_ncm, no_dots)
    
    def parse_cest_row(row):
        cols = [ele.text.strip() for ele in row.find_all('td')]
        cest_index = -1
        for i in range(len(cols)):
            val = cols[i]
            no_dots = val.replace(".","")
            if len(no_dots) == 7 and no_dots.isdigit():
                cest_index = i
                break
        if cest_index >= 0:
            cest = cols[cest_index].replace(".","")
            ncms = []
            ncm_index = -1
            for i in range(len(cols)):
                if i > cest_index:
                    vals = cols[i].split()
                    validation_results = [CestTable.is_ncm(val) 
                                          for val in vals]
                    all_true = all([x for x, y in validation_results])
                    if all_true:
                        ncm_index = i
                        ncms = [y for x, y in validation_results]
                        break
            description = ""
            for i in range(len(cols)):
                if i > cest_index and i > ncm_index:
                    val = cols[i]
                    no_dots = val.replace(".","")
                    if len(val) >= 4 and (not no_dots.isdigit()):
                        if len(val) > len(description):
                            description = val
            return [cest, ncms, description.lower()]
        else:
            return None

last_table = CestTable(last_cest)