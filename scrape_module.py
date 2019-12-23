import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import requests
import datetime


current_time = datetime.datetime.now()
#     coins accepts a list
class Scrape_Coin(object):

    def __init__(self,
                coins = None,
                start_date = '20130428',  # hardcoded startdate
                end_date = str(current_time.year) + str(current_time.month) + str(current_time.day)):
        self.coins = coins
        self.start_date = start_date
        self.end_date = end_date
        
    def scrape_hist(self, coin):
        source=requests.get(f"https://coinmarketcap.com/currencies/{coin}/historical-data/?start={self.start_date}&end={self.end_date}").text
        page_soup=soup(source,"lxml")
        scraped_page=page_soup.find_all("tr",{"class":"text-right"})
        return scraped_page
    
    def compile_csv(self):
        coin_list = {}
        for i in self.coins:
            coin_list.update( {i : self.scrape_hist(i)} )

        for i in coin_list.keys():
            filename= f"{i}.csv"
            f=open(filename,"w")
            headers="Date,Open,High,Low,Close,Volume,Market_Cap\n"
            f.write(headers)
            for j in range(len(coin_list[i])):
                date = coins[i][j].td.text
                price_list = coins[i][j].find_all("td")
                price = price_list[1].text
                high = price_list[2].text
                low = price_list[3].text
                close = price_list[4].text
                volume = price_list[5].text
                market_cap = price_list[6].text
                row=date.replace(","," ")+","+price.replace(",","") + ","+high.replace(",","")+","+low.replace(",","")+","+close.replace(",","")+","+volume.replace(",","")+","+market_cap.replace(",","")+"\n" 
                f.write(row)
            f.close()