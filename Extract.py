import pickle5 as pickle
import yfinance as yf


def get_constituents_from_pkl():
    ticker_list = []
    for i in range(5, len(data)):  # first 5 rows are empty
        for j in range(len(data.iloc[i, 0])):
            cur_tick = data.iloc[i, 0][j][0]
            if cur_tick not in ticker_list:
                ticker_list.append(cur_tick)
    return ticker_list

def extract_historical_ticker(ticker, ticker_list):
    if ticker in ticker_list:
        targ_hist = yf.download(tickers=ticker, start="2018-01-01")
        file_name = str(input_ticker) + "_history.csv"
        print(targ_hist)
        print("\n The history of " + str(input_ticker) + " has been saved to " + file_name)
        targ_hist.to_csv(file_name)
    else:
        print("The ticker you entered is either not valid or not in the constituent lists...")

if __name__ == '__main__':
    with open('constituents_history.pkl', 'rb') as f:
        data = pickle.load(f)
    input_ticker = input("Which ticker do you want (i.e. AAPL): ")

    ticker_list = get_constituents_from_pkl()
    extract_historical_ticker(input_ticker, ticker_list)

