# %%
from s0415 import get_code_df, get_code
from s0526_5_3 import cutter_1everyday_evaluate_and_record, visualize_evaluated_result
from s0526_buy_or_not import make_dataset, dataset_divider
from tensorflow import keras
import matplotlib.pyplot as plt
import numpy as np
import pandas_datareader as pdr


class Company:
    def __init__(self, name):
        self.name = name
        self.stock_data = None
        self.cutter_evaluate = {}


company_dict = {}
code_df = get_code_df()


# %%
company_name = "삼성전자"
temp_company = Company(name=company_name)
company_dict[company_name] = temp_company
temp_company.stock_data = pdr.get_data_yahoo(get_code(code_df, company_name)).iloc[:-1]


# %%
plt.plot((company_dict[company_name]).stock_data['Close'])
plt.title(temp_company.name)
plt.show()


# %%
criteria_list = (0.05, 0.10)
# criteria_list = (0.01, 0.03, 0.05, 0.07, 0.10)
for i in criteria_list:
    for j in criteria_list:
        # cutter_1everyday_evaluate_and_record(temp_company, (i, j))
        visualize_evaluated_result(temp_company, (i, j), y_lim=(1/1.2, 1.2))


# %%
his, lab = make_dataset(temp_company.cutter_evaluate[(0.05, 0.05)]['evaluate_list'])

# %%
train_data, train_label, test_data, test_label = dataset_divider(his, lab, portion=0.7)

# %%
model = keras.Sequential([
    keras.layers.Flatten(input_shape=(7,)),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(2, activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# %%모델 훈련
model.fit(train_data, train_label, epochs=100)

# %%정확도 평가
test_loss, test_acc = model.evaluate(test_data, test_label, verbose=2)
print('\n테스트 정확도:', test_acc)

# %%훈련된 모델을 이용하여 이미지에 대한 예측하기
predictions = model.predict(test_data)
for i in range(len(test_label)):
    print(i, ': 모델 예측:', np.argmax(predictions[i]), "실제:", test_label[i])


# %%
earn_portion = sum(test_label)/len(test_label)
lost_portion = 1 - earn_portion

# %%
temp_pred = []
for data in test_data:
    if data[0] < 1:
        temp_pred.append(0)
    else:
        temp_pred.append(1)

earn_correct, lost_correct = 0, 0

for i in range(len(test_data)):
    if temp_pred[i] == 0:
        if test_label[i] == 0:
            lost_correct += 1
    else:
        if test_label[i] == 1:
            earn_correct += 1

print(f"Earn: {earn_portion}, Lost: {lost_portion}")
print(f"Earn Correct: {earn_correct/sum(temp_pred)}  ({earn_correct}/{sum(temp_pred)})")
print(f"Lost Correct: {lost_correct/(len(temp_pred)-sum(temp_pred))}  ({lost_correct}/{(len(temp_pred)-sum(temp_pred))})")


