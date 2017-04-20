class ReturnChart:
    def __init__(self, ax):
        ax.set_title('Return', fontsize=10, loc='left', color='black')
        pass

    def draw(self, engine):
        account = engine.get_account()
        print(account.current_date, account.current_time, account.baseline_return())
        pass
