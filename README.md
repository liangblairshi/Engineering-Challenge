# Engineering-Challenge

If you want to take a look at the result first, feel free to jump to Part 4 for Visualization directly. It might be easier if you pull/download all files first and put them under the same directory.

## 1) Extract

First of all, we want to fetch the historical data of the constituents within the [constituents_history.pkl](https://github.com/liangblairshi/Engineering-Challenge/blob/main/constituents_history.pkl) file.

My script in Python here allows user to input a ticker(i.e. AAPL), and then returns the historical data fetched from the API.

### Steps to run:
  1. Having python3 in local environment
  2. If you don't have pickle5 and yfinance on your local yet, install it using ```pip install pickle5``` and ```pip install yfinance```
  3. Download [constituents_history.pkl](https://github.com/liangblairshi/Engineering-Challenge/blob/main/constituents_history.pkl) and the script [Extract.py](https://github.com/liangblairshi/Engineering-Challenge/blob/main/Extract.py) in the same directory
  4. For linux/Mac terminal, go to the file directory and run ```python3 Extract.py```
  5. Input a ticker(i.e. AAPL). If it's in the constituents list, it will return it's historical data and save it to a csv file under the same directory. 

## 2) Transform & Load

I stored the historical data into AWS RDS MySQL database. One can also install MySQL Workbench locally and connect to AWS RDS to query the data. Historical data for each ticker is stored in one table. 

### About the database: 
  1. Connection credential details of AWS RDS MySQL db can be found here: [config.py](https://github.com/liangblairshi/Engineering-Challenge/blob/main/config.py)
  2. Installing MySQL Workbanch and apply the same connection credentials if interested in query locally: https://downloads.mysql.com/archives/workbench/
  3. The database storing daily constituents historical data is called ```Hist_db```
  4. The historical data has already been stored in the database. Running the script below will not update the existing table unless change the code ```if_exists='fail'``` parameter in the script.
  5. Some tickers do not exist in Yahoo Finance and therefore no historical data available, so I choose not to store those table in the database.

### How to run:
  1. If you haven't done so, install SQLAlchemy by running ```pip install SQLAlchemy```
  2. Download the script [ETL.py](https://github.com/liangblairshi/Engineering-Challenge/blob/main/ETL.py) and [config.py](https://github.com/liangblairshi/Engineering-Challenge/blob/main/config.pyhttps://github.com/liangblairshi/Engineering-Challenge/blob/main/config.py) under the same directory
  3. Run script using ```python3 ETL.py```

## 3) Analyze

This section calculate (1) the index value (price) for each day that you have data from 2018, 2019, and 2020 and store into the database
                       (2) the sector distribution within the index factoring their relative weights
                       
### Details
  1. I calculated daily index value using daily Adj Close for each existing constituent (not all tickers exist in Yahoo Finance).
  2. The index value is calculated using Price Weighted index technique which can be found here: https://investinganswers.com/dictionary/p/price-weighted-index
  3. Not all constituent have historical data back from 2018 (i.e. some constituents are new to the market, others may no longer exist). So when calculating the index value using Price Weighted index, the denominator is the number of existing constituents on a daily level.
  4. These two data sets are also stored in AWS RDS but in a different database called ```Anal_db```. Also when running the script below, it will save to csv files under the same directory.
  5. The analytical data is already stored in database. Running the script below will not update the existing table in db unless change the code ```if_exists='fail'``` parameter in the script.

### How to run:
  1. Download the scripts [Analyze.py](https://github.com/liangblairshi/Engineering-Challenge/blob/main/Analyze.py) and put it under the same directory as config.py and ETL.py
  2. Run script using ```python3 Analyze.py```

## 4) Visualize (Bonus)

I mainly used Dash to set up the webpage. The website has the following elements:
    1. Dropdown with all the constituents you have in the database.
    2. Chart with the historical data of the current constituents selected in the dropdown.
    
### How to run:
  1. Please use pip install ```dash```, ```dash_core_components```, ```dash_html_components```, ```dash_table```, and other packages mentioned in the previous steps if you haven't done so.
  2. Download the scripts [web_app.py](https://github.com/liangblairshi/Engineering-Challenge/blob/main/config.pyhttps://github.com/liangblairshi/Engineering-Challenge/blob/main/web_app.py) and put it under the same directory as your [config.py](https://github.com/liangblairshi/Engineering-Challenge/blob/main/config.pyhttps://github.com/liangblairshi/Engineering-Challenge/blob/main/config.py)
  3. Run script using ```python3 web_app.py```
  4. Once the script is running, you will find a URL in your linux commendline/terminal (i.e. http://127.0.0.1:8050/) Copy and paste it into a browser.
  5. You can choose between which database you want to display under the first dropdown: ```Hist_db```(constituents historical data) or ```Anal_db``` (Index value & sector distribution), and then choose either a ticker or an analytical result under the second dropdown. The table below will get updated.
