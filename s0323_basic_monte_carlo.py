# %%
import numpy as np
import math
import random
from sympy import exp, sqrt, Integral, pi, Symbol
import matplotlib.pyplot as plt

# import pandas as pd

# %%
S0 = 100.0  # 초기 주가
N = 100
dt = 1 / N
u = 0.15
vol = 0.3
row = 100


# %%
def basic_monte_carlo(stock_number, day_number):
    stock_data = np.zeros(stock_number * day_number).reshape(stock_number, day_number)
    for stock in range(stock_number):
        stock_data[stock][0] = S0
        for day in range(1, day_number):
            stock_data[stock][day] = stock_data[stock][day - 1] * (
                    1 + u * dt + vol * math.sqrt(dt) * random.gauss(0.0, 1.0))
    return stock_data


# %%
def Z(a):
    x = Symbol('x')
    f = exp(-x ** 2 / 2) / sqrt(2 * pi)
    return Integral(f, (x, -100000, a)).doit().evalf()


def L(p, q):
    a_p = math.log(1 + p)
    a_q = math.log(1 + q)
    alpha1 = (q - u * dt) / (vol * np.sqrt(dt))
    alpha2 = (p - u * dt) / (vol * np.sqrt(dt))
    z1=Z(alpha1)
    z2=Z(alpha2)

    x=Symbol('x')
    f=x*exp(-x**2/2)/sqrt(2*pi)/(z2-z1)
    E_x=Integral(f,(x,q,p)).doit().evalf()

    l_p=math.exp(a_p*N*(1-z2))
    l_q=math.exp(a_q*N*z1)
    l_r=(z2-z1)*(1+z1-z2)*(1+N*(z2-z1)*E_x)
    return N*l_p*l_q*l_r

def L_ex(mat):
    row=np.shape(mat)[0]
    sum=0
    for i in range(row):
        sum+=mat[i][N-1]
    return sum/row

# %%
X_axis=list(np.arange(1,N+1))
matrix=basic_monte_carlo(row,N)
print(L_ex(matrix),'\n',L(0.99999,-0.5))
print(np.shape(X_axis),np.shape(matrix),np.shape(matrix[1][:]))

plt.figure()
for each_stock in range(row):
    plt.plot(matrix[each_stock])
plt.show()
