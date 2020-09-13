# https://kind.krx.co.kr/corpgeneral/corpList.do?method=loadInitPage
# %%
import csv
directory = "./company_list.csv"

with open(directory, "r") as file:
    reader = csv.reader(file)
    for txt in reader:
        print(txt)