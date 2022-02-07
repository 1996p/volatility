
# Описание предметной области:
#
# При торгах на бирже совершаются сделки - один купил, второй продал.
# Покупают и продают ценные бумаги (акции, облигации, фьючерсы, етс). Ценные бумаги - это по сути долговые расписки.
# Ценные бумаги выпускаются партиями, от десятка до несколько миллионов штук.
# Каждая такая партия (выпуск) имеет свой торговый код на бирже - тикер - https://goo.gl/MJQ5Lq
# Все бумаги из этой партии (выпуска) одинаковы в цене, поэтому говорят о цене одной бумаги.
# У разных выпусков бумаг - разные цены, которые могут отличаться в сотни и тысячи раз.
# Каждая биржевая сделка характеризуется:
#   тикер ценнной бумаги
#   время сделки
#   цена сделки
#   обьем сделки (сколько ценных бумаг было куплено)
#
# В ходе торгов цены сделок могут со временем расти и понижаться. Величина изменения цен называтея волатильностью.
# Например, если бумага №1 торговалась с ценами 11, 11, 12, 11, 12, 11, 11, 11 - то она мало волатильна.
# А если у бумаги №2 цены сделок были: 20, 15, 23, 56, 100, 50, 3, 10 - то такая бумага имеет большую волатильность.
# Волатильность можно считать разными способами, мы будем считать сильно упрощенным способом -
# отклонение в процентах от средней цены за торговую сессию:
#   средняя цена = (максимальная цена + минимальная цена) / 2
#   волатильность = ((максимальная цена - минимальная цена) / средняя цена) * 100%
# Например для бумаги №1:
#   average_price = (12 + 11) / 2 = 11.5
#   volatility = ((12 - 11) / average_price) * 100 = 8.7%
# Для бумаги №2:
#   average_price = (100 + 3) / 2 = 51.5
#   volatility = ((100 - 3) / average_price) * 100 = 188.34%
#
#
# Задача: вычислить 3 тикера с максимальной и 3 тикера с минимальной волатильностью.
# Бумаги с нулевой волатильностью вывести отдельно.
# Результаты вывести на консоль в виде:
#   Максимальная волатильность:
#       ТИКЕР1 - ХХХ.ХХ %
#       ТИКЕР2 - ХХХ.ХХ %
#       ТИКЕР3 - ХХХ.ХХ %
#   Минимальная волатильность:
#       ТИКЕР4 - ХХХ.ХХ %
#       ТИКЕР5 - ХХХ.ХХ %
#       ТИКЕР6 - ХХХ.ХХ %
#   Нулевая волатильность:
#       ТИКЕР7, ТИКЕР8, ТИКЕР9, ТИКЕР10, ТИКЕР11, ТИКЕР12
# Волатильности указывать в порядке убывания. Тикеры с нулевой волатильностью упорядочить по имени.
# В каждом файле в папке trades содержится данные по сделакам по одному тикеру, разделенные запятыми.
#   Первая строка - название колонок:
#       SECID - тикер
#       TRADETIME - время сделки
#       PRICE - цена сделки
#       QUANTITY - количество бумаг в этой сделке
#   Все последующие строки в файле - данные о сделках
# TODO написать код в однопоточном/однопроцессорном стиле

import os
import threading

class Ticker(threading.Thread):

    def __init__(self, ticker_file: str, all_ticker_volatility: list, zero_volatility_tickers:list, lock: threading.Lock, *args, **kwargs):
        super(Ticker, self).__init__(*args, **kwargs)
        self.file = open("trades/" + ticker_file, 'r').readlines()
        self.SECID = self.file[1].split(',')[0]
        self.max_price = self.min_price = float(self.file[1].split(',')[2])
        self.volatility = 0
        self.all_ticker_volatility = all_ticker_volatility
        self.zero_volatility_tickers = zero_volatility_tickers
        self.lock = lock

    #   средняя цена = (максимальная цена + минимальная цена) / 2
    #   волатильность = ((максимальная цена - минимальная цена) / средняя цена) * 100%

    def get_volatility(self) -> float:
        average_price = (self.max_price + self.min_price) / 2
        volatility = ((self.max_price - self.min_price) / average_price) * 100
        return round(volatility, 3)

    def run(self) -> None:
        for i in range(1, len(self.file)):
            ticket_data = self.file[i].split(',')

            if float(ticket_data[2]) > self.max_price:
                self.max_price = float(ticket_data[2])

            elif float(ticket_data[2]) < self.min_price:
                self.min_price = float(ticket_data[2])

        self.volatility = self.get_volatility()
        if self.volatility == 0:
            self.zero_volatility_tickers.append(self.SECID)
        else:
            with self.lock:
                self.all_ticker_volatility.append(self.volatility)


files_paths = os.listdir(os.curdir + '/trades')
all_ticker_volatility = []
zero_volatility_tickers = []
lock = threading.Lock()


tickers = [Ticker(ticker_file=file_path, all_ticker_volatility=all_ticker_volatility, zero_volatility_tickers=zero_volatility_tickers, lock=lock) for file_path in files_paths]

for ticker in tickers:
    ticker.start()

for ticker in tickers:
    ticker.join()

all_ticker_volatility = sorted(all_ticker_volatility)
zero_volatility_tickers = sorted(zero_volatility_tickers)

print(f'top 3 maximal volatility: \n 1) {all_ticker_volatility[-1]}, \n 2) {all_ticker_volatility[-2]}, \n 3) {all_ticker_volatility[-3]} \n')
print(f'top 3 minimal volatility: \n 1) {all_ticker_volatility[0]}, \n 2) {all_ticker_volatility[1]}, \n 3) {all_ticker_volatility[2]} \n')


print(f'Zero volatility tickers:')
for ticker in zero_volatility_tickers:
    print(ticker, end=', ')



























