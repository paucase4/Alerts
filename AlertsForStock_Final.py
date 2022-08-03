import time
import yfinance as yf
from datetime import datetime,timedelta,date
import time
import urllib3 as u3
import gspread
import collections
import sys
from Data import current_Info, weekly_Info
from Client import Client
from HTML_Email import Emailer

def update_dict():# will return dictionary with email as key and all features as attrributes
    
    print("{}:{}:{}, updating dictionary".format(datetime.today().hour,datetime.today().minute,datetime.today().second))
    counter = 2
    n = []
    notsent_length = 0
    gc = gspread.service_account(filename="/usr/lib/python3.5/gspread/service_account.json")
    d = collections.defaultdict(list)
    sh = gc.open_by_key("1turCoY14yRgMmZ48oVWMraaSzlgSinYo7m27K-6TnfE")
    worksheet = sh.get_worksheet(0)
    while True:
        mail_cell = str(worksheet.acell('B' + str(counter)).value).replace(" ", "")
        if "@" not in mail_cell:
            break
        signup_date = str(worksheet.acell('A' + str(counter)).value.strip())
        name = str(worksheet.acell('C' + str(counter)).value).replace(" ", "")
        tickers = list(dict.fromkeys(str(worksheet.acell('D' + str(counter)).value).replace(" ", "").split(",")))
        notifications_pre = str(worksheet.acell('E' + str(counter)).value).replace(" ", "").split(",")
        #   qty_cell = str(worksheet.acell('E' + str(counter)).value).replace(" ", "").split(",")
        notifications = []
        
        for notification in notifications_pre:
            if notification == "Baixadadel5%":
                notifications.append(1)
                notsent_length += 1
            elif notification == "Pujadadel5%":
                notifications.append(2)
                if notsent_length == 0:
                    notsent_length += 1
            elif notification == "Notificaciódiàriadelpreu(16:00)":
                notifications.append(3)
            elif notification == "Avísquanbaixiopugiun10%apartird'avui":
                notifications.append(4)
                notsent_length += 1
        
        notsent1 = [True] * len(tickers) 
        
        val1 = mail_cell
        user_id = counter - 1
        val2 = Client(user_id ,name, mail_cell, signup_date, tickers,notifications,notsent1)
        
        notsent_length = 0
        n = []
        
        d[val1] = val2
        counter += 1
    print("{}:{}:{}, finished updating dictionary".format(datetime.today().hour,datetime.today().minute,datetime.today().second))
    return d

def get_tickers(d):
    all_tickers = [] 
    notsent1 = {}
    notsent2 = {}
    for person in d:
        for ticker in d[person].tickers:
            if ticker not in all_tickers:
                all_tickers.append(ticker)
    for t in  all_tickers:
        notsent1[t] = True
        notsent2[t] = True
    return all_tickers,notsent1,notsent2

def connection():
    http = u3.PoolManager()
    try:
        http.request('GET',"google.com")
        return True
    except:
        return False

def allprices(tickers,target_prices,notsent):
    print("{}:{}:{}, start checking target".format(datetime.today().hour,datetime.today().minute,datetime.today().second))
    
    notSent = notsent
    for idx,ticker in enumerate(tickers):
        current_price = get_price(ticker)
        if current_price <= target_prices[idx] and notSent[idx] == True and current_price != -10:
            print("Price is lower than target, values: PRICE {}, TARGET {}".format(get_price(ticker),target_prices[idx])) 
            sender.target_email(MAIL_PAU,ticker,False,"Pau")
            notSent[idx] = False
    print("{}:{}:{}, finished checking target".format(datetime.today().hour,datetime.today().minute,datetime.today().second))
    
    return notSent

def get_price(ticker):
    a = ""
    if connection():
        try:
            close = info.price(ticker)
        except:
            return -10
    else:
        print("No connection.")
        return -10
    return round(float(close),4)

def get_prices(tickers):    
    prices = []
    for ticker in tickers:
        price = get_price(ticker)
        prices.append(price)
    return prices

def get_change(ticker):
    price = get_price(ticker)
    try:
        percent_change = info.change(ticker)
    except:
        return -101
        #print('Error downloading data | Ticker: ' + ticker )
    return percent_change

def addzero(string):
    if len(string) == 1:
        return "0" + string
    else:
        return string
        
def check_losses_and_wins5(tickers):
    global NOTSENT1
    pct = 5
    prices = get_prices(tickers)
    data_found = True
    print("{}:{}:{}, start checking 5%".format(datetime.today().hour,datetime.today().minute,datetime.today().second))
    for idx,ticker in enumerate(tickers):
        if info.is_traded(ticker) == False:
            pass
        else:
            if prices[idx] == -10:
                data_found = False
            if data_found:
                change = get_change(ticker)
                if 5.0 < abs(change) and connection() and change != -101 and NOTSENT1[ticker] == True:                        
                    for p in d:
                        if change < 0 and 1 in d[p].notifications:
                            if tickers[idx] in d[p].tickers:
                                print("5% down: " + str(tickers[idx]) + " " + str(p))
                                sender.loss_email(d[p].email,tickers[idx],prices[idx],change,False)
                    
                        elif change > 0 and 2 in d[p].notifications:
                            if tickers[idx] in d[p].tickers:
                                print("5% up: " + str(tickers[idx]) + " " + str(p))
                                sender.win_email(d[p].email,tickers[idx],prices[idx],change)
                                
                    NOTSENT1[ticker] = False
            else:
                print("Ticker {} is causing a problem.".format(ticker))
                data_found = True
    print("{}:{}:{}, finished checking 5%".format(datetime.today().hour,datetime.today().minute,datetime.today().second))
