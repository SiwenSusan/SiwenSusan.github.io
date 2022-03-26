import pandas as pd
import pandas_datareader as web
import re
from datetime import timedelta
from datetime import datetime
import yfinance as yf


def clean_stock_information(df):
    """
    clean the stock file to make it adaptable for future 
    data process

    input:
        df: a dataframe
    
    return:
        df: a dataframe which is formatted 
    """
    # drop repetitive col
    dropcolumn = []
    for name in df.columns:
        if (not 'Adj Close' in name) and (not "Date" in name):
            dropcolumn.append(name)
    
    df = df.drop(columns = dropcolumn)
    
    df.columns = [b for a, b in df.columns]
    df.reset_index(inplace=True)

    return df


def add_sector_y_datafile(df, industry):
    """
    to extract industry average stock price
    using stock price dataframe

    input:
        df: a dataframe which contains all stock price
        industry: a dataframe which contains which industry has which stocks

    return:
        save to csv 
    """

    df = df.fillna(0)
    
    for idx, row in industry.iterrows():
        row["Symbol"] = row["Symbol"].replace(".", "-")
        
    for sector in industry.Sector.unique():
        df[sector] = 0

    industry_group = industry.groupby('Sector')
    
    for idx, row in df.iterrows():
        for sector in industry.Sector.unique():
            stock_num = 0
            same_industry_stock = industry_group.get_group(sector)
            for stock in same_industry_stock.Symbol:
                if stock in df.columns and row[stock] != 0:
                    df[sector][idx] = row[sector] + row[stock]
                    stock_num += 1
            if stock_num != 0:                    
                row[sector] = row[sector] / stock_num
    df = df.iloc[::-1]
    df.to_csv('analyze_tweets/data/y_file_update.csv')
