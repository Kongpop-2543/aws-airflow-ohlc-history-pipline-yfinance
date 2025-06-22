Overview
========
In this project, I'm developing an AWS-based data pipeline utilizing airflow, python, AWS services. The objective is to Get historical OHLC data from [yfinanceAPI]https://github.com/ranaroussi/yfinance we :
- We’re pulling 1-minute timeframe data (but it’s adjustable) for the past 7 days.
- Using Python to transform data into the format we want
- And finally, store it on AWS S3

![Image](https://github.com/user-attachments/assets/e6248be0-0f7b-4ebb-b1ae-4519f1ecf6bb)


Project Contents
================
## Variable
<img width="600" alt="Image" src="https://github.com/user-attachments/assets/7ec66d9e-af54-4d0f-bcbb-0c1b26bfe563" />

defind variable as dictionary
- stock_list : list of stock list (we can add more stock name to fetch the data)
- TF : Time Frame of OHLC historical data 
- duration_date_number : Duration to fetch data as number

- BUCKETNAME : our bucket name

## Connection
<img width="600" alt="image" src="https://github.com/user-attachments/assets/45d628a9-408a-4835-aade-b466335e230f" />

S3 AWS connection
- aws_access_key_id
- aws_secret_access_key
- region_name

## Folder S3 Bucket Design
![image](https://github.com/user-attachments/assets/63d4b3d8-7ec2-4605-9c1a-49fc7ecbeac9)

Each S3 bucket is organized by date folders (one folder per day), and inside each date folder, the data is further separated by stock symbol — so each stock has its own folder.

Deploy Your Project
===================

First of all we have to load folder from command 

```astro dev init```

Start Airflow on your local machine by running 

```astro dev start```

Problem
===================
1. Log appearance : We couldn’t see the logs in Airflow webserver, so we had to update the airflow-setting.yml to enable log display.
2. XCOM : Since Airflow v2.3, it tries to serialize/deserialize DataFrames when passing data between tasks via XCom.
   By default, If we're sending a DataFrame through XCom, Airflow prefers using pyarrow (or a Pandas serializer that supports pyarrow). If your environment doesn't have pyarrow installed, you’ll either need to:
   - Install the pyarrow library
   - Change the way you're sending data — for example, convert your DataFrame to JSON before pushing it to XCom.
