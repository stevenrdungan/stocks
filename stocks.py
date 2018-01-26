import configparser
import requests
import pandas as pd
from bokeh.models import ColumnDataSource, Legend, LinearAxis, Range1d
from bokeh.plotting import curdoc, figure
from bokeh.driving import count
from bokeh.models.formatters import DatetimeTickFormatter
from datetime import datetime

'''
requires py.conf file like:
[AlphaVantage]
APIKEY='mykey'
'''
config = configparser.ConfigParser()
config.read('py.conf')
av = config['AlphaVantage']

def _get_intraday_data():
    # request parameters - see https://www.alphavantage.co/documentation
    function = 'TIME_SERIES_INTRADAY'
    symbol = 'COF'
    interval = '1min'
    outputsize = 'compact'
    datatype = 'csv'
    apikey = av['APIKEY']
    url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&outputsize={outputsize}&datatype={datatype}&apikey={apikey}'
    try:
        print('requesting...')
        # TODO: limit request time
        r = requests.get(url, timeout=10)
        print(f'response: {r.status_code}')
        with open('response.csv', 'w') as f:
            f.write(r.text)
        df = pd.read_csv('response.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except TimeoutError:
        print('could not complete request in time')
        df = pd.read_csv('response.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
# def _get_intraday_data():
#     df = pd.read_csv('response.csv')
#     df['timestamp'] = pd.to_datetime(df['timestamp'])
#     return df


source = ColumnDataSource(_get_intraday_data())
# source = ColumnDataSource(dict(timestamp=[],
#                                open=[],
#                                high=[],
#                                low=[],
#                                close=[],
#                                volume=[]))

p = figure(title='COF Stock',
           x_axis_label='timestamp',
           y_axis_label='USD',
           x_axis_type='datetime',
           plot_width=1000,
           plot_height=600)
p.y_range = Range1d(103, 105)
p.extra_y_ranges = {'volume': Range1d(start=0, end=50000)}
p.add_layout(LinearAxis(y_range_name='volume', axis_label='Trading Volume'), 'right')
p.toolbar.logo = None
p.toolbar_location = None
p.min_border_left = 50
p.min_border_bottom = 50
# p.xaxis.formatter=DatetimeTickFormatter(hours='%H:%M:%S',
#                                         minutes='%H:%M:%S',
#                                         seconds='%H:%M:%S')
p.xaxis.formatter=DatetimeTickFormatter(years='%Y-%m-%d %H:%M:%S',
                                        months='%Y-%m-%d %H:%M:%S',
                                        days='%Y-%m-%d %H:%M:%S',
                                        hours='%Y-%m-%d %H:%M:%S',
                                        minutes='%Y-%m-%d %H:%M:%S',
                                        seconds='%Y-%m-%d %H:%M:%S')

l1 = p.line(x='timestamp', y='open', color='red', line_width=2, source=source)
l2 = p.line(x='timestamp', y='high', color='blue', line_width=2, source=source)
l3 = p.line(x='timestamp', y='low', color='purple', line_width=2, source=source)
l4 = p.line(x='timestamp', y='close', color='green', line_width=2, source=source)
l5 = p.line(x='timestamp', y='volume', color='brown', line_width=1,
            y_range_name='volume', source=source)

legend = Legend(items=[
    ('open', [l1]),
    ('high', [l2]),
    ('low', [l3]),
    ('close', [l4]),
    ('volume', [l5])
    ], location=(5, -10))
p.add_layout(legend, 'right')


# @count()
# def update(t):
#     source = _get_intraday_data()
def update():
    print(f'updating {datetime.utcnow()}')
    source = _get_intraday_data()

# def update():
#     new_data = _get_intraday_data()
#     source.stream(dict(timestamp=new_data['timestamp'],
#                        open=new_data['open'],
#                        high=new_data['high'],
#                        low=new_data['low'],
#                        close=new_data['close'],
#                        volume=new_data['volume']))


curdoc().add_root(p)
curdoc().add_periodic_callback(update, 60000) # update data every minute
