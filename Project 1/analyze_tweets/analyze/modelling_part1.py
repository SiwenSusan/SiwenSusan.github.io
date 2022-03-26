import textblob
import csv
import pandas as pd
import re
import numpy as np


def get_weighted_ps_indicator(filename):
    """
    Perform sentiment analysis on Tweets and 
    assign weights
    
    Input:
        filename: string, for example: "data/tweets_china_021422.csv"
        
    Returns: 
        ave_polarity, ave_subjectivity, corpus (tuple):
            average polarity and average subjectivity
    """
    
    tweets = pd.read_csv(filename)
    tweets.columns = ["time","id1","id2","popularity","content"]
    total_polarity = 0
    total_subjectivity = 0
    num_tweets = 0
    corpus = ''

    for idx, row in tweets.iterrows():
        text = row["popularity"]
        if not text:
            break
        weight = re.search(r"(?<='like_count': )\w+", text)  ############ mutable
        weight = 1 + int(weight.group(0)) ############ mutable
        blob = textblob.TextBlob(row["content"])
        polarity, subjectivity = blob.sentiment
        total_polarity += polarity * weight
        total_subjectivity += subjectivity * weight
        num_tweets += weight
        if weight > 500:    ######## mutable
            corpus += row["content"]

    ave_polarity = total_polarity / num_tweets 
    ave_subjectivity = total_subjectivity / num_tweets 
    
    return ave_polarity, ave_subjectivity, corpus


def collect_y(dates, y_datafile, stock):
    """
    Collect relevant stock data

    Inputs:
        dates: dates in the format of list e.g. [215]
        y_datafile (str): for example: 'data/S&P_update.csv'
        stock: a list of stocks or sectors

    Returns:
        y_dummy:
        y_num:
    """
    y_num = []
    y_dummy = [] 

    for idx, day in enumerate(dates):
        day = str(day)
        day_text = "2022-0" + f"{day[0]}"+"-"+f"{day[1:]}"
        if idx == 0:
            preceding_index = y_datafile.index.get_loc(day_text) + 1
            preceding_date = y_datafile.index[preceding_index]
            y_num.append(y_datafile.loc[preceding_date][stock])
        y_num.append(y_datafile.loc[day_text][stock])
    starting_y = y_num[0]        
    for y in y_num[1:]:
        if y > starting_y:
            y_dummy.append(1)
        else:
            y_dummy.append(0)
        starting_y = y
        
    y_num = np.array(y_num[1:])
    
    return y_dummy, y_num


def five_days(date, y_datafile, stock):
    '''
    Computes 5-day moving average

     Inputs:
        dates: dates in the format of list e.g. [215]
        y_datafile (str): for example: 'data/S&P_update.csv'
        stock: a list of stocks or sectors

    Returns:
        5-day moving average (float)

    '''
    stock_price = []
    for i in range(5):
        preceding_index = y_datafile.index.get_loc(date) + (i+1)
        preceding_date = y_datafile.index[preceding_index]
        new = y_datafile.loc[preceding_date][stock] 
        stock_price.append(new)
    sum = 0
    for s in stock_price:
        sum += s
    return sum / len(stock_price)


def five_days_stock_price(dates, y_datafile, stock):
    '''
    Creates an array of 5-day stock prices

    Inputs:
        dates: dates in the format of list e.g. [215]
        y_datafile (str): for example: 'data/S&P_update.csv'
        stock: a list of stocks or sectors

    Returns:
        (numpy array) 5-day price list
    '''
    price_list = []
    for d in dates:
        day = str(d)
        day_text = "2022-0" + f"{day[0]}"+"-"+f"{day[1:]}"
        p = five_days(day_text, y_datafile, stock)
        price_list.append(p)
    return np.array(price_list)


def collect_x(dates, topic):
    '''
    Collects relevant independent variable data
    Inputs: 
        dates in the format of list e.g. [215]
        topic: "covid" or "china"

    Returns:
        Xs: numpy array of average polarity and subjectivity
    '''
    
    all_ave_polarity = []
    all_ave_subjectivity = []
    for date in dates:
        filename = f"analyze_tweets/data/tweets_{topic}_0{date}22.csv"
        ave_polarity, ave_subjectivity, _ = get_weighted_ps_indicator(filename)
        all_ave_polarity.append(ave_polarity)
        all_ave_subjectivity.append(ave_subjectivity)
    Xs = np.column_stack([all_ave_polarity, all_ave_subjectivity])
    
    return Xs


def collect_all_x_and_y(dates, topics, y_filename, stocks):
    """
    collect the dependent variable and independent variable of specified dates and topics average directly
    
    input:
        dates: a list of dates, the date should only be trading dates.
                for example, [214,215,216,217,218,222,223,224,225,228,301,302]
        topic: string, either "covid" or "china"
        y_filename: for example: 'data/S&P_update.csv'
        stocks: a list of stocks or sectors
        
    return(tuple): a tuple of average polarity and average subjectivity
    """
    print("---> working on extracting sentiment indicator")

    x_dic = {}
    for topic in topics:
        x_dic[topic] = collect_x(dates, topic)
        
    print("---> working on extracting dependent variable")
    y_dic = {}
    x3_dic = {}
    y_datafile = pd.read_csv(y_filename, header = 0, thousands=',')
    y_datafile.set_index("Date", inplace = True)
    for stock in stocks:
        moving_average = five_days_stock_price(dates, y_datafile, stock)
        y_dic[stock] = collect_y(dates, y_datafile, stock)
        x3_dic[stock] = moving_average
        
    return y_dic, x_dic, x3_dic
