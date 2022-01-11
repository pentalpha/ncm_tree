#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  5 15:05:35 2021

@author: pitagoras
"""
#import requests
import pandas as pd
from tqdm import tqdm
import roman

ncm_url = "https://balanca.economia.gov.br/balanca/bd/tabelas/NCM.csv"
sh_url = "https://balanca.economia.gov.br/balanca/bd/tabelas/NCM_SH.csv"

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
    '''while parts[-1] == '00':
        parts = parts[:-1]'''
    return ".".join(parts)

def download_codes(ncm_url, sh_url):
    ncm_df = pd.read_csv(
        ncm_url,
        encoding ='ISO-8859-1',
        sep=';',
        dtype=str)
    
    ncm_df['ncm'] = ncm_df['CO_NCM']
    ncm_df['descricao'] = ncm_df['NO_NCM_POR']
    ncm_df = ncm_df[['ncm', 'descricao']]
    
    sh_df = pd.read_csv(sh_url,
        encoding ='ISO-8859-1',
        sep=';',
        dtype=str)
    
    sh_df['SH6'] = sh_df['CO_SH6']
    sh_df['SH6_DESCRICAO'] = sh_df['NO_SH6_POR']
    sh_df['SH4'] = sh_df['CO_SH4']
    sh_df['SH4_DESCRICAO'] = sh_df['NO_SH6_POR']
    sh_df['SH2'] = sh_df['CO_SH2']
    sh_df['SH2_DESCRICAO'] = sh_df['NO_SH2_POR']
    sh_df['SEC'] = sh_df['CO_NCM_SECROM']
    sh_df['SEC_DESCRICAO'] = sh_df['NO_SEC_POR']
    sh_df = sh_df[['SH6', 'SH6_DESCRICAO', 'SH4', 'SH4_DESCRICAO',
                   'SH2', 'SH2_DESCRICAO', 'SEC', 'SEC_DESCRICAO']]
    
    sh_df['SEC'] = sh_df['SEC'].apply(lambda x: str(roman.fromRoman(x)))
    #sh_df['SEC'] = sh_df['SEC'].apply(lambda x: x if len(x) == 2 else '0'+x)
    
    codes = {}
    cap_to_section = {}
    for i, row in ncm_df.iterrows():
        codes[treat_ncm(row['ncm'])] = treat_description(row['descricao'])
    
    for i, row in sh_df.iterrows():
        codes[treat_ncm(row['SH6'])] = treat_description(row['SH6_DESCRICAO'])
        codes[treat_ncm(row['SH4'])] = treat_description(row['SH4_DESCRICAO'])
        codes[treat_ncm(row['SH2'])] = treat_description(row['SH2_DESCRICAO'])
        sec = 'secao'+row['SEC']
        cap_to_section[treat_ncm(row['SH2'])] = sec
        codes[sec] = treat_description(row['SEC_DESCRICAO'])
        
    return codes, cap_to_section
#%%
#df = get_all_ncms()
#df.to_csv("ncms.tsv",sep='\t',index=False)

codes, cap_to_section = download_codes(ncm_url, sh_url)

lines = []
for code, desc in codes.items():
    parts = code.split(".")
    parent = ".".join(parts[:-1])
    if 'secao' in code:
        parent = "Raiz"
    elif not parent in codes:
        parent = cap_to_section[code]
    if len(parent) > 0:
        lines.append({"nome": desc, 'ncm': code, 'pai': parent})
    else:
        print("incorrento:")
        print(code, desc, parent)
lines.sort(key=lambda x: len(x['ncm']))
df = pd.DataFrame(lines)
df.to_csv("ncms.tsv", sep='\t', index=False, encoding='utf-8')