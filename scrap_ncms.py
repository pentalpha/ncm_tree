#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  5 15:05:35 2021

@author: pitagoras
"""
#import requests
import pandas as pd
#from bs4 import BeautifulSoup as bs
from tqdm import tqdm
ncm_base_url = "https://www.qualncm.com.br/ncm/"

def get_ncm_chapter_url(chapter_int):
    s = str(chapter_int)
    if chapter_int < 10:
        s = '0'+s
    return ncm_base_url+s

def verify_ncm_code(code):
    no_dots = code.replace('.','')
    return no_dots.isdigit()

def split_ncm(code_str, length = 2):
    list_of_strings = []
    for i in range(0, len(code_str), length):
        list_of_strings.append(code_str[i:length+i])
    return list_of_strings

def treat_description(raw_description):
    description = raw_description.lower()
    #add spaces after ponctuation
    for ponct in ['.', ',', ':', ';']:
        if ponct in description:
            parts = description.split(ponct)
            new_parts = []
            if len(parts) == 1:
                new_parts = parts
            else:
                new_parts.append(parts[0])
                for part in parts[1:]:
                    if len(part) == 0:
                        new_parts.append(part)
                    elif part[0] == ' ':
                        new_parts.append(part)
                    elif part[0] != ' ':
                        new_parts.append(' ' + part)
            description = ponct.join(new_parts)
    return description

def treat_ncm(raw_code):
    no_dots = raw_code.replace('.','')
    parts = split_ncm(no_dots)
    while parts[-1] == '00':
        parts = parts[:-1]
    return ".".join(parts)

def get_chapter_df(chapter_int):
    try:
        dfs = pd.read_html(get_ncm_chapter_url(chapter_int))
    except Exception as ex:
        print("Exception when retrieving", chapter_int, ":", ex)
        return None
    if len(dfs) == 0:
        return None
    else:
        if len(dfs[0]) == 0:
            return None
        
    df = dfs[0]
    df['valid_ncm'] = df.apply(lambda row: verify_ncm_code(row[0]), axis=1)
    df = df[df['valid_ncm'] == True].copy()
    df['nome'] = df.apply(lambda row: treat_description(row[1]), axis=1)
    df['ncm'] = df.apply(lambda row: treat_ncm(row[0]), axis=1)
    del df[0]
    del df[1]
    del df['valid_ncm']
    df = df.drop_duplicates(subset=['ncm'])
    return df

def get_all_ncms():
    chapters = list(range(1,100))
    ncm_df = get_chapter_df(chapters[0])
    for chapter in tqdm(chapters[1:]):
        ncm_df = ncm_df.append(get_chapter_df(chapter))
    return ncm_df

df = get_all_ncms()
df.to_csv("ncms.tsv",sep='\t',index=False)
