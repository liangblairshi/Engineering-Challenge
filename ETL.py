import pickle
import yfinance as yf
from sqlalchemy import create_engine
import config

# read pkl file
def read_pkl(pkl_name):
    with open(pkl_name, 'rb') as f:
        data = pickle.load(f)
    return data

# generate ticker and sector list from constituents history list
def get_constituents_from_pkl(data):
    ticker_list = []
    sector_list = []
    for i in range(5, len(data)): # first 5 rows are empty
        for j in range(len(data.iloc[i,0])):
            cur_tick = data.iloc[i,0][j][0]
            cur_sec = data.iloc[i,0][j][2]
            if cur_tick not in ticker_list and cur_tick != "OXY WS WI" and cur_tick != "-": # these two tickers are empty and is causing errors
                ticker_list.append(cur_tick)
                sector_list.append(cur_sec)
    return ticker_list, sector_list

# download historical data on yahoo finance from the target ticker
def download_historical_data_from_ticker(ticker, ticker_list):
    if ticker in ticker_list:
        return yf.download(tickers=ticker, start="2018-01-01")

# generate historical data list for the target ticker
def gen_hist_data(targ_ticker, ticker_list):
    targ_hist = download_historical_data_from_ticker(targ_ticker, ticker_list)
    return targ_hist

# transfer and load the data to AWS RDS MySQL
def trans_load_database(ticker_list, engine):
    for ticker in ticker_list:
        print("ETL daily historical data for " + str(ticker) + " ...")
        targ_hist = gen_hist_data(ticker, ticker_list)
        try:
            if not targ_hist.empty:
                targ_hist.index = targ_hist.index.date
                targ_hist.index.name = 'Date'
                targ_hist.to_sql(ticker, con=engine, if_exists='fail')
        except ValueError as e:
            print("Table " + str(ticker) + " already exists.")
    print("...DONE...All constituents daily history has been uploaded to AWS RDS...")

if __name__ == '__main__':

    engine = create_engine("mysql+mysqlconnector://{user}:{pw}@{host}/{db}".format(user=config.user, pw=config.passwd, host=config.host, db=config.ETL_db_name))

    data = read_pkl('constituents_history.pkl')
    ticker_list, sector_list = get_constituents_from_pkl(data)  # generate ticker and sector list from constituents history list
    trans_load_database(ticker_list, engine) # loading all historical data takes a while
