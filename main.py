from bs4 import BeautifulSoup
import requests
import os.path
import sendslack

url = "https://sg.kobobooks.com/collections/ereaders"
urlprefix = "https://sg.kobobooks.com"

soup = BeautifulSoup(requests.get(url).content, 'lxml')
items = soup.find_all('h2', class_="product-title")

itemList = []

for item in items:
    itemList.append(item.text.strip())

itemList.sort()

#if baseline file not found, write current items to file
basefile = "baseline.txt"
if not (os.path.isfile(basefile)):
    f = open(basefile, 'w')
    for item in itemList:
        f.write(item+'\n')
        #print(urlprefix+item.find('a')['href'])
    f.close()

baselineList = []
f = open(basefile, 'r')
for line in f:
    if line:
        baselineList.append(line.rstrip())
f.close()
baselineList.sort()

if not (baselineList==itemList): #differences found. Either added or removed items
    message = ''
    message += 'Removed devices:\n\n'
    for r in baselineList:
        if r not in itemList:
            message+='\t'+r+'\n'

    message += '\nAdded devices:\n\n'
    for a in itemList:
        if a not in baselineList:
            message+= '\t'+a+'\n'
    
    message += '\nCheck out at '+url+'\n'
    
    f = open(basefile, 'w')
    for item in itemList:
        f.write(item+'\n')
    f.close()

    sendslack.slack_webhook("Kobo Update", message)
