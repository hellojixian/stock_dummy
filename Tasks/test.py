import matplotlib.pyplot as plt
from matplotlib import ticker
import matplotlib.patches as patches
import numpy as np

data = {
    "current": {
        "date": "2015-01-12",
        "index": {
            "open": -0.827902757951057
        },
        "stock": {
            "open": 1.4837554361729297
        }
    },
    "prev": {
        "date": "2015-01-09",
        "index": {
            "open": -0.5006892447456547,
            "high": 3.381550102323996,
            "low": -0.7879251607731631,
            "close": -0.2444237974652852,
            "open_2": -2.874375731709125,
            "high_2": 0.9152477066939377,
            "low_2": -3.1547592584359463,
            "close_2": -2.624223832599771,
            "open_3": -2.2223216816601776,
            "high_3": 1.5927434394068272,
            "low_3": -2.5045875665756494,
            "close_3": -1.9704903847588346,
            "bar": 0.2575549974519161,
            "upline": 3.9017751154267555,
            "downline": 0.5462363097617505,
            "vol30": 0.8534959036001517,
            "vol60": 1.1336313337462676
        },
        "stock": {
            "open": -0.9647118558009713,
            "high": 1.243970550901249,
            "low": -1.6247778624016262,
            "close": -0.7616146230007544,
            "open_2": 5.347015933027267,
            "high_2": 7.696462327842293,
            "low_2": 4.644882527680256,
            "close_2": 5.563056980826363,
            "open_3": 8.99692651578653,
            "high_3": 11.427773120983526,
            "low_3": 8.270466610785137,
            "close_3": 9.220452640402359,
            "bar": 0.20507562163549192,
            "upline": 2.230197385285836,
            "downline": 0.8715713919507907,
            "vol30": 1.141276147388635,
            "vol60": 1.3349397697624448
        }
    },
    "prev2": {
        "date": "2015-01-09",
        "index": {
            "open": -0.058981312704686845,
            "high": 0.22584804161295652,
            "low": -2.6334118762874352,
            "close": -2.3856310852265086,
            "bar": -2.3280228709711857,
            "upline": 0.2849974495545655,
            "downline": 0.24792702167285874,
            "vol30": 0.7760640751192426,
            "vol60": 0.7760640751192426
        },
        "stock": {
            "open": 0.7291385363218904,
            "high": 9.37078044828517,
            "low": 0.6211180124223518,
            "close": 6.3732109100729115,
            "bar": 5.603217158176953,
            "upline": 2.975871313672921,
            "downline": 0.10723860589812104,
            "vol30": 2.294835736044893,
            "vol60": 2.294835736044893
        }
    },
    "prev3": {
        "date": "2015-01-09",
        "index": {
            "change": 0.6713512061943339,
            "bar": 1.4218508108757977,
            "vol30": 0.822791202689837,
            "vol60": 0.822791202689837
        },
        "stock": {
            "change": 3.4646549315451303,
            "bar": 3.3780011166945867,
            "vol30": 1.7504647762144798,
            "vol60": 1.7504647762144798
        }
    }
}

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

index_width = 0.4
stock_width = 0.4
y_max = 10
y_min = -10
labels = ['change', 'bar', 'vol', '',
          'open', 'high', 'low', 'close', 'upline', 'downline', 'bar', 'vol', '',
          'open_3', 'high_3', 'low_3', 'close_3', 'open_2', 'high_2', 'low_2', 'close_2', 'open', 'high', 'low',
          'close', 'upline', 'downline', 'bar', 'vol', '',
          'open']

def _annotate_bar(pos, value):
    if value > 0:
        sign = '+'
        color = 'red'
    else:
        sign = ''
        color = 'green'
    ax.annotate('{}{:.2f}%'.format(sign, value),
                xy=(pos, -9.6), xycoords='data',
                color=color, weight='bold',
                ha='center', va='bottom', rotation=90,
                fontsize=7)


def _draw_bar(pos, type, value):
    if value > 0:
        color = 'red'
    else:
        color = 'green'

    if type == 'index':
        offset = 0.15
        if color == 'red':
            color = 'firebrick'
        elif color == 'green':
            color = 'darkgreen'
    else:
        offset = - 0.15

    ax.bar(pos + offset, value, 0.3, color=color)


