import time
import sys
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import *
import re
import os
import pandas as pd
import requests
import math
from datetime import datetime
import random

class aspc_scraper:
    
    FirstLine = True
    #Excel row value
    Rows = 0
    ## Defining options for chrome browser
    options = webdriver.ChromeOptions()
    #ssl certificate error ignore
    options.add_argument("--ignore-certificate-errors")
    #Adding proxy
    #options.add_argument('--proxy-server=%s' % PROXY')


    browser = webdriver.Chrome(executable_path = "chromedriver",options = options)
    links = []

    #Excel File Name
    FileName = "ScrapedData"+str(random.randint(1,9789))+"-"+str(datetime.today().date())+".xlsx"
    print("Excel Filename: "+FileName)
    #Defining Excel Writer
    ExcelFile = pd.ExcelWriter(FileName)

    def Search(self):
        self.browser.get("https://www.aspc.co.uk")

        #Selecting dropdown option for property type its going to select it by its value which is going to be "Residential"
        select = Select(self.browser.find_element_by_xpath("//div[@class='form__field--inline-padding']//select[@data-key='propertyType']"))
 

        select.select_by_value("Residential")


        #Clicking on All Residential Type button after that modal will open.
        button1 = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@class='btn-overflow btn--full-width search-form__property-type-btn-el']")))
           
        button1.click()


        #Will select the label of the checkbox and click on it
        checkbox1 = WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='row form-area-filters__top-filter-row']//div[@class='form__field form__field--xl-border form__field--mobile-border']//label[@class='form__checkbox-label']")))
           

        checkbox1.click()
        #Sleep to let the load correctly
        time.sleep(0.5)

        #Closing Modal
        closebutton = WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='react-overlay react-overlay--top-bar-style-alt']//button[@class='react-overlay__close-btn']"))).click()
           
        #Seach Data by clicking it
        searchbutton = WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='react-notification react-notification--success ']//a[@class='react-notification__anchor']")))
 
        searchbutton.click()


        #This function will extract all the under offer properties urls and store them into the list globally
        self.Extracting_Urls()



    def Extracting_Urls(self):

        #Sleeping so the data can be loading completely
        time.sleep(3)


#
        #Getting the search result found
        totalResult = WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@class='results-bar__item results-bar__item-result-count']//span[@class='results-count__number']"))).text
        print("Total search results found: "+totalResult)

        #There are atleast 13 result per page so dividing 13 by total results will give us that how many pages do we have to scroll.
        totalResult = math.ceil(int(totalResult)/13)

        print("Total pages to scroll: "+str(totalResult))

        #This loop will over totalpages we found
        for i in range(totalResult):
            #        
            #Clicking on body so we can press pagedown button without any interruptions
            pagebody = self.browser.find_element_by_tag_name('body')
            pagebody.click()
            #Press pagedown key 7 times
            for j in range(7):
                pagebody.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.2)

            time.sleep(0.8)
            print("Page Scrolled : "+str(i)+" out of "+str(totalResult)+" remaining scrolls : "+str(totalResult - i))


        #Extracting underoffer properties links and storing it in list     
        try:
            houseCard = WebDriverWait(self.browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='information-card property-card property-card--underoffer col  ']//a[@class='information-card__text-container']")))
            for card  in houseCard:
                self.links.append(card.get_attribute('href'))
        except TimeoutException:
            pass

#
        #Connector function will iterate through all the links found and collect , store by the help of other functions.
        self.connector()


    def Collecting_Data(self,url):
        #Redirecting to Property Link
        self.browser.get(url)
#

        #Getting house div e.g "66 Kinmundy Avenue" then will extract only integer from it which will be number and strip and that interger from original string so we can get Street
        housenumberdiv = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//h1[@class='detail-title-panel__main-title']"))).text
#       
        housenumber = [int(s) for s in housenumberdiv.split() if s.isdigit()]

        try:
            street = housenumberdiv.replace(str(housenumber[0]),'').lstrip().rstrip()
        except:
            street = housenumberdiv

        ###


        #sub details will contain city/town , postcode sometimes street but we will skip streets e.g Milltimber, Aberdeen, AB13 0AW
        subdetails = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//h2[@class='detail-title-panel__sub-title']"))).text

        subdetails = subdetails.split(',')

        if(len(subdetails) < 3):
            town = subdetails[0].lstrip().rstrip()
            postcode = subdetails[-1].lstrip().rstrip()
        else:
            town = subdetails[1].lstrip().rstrip()
            postcode = subdetails[-1].lstrip().rstrip()



        #Will extract the price and strip str from it
        pricediv = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='detail-title-panel__price ']"))).text
        pricediv = pricediv.replace('Price over','')
        pricediv = pricediv.replace('Price around','')
        pricediv = pricediv.replace('Fixed price','')


        #getting number of bedrooms 
        bedroom = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//ul[@class='property-card-features detail-title-panel__icon-list']//li[@class='property-card-feature-bedroom']"))).text


        #getting number of bathrooms
        bathrooms = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//ul[@class='property-card-features detail-title-panel__icon-list']//li[@class='property-card-feature-bathroom']"))).text






        #This will get list of features 
        details = WebDriverWait(self.browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='results-grid__details-inner']//div[@class='feature-icon-list']//ul[@class='feature-icon-list__list']//li")))


        Garage = False
        Garden = False
        for detail in details:
            if detail.text == 'Garden':
                Garden = True

            if detail.text == 'Garage':
                Garage = True



        try:
            self.WriteDataToExcel(url,housenumber[0],street,town,postcode,'House',pricediv,bedroom,bathrooms,Garage,Garden)
        except:
            self.WriteDataToExcel(url,'',street,town,postcode,'House',pricediv,bedroom,bathrooms,Garage,Garden)


    def connector(self):
        urls = self.links
        #log
        print("Total Properties found of UnderOffer : ",len(urls))
        i = 0
        for url in urls:
            i += 1
            print("Property Scraping : "+url)
            #Collecting data will collect the required data and store it to excel file
            self.Collecting_Data(url)
            #log
            print("Property Scraped : "+str(i+1)+" out of "+str(len(urls))+" remaining urls : "+str(len(urls) - i+1))







    def WriteDataToExcel(self,url,number,street,town,postcode,propertytype,price,bedroom,bathroom,garage,garden):
        Data_Dict = {
            'URL' : '=HYPERLINK("'+url+'")',
            'Number/Name' : number,
            'Street' : street,
            'Town/City' : town,
            'Post Code' : postcode,
            'Property Type' : propertytype,
            'Price' : price,
            'Bedrooms' : bedroom,
            'Bathrooms' : bathroom,
            'Garage' : garage,
            'Garden' : garden,
        }

        if self.FirstLine == True:
            df = pd.DataFrame([Data_Dict])
            df.to_excel(self.ExcelFile,index=False,sheet_name='Data',header=True,startrow=self.Rows)
            self.Rows = self.ExcelFile.sheets['Data'].max_row
            self.FirstLine = False
        else:
            df = pd.DataFrame([Data_Dict])
            df.to_excel(self.ExcelFile,index=False,sheet_name='Data',header=False,startrow=self.Rows)
            self.Rows = self.ExcelFile.sheets['Data'].max_row

        self.ExcelFile.save()




a=aspc_scraper()
a.Search()




  

