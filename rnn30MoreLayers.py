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

FUTURE_PERIOD_PREDICT = 3  # how far into the future are we trying to predict?
EPOCHS = 10  # how many passes through our data
BATCH_SIZE = 64  # how many batches? Try smaller batch if you're getting OOM (out of memory) errors.
NAME = f"test1-{int(time.time())}"

def train_model(boss_ID, difficulty, steps):
    df = pd.read_csv(boss_ID + "_" + str(difficulty) + '_30.csv')   
    df = df.dropna()
    NAME = boss_ID + f"-{int(time.time())}"

    tag_df = df['0']
    #print(tag_df)
    #print(df.shape)
    df.drop(columns=df.columns[0], axis=1, inplace=True)
    df.drop(columns=df.columns[0], axis=1, inplace=True)
    #df.drop(columns=df.columns[0], axis=1, inplace=True)
    #df.drop('0', axis=1, inplace=True)
    #df.drop('duration', inplace=True)
    #df.drop('Unnamed', inplace=True)

    #print(df.shape)
    X = []

    for i in range(df.shape[0]):
        print(len(df.iloc[i]))
        dps = df.iloc[i][0:steps].values
        hps = df.iloc[i][steps:steps * 2].values
        dtps = df.iloc[i][steps * 2:].values


        temp_list = []
        temp_list.append(dps)
        temp_list.append(hps)
        temp_list.append(dtps)
        temp_list = np.array(temp_list).T
        #print(temp_list)
        X.append(temp_list)

    X = np.array(X)


    x_train, x_test, y_train, y_test = train_test_split(X, tag_df, test_size=0.2, random_state=42)

    print(x_test.shape)

    print(x_train.shape[1:])
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
    model.save("models/" + str(boss_ID) + "_" + str(difficulty) + ".model")
    #model.save("models/{}".format(NAME))

    y = model.predict(x_test)
    i = 0

    correct = 0
    wrong = 0
    for tag in y_test:
        if y[i][0] > y[i][1]:
            if tag == 0:
                correct = correct + 1

        else:
            if tag == 1:
                correct = correct + 1

        i = i + 1

    print( correct / i)


