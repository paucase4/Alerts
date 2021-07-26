#!/usr/bin/env python
# coding: utf-8

# In[3]:


import os
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
from email.utils import make_msgid
import calendar
import mimetypes
import yfinance as yf
from datetime import datetime,timedelta,date
import urllib3 as u3
from Data import current_Info, weekly_Info

HAPPY = ["stonks.jpg","yes_youre_this.jpg"]
RELAX = [""]
MOTIVATION = ["willitbeeasy.jpg","struggle_today.jpg","comeback_stronger.jpg"]
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587 
GMAIL_USERNAME = 'stocknotificacions@gmail.com' 
GMAIL_PASSWORD = 'St0ck1nf0'
info = current_Info()

def get_pct(ticker):
    price = get_price(ticker)
    try:
        percent_change = info.change(ticker)
    except:
        return -101
    return percent_change

def get_price(ticker):
    a = ""
    if connection():
        try:
            close = info.price(ticker)
        except:
            return -10
            print("Error occurred while trying to download data of " + str(ticker))
    else:
        print("No connection.")
        return -10
    return round(float(close),4)
    
def connection():
    http = u3.PoolManager()
    try:
        http.request('GET',"google.com")
        return True
    except:
        return False

def send(recipient,msg):
        s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        s.sendmail(GMAIL_USERNAME, recipient, msg.as_string())
        s.quit()
def get_company_name(ticker):
    try:
        company_name = info.company_name(ticker)
    except:
        company_name = ticker
    return company_name
