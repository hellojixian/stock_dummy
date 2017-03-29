import Common.config as config
import pandas as pd
from sqlalchemy.orm import sessionmaker


def fetch_daily_data(code, start_date, end_date):
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
            `turnover`,
            `change`
        FROM
            raw_stock_trading_daily
        WHERE
            `code` = '{0}'
                AND `date` > '{1}'
                AND `date` < '{2}' ;
        """.format(code, start_date, end_date)
    rs = db.execute(sql)
    df = pd.DataFrame(rs.fetchall())
    df.columns = ['date', 'open', 'high', 'low', 'close', 'vol', 'turnover', 'change']
    db.close()
    return df
