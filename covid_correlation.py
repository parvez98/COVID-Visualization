import pandas as pd
import numpy as np
from datetime import date
from bokeh.sampledata.us_states import data as states
from bokeh.plotting import figure, curdoc, show
from bokeh.transform import factor_cmap, linear_cmap
from bokeh.palettes import Spectral11, Spectral3, Viridis256
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider, DateRangeSlider, ColorBar, FixedTicker, Legend, LegendItem, Title

col_list = ["date", "state", "death", "totalTestResults"]
df = pd.read_csv('all-states-history.csv', usecols=col_list, sep=",")
del_states = ["AK", "HI", "PR"]
state_coord = pd.read_csv('states.csv')
x = []
y = []
state_order = []
for i, j in state_coord.iterrows():
    if j['state'] not in del_states:
        x.append(j['longitude'])
        y.append(j['latitude'])
        state_order.append(j['state'])
del states["HI"]
del states["AK"]
state_xs = [states[code]["lons"] for code in states]
state_ys = [states[code]["lats"] for code in states]

casesByState = {}
testsByState = {}
for i in state_order:
    new_df = df.copy(deep=True)
    new_df.loc[:,'X_date'] = new_df['date']
    new_df = new_df[new_df['state'] == str(i)]
    new_df['date'] = pd.to_datetime(new_df['date'], format="%Y/%m/%d")
    new_df = new_df[new_df['date'].dt.month >= 3]
    new_df = new_df[new_df['date'].dt.month <= 10]
    new_df['X_date'] = pd.to_datetime(new_df['X_date'], format="%Y/%m/%d")
    new_df.set_index('date', inplace=True)
    resampled_df = new_df.resample('M').sum()
    positive = resampled_df['death'].to_list()
    tests = resampled_df['totalTestResults'].to_list()
    casesByState.update({i: positive})
    testsByState.update({i: tests})
    new_df.iloc[0:0]

size_list = []
actual_size = []
color_list = []
for i in casesByState:      # size
    size_list.append(float(casesByState[i][6])/9000)

for i in testsByState:      # color
    color_list.append(int(testsByState[i][6]))

p = figure(title="COVID-19 Number of Deaths vs Testing: September", plot_width=1200, plot_height=800)
p.patches(state_xs, state_ys, line_color="#000000", line_width=2, fill_color="#ffffff")
source = ColumnDataSource(dict(x=x, y=y, size_list=size_list, color_list=color_list))
mapper = linear_cmap(field_name='color_list', palette=Spectral11, low=min(color_list), high=max(color_list))
renderer = p.circle(source=source, x='x', y='y', size='size_list', fill_color=mapper)
color_bar = ColorBar(title='Testing', color_mapper=mapper['transform'], width=10)
relation = {3: 0, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7}
months = {3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October'}
event_legend1 = Legend(items=[LegendItem(label='R1', renderers=[renderer])],
                       location=(20, 120), label_height=3, label_standoff=10, title="Number of Cases")
event_legend2 = Legend(items=[LegendItem(label='R2', renderers=[renderer])],
                       location=(14, 95), label_standoff=5)
event_legend3 = Legend(items=[LegendItem(label='R3', renderers=[renderer])],
                       location=(8, 70), label_standoff=0)
event_legend4 = Legend(items=[LegendItem(label='R4', renderers=[renderer])],
                       location=(2, 40), label_standoff=-5)
event_legend_list = [event_legend1, event_legend2, event_legend3, event_legend4]
for legend in event_legend_list:
    p.add_layout(legend)
size_list = [15, 26, 37, 48]
index_list = [0, 1, 2, 3]
for index, size in zip(index_list, size_list):
    p.legend[index].glyph_height = size
    p.legend[index].glyph_width = size
    p.legend[index].padding = 0
    p.legend[index].margin = 0
    p.legend[index].border_line_alpha = 0
    p.legend[index].background_fill_alpha = 0


def update_plot(attr, old, new):
    month = int(slider.value)
    global color_list
    global mapper
    global p
    test = []
    test2 = []
    for k in casesByState:
        test.append(float(casesByState[k][relation[month]])/9000)     # normalized
    for l in testsByState:
        test2.append(testsByState[l][relation[month]])
    p.title.text = "COVID-19 Number of Deaths vs Testing: " + str(months[month])
    source.data['size_list'] = test
    source.data['color_list'] = test2
    color_list = test2
    mapper = test2


slider = Slider(title='Month:', start=3, end=10, step=1, value=9)
slider.on_change('value', update_plot)
layout = column(p, slider)
p.add_layout(color_bar, 'right')
show(layout)
curdoc().add_root(layout)
