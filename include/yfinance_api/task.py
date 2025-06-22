import yfinance as yf
from datetime import date
import datetime as dt
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


from airflow.models import Variable

# defind date depend on number of days
def ii_duration_date(number):
    start_date = date.today() - dt.timedelta(number)
    end_date = date.today()
    return start_date, end_date

# load data from yfinance
def ii_get_data(ticker, TF, start_date, end_date):
  ticker_df = yf.download(ticker, start = start_date, end = end_date, interval = TF)
  return ticker_df

# clean column name
def ii_clean_col_name(df):
  df.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
  df.reset_index(inplace = True)
  return df

# Get ticker data by stock_list
def i_loop_ticker(stock_list, TF, number):
  ohlcv_data_intra = {}
  start_date, end_date = ii_duration_date(number)
  for ticker in stock_list:
    ohlcv_data_intra[ticker] = ii_get_data(ticker, TF, start_date, end_date)
    ohlcv_data_intra[ticker] = ii_clean_col_name(ohlcv_data_intra[ticker])
    # defind asset each name
    ohlcv_data_intra[ticker]['assetname'] = ticker

    # convert to json format
    ohlcv_data_intra[ticker] = ohlcv_data_intra[ticker].to_json(orient = 'records')

  return ohlcv_data_intra

def _get_variable():
   stock_list = Variable.get("stock_list", deserialize_json = True)
   print(f"stock_list : {stock_list}")
   return stock_list

def _get_ticker(ti = None):
    stock_list = ti.xcom_pull(task_ids = "get_stock_list")
    print(f"This is stock_list that we are gonna fetch data : {stock_list}")

    TF = stock_list['TF']
    stock = stock_list['stock_list']
    number = stock_list['duration_date_number']

    df_dict = i_loop_ticker(stock, TF, number)
    return df_dict

def _load_json_to_s3(**context):
    ti = context['task_instance']
    json_data = ti.xcom_pull(task_ids = "get_ticker") # get data from previous task
    stock_list = ti.xcom_pull(task_ids = "get_stock_list") # get variable from previouse task

    TF = stock_list['TF'] # Get Time Frame
    number = stock_list['duration_date_number'] # Get duration date number

    BUCKET_NAME = Variable.get("BUCKET_NAME") # get bucket name from airflow variabel
    s3_hook = S3Hook(aws_conn_id = "s3_bucket") # create s3 hook

    start_date, end_date = ii_duration_date(number)

    for ticker in json_data.keys():
       filename = f'ohlcv_{TF}_{start_date} - {end_date}/{ticker}'
       s3_hook.load_string(
          string_data = json_data[ticker],
          key = filename,
          bucket_name = BUCKET_NAME,
          replace = True
          )
    print(f"Successfully uploaded JSON to s3://{filename} successfully")

#def _load_json_to_s3(**context):
    ti = context['task_instance']
    json_data = ti.xcom_pull(task_ids = "get_ticker") # get data from previous task
    BUCKET_NAME = Variable.get("BUCKET_NAME") # get bucket name from airflow variabel
    s3_hook = S3Hook(aws_conn_id="s3_bucket") # create s3 hook
    s3_hook.load_string(
       string_data = json_data['AMZN'],
       key = "yfinance_data.json",
       bucket_name = BUCKET_NAME,
       replace = True
    )
    print(f"Successfully uploaded JSON to s3://{BUCKET_NAME}/yfinance_data.json")