import datetime
from datetime import date
import pandas as pd
import yfinance as yf
from collection import collecting_tweets
from collection import update


def auto_update(today):
    """
    To conduct auto update of today's tweets and today's stock price

    input:
        today: a string, the date of today

    return:
        the return is already saved in csv 
    """
 
    # collect the data that which industry is containing which stocks
    # this will be used to compute averate industry stock price
    comp = pd.read_csv('analyze_tweets/data/constituents.csv')
    comp_lst = pd.Series(comp['Symbol']).str.replace(".", '-')
    comp_lst = list(comp_lst)
    comp_lst = ['SPY'] + comp_lst
    
    print("----------------------------------- start to collect today's tweet data -----------------------------------")
    collecting_tweets.collect_tweets("china", today)
    collecting_tweets.collect_tweets("covid", today)

    print("----------------------------------- start to collect today's stock data -----------------------------------")
    y_file = yf.download(comp_lst, start='2022-02-04', end = today)    
    
    y_file = update.clean_stock_information(y_file)
    y_file = update.add_sector_y_datafile(y_file, comp)
    
    print("-----------------------------------finishing update-----------------------------------")
