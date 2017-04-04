import Common.config as config
from sqlalchemy.orm import sessionmaker
from FeatureExtractors.Timestep import *


def fetch_minutes_data(code, start_date, end_date):
    session = sessionmaker()
    session.configure(bind=config.DB_CONN)
    db = session()
    sql = """
        SELECT
            date(`time`) as 'date',
			time(`time`) as 'time',
            `open`,
            `high`,
            `low`,
            `close`,
            `vol`
        FROM
            raw_stock_trading_1min
        WHERE
            `code` = '{0}'
                AND `time` > '{1}'
                AND `time` < '{2}' ;
        """.format(code, start_date, end_date)
    rs = db.execute(sql)
    df = pd.DataFrame(rs.fetchall())
    df.columns = ['date', 'time', 'open', 'high', 'low', 'close', 'vol']
    db.close()
    df = df.set_index(['date'])
    return df