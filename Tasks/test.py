import matplotlib.pyplot as plt
import numpy as np

_data = {
    'prev3': {
        'bar': 5,
        'change': 6
    },
    'prev2': {
        'change': -5,
        'bar': 3,
        'open_change': 10,
        'upline': 4,
        'downline': 2,
        'amp_abs': 15,
    },
    'prev2_index': {
        'change': -5,
        'bar': 3,
        'open_change': 10,
        'upline': 4,
        'downline': 2,
        'amp_abs': 15,
    },
    'prev': {
        'change': -5,
        'bar': 3,
        'open_change': 10,
        'upline': 4,
        'downline': 2,
        'amp_abs': 15,
    },
    'prev_index': {
        'change': -5,
        'bar': 3,
        'open_change': 10,
        'upline': 4,
        'downline': 2,
        'amp_abs': 15,
    },
}

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

data = ((3, 100), (-10, -3), (100, 30), (500, 800), (50, 1))

dim = len(data[0])
w = 0.75
dimw = w / dim

x = np.arange(len(data))
for i in range(len(data[0])):
    y = [d[i] for d in data]
    b = ax.bar(x + i * dimw, y, dimw)

ax.set_xticks(x + dimw / 2, map(str, x))
ax.set_ylim(200, -200)
# ax.set_xticklabels(_data.keys())
plt.show()
