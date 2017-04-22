from sqlalchemy import create_engine
import pandas as pd
import os, sys
from os.path import expanduser

home = expanduser("~")

STOCK_DATA_PATH = os.path.join(home, 'stock_data', 'stock_daily_data')
INDEX_DATA_PATH = os.path.join(home, 'stock_data', 'index_daily_data')
MINUTE_DATA_PATH = os.path.join(home, 'stock_data', 'minute_daily_data')

MYSQL_CONN = 'mysql://stock_prediction:jixian@192.168.100.118/stock_prediction?charset=utf8'
DB_CONN = create_engine(MYSQL_CONN)

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)
CACHE_DIR = os.path.join(PROJECT_ROOT, 'CacheRoot')
MODEL_DIR = os.path.join(PROJECT_ROOT, 'ModelParameters')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'Output')
LOG_DIR = os.path.join(PROJECT_ROOT, 'Logs')

pd.set_option('display.width', 2000)
pd.set_option('display.max_columns', 200)
pd.set_option('display.max_rows', 2000)

LARGE_FONT_SIZE = 10
MIDDLE_FONT_SIZE = 9
SMALL_FONT_SIZE = 7
