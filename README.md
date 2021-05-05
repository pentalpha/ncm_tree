# NCM Tree
NCM (Nomenclatura Comum do Mercosul) are codes used to classify products in South America. The NCM is an expansion of the Harmonized System (HS), used worldwide. The NCM has a hierarquical structure, with each category being part of a parent category. Each NCM category is represented by a code of 2,4,6 or 8 digits and has a textual description.

## Good specifications are not easily available for NCM codes
Unfortunately, official sources do not publish easily parseable files with the codes and their names. No Excel, CSV or JSON is available. There are only code-consult webpages and PDF files. 

## So I created the parseable NCM files
In order to make development of software who use NCM codes easier, I created this project to scrap and parse the tree of NCM codes, as well as the textual descriptions.

## The files:

- ncms.tsv: The codes, their descriptions and parent codes;
- ncm_tree.json: The NCM tree edges in JSON format, can be loaded using NetworkX library;