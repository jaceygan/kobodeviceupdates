from bs4 import BeautifulSoup
import requests
import os.path
import sendslack
from device import device
import logging

logging.basicConfig(filename='app.log', level=logging.INFO, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


url = "https://sg.kobobooks.com/collections/ereaders"
soup = BeautifulSoup(requests.get(url).content, 'lxml')

logging.info(f'Receved soup from {url}')
logging.debug(soup)

urlprefix = "https://sg.kobobooks.com"

def writeItemsToFile(filename, productList):
    f = open(filename, 'w')
    for item in productList:
        f.write(item.printDevice())
    f.close()
    logging.info (f'Written to {filename}')


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
logging.info(f'productList created: {productList}')

bfile = 'pbaseline.txt'
if not (os.path.isfile(bfile)): 
    #file not found means first time running. so generate baseline from current list
    logging.warning(f'Baseline file not found. Create new baseline file {bfile}')
    writeItemsToFile(bfile, productList)
    

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
logging.info(f'baselineList created: {baselineList}')

# check for added/remove devices and inform if found
if (baselineList != productList):
    logging.info('Differences found between product and baseline')
    for r in baselineList:
        if r not in productList:
            logging.info(f'Building slack message for {str(r)} removal')
            message = 'Price was: ' + r.price + '\n'
            message+= 'Device url: '+ r.url + '\n'
            message+= '\nCheck out at '+url


            if sendslack.slack_webhook(str(r) + " Removed", message) == 200:
                logging.info('Device removal message sent to slack')

    
    for a in productList:
        if a not in baselineList:
            logging.info(f'Building slack message for {str(r)} addition')
            message = 'Price: ' + a.price + '\n'
            message+= 'Features:'+ '\n'
            for f in a.features.split('\t'):
                message += '\t'+f+'\n'
            message+= '\n'+ "Check out "+ str(a) +" at:\n" + a.url
            
            if sendslack.slack_webhook(str(a) + " Added", message) == 200:
                logging.info('New device addition message sent to slack')

    #write current lineup to baseline file
    writeItemsToFile(bfile, productList)

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

            if sendslack.slack_webhook("Price changed for "+str(p), m) == 200:
                logging.info('Price change message sent to slack')


if changesfound>0:
    writeItemsToFile(bfile, productList)