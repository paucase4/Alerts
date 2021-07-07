#!/usr/bin/env python
# coding: utf-8

# In[111]:


import re
import time
from requests_html import HTMLSession
class Info:
    def get_content(self,ticker):
        session = HTMLSession()
        r = session.get("https://finance.yahoo.com/quote/{}".format(ticker))
        web = r.html.raw_html.decode()
        return web

    def price(self,ticker):
        regex = '<span class="Trsdu\(0.3s\) Fw\(b\) Fz\(36px\) Mb\(-4px\) D\(ib\)" data-reactid="32">.*<\/span>'
        web = self.get_content(ticker)
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
        regex = '<span class="Trsdu\(0.3s\) Fw\(500\) Pstart\(10px\) Fz\(24px\) C\(\$.*olor\)" data-reactid="33">.*<\/span>'
        web = self.get_content(ticker)
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
        regex = '<h1 class="D\(ib\) Fz\(18px\)" data-reactid="7">.*<\/h1>'
        web = self.get_content(ticker)
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