#!/usr/bin/env python3

import os, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from Visualizers.CandleChart import plot_kchart
from DataProviders.DailyData import *
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, Dropout, Convolution2D, BatchNormalization, Merge, LSTM, GRU
from keras.callbacks import ReduceLROnPlateau, ModelCheckpoint
from keras.optimizers import SGD, RMSprop
from keras.callbacks import EarlyStopping

secId = 'sh600003'
start_date = '2005-01-01'
end_date = '2008-12-30'

data = fetch_daily_data(secId, start_date, end_date)
data = extract_daily_features(data)
data = transform_daily_features(data)
results = generate_resultset(data)
data, results = trim_dataset(data, results, 60)

train_x, test_x = train_test_split(data, train_size=0.9)
train_y, test_y = train_test_split(results, train_size=0.9)

input_dim = train_x.shape[1]

model = Sequential([
    Dense(200, input_dim=input_dim),
    Activation('tanh'),
    # BatchNormalization(),
    # Dropout(0.2),
    # Dense(200),
    # Activation('tanh'),
    # BatchNormalization(),
    Dropout(0.2),
    Dense(100),
    Activation('tanh'),
    # BatchNormalization(),
    Dropout(0.2),
    Dense(100),
    Activation('tanh'),
    # BatchNormalization(),
    # Dropout(0.2),
    Dense(2),
    Activation('softmax')
])

model.compile(optimizer='adadelta',
              loss='categorical_crossentropy',
              metrics=['categorical_accuracy'])

model.fit(train_x, train_y,
          nb_epoch=1000,
          batch_size=32,
          validation_data=(test_x, test_y),
          shuffle=True,
          verbose=2)
