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

# Function a_editor() writes the content of <a> tags like: val("url")
def a_editor(text):
    for a in text.find_all('a'):
        href = a.get('href')
        a.append("(" + href + ")")
    
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
    #Selecting the main contents of the page
    main_content = art_parser.find('div', attrs={"role":"main"})
    #Extracting title
    name = main_content.find('h1', class_="single-title").contents[0].string
    Bando["Nome"] = name
    #Extracting publication date
    date = main_content.find('div', attrs={"class":"byline vcard"}).contents[0].string
    Bando["Data di pubblicazione"] = date
    
    ### Extracting data, everything I need is collected in the tag <section> with attribute
    ### itemprop = "articleBody"
    article_body = main_content.find("section", attrs={"itemprop":"articleBody"})
    
    ### There are 4 classes of informations: bando details, pdf, related contents,
    ### related pdf, and staff members
    ### Bando details are saved in tags <p> or <ul> or <ol>
    details = article_body.find_all(['p','ul','ol','div'], recursive = False)
    details_text = ""
    for tag in details:
        if (tag.name == 'p'):
            a_editor(tag)
            for text in tag.stripped_strings:
                details_text = details_text + text + " "
        elif (tag.name == 'ul'):
            a_editor(tag)
            for text in tag.find_all('li'):
                details_text = details_text + "-"
                for t in text.stripped_strings:
                    details_text = details_text + t + " "
        elif (tag.name == 'ol'):
            a_editor(tag)
            i = 1
            for text in tag.find_all('li'):
                details_text = details_text + str(i) +"."
                for t in text.stripped_strings:
                    details_text = details_text + t + " "
                i+=1
        elif(tag.name == 'div' and tag.get('class')[0] == "page"):
            a_editor(tag)
            sec_details = tag.find_all(['p','ul','ol'])
            for sec_tag in sec_details:
                if (sec_tag.name == 'p'):
                    for text in sec_tag.stripped_strings:
                        details_text = details_text + text + " "
                elif (sec_tag.name == 'ul'):
                    for text in sec_tag.find_all('li'):
                        details_text = details_text + "-"
                        for t in text.stripped_strings:
                            details_text = details_text + t + " "
                elif (sec_tag.name == 'ol'):
                    i = 1
                    for text in sec_tag.find_all('li'):
                        details_text = details_text + str(i) +"."
                        for t in text.stripped_strings:
                            details_text = details_text + t + " "
                        i+=1
    Bando["Dettagli"] = details_text
    ### PDF are saved in <div> tag with w3eden word in tag class
    ### related contents are in <div> tag with class = "contenuti-collegati-ul"
    ### related PDF are in the same tags as PDF but after related contents
    ### staff members are in <div> tag with class = "staff-directory"
    others = article_body.find_all('div', recursive=False)
    pdf_counter = 0
    related_contents_counter = 0
    related_pdf_counter = 0
    staff_counter = 0
    for element in others:
        if(element.get('class')[0]=="w3eden" and related_contents_counter==0):
            a_editor(element)
            pdf_counter += 1
            a_tag = element.find('div', class_="media-body")
            a_tag = a_tag.find('a')
            dic_name = "Allegati" + str(pdf_counter)
            pdf_url=""
            for text in a_tag.stripped_strings:
                pdf_url = pdf_url + text
            Bando[dic_name] = pdf_url
        elif(element.get('class')[0]=="contenuti-collegati-ul"):
            a_editor(element)
            a_tags = element.find_all('a')
            for points in a_tags:
                related_contents_counter += 1
                dic_name = "Contenuto Collegati" + str(related_contents_counter)
                pdf_url=""
                for text in a_tag.stripped_strings:
                    pdf_url = pdf_url + text
                Bando[dic_name] = pdf_url
        elif(element.get('class')[0]=="w3eden" and related_contents_counter>0):
            a_editor(element)
            related_pdf_counter += 1
            a_tag = element.find('div', class_="media-body")
            a_tag = a_tag.find('a')
            dic_name = "PDF Collegati" + str(related_pdf_counter)
            pdf_url=""
            for text in a_tag.stripped_strings:
                pdf_url = pdf_url + text
            Bando[dic_name] = pdf_url
        elif(element.get('class')[0]=="staff-directory"):
            staff_counter += 1
            name_staff = element.find('h3', class_=False).string
            role = ""
            for staff_info in element.find_all('span', 
                                               class_=re.compile("olo-red-label"),
                                               string = True):
                role = role + ", " + staff_info.string
            contacts = ""
            for contact_info in element.find('div', class_= "olo-staff-field-cont").contents:
                for text in contact_info.stripped_strings:
                    contacts = contacts + ", " + text
            staff = name_staff + role + contacts
            dic_name = "Responsabile" + str(staff_counter)
            Bando[dic_name] = staff
                    
            
            
    
    
    
    
    # Writing on file
    file.write(json.dumps(Bando, ensure_ascii=False, indent=""))    
    file.write("\n\n\n")

# Reading websites

web3 = requests.get("https://www.euroinfosicilia.it/po-fesr-sicilia-2014-2020/bandi-e-avvisi/")
web4 = requests.get("http://www.psrsicilia.it/2014-2020/psr-bandieavvisi.php")
web5 = requests.get("http://www.gurs.regione.sicilia.it/gursmenu.php")



## Opening the file where I will write extracted data
file = open(r"C:\Users\yongt\OneDrive\Desktop\Tesi\risultato.txt", "w", encoding="utf-8")
 
## Web Crawling
initial_page = requests.get("https://www.euroinfosicilia.it/po-fesr-sicilia-2014-2020/bandi-e-avvisi/")
try:
    initial_page.raise_for_status()
except Exception:
    print("Cannot read the first website")
    initial_page = ""
parser = bs4.BeautifulSoup(initial_page.text, 'html.parser')
main_content = parser.find("div", attrs={"class":"wpb_column vc_column_container vc_col-sm-8 mpc-column"})
url_aperti = main_content.find("a", attrs={"class":"olo-content-box-bandi color-aperti"})
pages = [url_aperti.get("href")]
for p in pages:
    web = requests.get(p)
    try:
        web.raise_for_status()
    except Exception:
        print("Cannot read the first website")
        web = ""
    parser = bs4.BeautifulSoup(web.text, 'html.parser')
    main_content = parser.find("div", attrs={"class":"wpb_column vc_column_container vc_col-sm-8 mpc-column"})
    bandi = parser.find_all("div", attrs={"class":"mpc-post"})
    for site in bandi:
        header_bando = site.find("h3", attrs={"class":"mpc-post__heading mpc-transition"})
        url = header_bando.find("a").get('href')
        scrap(url,file)
    pagelist = main_content.find_all("li", attrs={"data-page":"next"})
    for nextpage in pagelist:
        
        nextpageurl = nextpage.find("a").get('href')
        print(nextpageurl)
        pages.append(nextpageurl)

    
        
file.close()
        



