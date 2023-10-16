import pandas as pd
from collections import deque
import random
import numpy as np
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, CuDNNLSTM, BatchNormalization
from keras.callbacks import TensorBoard
from keras.callbacks import ModelCheckpoint, ModelCheckpoint
import time
from sklearn import preprocessing

from sklearn.model_selection import train_test_split

SEQ_LEN = 241  # how long of a preceeding sequence to collect for RNN
FUTURE_PERIOD_PREDICT = 3  # how far into the future are we trying to predict?
EPOCHS = 10  # how many passes through our data
BATCH_SIZE = 64  # how many batches? Try smaller batch if you're getting OOM (out of memory) errors.
NAME = f"test1-{int(time.time())}"



df = pd.read_csv('754_4.csv')
df = df.dropna()



tag_df = df['tag']


df.drop(columns=df.columns[0], axis=1, inplace=True)
df.drop(columns=df.columns[0], axis=1, inplace=True)
df.drop(columns=df.columns[0], axis=1, inplace=True)
#df.drop('0', axis=1, inplace=True)
#df.drop('duration', inplace=True)
#df.drop('Unnamed', inplace=True)


X = []

for i in range(df.shape[0]):
    dps = df.iloc[i][0:241].values
    hps = df.iloc[i][241:482].values
    dtps = df.iloc[i][482:].values

    temp_list = []
    temp_list.append(dps)
    temp_list.append(hps)
    temp_list.append(dtps)
    temp_list = np.array(temp_list).T
    #print(temp_list)
    X.append(temp_list)

X = np.array(X)


x_train, x_test, y_train, y_test = train_test_split(X, tag_df, test_size=0.2, random_state=42)


print(x_train.shape)
print(y_train.shape)
print(x_test.shape)
print(y_test.shape)

model = Sequential()
model.add(LSTM(128, input_shape=(x_train.shape[1:]), return_sequences=True))
model.add(Dropout(0.2))
model.add(BatchNormalization())

model.add(LSTM(128, return_sequences=True))
model.add(Dropout(0.1))
model.add(BatchNormalization())

model.add(LSTM(128))
model.add(Dropout(0.2))
model.add(BatchNormalization())

model.add(Dense(32, activation='relu'))
model.add(Dropout(0.2))

model.add(Dense(2, activation='softmax'))

opt = tf.keras.optimizers.Adam(lr=0.001, decay=1e-6)

# Compile model
model.compile(
    loss='sparse_categorical_crossentropy',
    optimizer=opt,
    metrics=['accuracy']
)

tensorboard = TensorBoard(log_dir="logs/{}".format(NAME))

filepath = "RNN_Final-{epoch:02d}-{val_accuracy:.3f}"
checkpoint = ModelCheckpoint("models/{}.model".format(filepath, monitor='val_accuracy', verbose=1, save_best_only=True, mode='max')) # saves only the best ones


train_x = np.asarray(x_train)
train_y = np.asarray(y_train)
validation_x = np.asarray(x_test)
validation_y = np.asarray(y_test)

# Train model
history = model.fit(
    train_x, train_y,
    batch_size=BATCH_SIZE,
    epochs=EPOCHS,
    validation_data=(validation_x, validation_y),
    callbacks=[tensorboard, checkpoint],
)

# Score model
score = model.evaluate(validation_x, validation_y, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])
# Save model
model.save("models/{}".format(NAME))


