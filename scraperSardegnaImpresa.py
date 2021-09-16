# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# Import libraies

import requests, bs4
import re
import json

# Functions definition

# Function a_remover() removes <a> tags like; <a href="url">val</a>
# and writes the content like: val("url")
def a_remover(text):
    for a in text.find_all('a'):
        href = a.get('href')
        a.append("(" + href + ")")
        a.unwrap()
    
    return ""
def scrap(url,file):
    ## Creating Bando dictionary that contains the data I have to extract.
    ## Key = label, Value = item
    Bando = {}
    ## Opening articles' website to extract data
    article = requests.get(url)
    try:
        article.raise_for_status()
    except Exception:
        print("error")
        article = ""
    art_parser = bs4.BeautifulSoup(article.text, 'html.parser')
    
    #Extracting title
    name = art_parser.find('h1', class_="page-header").contents[0].string
    Bando["Nome"] = name
    ### Extracting data, everything I need is collected in the tag <div> with attribute
    ### class = "content"
    
    content = art_parser.find("div", class_="region region-content")
    content = content.find("div", class_="content")
    
    fields = content.find_all("div", recursive=False)   
    
    for field in fields:
        if(field.get('class')[0] == 'pdf'):
            pdf = field.find("a").get('href')
            pdf = "https://www.sardegnaimpresa.eu"+pdf
            Bando["pdf"] = pdf
        else:
            # Using a_remover to edit links and to remove 'a' tags
            a_remover(field)
            label = field.find(class_="field--label").string
            # Item tag's name can be 'field--item' or 'field__items' so I use 
            # re.compile() to find both situations
            item = field.find(class_= re.compile("field--item|field__items")).contents
            # Item's value can contain some HTML code in addition to text.
            # Cleaning item's value 
            value = ""
            
            for text in item:
                if (text.name == 'ul'):
                    value = value + " -"
                    for elem in text.find_all('li'):
                        for val in elem.stripped_strings:
                            value = value + val
                        value = value + ". -"
                    value = value[0:-3] + "    "
                else:
                    for val in text.stripped_strings:
                        value = value + val + " " 
               
                    
                       
            value = re.sub(r" {5,20}", "", value)
            
            Bando[label] = value
    
    # Writing on file
    file.write(json.dumps(Bando, ensure_ascii=False, indent=""))    
    file.write("\n\n\n")

# Reading websites

web1 = requests.get("https://sardegnaimpresa.eu/it/agevolazioni")
web3 = requests.get("https://www.euroinfosicilia.it/po-fesr-sicilia-2014-2020/bandi-e-avvisi/")
web4 = requests.get("http://www.psrsicilia.it/2014-2020/psr-bandieavvisi.php")
web5 = requests.get("http://www.gurs.regione.sicilia.it/gursmenu.php")



## Opening the file where I will write extracted data
file = open(r"C:\Users\yongt\OneDrive\Desktop\Tesi\risultato.txt", "w", encoding="utf-8")
 
## Web Crawling
pages = ["https://sardegnaimpresa.eu/it/agevolazioni"]
for p in pages:
    web = requests.get(p)
    try:
        web.raise_for_status()
    except Exception:
        print("Connection failed")
        web = ""
    parser = bs4.BeautifulSoup(web.text, 'html.parser')
    
    contents = parser.find("div", attrs={"role":"main"})
    bandi = contents.find_all("a", attrs={"rel":"bookmark"})
    for site in bandi:
        url = site.get('href')
        url = "https://www.sardegnaimpresa.eu"+url
        scrap(url,file)

    pagelist = parser.find_all("a", attrs={"rel":"next"})
    for nextpage in pagelist:
        nextpageurl = "https://sardegnaimpresa.eu/it/agevolazioni" + nextpage.get('href')
        pages.append(nextpageurl)

    
        
file.close()
        



