import numpy as np

def handle_data(account, data):
    if account.current_time == '09:35':
        if np.random.uniform() > 0.5:
            account.order(10)
        else:
            account.order(-10)
    pass