_draw_bar(0, 'stock', data['prev3']['stock']['change'])
_draw_bar(1, 'stock', data['prev3']['stock']['bar'])
_draw_bar(2, 'stock', data['prev3']['stock']['vol60'])
_draw_bar(0, 'index', data['prev3']['index']['change'])
_draw_bar(1, 'index', data['prev3']['index']['bar'])
_draw_bar(2, 'index', data['prev3']['index']['vol60'])
_annotate_bar(0, data['prev3']['stock']['change'])
_annotate_bar(1, data['prev3']['stock']['bar'])
_annotate_bar(2, data['prev3']['stock']['vol60'])
ax.plot([3, 3], [y_min, y_max], linewidth=1, color='black', alpha=0.5)

ax.add_patch(patches.Rectangle((3.5, y_max), 4, y_min, fill=True, color='black', alpha=0.1))
ax.add_patch(patches.Rectangle((3.5, y_min), 4, y_max, fill=True, color='black', alpha=0.1))
_draw_bar(4, 'stock', data['prev2']['stock']['open'])
_draw_bar(5, 'stock', data['prev2']['stock']['high'])
_draw_bar(6, 'stock', data['prev2']['stock']['low'])
_draw_bar(7, 'stock', data['prev2']['stock']['close'])
_draw_bar(8, 'stock', data['prev2']['stock']['upline'])
_draw_bar(9, 'stock', data['prev2']['stock']['downline'])
_draw_bar(10, 'stock', data['prev2']['stock']['bar'])
_draw_bar(11, 'stock', data['prev2']['stock']['vol60'])
_draw_bar(4, 'index', data['prev2']['index']['open'])
_draw_bar(5, 'index', data['prev2']['index']['high'])
_draw_bar(6, 'index', data['prev2']['index']['low'])
_draw_bar(7, 'index', data['prev2']['index']['close'])
_draw_bar(8, 'index', data['prev2']['index']['upline'])
_draw_bar(9, 'index', data['prev2']['index']['downline'])
_draw_bar(10, 'index', data['prev2']['index']['bar'])
_draw_bar(11, 'index', data['prev2']['index']['vol60'])
_annotate_bar(4, data['prev2']['stock']['open'])
_annotate_bar(5, data['prev2']['stock']['high'])
_annotate_bar(6, data['prev2']['stock']['low'])
_annotate_bar(7, data['prev2']['stock']['close'])
_annotate_bar(8, data['prev2']['stock']['upline'])
_annotate_bar(9, data['prev2']['stock']['downline'])
_annotate_bar(10, data['prev2']['stock']['bar'])
_annotate_bar(11, data['prev2']['stock']['vol60'])
ax.plot([12, 12], [y_min, y_max], linewidth=1, color='black', alpha=0.5)

