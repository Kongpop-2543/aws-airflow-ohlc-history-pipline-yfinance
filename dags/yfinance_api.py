from airflow.decorators import dag, task
from pendulum import datetime, duration
from airflow.models import Variable
from airflow.operators.python import PythonOperator

from include.yfinance_api.task import _get_variable, _get_ticker, _load_json_to_s3

@dag(
    start_date = datetime(2025, 6, 1),
    schedule = "@weekly",
    catchup = False,
    default_args = {
        "retries" : 1,
        "retry_delay" : duration(seconds = 2),
        "retry_exponential_backoff" : True
    },
    tags = ['yfinance_API'])

def yfinance_api():
    get_stock_list  = PythonOperator(
        task_id = "get_stock_list",
        python_callable = _get_variable
    )
    
    get_ticker = PythonOperator(
        task_id = "get_ticker",
        python_callable = _get_ticker
    )
    
    load_json_to_s3 = PythonOperator(
        task_id = "load_json_to_s3",
        python_callable = _load_json_to_s3
    )

    get_stock_list >> get_ticker >> load_json_to_s3

yfinance_api()