def check_losses_and_wins10(tickers):
    global NOTSENT2
    print("{}:{}:{}, start checking 10%".format(datetime.today().hour,datetime.today().minute,datetime.today().second))
    pct = 10
    prices = get_prices(tickers)
    data_found = True
    for idx,price in enumerate(prices):  
        if info.is_traded(tickers[idx]) == False:
            pass
        else:
            if price == -10:
                data_found = False
            if data_found:
                change = get_change(tickers[idx])
                if 10.0 < abs(change) and connection() and change != -101 and NOTSENT2[tickers[idx]] == True:                        
                    for p in d:
                        if 4 in d[p].notifications:
                            if change < 0:
                                if tickers[idx] in d[p].tickers:
                                    print("10% down: " + str(tickers[idx]) + " " + str(p))
                                    sender.loss_email(d[p].email,tickers[idx],prices[idx],change,False)
                                    
                            elif change > 0:
                                if tickers[idx] in d[p].tickers and 3 in d[p].notifications:
                                    print("10% up: " + str(tickers[idx]) + " " + str(p))
                                    sender.win_email(d[p].email,tickers[idx],prices[idx],change)
                    NOTSENT2[tickers[idx]] = False
            else:
                print("Ticker {} is causing a problem.".format(tickers[idx]))
                data_found = True
    
    print("{}:{}:{}, finished checking 10%".format(datetime.today().hour,datetime.today().minute,datetime.today().second))
                                
def reset_everything():
    global d
    global NOTSENT1
    global NOTSENT2
    ALL_TICKERS,NOTSENT1,NOTSENT2 = get_tickers(d)
    DAILY_NOTSENT = True
    TARGET_NOT_SENT = [True]*len(TARGET_TICKERS)
    return True
    
def weekly_report():
    for person in d:
        if 3 in d[person].notifications:
            Emailer().weekly_email(d[person].email,d[person].tickers,d[person].name)
    
def monthly_report():
    for person in d:
        if 3 in d[person].notifications:
            Emailer().monthly_email(d[person].email,d[person].tickers,d[person].name)
    
def weekend():
    day = datetime.today().isoweekday()
    if day == 6:
        if datetime.today().day == 1:
            monthly_report()
        weekly_report()
    while day == 6 or day == 7:
        if datetime.today().day == 1:
            monthly_report()
        time.sleep(28888)
        day = datetime.today().isoweekday()
        
def sleeping(wakeup):
    day = datetime.today()
    h = day.hour
    
    if h >= 21:
        if datetime.today().day == 1:
            monthly_report()
        print("Going to sleep.")
        t = 3610*3
        time.sleep(t)
        day = datetime.today()
        h = day.hour
        m = day.minute
        t = 60 * ((30+60*(int(wakeup)-h)) - m)
        time.sleep(t)
        d = update_dict()
        reset_everything()
        print("Market open in Europe! " + str(datetime.today()))
        h = datetime.today().hour
        return True
    elif h < 7:
        t = 60 * ((30+60*(7-h)) - datetime.today().minute)
        time.sleep(t)
        d = update_dict()
        reset_everything()
        print("Markets open in Europe! " + str(datetime.today()))
        
        return True
    return False

def start_message():
    day = datetime.today()
    print(str(day.hour)+ ":" + addzero(str(day.minute)) + ":" + addzero(str(day.minute)))
    
def main():
    reset_everything()
    DAILY_NOTSENT = True
    TARGET_NOT_SENT = [True]*len(TARGET_TICKERS)
    while True:        
        global checkpoint
        global d
        global NOTSENT1
        global NOTSENT2
        checkpoint = 1
        start_message()
        checkpoint = 2
        weekend()
        checkpoint = 3
        if sleeping(7):
            try:
                d = update_dict()
            except:
                print("Couldn't update user dictionary.")
            DAILY_NOTSENT = True
            TARGET_NOT_SENT = [True]*len(TARGET_TICKERS)
            ALL_TICKERS,NOTSENT1,NOTSENT2 = get_tickers(d)
        
        checkpoint = 4
        check_losses_and_wins5(ALL_TICKERS)
        
        checkpoint = 5
        check_losses_and_wins10(ALL_TICKERS)
        
        checkpoint = 6
        if connection():
            TARGET_NOT_SENT = allprices(TARGET_TICKERS,TARGET_PRICES,TARGET_NOT_SENT)     # check prices w targets and email if necessary. If emailed, change notsent.
        checkpoint = 7
        day = datetime.today()
        if DAILY_NOTSENT and datetime.today().hour == 14:
            for p in d:
                if 3 in d[p].notifications:
                    sender.daily_email(d[p].email,d[p].tickers,d[p].name)
                    DAILY_NOTSENT = False
        time.sleep(450)

d = update_dict()
info = current_Info()
DAILY_NOTSENT = True
MAIL_PAU = "paucase4@gmail.com"
sender = Emailer()
TARGET_TICKERS = ["V","T","EA","AAPL","GOOGL","AMZN","ADBE"]
TARGET_PRICES = [200,27,125,120,1900,2950,440]
checkpoint = 0
ALL_TICKERS,NOTSENT1,NOTSENT2 = get_tickers(d)

def error_message(e,checkpoint):
    exception_type, exception_object, exception_traceback = sys.exc_info()
    line_number = exception_traceback.tb_lineno
    filename = exception_traceback.tb_frame.f_code.co_filename
    return f"Exception: {e} <br>\nException Type: {exception_type}\n<br>Exception File: {filename}\n<br>Exception in line: {line_number}\n<br>Checkpoint: {checkpoint}"
    
try:
    main()
except Exception as e:
    Emailer().error_email(e)
    error_message = error_message(e,checkpoint)
    print(error_message)
    Emailer().error_email(error_message) # report error to host