ax.add_patch(patches.Rectangle((12.5, y_max), 4, y_min, fill=True, color='black', alpha=0.1))
ax.add_patch(patches.Rectangle((12.5, y_min), 4, y_max, fill=True, color='black', alpha=0.1))
ax.add_patch(patches.Rectangle((20.5, y_max), 4, y_min, fill=True, color='black', alpha=0.1))
ax.add_patch(patches.Rectangle((20.5, y_min), 4, y_max, fill=True, color='black', alpha=0.1))
_draw_bar(13, 'stock', data['prev']['stock']['open_3'])
_draw_bar(14, 'stock', data['prev']['stock']['high_3'])
_draw_bar(15, 'stock', data['prev']['stock']['low_3'])
_draw_bar(16, 'stock', data['prev']['stock']['close_3'])
_draw_bar(17, 'stock', data['prev']['stock']['open_2'])
_draw_bar(18, 'stock', data['prev']['stock']['high_2'])
_draw_bar(19, 'stock', data['prev']['stock']['low_2'])
_draw_bar(20, 'stock', data['prev']['stock']['close_2'])
_draw_bar(21, 'stock', data['prev']['stock']['open'])
_draw_bar(22, 'stock', data['prev']['stock']['high'])
_draw_bar(23, 'stock', data['prev']['stock']['low'])
_draw_bar(24, 'stock', data['prev']['stock']['close'])
_draw_bar(25, 'stock', data['prev']['stock']['upline'])
_draw_bar(26, 'stock', data['prev']['stock']['downline'])
_draw_bar(27, 'stock', data['prev']['stock']['bar'])
_draw_bar(28, 'stock', data['prev']['stock']['vol60'])
_draw_bar(13, 'index', data['prev']['index']['open'])
_draw_bar(14, 'index', data['prev']['index']['high_3'])
_draw_bar(15, 'index', data['prev']['index']['low_3'])
_draw_bar(16, 'index', data['prev']['index']['close_3'])
_draw_bar(17, 'index', data['prev']['index']['open_2'])
_draw_bar(18, 'index', data['prev']['index']['high_2'])
_draw_bar(19, 'index', data['prev']['index']['low_2'])
_draw_bar(20, 'index', data['prev']['index']['close_2'])
_draw_bar(21, 'index', data['prev']['index']['open'])
_draw_bar(22, 'index', data['prev']['index']['high'])
_draw_bar(23, 'index', data['prev']['index']['low'])
_draw_bar(24, 'index', data['prev']['index']['close'])
_draw_bar(25, 'index', data['prev']['index']['upline'])
_draw_bar(26, 'index', data['prev']['index']['downline'])
_draw_bar(27, 'index', data['prev']['index']['bar'])
_draw_bar(28, 'index', data['prev']['index']['vol60'])
_annotate_bar(13, data['prev']['stock']['open_3'])
_annotate_bar(14, data['prev']['stock']['high_3'])
_annotate_bar(15, data['prev']['stock']['low_3'])
_annotate_bar(16, data['prev']['stock']['close_3'])
_annotate_bar(17, data['prev']['stock']['open_2'])
_annotate_bar(18, data['prev']['stock']['high_2'])
_annotate_bar(19, data['prev']['stock']['low_2'])
_annotate_bar(20, data['prev']['stock']['close_2'])
_annotate_bar(21, data['prev']['stock']['open'])
_annotate_bar(22, data['prev']['stock']['high'])
_annotate_bar(23, data['prev']['stock']['low'])
_annotate_bar(24, data['prev']['stock']['close'])
_annotate_bar(25, data['prev']['stock']['upline'])
_annotate_bar(26, data['prev']['stock']['downline'])
_annotate_bar(27, data['prev']['stock']['bar'])
_annotate_bar(28, data['prev']['stock']['vol60'])
ax.plot([29, 29], [y_min, y_max], linewidth=1, color='black', alpha=0.5)

_draw_bar(30, 'stock', data['current']['stock']['open'])
_draw_bar(30, 'index', data['current']['index']['open'])
_annotate_bar(30, data['current']['stock']['open'])

ax.set_xticks(range(0, 31))
ax.set_xticklabels(labels, rotation=90,
                   rotation_mode="anchor", ha='right', va='center', fontsize=8)
ax.set_yticks(range(y_min, y_max + 1))
ax.set_yticklabels(range(-10, 11), fontsize=8)
ax.set_ylim(y_min, y_max)
ax.set_xlim(-0.5, 30.5)


ax.set_yticks(np.linspace(y_min, y_max, 11), minor=False)
ax.set_yticks(np.linspace(y_min, y_max, 21), minor=True)

ax.grid(True)
ax.grid(which='major', alpha=0.6)
ax.grid(which='minor', alpha=0.3)

y_pos = 9.8
ax.annotate('Prev 3',
            xy=(-0.5, y_pos), xycoords='data',
            color='black', weight='bold',
            ha='left', va='top', rotation=0,
            fontsize=7)
ax.annotate('Previous 2',
            xy=(3.1, y_pos), xycoords='data',
            color='black', weight='bold',
            ha='left', va='top', rotation=0,
            fontsize=7)
ax.annotate('Previous',
            xy=(12.1, y_pos), xycoords='data',
            color='black', weight='bold',
            ha='left', va='top', rotation=0,
            fontsize=7)
ax.annotate('Cur',
            xy=(29.1, y_pos), xycoords='data',
            color='black', weight='bold',
            ha='left', va='top', rotation=0,
            fontsize=7)


def _y_formatter(y, p):
    return "{:g}%".format(y)


ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(_y_formatter))

plt.show()
