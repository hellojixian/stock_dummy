import Common.config as config
from sqlalchemy.orm import sessionmaker
from FeatureExtractors.Timestep import *


def fetch_index_data(code, start_date, end_date):
    session = sessionmaker()
    session.configure(bind=config.DB_CONN)
    db = session()
    sql = """
        SELECT
            `date`,
            `open`,
            `high`,
            `low`,
            `close`,
            `volume`,
            `change`
        FROM
            raw_stock_index_daily
        WHERE
            `code` = '{0}'
                AND `date` >= '{1}'
                AND `date` < '{2}' ;
        """.format(code, start_date, end_date)
    rs = db.execute(sql)
    df = pd.DataFrame(rs.fetchall())
    df.columns = ['date', 'open', 'high', 'low', 'close', 'vol', 'change']
    db.close()
    df = df.set_index(['date'])
    return df


def fetch_index_history_data(code, start_date, range):
    session = sessionmaker()
    session.configure(bind=config.DB_CONN)
    db = session()
    sql = """
        SELECT
            `date`,
            `open`,
            `high`,
            `low`,
            `close`,
            `volume`,
            `change`
        FROM
            raw_stock_index_daily
        WHERE
            `code` = '{0}' AND `date` < '{1}'
        ORDER BY
            `date` DESC
        LIMIT 0,{2};
        """.format(code, start_date, range)
    rs = db.execute(sql)
    df = pd.DataFrame(rs.fetchall())
    df.columns = ['date', 'open', 'high', 'low', 'close', 'vol', 'change']
    db.close()
    df = df.sort_values(by=['date'], ascending=True)
    df = df.set_index(['date'])
    return df


def extract_index_features(data):
    return data
