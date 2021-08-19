# Engineering-Challenge


## Setting up EC2 connection
I've put all files under AWS EC2 to make the running process more easier. Please follow the step to access my EC2 instance.
  1. Make sure to download the [IMFS.pem](https://github.com/liangblairshi/Engineering-Challenge/blob/a8ee9aa8d1b48bfaeb1e3bb5e0c1774def37a146/IMFS.pem) credential file to your local
  2. Make sure you change the .pem permission using ```chmod 600 /your-full-path-of-local-pem-file/IMFS.pem```
  3. SSH to access my EC2 instance. Use the following commend in your terminal/linux environment: ```ssh -i /your-full-path-of-local-pem-file/IMFS.pem ec2-user@ec2-13-58-134-135.us-east-2.compute.amazonaws.com```
  4. Once you successfully access the instance, go to the folder IMFS-challenge by using ```cd IMFS-challenge``` commend. All my .py files are under this directory.

Once you are here, please feel to follow the steps below or jump to Part 4 for Visualization directly if you want.


## 1) Extract

First of all, we want to fetch the historical data of the constituents within the [constituents_history.pkl](https://github.com/liangblairshi/Engineering-Challenge/blob/f4fd5e9c7b9a4a173b4e83696c0d997617e39d4d/constituents_history.pkl) file.

My script in Python here allows user to input a ticker(i.e. AAPL), and then returns the historical data fetched from the API.

### Steps to run through SSH:
  1. In your SSH EC2 environment (under directory ```IMFS-challenge```), run ```python3 Extract.py```
  2. Input a ticker(i.e. AAPL). If it's in the constituents list, it will return it's historical data and save it to a csv file under the same directory. 

Note: I'm having trouble installing ```pickle5``` on EC2. What I did alternatively was to load .pkl file locally using pickle5, and then dump to a new .pkl file using pickle instead of pickle5 to avoid version issue as the given .pkl file was most likely saved under protocol 5. This does not change the outcome. 

## 2) Transform & Load

I stored the historical data into AWS RDS MySQL database. One can also install MySQL Workbench locally and connect to AWS RDS to query the data. Historical data for each ticker is stored in one table. 

### About the database: 
  1. Connection credential details of AWS RDS MySQL db can be found here: [config.py](https://github.com/liangblairshi/Engineering-Challenge/blob/f4fd5e9c7b9a4a173b4e83696c0d997617e39d4d/config.py)
  2. Installing MySQL Workbanch and apply the same connection credentials if interested in query locally: https://downloads.mysql.com/archives/workbench/
  3. The database storing daily constituents historical data is called ```Hist_db```
  4. The historical data has already been stored in the database. Running the script below will not update the existing table unless change the code ```if_exists='fail'``` parameter in the script.
  5. Some tickers do not exist in Yahoo Finance and therefore no historical data available, so I choose not to store those table in the database.

### How to run:
  In your SSH EC2 environment (under directory ```IMFS-challenge```), run script using ```python3 ETL.py```

## 3) Analyze

This section calculate (1) the index value (price) for each day that you have data from 2018, 2019, and 2020 and store into the database
                       (2) the sector year-end distribution within the index factoring their relative weights
                       
### Details
  1. I calculated daily index value using daily Adj Close for each existing constituent (not all tickers exist in Yahoo Finance).
  2. The index value is calculated using Price Weighted index technique which can be found here: https://investinganswers.com/dictionary/p/price-weighted-index
  3. Not all constituent have historical data back from 2018 (i.e. some constituents are new to the market, others may no longer exist). So when calculating the index value using Price Weighted index, the denominator is the number of existing constituents on a daily level.
  4. The sector distribution is calculated by grouping constituents by sector and then divided the total value to get the weight. The sector distribution is at year end.
  5. These two data sets are also stored in AWS RDS but in a different database called ```Anal_db```. Also when running the script below, it will save to csv files under the same directory.
  6. The analytical data is already stored in database. Running the script below will not update the existing table in db unless change the code ```if_exists='fail'``` parameter in the script.

### How to run:
  In your SSH EC2 environment (under directory ```IMFS-challenge```), run script using ```python3 Analyze.py```

## 4) Visualize (Bonus)

I mainly used Dash to set up the webpage. The website has the following elements:
    1. Dropdown with all the constituents you have in the database.
    2. Chart with the historical data of the current constituents selected in the dropdown.
    
### How to run:
  1. In your SSH EC2 environment (under directory ```IMFS-challenge```), run script using ```python3 web_app.py```
  2. Once the script is up and running, open your browser and access this URL: http://13.58.134.135:8050/
  3. You can choose between which database you want to display under the first dropdown: ```Hist_db```(constituents historical data) or ```Anal_db``` (Index value & sector distribution), and then choose either a ticker or an analytical result under the second dropdown. The table below will get updated.
