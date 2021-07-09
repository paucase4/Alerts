import time
import yfinance as yf
from datetime import datetime,timedelta,date
import time
import urllib3 as u3
from HTML_Email import Emailer
import gspread
import collections

from Data import Info

def update_dict():
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
        name_cell = str(worksheet.acell('C' + str(counter)).value).replace(" ", "")
        tickers_cell = str(worksheet.acell('D' + str(counter)).value).replace(" ", "").split(",")
        notification_cell = str(worksheet.acell('E' + str(counter)).value).replace(" ", "").split(",")
        #   qty_cell = str(worksheet.acell('E' + str(counter)).value).replace(" ", "").split(",")
        
        for asd in notification_cell:
            if asd == "Baixadadel5%":
                n.append(1)
                notsent_length += 1 
            elif asd == "Pujadadel5%":
                n.append(2)
                if notsent_length == 0:
                    notsent_length += 1
            elif asd == "Notificaciódiàriadelpreu(16:00)":
                n.append(3)
            elif asd == "Avísquanbaixiopugiun10%apartird'avui":
                n.append(4)
                notsent_length += 1
        
        notsent1 = [True] * len(tickers_cell) 
        notsent2 = [True] * len(tickers_cell) 
        notsent3 = [True] * len(tickers_cell)
        
        val1 = mail_cell
        
        if notsent_length == 1:
            val2 = [name_cell, tickers_cell, n,notsent1]
        elif notsent_length == 2:
            val2 = [name_cell, tickers_cell, n,notsent1,notsent2]
        elif notsent_length == 0:
            val2 = [name_cell, tickers_cell, n]
        notsent_length = 0
        n = []
        d[val1] = val2
        counter += 1
    print("{}:{}:{}, finished updating dictionary".format(datetime.today().hour,datetime.today().minute,datetime.today().second))
    return d

def set_as_sent(p,index):
    d[p][3][index] = False

def get_tickers(d):
    all_tickers = []    
    for p in d:
        if 1 not in get_notifications(p) and 2 not in get_notifications(p) and 4 not in get_notifications(p):
            pass
        else:
            tickers = d[p][1]
            for t in tickers:
                if t not in all_tickers:
                    all_tickers.append(t)
    return all_tickers

def get_tickers_person(p):
    all_tickers = []
    tickers = d[p][1]
    for t in tickers:
        if t not in all_tickers:
            all_tickers.append(t)
    return all_tickers    
    
def get_mails(d):
    all_mails = []
    for person in d:
        all_mails.append(person)
    return all_mails

def get_name(p):
    all_names = []
    return d[p][0]


def get_notifications(person):
    global d
    
    return d[person][2]

def get_notsent1(person):
    e = d[person][3]
    return e

def get_notsent2(person):
    try:
        f = d[person][4]
        return f 
    except:
        pass

def set_as_sent(p,num,index):
    if len(d[p][3]) < 1:
        d[p][3][num][index] = False
    else:
        d[p][3][index] = False

def set_as_sent2(p,num,index):
    if len(d[p][4]) < 1:
        d[p][4][num][index] = False
    else:
        d[p][4][index] = False

DAILY_NOTSENT = True
MAIL_PAU = "paucase4@gmail.com"

sender = Emailer()

TARGET_TICKERS = ["V","T","EA","AAPL","GOOGL","AMZN","ADBE"]
TARGET_PRICES = [200,27,125,120,1900,2950,440]


def same_day(s1):
    last_close_day = str(s1.index[-1])[0:10]
    today = str(date.today())
    counter = 0
    i = 0
    while i < len(today):
        letter = today[i]
        if letter == last_close_day[i]:
            counter += 1
        i +=1
    if counter == len(today):
        return True
    else:
        return False

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
        if get_price(ticker) <= target_prices[idx] and notSent[idx] == True:
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
            #print("Error occurred while trying to download data of " + str(ticker))
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
        


def addzero(string):
    if len(string) == 1:
        return "0" + string
    else:
        return string
    

def get_change(ticker):
    price = get_price(ticker)
    try:
        percent_change = info.change(ticker)
    except:
        return -101
        #print('Error downloading data | Ticker: ' + ticker )
    return percent_change
        
