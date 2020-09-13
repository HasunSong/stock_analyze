# %%
import time
import csv
import requests
from bs4 import BeautifulSoup
from s0722_send_email2 import send_mail
import math


# %%
def market_open():
    current_time = time.localtime()
    if 0 <= current_time.tm_wday <= 4:
        if 9 <= current_time.tm_hour <= 14:
            return True
        elif current_time.tm_hour == 15:
            if current_time.tm_min <= 30:
                return True
    return False


def time_str():
    return time.ctime(time.time())


# %%
NAVER_URL = "https://finance.naver.com/item/frgn.nhn?code="


def get_stock_price(company_code):
    url = NAVER_URL + str(company_code)
    result = requests.get(url)
    soup = BeautifulSoup(result.content, 'html.parser', from_encoding='utf-8')
    current_price = soup.find("p", {"class": "no_today"}).find("span",{"class": "blind"}).text
    return int(current_price.replace(",", ""))


def get_total_price(company_code):
    url = NAVER_URL + str(company_code)
    result = requests.get(url)
    soup = BeautifulSoup(result.content, 'html.parser', from_encoding='utf-8')
    total_price_str = soup.find("em", {"id": "_market_sum"}).get_text().replace("\n", "").replace("\t", "").replace(",", "")
    if "조" in total_price_str:
        sp = total_price_str.split("조")
        return int(sp[0])*10000 + int(sp[1])
    else:
        return int(total_price_str)


# %%
class Company:
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.price = 0

    def __str__(self):
        return f"{self.name}({self.code}) Current Price: {self.price}"

    def get_stock_price(self):
        return get_stock_price(self.code)

    def get_total_price(self):
        return get_total_price(self.code)

    def update_stock_price(self):
        self.price = self.get_stock_price()

    def screen(self, lower, upper):
        if self.price < lower or self.price > upper:
            send_mail(self.name+"("+self.code+") "+str(self.price))
            print("<<ALERT!!>>", self.name+" "+self.code+" "+str(self.price))


# %%
class Screener:
    def __init__(self, target_name, crit):
        self.target_name = target_name
        self.lower, self.upper = crit
        self.last_alert = None
        self.active = True

    def __str__(self):
        return f"{self.target_name}, Crit: ({self.lower}, {self.upper}), Active: {self.active}, Last Alert: {self.last_alert}"

    def screen(self, stock_dct):
        price = stock_dct[self.target_name].price
        code = stock_dct[self.target_name].code
        lower, upper = self.lower, self.upper
        if price < lower or price > upper:
            self.last_alert = time_str()
            send_mail(self.target_name + "(" + code + ") " + str(price))
            print("<<ALERT!!>>", self.target_name + " " + code + " " + str(price))


# %%
class Group:
    def __init__(self, stem):
        self.stem = stem
        self.name = stem.name
        self.leaves = {}

    def update_leaf(self, leaf, portion = 1):
        if leaf.name in self.leaves.keys():
            self.leaves[leaf.name][1] = portion
        else:
            self.leaves[leaf.name] = (leaf, portion)

    def eval_by_leaves(self):
        leaves_value = 0


# %%
def update_stock_list(stock_dct):
    directory = "./stock_list.csv"
    with open(directory, "r") as file:
        reader = csv.reader(file)
        for item in reader:
            if item[0] == "회사명" or item[0] == "":
                continue
            elif item[0] == "End":
                break
            else:
                company_name = item[0]
                company_code = item[1].zfill(6)

                if item[4] == "":
                    if company_name not in stock_dct.keys():
                        stock_dct[company_name] = Company(company_name, company_code)
                else:
                    if company_name in stock_dct.keys():
                        del stock_dct[company_name]


def update_stock_price(stock_dct):
    for company_name in stock_dct.keys():
        stock_dct[company_name].update_stock_price()


def update_screen_list(screen_dct):
    directory = "./stock_list.csv"
    with open(directory, "r") as file:
        reader = csv.reader(file)
        for item in reader:
            if item[0] == "회사명" or item[0] == "":
                continue
            elif item[0] == "End":
                break
            else:
                company_name = item[0]
                if item[2] == "":
                    lower = 0
                else:
                    lower = int(item[2])
                if item[3] == "":
                    upper = math.inf
                else:
                    upper = int(item[3])

                if company_name in screen_dct.keys():
                    if (screen_dct[company_name].lower, screen_dct[company_name].upper) != (lower, upper):
                        screen_dct[company_name].lower, screen_dct[company_name].upper = lower, upper
                        screen_dct[company_name].last_alert = None
                else:
                    screen_dct[company_name] = Screener(company_name, (lower, upper))

                if item[4] != "": # 스크린 중단
                    screen_dct[company_name].active = False
                else:
                    screen_dct[company_name].active = True


def screen_stocks(stock_dct, screen_dct):
    for key in screen_dct.keys():
        screener = screen_dct[key]
        if (not screener.active) or (screener.last_alert is not None):
            continue
        else:
            screener.screen(stock_dct)

# %%
stock_dict = {}
screen_dict = []

if market_open():
    print("Market Open. Start Monitor")
    send_mail("Market Open. Start Monitor")
while market_open():
    print(f"=================({time_str()})=================")
    update_stock_list(stock_dict)
    update_stock_price(stock_dict)
    update_screen_list(screen_dict)
    screen_stocks(stock_dict, screen_dict)
    time.sleep(3 * 60)
print("Market Closed\t", time_str())


# %%
"""
# %%
# 장 닫히면 스크린 중지. 시작버튼 눌러야 다시 시작
stock_dict = {}
screen_dict = []

while True:
    if market_open():
        print("Market Open. Start Monitor")
        send_mail("Market Open. Start Monitor")
    while market_open():
        print(f"=================({time_str()})=================")
        screen_list = update_screen(company_dict)
        for company_name in screen_list:
            company_dict[company_name].screen()
        time.sleep(3 * 60)
    print("Market Closed\t", time_str())
    keep_running = input("Run Monitor?(y/n): ")
    print()
    if keep_running == "y":
        print("Start Monitor...")
        continue
    else:
        print("Program Terminated")
        break
"""
