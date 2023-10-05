import pandas as pd
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
import numpy as np

df = pd.read_excel('C:/Users/rs/Desktop/MA72均线/上证指数MA72均线.xls', engine='xlrd')
x = 1000
收盘价 = df['收盘价'].iloc[0:x]

# 示例用法
prices = 收盘价.values  # 替换为实际的价格数据

# 定义不同的y和z取值
y_values = list(range(1, 10))             #注意加1对于后面的值
z_values = list(range(50, 60))


# 存储不同情况下的sum_of_differences
sum_of_differences_list = []
y_values_list = []
z_values_list = []

def calculate_ma(prices, window):
    ma_values = []
    for i in range(len(prices) - window + 1):
        window_prices = prices[i:i + window]
        ma_value = sum(window_prices) / window
        ma_values.append(ma_value)
    return ma_values

def interpolate_data(dates, prices, num_points):
    # 将日期转换为数值表示，以便进行插值
    date_numbers = mdates.date2num(dates)
    f = interp1d(date_numbers, prices, kind='cubic')
    new_date_numbers = np.linspace(date_numbers[0], date_numbers[-1], num_points)
    new_dates = mdates.num2date(new_date_numbers)
    new_prices = f(new_date_numbers)
    return new_dates, new_prices

for y in y_values:
    for z in z_values:
        window_size = z
        window_size1 = y
        ma72_values = calculate_ma(prices, window_size)
        ma7_values1 = calculate_ma(prices, window_size1)
        ma7_values =  ma7_values1[z-y:]

        # 模拟交易日日期，可根据实际情况替换为真实的日期数据
        # 假设日期数据从"2023-07-01"开始，每日递增
        start_date_str = "2023-07-01"
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        dates = [start_date + timedelta(days=day-1) for day in range(1, len(prices) + 1)]

        # 去掉前72组收盘价数据
        prices_trimmed = prices[window_size - 1:]
        dates_trimmed = dates[window_size - 1:]
        prices_trimmed1 = prices[window_size1 - 1:]
        dates_trimmed1 = dates[window_size1 - 1:]

        # 插值处理，增加数据点
        num_points = len(dates_trimmed) * 20
        dates_interpolated, prices_interpolated = interpolate_data(dates_trimmed, prices_trimmed, num_points)
        ma72_interpolated = interpolate_data(dates_trimmed, ma72_values, num_points)[1]
        ma7_interpolated = interpolate_data(dates_trimmed, ma7_values, num_points)[1]

        # 寻找MA72和收盘价线的交点
        crossing_points = []
        crossing_dates = []
        crossing_prices = []

        for i in range(1, len(ma72_interpolated)):
            if (ma72_interpolated[i - 1] > ma7_interpolated[i - 1] and ma72_interpolated[i] < ma7_interpolated[i]) or \
                    (ma72_interpolated[i - 1] < ma7_interpolated[i - 1] and ma72_interpolated[i] > ma7_interpolated[i]):
                current_date = dates_interpolated[i]
                current_price = ma7_interpolated[i]
                crossing_points.append((current_date, current_price))
                crossing_dates.append(current_date)
                crossing_prices.append(current_price)

        for date, price in zip(crossing_dates, crossing_prices):
            nearest_date_idx = np.abs(np.array(dates_interpolated) - date).argmin()
            nearest_date = dates_interpolated[nearest_date_idx]


        crossing_points = []
        for i in range(1, len(ma72_interpolated)):
            if (ma72_interpolated[i - 1] > ma7_interpolated[i - 1] and ma72_interpolated[i] < ma7_interpolated[i]):
                # MA72从上方穿越收盘价线，做空信号
                current_date = dates_interpolated[i]
                current_price = prices_interpolated[i]
                crossing_points.append((current_date, current_price, "Long"))
            elif (ma72_interpolated[i - 1] < ma7_interpolated[i - 1] and ma72_interpolated[i] > ma7_interpolated[i]):
                # MA72从下方穿越收盘价线，做多信号
                current_date = dates_interpolated[i]
                current_price = prices_interpolated[i]
                crossing_points.append((current_date, current_price, "Short"))

        # 计算差值并输出
        sum_of_differences = 0  # 用于累积差值的变量
        for i in range(len(crossing_points) - 1):
            current_date, current_price, signal = crossing_points[i]
            next_date, next_price, _ = crossing_points[i+1]

            if signal == "Long":
                diff = next_price - current_price
            elif signal == "Short":
                diff = current_price - next_price
            else:
                diff = None  # 无效信号

            if diff is not None:
                sum_of_differences += diff  # 将差值累积到总和变量中

        sum_of_differences_list.append(sum_of_differences)
        y_values_list.append(y)
        z_values_list.append(z)

    # 输出所有情况下的sum_of_differences
    print("所有情况下的sum_of_differences:", sum_of_differences_list)

    # 找到最大sum_of_differences的索引
    max_index = np.argmax(sum_of_differences_list)

    # 输出最大sum_of_differences及对应的y和z值
    max_sum_of_differences = sum_of_differences_list[max_index]
    max_y_value = y_values_list[max_index]
    max_z_value = z_values_list[max_index]
    print("最大sum_of_differences:", max_sum_of_differences)
    print("对应的y值:", max_y_value)
    print("对应的z值:", max_z_value)