def check_losses_and_wins5(tickers):
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
                if 5.0 < abs(change) and connection() and change != -101:                        
                    for p in d:
                        if change < 0:
                            print("lower than 5!")
                            if 1 in get_notifications(p):
                                if tickers[idx] in get_tickers_person(p) and get_notsent1(p)[d[p][1].index(tickers[idx])] == True:
                                    print("5% down: " + str(tickers[idx]) + " " + str(p))
                                    sender.loss_email(p,tickers[idx],prices[idx],change, False)
                                    set_as_sent(p,0,d[p][1].index(tickers[idx]))
                        elif change > 0:
                            if 2 in get_notifications(p):
                                if tickers[idx] in get_tickers_person(p) and get_notsent1(p)[d[p][1].index(tickers[idx])] == True:
                                    print("5% up: " + str(tickers[idx]) + " " + str(p))
                                    sender.win_email(p,tickers[idx],prices[idx],change)
                                    set_as_sent(p,0,d[p][1].index(tickers[idx]))
            else:
                print("Ticker {} is causing a problem.".format(ticker))
                data_found = True
    print("{}:{}:{}, finished checking 5%".format(datetime.today().hour,datetime.today().minute,datetime.today().second))
def check_losses_and_wins10(tickers):
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
                if 10.0 < abs(change) and connection() and change != -101:                        
                    for p in d:
                        if 4 in get_notifications(p):
                            if change < 0:
                                if tickers[idx] in get_tickers_person(p) and get_notsent2(p)[d[p][1].index(tickers[idx])] == True:
                                    print("10% down: " + str(tickers[idx]) + " " + str(p))
                                    sender.loss_email(p,tickers[idx],prices[idx],change, False)
                                    set_as_sent2(p,0,d[p][1].index(tickers[idx]))
                            elif change > 0:
                                if tickers[idx] in get_tickers_person(p) and get_notsent2(p)[d[p][1].index(tickers[idx])] == True and 3 in get_notifications(p):
                                    print("10% up: " + str(tickers[idx]) + " " + str(p))
                                    sender.win_email(p,tickers[idx],prices[idx],change)
                                    set_as_sent2(p,0,d[p][1].index(tickers[idx]))
            else:
                print("Ticker {} is causing a problem.".format(tickers[idx]))
                data_found = True
    
    print("{}:{}:{}, finished checking 10%".format(datetime.today().hour,datetime.today().minute,datetime.today().second))
                                
def reset_everything():
    global d
    ALL_TICKERS = get_tickers(d)
    DAILY_NOTSENT = True
    TARGET_NOT_SENT = [True]*len(TARGET_TICKERS)
    
    for p in d:
        if len(d[p]) > 3:
            d[p][3] = [True] * len(d[p][3])
        if len(d[p]) == 5:
            d[p][4] = [True] * len(d[p][4])  
    return d
    
def check_all():
    return 0

def weekend():
    day = datetime.today().isoweekday()
    print(day)
    if day == 6 or day == 7:
        check_all()
    while day == 6 or day == 7:
        time.sleep(28888)
        day = datetime.today().isoweekday()
        
def sleeping(wakeup):
    day = datetime.today()
    h = day.hour
    if h >= 21:
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
        t = 60 * ((30+60*(7-h)) - m)
        time.sleep(t)
        d = update_dict()
        reset_everything()
        print("Markets open in Europe! " + str(datetime.today()))
        
        return True
    return False


def main():
    reset_everything()
    DAILY_NOTSENT = True
    TARGET_NOT_SENT = [True]*len(TARGET_TICKERS)
    
    while True: 
        global d
        weekend()
        if sleeping(7):
            d = update_dict()
        day = datetime.today()
        print(str(day.hour)+ ":" + addzero(str(day.minute)) + ":" + addzero(str(day.minute)))
        check_losses_and_wins5(get_tickers(d))
        check_losses_and_wins10(get_tickers(d))
        if connection():
            TARGET_NOT_SENT = allprices(TARGET_TICKERS,TARGET_PRICES,TARGET_NOT_SENT)     # check prices w targets and email if necessary. If emailed, change notsent.
                        # send email if there are 5% losses 
        day = datetime.today()
        if DAILY_NOTSENT and datetime.today().hour == 14:
            for p in d:
                if 3 in get_notifications(p):
                    sender.daily_email(p,get_tickers_person(p),get_name(p))
                    DAILY_NOTSENT = False
        time.sleep(450)

d = update_dict()
info = Info()
try:
    main()
except Exception as exc:
    print(exc)
    sender2 = Emailer()
    sender2.error_email(exc) # report error to host