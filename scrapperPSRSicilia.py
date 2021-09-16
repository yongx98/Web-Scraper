# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# Import libraies

import requests, bs4
import re
import json

# Definizione delle funzioni

# a_editor() scrive il contenuto dei tag <a> nella forma: val("url")
def a_editor2(text):
    for a in text.find_all('a'):
        href = a.get('href')
        #molti link potrebbero essere scritti nella forma  
        #in questi casi sostituisco ../../../.. con http://www.psrsicilia.it
        if(href[:3]=="../"):
            href = "http://www.psrsicilia.it" + href[11:]
        a.append("(" + href + ")")
    
    return ""



file = open(r"C:\Users\yongt\OneDrive\Desktop\Tesi\risultato.txt", "w", encoding="utf-8")
 
## Web Crawling
#Essendo i bandi suddivisi tra aperti e chiusi,
#per semplicità considero solo quelli aperti.
initial_page = requests.get("http://www.psrsicilia.it/2014-2020/psr-bandieavvisi.php")
try:
    initial_page.raise_for_status()
except Exception:
    print("Cannot read the first website")
    initial_page = ""
parser = bs4.BeautifulSoup(initial_page.text, 'html.parser')
#Ricerca per contenuto, non essendoci caratteristiche particolari nel tag <a>
#cerco direttamente il stringa "Bandi aperti" e uso find_parent() per trovare 
#il tag <a> che contiene l'indirizzo della lista dei bandi aperti
string_bando = parser.find(string="Bandi aperti")
url_aperti = string_bando.find_parent("a")
page = url_aperti.get("href")
web = requests.get(page)
try:
    web.raise_for_status()
except Exception:
    print("Cannot read the first website")
    web = ""
parser = bs4.BeautifulSoup(web.text, 'html.parser')
#In questo caso i ci sono sono altri link da aprire perchè gli articoli dei bandi
#sono tutti su un'unica pagina
#La descrizione dei bandi è contenuta nel tag <div id="description-content">
main_content = parser.find('div', id="description-content")
#Ognuno degli articoli è contenuto in un tag <div id="description-reg-eur">
for article in main_content.find_all('div', id="description-reg-eur"):
    a_editor2(article)
    Bando = {}
    #il titolo del bando si trova nel tag <div class="b-title">
    title = article.find('div', class_="b-title")
    Bando["Nome"] = title.string
    #Dopo il titolo ci sono dei tag <div id="b-title-reg-eur">
    #Il primo è una descrizione del bando
    arguments = article.find_all('div', id="b-title-reg-eur")
    description = arguments[0].string
    Bando["Descrizione"] = description
    #Dal secondo in poi sono aggiornamenti
    for update in arguments[1:]:
        first = True
        end = False
        val_content=""
        val_attach=""

        contents = update.stripped_strings
        for text in contents:
            if(first == True):
                date = text
                first = False
            elif(end == False):
                if(text=="Documenti allegati:"):
                    end = True
                else:
                    val_content = val_content + text + " "
            else:
                val_attach = val_attach + text + " "
        val_attach = re.sub(r"\n *", "", val_attach)
        Bando[date] = val_content
        Bando["Allegati " + date] = val_attach
    file.write(json.dumps(Bando, ensure_ascii=False, indent=""))    
    file.write("\n\n\n")
        
        
    

    
        
file.close()
        



