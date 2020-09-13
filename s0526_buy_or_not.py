# %%
from tensorflow import keras
import matplotlib.pyplot as plt
import numpy as np


def make_dataset(date_evaluate_list):
    history = []
    labels = []
    for item in date_evaluate_list:
        if item.profit is not None:
            if item.profit > 0:
                labels.append(1)
            else:
                labels.append(0)
            history.append(np.array(item.history[-7:])/item.history[-1])
    return np.array(history), np.array(labels)


def dataset_divider(data, label, portion=0.7):
    temp_train_data = []
    temp_train_label = []
    temp_test_data = []
    temp_test_label = []
    for ind in range(np.shape(data)[0]):
        if ind % 10 < portion * 10:
            temp_train_data.append(data[ind])
            temp_train_label.append(label[ind])
        else:
            temp_test_data.append(data[ind])
            temp_test_label.append(label[ind])
    return np.array(temp_train_data), np.array(temp_train_label), \
           np.array(temp_test_data), np.array(temp_test_label)

"""
# %%
model = keras.Sequential([
    keras.layers.Flatten(input_shape=(32, )),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(2, activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

#%%모델 훈련
model.fit(train_data, train_label, epochs=100)

#%%정확도 평가
test_loss, test_acc=model.evaluate(test_data, test_label,verbose=2)
print('\n테스트 정확도:',test_acc)

#%%훈련된 모델을 이용하여 이미지에 대한 예측하기
predictions=model.predict(test_data)
for i in range(len(test_label)):
    print(i, ': 모델 예측:',np.argmax(predictions[i]))
"""