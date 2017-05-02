
def get_static_env(date, engine):
    daily_data = engine.get_daily_data()
    index_data = engine.get_index_daily_data()

    print(index_data.head(50))
    return
