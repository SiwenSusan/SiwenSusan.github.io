# Analyzing Twitter Sentiment on Stock Market Movements
We look into how the polarity of sentiments in tweets is 
related to the daily movements of stock prices!

## Requirements
```bash
pip install -r requirements.txt
```

## Usage
```python
# from the proj-fight_potatoes directory:
python3 analyze_tweets/app.py
```

### Command-line inputs
All possible dates for training/testing dates:
```bash
214 215 216 217 218 222 223 224 225 301 302 303 304 307 314 315
```

Default training dates:
```bash
214 215 216 217 218 222 223 224 225 301 302
```

Default testing dates:
```bash
303 304 307 314 315
```

## Example Output
Part 1:
![Alt text](pic_part1.png?raw=true "Title")

Part 2:
![Alt text](pic_part2.png?raw=true "Title")

## Project Introduction
Stock prices are influenced by the public attitude towards the market. Psychological research shows that emotions play a significant role in human decision-making. Similarly, behavioral finance research shows that financial decisions are influenced by people's emotions and moods.
Twitter is a popular place for users to express their moods and sentiments towards a variety of topics. We look into how the polarity of sentiments in tweets is related to the daily movements of stock prices!
Data:
Tweets were collected from the Twitter Developer API. We gathered around 1.6 million tweets related to COVID-19 and US-China Relations from Feb 14 to March 15.
The query keywords used to collect tweets are as follows:
COVID-19: covid19, covid, covid-19, vaccine, vaccination, omicron, booster, mask, mandate, lockdown, death rate, travel restriction, total infections, breakthrough infections, social distancing, quarantine, isolation, pandemic, & shutdown.
US-China Relations: Trump, Biden, trade war, Xi Jinping, Eileen Gu, Taiwan, Hong Kong, CCP, TikTok, Huawei, tariffs, human rights, Xinjiang, Zhao Lijian, & Ned Price.
We collected stock data from all S&P 500 companies and grouped the data into 11 different sectors: Information Technology, Health Care, Consumer Discretionary, Financials, Communication Services, Industrials, Consumer Staples, Energy, Real Estate, Materials, and Utilities.


## How to interact with the application and what it produces. 
Users can interact with the project through the command line and the web application.
Screenshots of the output are presented in README.md.
There are 3 user input opportunities in the command line:
(1) users can choose to have the tweets and the financial data auto-update for the day you interact with this project;
Example input: yes (Note: User can always press enter to use the default value)
(2) users can choose training and testing dates used in the models;:
Example input: 214 215 216 217 (Note: User can always press enter to
use the default value)
(3) finally, users are able to choose different independent variables (polarity of the tweets, subjectivity of the tweets and/or 5-day moving average)
Example input: 0 1 2 (Note: User can always press enter to use the default value)
All command line inputs should be integers representing dates/variables; multiple selections should be separated by a space (examples are given in the command line prompt).
In the web application, the application will produce two graphs and one table. One of the graphs is for the testing data and the other one is for training data. Users can
check out the different graphs through the various dropdown menus.
You can choose a topic (Covid or China) and a model to see the accuracy of the prediction using average Twitter sentiments on stock market movement. If you choose the linear regression model, you can also select a sector. For all other models, we show the accuracy of the models with all sectors on one plot.
