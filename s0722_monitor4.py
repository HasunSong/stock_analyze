# https://lemontia.tistory.com/508
# %%
import time
import csv
import requests
from bs4 import BeautifulSoup
from s0722_send_email2 import send_mail
import math

# %%
# 종목코드 매치
code_dict = {}
directory = "./company_list.csv"

with open(directory, "r") as file:
    reader = csv.reader(file)
    for item in reader:
        code_dict[item[0]] = item[1]


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
NAVER_STOCK_URL1 = "https://m.stock.naver.com/item/main.nhn#/stocks/"
NAVER_STOCK_URL2 = "/total"
YAHOO_FINANCE_URL1 = "https://finance.yahoo.com/quote/"
YAHOO_FINANCE_URL2 = ".KS"
NAVER_URL = "https://finance.naver.com/item/frgn.nhn?code="


def get_stock_price(company_code):
    # url = NAVER_STOCK_URL1 + code_dict[company_name] + NAVER_STOCK_URL2
    # url = YAHOO_FINANCE_URL1 + code_dict[company_name] + YAHOO_FINANCE_URL2
    url = NAVER_URL + str(company_code)
    result = requests.get(url)
    soup = BeautifulSoup(result.content, 'html.parser', from_encoding='utf-8')
    # soup = BeautifulSoup(result.text, 'html.parser', from_encoding='utf-8')
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
    def __init__(self, name, code, price_crit=(0, math.inf)):
        self.name = name
        self.code = code
        self.price_crit = price_crit
        self.alert_date = None

    def __str__(self):
        return f"{self.name}({self.code}) Screen: {self.price_crit}"

    def get_stock_price(self):
        return get_stock_price(self.code)

    def get_total_price(self):
        return get_total_price(self.code)

    def screen(self):
        price = self.get_stock_price()
        if price < self.price_crit[0] or price > self.price_crit[1]:
            alert_date = time.localtime().tm_mday, time.localtime().tm_mon, time.localtime().tm_year
            if alert_date != self.alert_date:
                send_mail(self.name+"("+self.code+") "+str(price))
                print("<<ALERT!!>>", self.name+" "+self.code+" "+str(price))
                self.alert_date = alert_date


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
def update_screen(screen_dct):
    screen_lst = []
    directory = "./stock_list.csv"
    with open(directory, "r") as file:
        reader = csv.reader(file)
        for item in reader:
            if item[0] == "회사명" or item[0] == "":
                continue
            elif item[0] == "End":
                break
            else:
                if item[4] != "":
                    continue
                company_name = item[0]
                company_code = item[1].zfill(6)
                if item[2] == "":
                    lower = 0
                else:
                    lower = int(item[2])
                if item[3] == "":
                    upper = math.inf
                else:
                    upper = int(item[3])
                screen_lst.append(company_name)
                if company_name in screen_dct.keys():
                    if screen_dct[company_name].price_crit == (lower, upper):
                        continue
                    else:
                        screen_dct[company_name].price_crit = (lower, upper)
                        screen_dct[company_name].alert_date = None
                else:
                    screen_dct[company_name] = Company(company_name, company_code, (lower, upper))
    return screen_lst


# %%
# 장 닫히면 스크린 중지. 시작버튼 눌러야 다시 시작
company_dict = {}
screen_list = []
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



# %%
def per():
    PER = float(input("PER: "))
    PBR = float(input("PBR: "))
    ROE = PBR/PER
    print(f"PER: {PER}")
    print(f"PBR: {PBR}")
    print(f"ROE: {round(ROE*100, 2)}%")
    print(f"ROE/PER: {round(ROE/PER*100, 2)} (over 3 recommended)")
    print(f"ROE/PBR: {round(ROE / PBR * 100, 2)} (주당 회사가 버는 돈)")


# %%
def rim():
    B0 = float(input("B0: (억 원)")) * 100000000
    ROE = float(input("ROE: (%)")) / 100
    Ke = float(input("Ke: (%)")) / 100
    stock_num = float(input("Stock Num: (천 주)")) * 1000
    price = B0 * ROE / Ke / stock_num
    print(f"Price: {round(price, 2)}")
    # 이건 현재가/PBR*ROE/Ke랑 같다.


# %%
# 장 닫히든 말든 계속 돌림
last_screen_date = time.localtime().tm_mday
while True:
    if market_open():
        screen()
        if time.localtime().tm_mday != last_screen_date:
            print("Market Open. Start Monitor")
            send_mail("Market Open. Start Monitor")
            last_screen_date = time.localtime().tm_mday
        time.sleep(30 * 60)
    else:
        print("Market Closed\t", time_str())
        if 8 <= time.localtime().tm_hour <= 9:
            left_hr = 9-time.localtime().tm_hour
            left_min = 60-time.localtime().tm_min
            time.sleep(left_hr*3600+left_min*60+10)
        else:
            time.sleep(2 * 3600)


