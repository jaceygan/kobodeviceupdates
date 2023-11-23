from bs4 import BeautifulSoup
import requests
import os.path
import sendslack
from device import device

url = "https://sg.kobobooks.com/collections/ereaders"
soup = BeautifulSoup(requests.get(url).content, 'lxml')
urlprefix = "https://sg.kobobooks.com"

#scrape URL to get all current products
products = soup.find_all('div', "productitem-ereader--info")
productList= []
for p in products:
    featureList = ''
    for feature in p.find_all('li', class_="productitem--feature"):
        featureList+=feature.text.strip()+'\t'
    featureList = featureList[:-1] #remove last tab

    d = device(p.find('h2', class_="product-title").text.strip(), p.find(class_="money").text.strip(),
                urlprefix+p.find('a')['href'], featureList)

    productList.append(d)

productList.sort()

bfile = 'pbaseline.txt'
if not (os.path.isfile(bfile)): #file not found means first time running. so generate baseline from current list
    f = open(bfile, 'w')
    for p in productList:
        f.write(p.printDevice())
    f.close()

# get baseline list from file
baselineList = []
f = open(bfile, 'r')
for line in f:
    if line:
        dlist = line.split('\t', 3)
        d = device(dlist[0], dlist[1], dlist[2], dlist[3])
        baselineList.append(d)
f.close()

baselineList.sort()

# check for added/remove devices and inform if found
#TODO: to notify for individual device addtion/ removal
#TODO: Add logging everywhere
if (baselineList != productList):
    message = ''
    message += 'Removed devices:\n'
    for r in baselineList:
        if r not in productList:
            message+='\t'+str(r)+'\n'

    message += '\nAdded devices:\n'
    for a in productList:
        if a not in baselineList:
            message+= '\t'+str(a)+'\n'
    
    message += '\nCheck out at '+url

    sendslack.slack_webhook("Kobo Device Lineup Changes", message)
    #write new info to baseline file
    f = open(bfile, 'w')
    for item in productList:
        f.write(item.printDevice())
    f.close()

#check for price changes and inform if found
changesfound = 0
for p in productList:
    if p in baselineList:
        bindex = baselineList.index(p)
        op = baselineList[bindex]
        if p.priceChanged(op):
            changesfound +=1
            m = ''
            m+= "Previous Price: "+op.price+'\n'
            m+= "New Price: " +p.price+'\n'
            m+= "Check it out at " + p.url

            sendslack.slack_webhook("Price changed for "+str(p), m)

if changesfound>0:
    f = open(bfile, 'w')
    for item in productList:
        f.write(item.printDevice())
    f.close()



    

