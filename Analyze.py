from sqlalchemy import create_engine
import pandas as pd
import config
import ETL

# get valid constituents list
def get_reduced_constituents_info():
    data = ETL.read_pkl('constituents_history.pkl')
    ticker_list, sector_list = ETL.get_constituents_from_pkl(data)
    ticker_sec_lookup = {ticker_list[i]: sector_list[i] for i in range(len(ticker_list))}
    table_list = pd.read_sql("SHOW TABLES;", con=hist_engine)
    new_ticker_list = table_list[table_list.columns].squeeze()
    new_ticker_sec_lookup = ticker_sec_lookup.copy()
    for ticker in ticker_list:
        if ticker not in new_ticker_list.tolist():
            new_ticker_sec_lookup.pop(ticker)
    return new_ticker_list, new_ticker_sec_lookup

# merge Adj Close price for all constituents history into one table
def merge_ticker_value_in_one_table(ticker_list):
    print("Getting constituents daily Adj Close price...This may take a while...")
    df_list = [[] for i in range(len(ticker_list))]
    df_merged_price = pd.read_sql('SELECT * from `' + str(ticker_list[0]) + '`', con=hist_engine)[['Date', 'Adj Close']]
    for i in range(1, len(ticker_list)):
        df_list[i] = pd.read_sql('SELECT * from `' + str(ticker_list[i]) + '`', con=hist_engine)[['Date', 'Adj Close']]
        df_merged_price = pd.merge(df_merged_price, df_list[i], how='outer', on='Date')

    df_merged_price = df_merged_price.set_index('Date')
    df_merged_price = df_merged_price.sort_index()
    df_merged_price.columns = ticker_list
    mask = (df_merged_price.index >= pd.to_datetime('2018-01-01').date()) & (df_merged_price.index < pd.to_datetime('2021-01-01').date())
    df_merged_price = df_merged_price.loc[mask]
    print("...Done\n")
    return df_merged_price

# calculate index value
def cal_index_value(df_merged_price):
    print("Calculating Daily Index Value...")
    index_value_table = df_merged_price.copy()
    index_value_table['Total Valid Constituents'] = index_value_table.count(axis=1)
    index_value_table['Index Value'] = index_value_table.sum(axis=1) / index_value_table['Total Valid Constituents']
    index_value_table = index_value_table.iloc[:,-2:]
    print("...Done\n")
    return index_value_table

# calculate sector distribution
def cal_sector_dist(new_ticker_sec_lookup, df_merged_price):
    print("Calculating Yearly Sector Weight Distribution...")
    sector_table = df_merged_price.copy()
    ticker_sec_tuples = [(k, v) for k, v in new_ticker_sec_lookup.items()]

    sector_table.columns = pd.MultiIndex.from_tuples(ticker_sec_tuples)
    sector_table = sector_table.groupby(level=1, axis=1).sum()
    sector_table['Total Value'] = sector_table.sum(axis=1)
    sector_weight_table = sector_table.div(sector_table['Total Value'], axis=0)
    year_end_date = [pd.to_datetime('2018-12-31').date(), pd.to_datetime('2019-12-31').date(),
                     pd.to_datetime('2020-12-31').date()]
    sector_weight_table = sector_weight_table.loc[year_end_date]
    print("...Done\n")
    return sector_weight_table

# save the analytical results to database and to csv
def save_results(index_value_table, sector_weight_table):
    # write to db
    try:
        name = 'Daily_Index_Value'
        if not index_value_table.empty:
            index_value_table.to_sql(name, con=anal_engine, if_exists='fail')
    except ValueError:
        print("Table " + name + " already exists.")
    try:
        name = 'YearEnd_Sector_Weight'
        if not sector_weight_table.empty:
            sector_weight_table.to_sql(name, con=anal_engine, if_exists='fail')
    except ValueError:
        print("Table " + name + " already exists.")

    #write to csv
    index_value_table.to_csv('Daily_Index_Value.csv')
    sector_weight_table.to_csv('YearEnd_Sector_Weight.csv')


if __name__ == '__main__':

    # hist_engine is used to read historical constituents data from ETL db
    hist_engine = create_engine("mysql+mysqlconnector://{user}:{pw}@{host}/{db}".format(user=config.user, pw=config.passwd, host=config.host, db=config.ETL_db_name))
    # anal_engine is used to write the analytical data to analyze db
    anal_engine = create_engine("mysql+mysqlconnector://{user}:{pw}@{host}/{db}".format(user=config.user, pw=config.passwd, host=config.host, db=config.anal_db_name))

    # Analyze
    new_ticker_list, new_ticker_sec_lookup = get_reduced_constituents_info()
    df_merged_price = merge_ticker_value_in_one_table(new_ticker_list)
    index_value_table =cal_index_value(df_merged_price) # calculate the daily index value (price)
    sector_weight_table = cal_sector_dist(new_ticker_sec_lookup, df_merged_price) # calculate the year end sector distribution

    save_results(index_value_table, sector_weight_table)


