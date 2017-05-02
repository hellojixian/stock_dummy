from Common import config


class EnvironmentAnalysis:
    def __init__(self, ax):
        self._ax = ax
        self._vol_ax = self._ax.twinx()
        self._account = None
        self._engine = None
        self._data = None
        return

    def draw(self, engine):
        self._ax.clear()
        self._data = engine.get_static_env()
        self._ax.set_title('Environment Analysis', fontsize=config.SMALL_FONT_SIZE, loc='left', color='black')
        return
