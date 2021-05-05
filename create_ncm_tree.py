import pandas as pd
import networkx as nx
from tqdm import tqdm
from networkx.readwrite import json_graph
import json

ncm_df = pd.read_csv('ncms.tsv', sep='\t')
df_copy = ncm_df.copy()

def expand_name(ncm, name, aux_df):
    shorter_code = ncm[:-1]
    sliced = aux_df[aux_df['ncm'] == shorter_code]
    if len(sliced) > 0:
        shorter_name = sliced['nome'].tolist()[0]
        if shorter_name[-1] != ":":
            shorter_name = shorter_name+":"
        name = shorter_name + " " + name
    return name

def longest(strs):
    longer_i = 0
    for i in range(len(strs)):
        if len(strs[i]) > len(strs[longer_i]):
            longer_i = i
    return strs[longer_i]

def define_parent(ncm, valid_codes):
    parts = ncm.split('.')
    if len(parts) == 1:
        return 'Raiz'
    else:    
        candidate_parts = parts[:-1]
        while not (".".join(candidate_parts) in valid_codes):
            print(ncm + ": Candidate parent", ".".join(candidate_parts),
                  "not found. Trying next relative.")
            candidate_parts = candidate_parts[:-1]
        return ".".join(candidate_parts)
    
#expand names to eliminate codes with odd length
ncm_df['nome'] = ncm_df.apply(
    lambda row: expand_name(row['ncm'], row['nome'], df_copy),
    axis=1)
ncm_df['odd_code'] = ncm_df.apply(
    lambda row: (len(row['ncm'].split('.')[-1]) % 2) != 0,
    axis=1)
ncm_df = ncm_df[ncm_df['odd_code'] == False]
del ncm_df['odd_code']

#find parent for each NCM
tree_df = ncm_df.copy()
valid_ncms = set(tree_df['ncm'].tolist())
tree_df['pai'] = tree_df.apply(
    lambda row: define_parent(row['ncm'], valid_ncms),
    axis=1)

#save in graph format
graph = nx.from_pandas_edgelist(tree_df, "ncm", "pai")
data = json_graph.adjacency_data(graph)
s = json.dumps(data)
open("ncm_tree.json", 'w').write(s)