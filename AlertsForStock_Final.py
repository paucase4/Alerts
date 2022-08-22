import time
import yfinance as yf
from datetime import datetime,timedelta,date
import time
import urllib3 as u3
import gspread
import collections
import sys
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST, TimeFrame
from alpaca_trade_api.stream import Stream
from Data import current_Info, weekly_Info
from Client import Client
from HTML_Email import Emailer

def get_keys():
    path = ""
    with open(path + '/api_key.txt','rb') as f:
        key = str(f.readlines()[0])[2:-1]
    with open(path + '/secret_key.txt','rb') as f:
        lines2 = str(f.readlines()[0])[2:-1]
    return key,lines2
 
def connection():
    http = u3.PoolManager()
    try:
        http.request('GET',"google.com")
        return True
    except:
        return False

def mkt_open():
    global rest_api
    return rest_api.get_clock().is_open
def get_price(ticker):
    global rest_api
    a = ""
    if connection():
        try:
            close = rest_api.get_position(ticker).current_price
           
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
    global rest_api
    try:
        return float(rest_api.get_position(ticker).change_today)
    except:
        return -101
        print('Error downloading data | Ticker: ' + ticker)

def addzero(string):
    if len(string) == 1:
        return "0" + string
    else:
        return string
        
def check_losses_and_wins5(tickers):
    global NOTSENT1
    global rest_api
    pct = 5
    prices = get_prices(tickers)
    print("{}:{}:{}, start checking 5%".format(datetime.today().hour,datetime.today().minute,datetime.today().second))
    for idx,ticker in enumerate(tickers):
        if prices[idx] == -10:
            data_found = False
            print("Ticker {} is causing a problem.".format(ticker))
        else:
            change = get_change(ticker)
            if 5.0 < abs(change) and connection() and change != -101 and NOTSENT1[idx] == True:                        
                if change < 0:
                    if rest_api.get_position(tickers[idx]).side == 'long':
                        sender.loss_email(MAIL_PAU,tickers[idx],prices[idx],change,True)
                    else:
                        sender.win_email_email(MAIL_PAU,tickers[idx],prices[idx],change)
                    
                else:
                    if rest_api.get_position(tickers[idx]).side == 'long':
                        sender.win_email(MAIL_PAU,tickers[idx],prices[idx],change)
                    else:
                        sender.loss_email_email(MAIL_PAU,tickers[idx],prices[idx],change, True)
                NOTSENT1[idx] = False    
    print("{}:{}:{}, finished checking 5%".format(datetime.today().hour,datetime.today().minute,datetime.today().second))
                                
def reset_everything():
    global NOTSENT1
    global ALL_TICKERS
    ALL_TICKERS,NOTSENT1 = get_all_tickers()
    DAILY_NOTSENT = True
    return True
    
def weekly_report():
    Emailer().weekly_email(MAIL_PAU,get_all_tickers()[0],"Pau")
    
def monthly_report():
    Emailer().monthly_email(MAIL_PAU,get_all_tickers()[0],"Pau")


def sign_in():
    API_KEY,SECRET_KEY = get_keys()
    rest_api = REST(API_KEY, SECRET_KEY, 'https://api.alpaca.markets')
    return rest_api
def get_all_tickers():    
    tickers = []
    notsent1 = {}
    for pos in rest_api.list_positions():
        tickers.append(pos.symbol)
        notsent1[pos.symbol] = [True]
    return tickers, notsent1

def start_message():
    day = datetime.today()
    print(str(day.hour)+ ":" + addzero(str(day.minute)) + ":" + addzero(str(day.minute)))
    
def main():
    reset_everything()
    DAILY_NOTSENT = True
    month = 20
    global rest_api
    global NOTSENT1
    while True: 
        while mkt_open():
            open = True
            sign_in()
            ALL_TICKERS = get_all_tickers()[0]
            print("Checking tickers: " + str(ALL_TICKERS))
            check_losses_and_wins5(ALL_TICKERS)
            weekend = False
            time.sleep(1000)
        if open:
            Emailer.daily_email(MAIL_PAU,get_all_tickers(),"Pau")
            open = False
            reset_everything()
            ALL_TICKERS, NOTSENT1 = get_all_tickers()
        if (datetime.today().weekday() + 1) == 4:
            weekly_report()
        if month !=  datetime.today().month:
            monthly_report()
        
            
            
API_KEY,SECRET_KEY = get_keys()
rest_api = REST(API_KEY, SECRET_KEY, 'https://api.alpaca.markets')       
info = current_Info()
DAILY_NOTSENT = True
MAIL_PAU = "paucase4@gmail.com"
sender = Emailer()
ALL_TICKERS,NOTSENT1 = get_all_tickers()

def error_message(e,checkpoint):
    checkpoint = 2 # sempre
    exception_type, exception_object, exception_traceback = sys.exc_info()
    line_number = exception_traceback.tb_lineno
    filename = exception_traceback.tb_frame.f_code.co_filename
    return f"Exception: {e} <br>\nException Type: {exception_type}\n<br>Exception File: {filename}\n<br>Exception in line: {line_number}\n<br>Checkpoint: {checkpoint}"
    
try:
    main()
except Exception as e:
    Emailer().error_email(e)
    checkpoint = 0
    error_message = error_message(e,checkpoint)
    print(error_message)
    Emailer().error_email(error_message) # report error to host
