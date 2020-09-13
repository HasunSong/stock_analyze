# %%
import matplotlib.pyplot as plt
from s0526_buy_or_not import make_dataset


class DateEvaluate:
    def __init__(self, buy_date, sell_date, days_passed, profit, percentage, avg_per, history):
        self.buy_date = buy_date
        self.sell_date = sell_date
        self.days_passed = days_passed
        self.profit = profit
        self.percentage = percentage
        self.avg_per = avg_per
        self.history = history

    def __str__(self):
        return f"buy: {self.buy_date}, sell: {self.sell_date}, {self.days_passed}days passed.\n" \
               f"profit: {self.profit}, percentage: {self.percentage}, avg_per: {self.avg_per}"


def get_history(data, current_index, term=7):
    return list(data.iloc[current_index-term+1:current_index+1]['Close'])


def cutter(data, buy_date_index, upper=0.05, lower=0.03):
    buy_date = str(data.iloc[buy_date_index].name)[:-9]
    buy_cost = int(data.iloc[buy_date_index]['Close'])
    upper_cost = buy_cost * (1 + upper)
    lower_cost = buy_cost * (1 - lower)
    sell_date_index = buy_date_index + 1
    while sell_date_index < len(data):
        new_cost = data.iloc[sell_date_index]['Close']
        if new_cost >= upper_cost or new_cost <= lower_cost:
            sell_date = str(data.iloc[sell_date_index].name)[:-9]
            profit = new_cost - buy_cost
            days_passed = sell_date_index - buy_date_index
            return DateEvaluate(buy_date, sell_date, days_passed, profit, profit/buy_cost, profit/buy_cost/days_passed, get_history(data, buy_date_index, term=32))
        sell_date_index += 1
    return DateEvaluate(buy_date, None, None, None, None, None, None)


def cutter_1everyday_evaluate_and_record(company, cutter_criteria):
    print(f"Evaluate And Recording Cutter{cutter_criteria} of {company.name}...")
    data = company.stock_data
    evaluate_list = []
    for buy_date_index in range(40, len(data)):
        temp = cutter(data, buy_date_index, cutter_criteria[0], cutter_criteria[1])
        evaluate_list.append(temp)
    company.cutter_evaluate[cutter_criteria] = {}
    company.cutter_evaluate[cutter_criteria]['evaluate_list'] = evaluate_list

    his, lab = make_dataset(evaluate_list)
    company.cutter_evaluate[cutter_criteria]['7d_history'] = his
    company.cutter_evaluate[cutter_criteria]['label'] = lab


def visualize_evaluated_result(company, cutter_criteria, y_lim=(0.7, 1.3)):
    print(f"Visualizing Cutter{cutter_criteria} of {company.name}...")
    plt.figure()
    eval_list = company.cutter_evaluate[cutter_criteria]['evaluate_list']
    prof_list_dn = []
    for item in eval_list:
        if item.sell_date is not None:
            prof_list_dn.append(item.percentage)

    earn, lost = 0, 0
    for item in prof_list_dn:
        if item > 0:
            earn += 1
        else:
            lost += 1

    plt.subplot(211)
    plt.plot(prof_list_dn)
    plt.title(f"Cutter{cutter_criteria} of {company.name}, Earn:{earn} Lost:{lost}")
    #plt.show()

    his, lab = company.cutter_evaluate[cutter_criteria]['7d_history'], company.cutter_evaluate[cutter_criteria]['label']

    # 휴리스틱한 직관을 위해
    plt.subplot(223)
    plt.ylim(y_lim[0], y_lim[1])
    for i in range(len(his)):
        if lab[i] == 1:
            plt.plot(his[i])
    plt.title(f"Cutter{cutter_criteria} of {company.name}, Earn")
    #plt.show()
    plt.subplot(224)
    plt.ylim(y_lim[0], y_lim[1])
    for i in range(len(his)):
        if lab[i] == 0:
            plt.plot(his[i])
    plt.title(f"Cutter{cutter_criteria} of {company.name}, Lost")

    plt.show()