class Emailer:
    def monthly_email(self,recipient,tickers,name):
        month = datetime.now().month
        months = ['Gener','Febrer','Març','Abril','Maig','Juny','Juliol','Agost','Setembre','Octubre','Novembre','Desembre']
        year = datetime.now().year
        subject = "Rendiment Mensual {month_name}, {month}-{year}".format(month_name = months[month-1], month= month, year = year)
        body = str(name).upper() + ", <b>Rendiment Mensual {} de l'any {}</b>".format(months[month-1],year) + "<table><tr><th>Empresa</th><th>Inici de Mes</th><th>Final de Mes</th><th>Rendiment</th></tr>"
        html = "<html><body><p><b>{}</b></p>".format(name)        
        if isinstance(tickers,str):
            ticker = tickers
            link = "https://finance.yahoo.com/quote/{}/".format(ticker)
            start_price,end_price,perc = weekly_Info().monthly_performance(ticker)
            company_name = get_company_name(ticker)
            
            if perc < 0:
                body += "<td> <a href='{LINK}'><b>{COMPANY_NAME}</b></a></td><td> <b style = color:#fb0f29>${START_PRICE}</b></td><td> <b style = color:#fb0f29>${END_PRICE}</b></td><td> <b style = color:#fb0f29>{CHANGE}%</b></td>".format(LINK = link,COMPANY_NAME = company_name,START_PRICE = start_price,END_PRICE = end_price,CHANGE = perc)
            else:
                body += "<td> <a href='{LINK}'><b>{COMPANY_NAME}</b></a></td><td> <b style = color:#00b52c>${START_PRICE}</b></td><td> <b style = color:#00b52c>${END_PRICE}</b></td><td> <b style = color:#00b52c>{CHANGE}%</b></td>".format(LINK = link,COMPANY_NAME = company_name,START_PRICE = start_price,END_PRICE = end_price,CHANGE = perc)
            body += "</body></html>"
        else:   
            for idx,ticker in enumerate(tickers):
                body += "<tr>"
                link = "https://finance.yahoo.com/quote/{}/".format(ticker)
                start_price,end_price,perc = weekly_Info().monthly_performance(ticker)
                company_name = get_company_name(ticker)
                
                if perc < 0:
                    body += "<td> <a href='{LINK}'><b>{COMPANY_NAME}</b></a></td><td> <b style = color:#fb0f29>${START_PRICE}</b></td><td> <b style = color:#fb0f29>${END_PRICE}</b></td><td> <b style = color:#fb0f29>{CHANGE}%</b></td>".format(LINK = link,COMPANY_NAME = company_name,START_PRICE = start_price,END_PRICE = end_price,CHANGE = perc)
                else:
                    body += "<td> <a href='{LINK}'><b>{COMPANY_NAME}</b></a></td><td> <b style = color:#00b52c>${START_PRICE}</b></td><td> <b style = color:#00b52c>${END_PRICE}</b></td><td> <b style = color:#00b52c>{CHANGE}%</b></td>".format(LINK = link,COMPANY_NAME = company_name,START_PRICE = start_price,END_PRICE = end_price,CHANGE = perc)
                    ## style="color:#00b52c" green
                    ## style="color:#fb0f29" red
                    ## link for stonks: https://codepen.io/havardob/pen/PoPaWaE
                body += "</tr>"
            body += "</table></body></html>"
        html = body.format(subtype = 'html')
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = GMAIL_USERNAME
        msg['To'] = recipient
        html = MIMEText(html,'html')
        msg.set_content(html)
        send(recipient,msg)
        
        
    def weekly_email(self,recipient,tickers,name):
        monday = date.today() - timedelta(days = 5)
        week = monday.isocalendar()[1]
        monday = str(monday)
        year = datetime.now().year
        subject = "Rendiment Setmanal Setmana {}, del dilluns {}".format(week,monday)
        body = str(name).upper() + ", <b>Rendiment Setmanal Setmana de la setmana {} de l'any {}</b>".format(week,year) + "<table><tr><th>Empresa</th><th>Inici de Setmana</th><th>Final de Setmana</th><th>Rendiment</th></tr>"
        html = "<html><body><p><b>{}</b></p>".format(name)        
        if isinstance(tickers,str):
            ticker = tickers
            link = "https://finance.yahoo.com/quote/{}/".format(ticker)
            start_price,end_price,perc = weekly_Info().weekly_performance(ticker,10)
            company_name = get_company_name(ticker)
            
            if perc < 0:
                body += "<td> <a href='{LINK}'><b>{COMPANY_NAME}</b></a></td><td> <b style = color:#fb0f29>${START_PRICE}</b></td><td> <b style = color:#fb0f29>${END_PRICE}</b></td><td> <b style = color:#fb0f29>{CHANGE}%</b></td>".format(LINK = link,COMPANY_NAME = company_name,START_PRICE = start_price,END_PRICE = end_price,CHANGE = perc)
            else:
                body += "<td> <a href='{LINK}'><b>{COMPANY_NAME}</b></a></td><td> <b style = color:#00b52c>${START_PRICE}</b></td><td> <b style = color:#00b52c>${END_PRICE}</b></td><td> <b style = color:#00b52c>{CHANGE}%</b></td>".format(LINK = link,COMPANY_NAME = company_name,START_PRICE = start_price,END_PRICE = end_price,CHANGE = perc)
            body += "</body></html>"
        else:   
            for idx,ticker in enumerate(tickers):
                body += "<tr>"
                link = "https://finance.yahoo.com/quote/{}/".format(ticker)
                start_price,end_price,perc = weekly_Info().weekly_performance(ticker,10)
                company_name = get_company_name(ticker)
                
                if perc < 0:
                    body += "<td> <a href='{LINK}'><b>{COMPANY_NAME}</b></a></td><td> <b style = color:#fb0f29>${START_PRICE}</b></td><td> <b style = color:#fb0f29>${END_PRICE}</b></td><td> <b style = color:#fb0f29>{CHANGE}%</b></td>".format(LINK = link,COMPANY_NAME = company_name,START_PRICE = start_price,END_PRICE = end_price,CHANGE = perc)
                else:
                    body += "<td> <a href='{LINK}'><b>{COMPANY_NAME}</b></a></td><td> <b style = color:#00b52c>${START_PRICE}</b></td><td> <b style = color:#00b52c>${END_PRICE}</b></td><td> <b style = color:#00b52c>{CHANGE}%</b></td>".format(LINK = link,COMPANY_NAME = company_name,START_PRICE = start_price,END_PRICE = end_price,CHANGE = perc)
                    ## style="color:#00b52c" green
                    ## style="color:#fb0f29" red
                    ## link for stonks: https://codepen.io/havardob/pen/PoPaWaE
                body += "</tr>"
            body += "</table></body></html>"
        html = body.format(subtype = 'html')
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = GMAIL_USERNAME
        msg['To'] = recipient
        html = MIMEText(html,'html')
        msg.set_content(html)
        send(recipient,msg)    
            
    def error_email(self,error_text):
        subject = "Stock Alerting has stopped on the " + str(date.today())
        body = "<html><body><h1>STOPPED APP - RESTART NEEDED - ERROR IN SCREEN</h1><h3>{}</h3></body></html>".format(error_text)        
        recipient = "paucase4@gmail.com"
        html = body.format(subtype = 'html')
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = GMAIL_USERNAME
        msg['To'] = recipient
        html = MIMEText(html,'html')
        msg.set_content(html)
        send(recipient,msg)
        
        
    def daily_email(self,recipient,tickers,name):
        subject = "Preus del dia " + str(date.today()) + " a les 16:00."
        body = str(name) + ", <b>PREUS DEL DIA " + str(date.today()) + " a les 16:00</b><table><tr><th>Empresa</th><th>Preu</th><th>Rendiment</th></tr>"
        html = "<html><body><p><b>{}</b></p>".format(name)        
        count_1 = 0
        if isinstance(tickers,str):
            ticker = tickers
            perc = get_pct(ticker)
            link = "https://finance.yahoo.com/quote/{}/".format(ticker)
            price = get_price(ticker)
            
            try:
                company_name = info.company_name(ticker)
            except:
                company_name = ticker
            if perc < 0:
                body += "<td> <a href='{}'><b>{}</b></a></td><td> <b style = color:#fb0f29>${}</b></td><td> <b style = color:#fb0f29>{}%</b></td>".format(link,company_name,price,perc)
                count_1 += 1
            else:
                body += "<td> <a href='{}'><b>{}</b></a></td><td> <b style = color:#00b52c>${}</b></td><td> <b style = color:#00b52c>{}%</b></td>".format(link,company_name,price,perc)
            body += "</body></html>"
        else:   
            for idx,ticker in enumerate(tickers):
                body += "<tr>"
                link = "https://finance.yahoo.com/quote/{}/".format(ticker)
                perc = get_pct(ticker)
                price = get_price(ticker)
                try:
                    company_name = info.company_name(ticker)
                except:
                    company_name = ticker
                if perc < 0:
                    body += "<td> <a href='{}'><b>{}</b></a></td><td> <b style = color:#fb0f29>${}</b></td><td> <b style = color:#fb0f29>{}%</b></td>".format(link,company_name,price,perc)
                    count_1 += 1
                else:
                    body += "<td> <a href='{}'><b>{}</b></a></td><td> <b style = color:#00b52c>${}</b></td><td> <b style = color:#00b52c>{}%</b></td>".format(link,company_name,price,perc)
                    ## style="color:#00b52c" green
                    ## style="color:#fb0f29" red
                    ## link for stonks: https://codepen.io/havardob/pen/PoPaWaE
                body += "</tr>"
            body += "</table></body></html>"
        if len(tickers) == count_1 and recipient == "fxcase@gmail.com":
            body = "<html><body><h1><b style = color:#fb0f29>GORDINFLOOOOOOO NOOOOO LUUUCK TODAYYYYY :( </b></h1></body></html>"
            html = body.format(subtype = 'html')
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = GMAIL_USERNAME
            msg['To'] = recipient
            html = MIMEText(html,'html')
            msg.set_content(html)
            send(recipient,msg)
        else:
            html = body.format(subtype = 'html')
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = GMAIL_USERNAME
            msg['To'] = recipient
            html = MIMEText(html,'html')
            msg.set_content(html)
            send(recipient,msg)
        
        
    def loss_email_content(self,ticker,price,percentage):
        d = datetime.today()
        day = str(date.today())
        h = str(d.hour + 2) 
        m = str(d.minute)
        s = str(d.second)
        percentage = round(percentage,2)
        if len(s) == 1:
            s = "0" + s
        if len(h) == 1:
            h = "0" + h
        if len(m) == 1:
            m = "0" + m
        link = "https://finance.yahoo.com/quote/" + ticker + "/"
        try:
            company_name = info.company_name(ticker)
        except:
            company_name = ticker

        subject = "CAIGUDA DEL {}% EN EL PREU DE {}".format(percentage,ticker)
        body = "El preu de: <b>{}</b>, dia {} a les {}:{}:{} és <b>${}</b>".format(company_name,day,h,m,s,price)
        b2 = "Comprova el preu a " + link
        img = MOTIVATION[random.randint(0, 2)]
        return subject,body,b2,img
    
    def loss_email(self, recipient, ticker, price, pc, img):
        subject, body, b2, image = self.loss_email_content(ticker, price, pc)
        yahoo_link = "https://finance.yahoo.com/quote/" + ticker + "/"
        a = "{}\n{}".format(body,b2)
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = GMAIL_USERNAME
        msg['To'] = recipient
        
        msg.set_content(body)

        if img:
            img_data = open(image, 'rb').read()
            image_cid = make_msgid()
            msg.add_alternative("""<html>
    <body>
        <p style="font-family:verdana">
    
        {body}</p>
        <br>    
        <p style="font-family:verdana"> {b2}</p>
        
        <img src="cid:{image_cid}">
    </body>
</html>
""".format(body=body,b2=b2,image_cid=image_cid[1:-1]), subtype='html')
            with open(image, 'rb') as img:
                maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')
        
                msg.get_payload()[1].add_related(img.read(), 
                                             maintype=maintype, 
                                             subtype=subtype, 
                                             cid=image_cid)
            
        else:

            ti= """<html>
    <body>
        <p style="font-family:verdana">
        {body}
        </p>
        <br>
        <p style="font-family:verdana">
        {b2}
        </p>
        
        <p> </p>
    </body>
</html>
""".format(body=body,b2=b2, subtype='html')
            
            text = MIMEText(ti, 'html')
            msg.set_content(text)
        
        send(recipient,msg)
    def win_email_content(self,ticker,price,percentage):
        d = datetime.today()
        day = str(date.today())
        h = str(d.hour + 2) 
        m = str(d.minute)
        s = str(d.second)
        percentage = round(percentage,2)
        if len(s) == 1:
            s = "0" + s
        if len(h) == 1:
            h = "0" + h
        if len(m) == 1:
            m = "0" + m
        link = "https://finance.yahoo.com/quote/" + ticker + "/"
        try:
            company_name = info.company_name(ticker)
        except:
            company_name = ticker
        subject = "ESCALADA DEL {}% EN EL PREU DE {}".format(percentage,company_name)
        body = "El preu de: <a href='{}'><b>{}</b></a>, dia {} a les {}:{}:{} és <b>${}</b>".format(link,company_name,day,h,m,s,price)
        
        return subject,body
    
    def win_email(self, recipient, ticker, price, pc):
        subject, body = self.win_email_content(ticker, price, pc)
        yahoo_link = "https://finance.yahoo.com/quote/" + ticker + "/"
        a = body
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = GMAIL_USERNAME
        msg['To'] = recipient
        msg.set_content(body)

        body = """<html>
    <body>
    
   <h1 style = text-align:center>STOOONKS</h1>
   <h2 style = color:green> {ei} </h2>
        <p>

        {body}

        </p>

        <br>    

        <p>

        </p>
    </body>
</html>
""".format(ei=subject,body=body, subtype='html')
        print(body)
        body = MIMEText(body, 'html')
        msg.set_content(body)
        send(recipient,msg)
        
    def target_email(self,receiver, ticker, img, name):
        yahoo_link = "https://finance.yahoo.com/quote/" + ticker + "/"
        try:
            company_name = info.company_name(ticker)
        except:
            company_name = ticker
        subject = "Oportunitat de compra a {}".format(company_name)
        text = "{}, {} ha arribat al preu de compra indicat. \nLink de {} a Yahoo finance {}".format(name,company_name,company_name,yahoo_link)
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = GMAIL_USERNAME
        msg['To'] = receiver
        
        
        msg.set_content(text)
        if img:
            img_data = open('buy_the_dip.jpg', 'rb').read()
            image_cid = make_msgid()
            msg.add_alternative("""<html>
    <body>
        <p style="font-family:verdana">
        {text}
        </p>
        <img src="cid:{image_cid}">
    </body>
</html>
""".format(text=text,image_cid=image_cid[1:-1]), subtype='html')
            with open('buy_the_dip.jpg', 'rb') as img:
                maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')
        
                msg.get_payload()[1].add_related(img.read(), 
                                             maintype=maintype, 
                                             subtype=subtype, 
                                             cid=image_cid)
            
        else:
            ti = """<html>
    <body>
        <p style="font-family:verdana">
        {text}
        </p>
    </body>
</html>
""".format(text=text, subtype='html')
            text = MIMEText(ti, 'html')
            msg.set_content(text)
        
        send(receiver,msg)



    

