#!/usr/bin/env python
# coding: utf-8

# In[111]:


import re
import time
from requests_html import HTMLSession
import yfinance as yf
import calendar

from datetime import datetime, date, timedelta
class weekly_Info:
    def baixar_dades_dies(self, ticker, dies_anteriors):
        dades = yf.Ticker(ticker)
        
        avui = datetime.now()
        
        dies_anteriors = timedelta(days = dies_anteriors)
        dia_fa_x_dies = avui - dies_anteriors 
        
        preus_i_volums = data = dades.history(period='1d', start=dia_fa_x_dies , end=avui)
        
        return preus_i_volums

    def weekly_performance(self,ticker,days):
        data = self.baixar_dades_dies(ticker,days)['Close']
        start_date = datetime.now() - timedelta(days = days)
        
        start_price_comprovation = round(data[str(start_date)[0:10]],4)
        start_price = round(data[0],4)
        if start_price == start_price_comprovation:        
            end_price = data[-1]
            change = round((end_price/start_price-1)*100,2)
            return round(start_price,4),round(end_price,4),change
        else:
            return -10,-10, -101
        
        
    def monthly_performance(self,ticker):
        year_40_before = datetime.now() - timedelta(days = 40)
        year_of_last_month = year_40_before.year
        last_day_of_last_month = calendar.monthrange(year_of_last_month,datetime.now().month-1)[1]
        data = self.baixar_dades_dies(ticker,35)['Close']
        i = 0
        b = True
        while b == True and i < 35:
            start_date = '{year}-{month}-{day}'.format(year = year_of_last_month,month = datetime.now().month-1,day = last_day_of_last_month-i)
            try:
                start_price = round(data[str(start_date)],4)
                b = False
            except:
                i+=1
        try:
            end_price = data[-2]
            change = round((end_price/start_price-1)*100,2)
            return round(start_price,4),round(end_price,4),change
        
        except:
            print("Unable to calculate monthly performance | Possibly due to a mistake in the code")
            return -10,-10,-101


class current_Info:
    def get_content(self,ticker):
        session = HTMLSession()
        try:
            r = session.get("https://finance.yahoo.com/quote/{}".format(ticker), timeout=15)
        except : 
            print("Timeout while trying to connect to yahoo. Ticker: "+ str(ticker))
            return ""
        web = r.html.raw_html.decode()
        return web

    def price(self,ticker):
        regex = '<span class="Trsdu\(0.3s\) Fw\(b\) Fz\(36px\) Mb\(-4px\) D\(ib\)" data-reactid=".*?">.*?<\/span>'
        web = self.get_content(ticker)
        if web == "":
            raise "NO DATA FOUND"
        for re_match in re.finditer(regex, web):
            idx = web.index(re_match.group())
            part = web[idx+74:idx+90]
            result = ""
            for letter in part:
                if letter != "<":
                    result += letter
                else:
                    break
            result = result.replace(',','')
        return float(result)
    
    def change(self,ticker):
        regex = '<span class="Trsdu\(0.3s\) Fw\(500\) Pstart\(10px\) Fz\(24px\) C\(\$.*olor\)" data-reactid=".*?">.*?<\/span>'
        web = self.get_content(ticker)
        if web == "":
            raise "NO DATA FOUND"
        for re_match in re.finditer(regex, web):
            idx = web.index(re_match.group())
            part = web[idx+92:idx+120]
            result = ""
            boolean  = False
            for letter in part:
                if letter == "(":
                    boolean = True
                elif letter == ")":
                    boolean = False
                else:
                    if boolean == True:
                        result += letter
            
        return float(result[:-1])
    
    def company_name(self,ticker):
        regex = '<h1 class="D\(ib\) Fz\(18px\)" data-reactid=".*?">.*?<\/h1>'
        web = self.get_content(ticker)
        if web == "":
            raise "NO DATA FOUND"
        for re_match in re.finditer(regex, web):
            idx = web.index(re_match.group())
            part = web[idx+44:idx+200]
            result = ""
            for letter in part:
                if letter != "(":
                    result += letter
                else:
                    break
        
        return result
        
    def is_traded(self,ticker):
        regex = '>At close:'
        web = self.get_content(ticker)
        if web == "":
            return False
        for re_match in re.finditer(regex, web):
            return False
        return True
    def is_us_ticker(self,ticker):
        if '.' in ticker:
            return False
        else:
            return True
    def is_us_market_closed(self):
        if datetime.today().hour < 21 and datetime.today().hour > 11:
            return False
        else:
            return True

    def get_currency(self,ticker):
        if '.' not in ticker:
            return "$"
        else:
            regex = 'Currency in '
            web = self.get_content(ticker)
            if web == "":
                return '\u20ac'
            for re_match in re.finditer(regex, web):
                idx = web.index(re_match.group())
                currency = web[idx+12:idx+15]
                return currency
            return '\u20ac'