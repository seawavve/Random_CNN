# -*- coding: utf-8 -*-
"""0902_rand_cnn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1p6_O9ie0cDHaiKxQBn935uTVwj85cEz9
"""

'''
pilab seawavve
random cnn
2020.05.20~

Acc: 91.28%  Epoch:75


****PATCH NOTE****
0520 cnn network구성
0000 EarlyStopping&ModelCheckpoint
0000 이미지증강
0621 bypass
0902 random
     depth&add확률 조정 요망
     summary에 체크한 레이어 수보다 많이 나오는 오류 디버깅 요망


'''

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import sys
import random
import numpy as np
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import datasets


def make_rand(net_list):         #파생된 레이어들을 list에 담아 반환
  lis=list()
  re_seed=random.randint(1,4)  #파생레이어 1~4개 생성
  for i in range(re_seed):
    seed=random.randint(1,4)    #한 레이어에서 파생레이어 생성
    if seed==1:
     im_output= layers.Conv2D(filters=64, kernel_size=[3,3], padding='same', activation='relu')(output)
    elif seed==2:
      im_output= layers.Dropout(rate=0.25)(output)
    elif seed==3:
     im_output= layers.MaxPooling2D(pool_size=[3, 3], padding='same', strides=1)(output)
    elif seed==4:
     im_output = layers.Activation('relu')(output)
    lis.append(im_output)
  return lis

def make_short_cut(a_layer,b_layer):  # 받은 두개의 레이어로 shortcut을 만들어 반환
  im_output = layers.Add()([a_layer,b_layer])
  return im_output

print('Python version : ', sys.version)
print('Keras version : ', keras.__version__)

img_rows = 28
img_cols = 28

(x_train, y_train), (x_test, y_test) = keras.datasets.fashion_mnist.load_data()

input_shape = (img_rows, img_cols, 1)
x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)

x_train = x_train.astype('float32') / 255.
x_test = x_test.astype('float32') / 255.

print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

batch_size = 128
num_classes = 10
epochs = 300
filename = 'checkpoint.h5'.format(epochs, batch_size)

early_stopping=EarlyStopping(monitor='val_loss',mode='min',patience=15,verbose=1)                           #얼리스타핑
checkpoint=ModelCheckpoint(filename,monitor='val_loss',verbose=1,save_best_only=True,mode='auto')           #체크포인트


y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

inputs = keras.Input(shape=input_shape, name='input' )
output= layers.Conv2D(filters=64, kernel_size=[3,3], padding='same', activation='relu')(inputs)

net_list=list()
add_num=0

for depth in range(5):                           #깊이정하기
  a=make_rand(net_list)                         #랜덤레이어 생성
  net_list.extend(a)
  print('make_list로 만든 리스트의 길이:',len(a))
  if len(a)==1:r_num=0                         #a 중에서 하나 레이어 골라서 output에 붙이기
  else:r_num=random.randint(0,len(a)-1)   
  print('랜덤 index number:',r_num+1)                   
  output=a[r_num]                   
  short_cut_dec=random.randint(1,5)             #20%확률적으로 shortcut
  if short_cut_dec==1 or short_cut_dec==2:
    add_num=add_num+1
    a_layer_num=random.randint(0,len(net_list)-1)
    c=make_short_cut(net_list[a_layer_num],output)    
    output=c

print('\n',depth+1,'개 레이어추가',add_num,'개 shortcut추가')

output = layers.GlobalAveragePooling2D()(output)
output = layers.Dense(1000, activation='relu')(output)
dropout = layers.Dropout(rate=0.25)(output)
output = layers.Dense(10, activation='softmax')(dropout)

model = keras.Model(inputs=inputs, outputs=output)

model.summary()

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

history = model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, verbose=1, validation_data=(x_test, y_test),callbacks=[checkpoint,early_stopping])

score = model.evaluate(x_test, y_test, verbose=0)
print('Test loss:',  score[0])
print('Test accuracy:', score[1])
model.save('MNIST_CNN_model.h5')