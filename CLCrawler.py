# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 10:59:34 2016

@author: mac28
"""


#import pandas as pd
import numpy as np
import os.path
#from pandas import DataFrame
from bs4 import BeautifulSoup
import requests
import time
import random
import datetime
import json
from pandas import DataFrame


#Determines if I have run code before, and if I have loads the previous results,
#Should always be empty since we explore all the id numbers 
    
def GetMasterApartmentData():
    if os.path.isfile('/Users/mac28/CLCrawler/MasterApartmentData.json') == True:
        f = open('/Users/mac28/CLCrawler/MasterApartmentData.json')      
        mydict = json.load(f)
        f.close()
        return mydict
    else:
        f = open('/Users/mac28/CLCrawler/MasterApartmentData.json','w')
        f.close()
        return GetMasterApartmentData()


'''what if craigslist reuses numbers? build in back up for that'''
'''create that day's dictionary, save it to the master'''
'''notificiation? it let's you know when it doesn't work'''
        
        
#this function gets the newest apartment entries
#and appends them to our existing list of unexplored ID numbers
def NumberGetter(unexplored_id_numbers,mydict,page):
    #get html information 
    url = 'http://portland.craigslist.org/search/mlt/apa'+page
    result = requests.get(url)
    c = result.content
    soup = BeautifulSoup(c,'lxml')

    #organize it down to just the ID numbers
    summary = soup.find("div",{'class':'content'})
    rows = summary.find_all("p",{'class':'row'})
    new_id_numbers = []
    
    for i in rows:
        r = str(i)
        new_id_numbers.append(r[25:35])
    for number in new_id_numbers:
        if number not in mydict:
            unexplored_id_numbers.append(number)
    return unexplored_id_numbers 


def InfoGetter(id_number,mydict):
    url = 'https://portland.craigslist.org/mlt/apa'+'/'+id_number+'.html'
    result = requests.get(url)
    c = result.content
    soup = BeautifulSoup(c,'lxml')
    
    if Deleted(soup) == True:
        return mydict
    else:
        #get the price
        price = GetPrice(soup)   
        #get the listed attributes    
        bedbathfeet, attributes = GetAttributes(soup)
        cat = Cat(attributes)
        dog = Dog(attributes)
        laundry = Laundry(attributes)
        housingtype = HousingType(attributes)
        parking = Parking(attributes)
        wheelchair = WheelChair(attributes)
        smoking = Smoking(attributes)
        bed, bath, feet = BedBathFeet(bedbathfeet)
        content = ContentLength(soup)
        lat, lon = LatLon(soup)
        hasmap = HasMap(soup)
        getphotos = GetPhotos(soup)
        date, time = TimePosted(soup)
        mydict[id_number]={'price':price,'bed':bed,'bath':bath,'cat':cat,'dog':dog,
        'feet':feet,'housingtype':housingtype,'laundry':laundry,'parking':parking,
        'wheelchair':wheelchair,'smoking':smoking,'content':content,'lat':lat,
        'long':lon,'hasmap':hasmap,'getphotos':getphotos,'date':date,'time':time}
        #print GetAttributes(soup)  
        return mydict


def BedBathFeet(bedbathfeet):
    try:
        bedbathfeet = [int(i) for i in bedbathfeet]
        if len(bedbathfeet) == 3:
            return bedbathfeet[0],bedbathfeet[1],bedbathfeet[2]
        
        elif len(bedbathfeet) == 2:
            if max(bedbathfeet) > 10:
                return bedbathfeet[0],np.nan,bedbathfeet[1]
            else:
                return bedbathfeet[0],bedbathfeet[1],np.nan
        elif len(bedbathfeet) == 1:
            if bedbathfeet[0] > 10:
                return np.nan,np.nan,bedbathfeet[0]
            else:
                return bedbathfeet[0],np.nan,np.nan
        elif len(bedbathfeet) == 0:
            return np.nan,np.nan,np.nan
    except ValueError:
        if len(bedbathfeet) == 3:
            return int(bedbathfeet[0]),str(bedbathfeet[1]),int(bedbathfeet[2])
        elif len(bedbathfeet) == 2:
            bath = bedbathfeet.pop(bedbathfeet.index(max(bedbathfeet)))
            if max(bedbathfeet) > 10:
                return np.nan,bath,bedbathfeet[0]
            else:
                return bedbathfeet[0],bath,np.nan
        elif len(bedbathfeet) == 1:
            return np.nan,bedbathfeet[0],np.nan
        elif len(bedbathfeet) == 0:
            return np.nan,np.nan,np.nan


def Smoking(attributes):
    x=[]    
    for i in attributes:
        if str(i) == 'no smoking':
            x.append(str(i))
    if len(x)>0:
        return str(x[0])
    else:
        return np.nan

def Furnished(attributes):
    x=[]    
    for i in attributes:
        if str(i) == 'furnished':
            x.append(str(i))
    if len(x)>0:
        return str(x[0])
    else:
        return np.nan
        
def WheelChair(attributes):
    x=[]    
    for i in attributes:
        if str(i) == 'wheelchair accessible':
            x.append(str(i))
    if len(x)>0:
        return str(x[0])
    else:
        return np.nan
        
def Laundry(attributes):
    x=[]    
    for i in attributes:
        if str(i) == 'w/d in unit':
            x.append(str(i))
        elif str(i) == 'laundry in bldg':
            x.append(str(i))
        elif str(i) == 'laundry on site':
            x.append(str(i))
        elif str(i) == 'w/d hookups':
            x.append(str(i))
        elif str(i) == 'no laundry on site':
            x.append(str(i))
    if len(x)>0:
        return str(x[0])
    else:
        return np.nan


def HousingType(attributes):
    x=[]    
    for i in attributes:
        if str(i) == 'apartment':
            x.append(str(i))
        elif str(i) == 'condo':
            x.append(str(i))
        elif str(i) == 'cottage/cabin':
            x.append(str(i))
        elif str(i) == 'duplex':
            x.append(str(i))
        elif str(i) == 'flat':
            x.append(str(i))
        elif str(i) == 'house':
            x.append(str(i))
        elif str(i) == 'in-law':
            x.append(str(i))
        elif str(i) == 'loft':
            x.append(str(i))
        elif str(i) == 'townhouse':
            x.append(str(i))
        elif str(i) == 'manufactured':
            x.append(str(i))
        elif str(i) == 'assisted living':
            x.append(str(i))
        elif str(i) == 'land':
            x.append(str(i))
    if len(x)>0:
        return str(x[0])
    else:
        return np.nan

def Parking(attributes):
    x=[]    
    for i in attributes:
        if str(i) == 'carport':
            x.append(str(i))
        elif str(i) == 'attached garage':
            x.append(str(i))
        elif str(i) == 'detached garage':
            x.append(str(i))
        elif str(i) == 'off-street parking':
            x.append(str(i))
        elif str(i) == 'street parking':
            x.append(str(i))
        elif str(i) == 'valet parking':
            x.append(str(i))
        elif str(i) == 'no parking':
            x.append(str(i))
    if len(x)>0:
        return str(x[0])
    else:
        return np.nan
    

def Available(attributes):
    x = []    
    for i in attributes:
        if "available" in i:
            x.append(i)
    if len(x) > 0:
        return str(x[0])[10:]
    else:
        return np.nan
            
def Cat(attributes):
    if u'cats are OK - purrr' in attributes:
         return 1
    else:
        return 0
        
def Dog(attributes):
    if u'dogs are OK - wooof' in attributes:
        return 1
    else:
        return 0
           
def Deleted(soup):
    summary = soup.find("div",{'class':"removed"}) 
    if summary == None:
        return False
    else:
        return True

  
       
def GetAttributes(soup):
    summary = soup.find("div",{'class':'mapAndAttrs'})
    summary2 = summary.find_all("span")
    summary3 = summary.find_all("b")
    summary2
    bedbathfeet = []
    attributes = []
    for i in summary3:
        text = i.find(text=True)
        if text != 'open house dates':
            bedbathfeet.append(text)
    for i in summary2:
        text = i.find(text=True)
        if text not in bedbathfeet:
            attributes.append(text)
    return bedbathfeet, attributes

    
def GetPrice(soup):
    summary = soup.find("span",{'class':'price'})
    if summary == None:
        return np.nan
    else: 
        text = summary.find(text=True)
        price = int(str(text)[1:])
        return price

def ContentLength(soup):
    summary = soup.find("section",{'id':'postingbody'})
    if summary == None:
        return np.nan
    else:
        summary2 = "".join(str(summary))
        return len(summary2)
    
def LatLon(soup):
    summary = soup.find("div",{'class':'viewposting'})
    if summary == None:
        return np.nan, np.nan
    else:
        summarystring = str(summary)
        if summarystring[58] == '"':
            if summarystring[96] == '"':
                lat = summarystring[59:68]
                lon = summarystring[86:96]
                return float(lat), float(lon)
            else:
                lat = summarystring[59:68]
                lon = summarystring[86:97]
                return float(lat), float(lon)
        else:
            if summarystring[95] == '"':
                lat = summarystring[58:67]
                lon = summarystring[85:95]
                return float(lat), float(lon)
            else:
                lat = summarystring[58:67]
                lon = summarystring[85:96]
                return float(lat), float(lon)
        
def HasMap(soup):
    summary = soup.find("div",{'class':'mapbox'})
    if summary == None:
        return 0
    else:
        return 1
        
def GetPhotos(soup):
    summary = soup.find("div",{'id':'thumbs'})
    if summary == None:
        return 0
    else:
        summary2 = summary.find_all("a")
    return len(summary2)

def TimePosted(soup):
    summary = soup.find("time",{'class':'timeago'})
    date = str(summary)[32:42]
    time = str(summary)[43:51]
    return date, time

def merge_two_dicts(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z

def dump(my_dict, fil):
    dframe = DataFrame.from_dict(my_dict)
    dframe.to_csv(fil)
    fil.close()
    

def Final():
    mydict = GetMasterApartmentData()
    print 'length of mydict is '+str(len(mydict))
    unexplored_id_numbers = []
    newdict = {}
    counter = 0
    page_numbers = ['']+["?s='"+str(x+1)+'00' for x in range(24)]
    for page in page_numbers:
        print str(page)        
        unexplored_id_numbers = NumberGetter(unexplored_id_numbers,mydict,page)
        time.sleep(random.randrange(3,6)) 
    print unexplored_id_numbers
    print len(unexplored_id_numbers)
    while len(unexplored_id_numbers)>0:
        for i in enumerate(unexplored_id_numbers):
            id_number = unexplored_id_numbers.pop(-1)
            if id_number not in mydict or newdict:
                print str(id_number)+' '+ str(counter)
                newdict = InfoGetter(id_number,newdict)
                time.sleep(random.randrange(2, 3))
                counter += 1
    date = str(datetime.datetime.now())[:19].replace(' ','_').replace(':','.')
    TodayData = open('/Users/mac28/CLCrawler/data/TodaysData'+date+'.json',"w")
    TodayMasterData = open('/Users/mac28/CLCrawler/data/MasterApartmentData'+date+'.json',"w")
    MasterData = open('/Users/mac28/CLCrawler/MasterApartmentData.json',"w")
    json.dump(newdict,TodayData)
    mydict = merge_two_dicts(mydict,newdict)   
    json.dump(mydict, TodayMasterData)
    json.dump(mydict, MasterData)

    
    
print Final()
 
'''find the duplicates'''       
'''what if you added a "date last seen" function. You're already collecting ALL 
the ID's, just add todays date to all of them. I measures how long entries stay up'''
'''have all functions organized by classes'''
'''make a version that saves off 1.just today's entries 2. 
todays updated dict and 3. updates the master file'''         
'''find a way for chekcing duplicate listings with different numbers'''
'''fix bedbath so that it works for everything'''
'''don't forget to put in a separate file for todays date'''
'''make a version that runs automatically every day'''
    
'''FOR WHEN YOU WANT TO USE PANDAS FOR ANALYSIS
dframe = DataFrame.from_dict(mydict)
dataindex = [['price','bed','bath','cat','dog','feet','housingtype',
'laundry','parking','wheelchair','smoking','content','lat','lon','hasmap','getphotos','date','time']]
dframe2 = dframe.set_index(dataindex)
dframe2.to_csv('practice.csv')'''

''' FOR WHEN YOU WANT EMAIL NOTIFICATIONS, 
        2 functions -> mydict got longer and mydict stayed the same
        
def send_email(user, pwd, recipient, subject, body):
    import smtplib

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"'''
