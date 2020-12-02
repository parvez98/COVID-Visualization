import pandas as pd
import math
import numpy as np
from datetime import date
from bokeh.sampledata.us_states import data as states
from bokeh.plotting import figure, curdoc, show
from bokeh.transform import factor_cmap, linear_cmap
from bokeh.palettes import Spectral11, Spectral3, Viridis256
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider, DateRangeSlider, ColorBar, FixedTicker, Legend, LegendItem, HoverTool

col_list = ["date", "state", "deathIncrease", "totalTestResultsIncrease"]
df = pd.read_csv('all-states-history.csv', usecols=col_list, sep=",")
del_states = ["AK", "HI", "PR"]
state_coord = pd.read_csv('states.csv')
population_df = pd.read_csv('State Populations.csv')
population = {}
for i, j in population_df.iterrows():
    population.update({j['State']: int(j['2018 Population'])})
x = []
y = []
state_order = []
final_population = {}
for i, j in state_coord.iterrows():
    if j['state'] not in del_states:
        x.append(j['longitude'])
        y.append(j['latitude'])
        state_order.append(j['state'])
        final_population.update({j['state']: population[j['name']]})
del states["HI"]
del states["AK"]
state_xs = [states[code]["lons"] for code in states]
state_ys = [states[code]["lats"] for code in states]

summ = 0
test_df = df.copy(deep=True)
for i, j in test_df.iterrows():
    if j['state'] == 'TX' and math.isnan(j['deathIncrease']) == False:
        summ = summ + j['deathIncrease']

deathsByState = {}
testsByState = {}
for i in state_order:
    new_df = df.copy(deep=True)
    new_df.loc[:, 'X_date'] = new_df['date']
    new_df = new_df[new_df['state'] == str(i)]
    new_df['date'] = pd.to_datetime(new_df['date'], format="%Y/%m/%d")
    new_df = new_df[new_df['date'].dt.month >= 3]
    new_df = new_df[new_df['date'].dt.month <= 11]
    new_df['X_date'] = pd.to_datetime(new_df['X_date'], format="%Y/%m/%d")
    new_df.set_index('date', inplace=True)
    resampled_df = new_df.resample('M').sum()
    death = resampled_df['deathIncrease'].to_list()
    tests = resampled_df['totalTestResultsIncrease'].to_list()
    deathsByState.update({i: death})
    testsByState.update({i: tests})

size_list = []
actual_size = []
color_list = []
for i in deathsByState:      # color
    size_list.append(float(deathsByState[i][6]))
    actual_size.append(deathsByState[i][6])

for i in testsByState:      # size
    color_list.append((float(testsByState[i][6])/final_population[i])*250)

p = figure(title="COVID-19 Number of Deaths vs Testing: September", plot_width=1200, plot_height=800)
p.patches(state_xs, state_ys, line_color="#000000", line_width=2, fill_color="#ffffff")
source = ColumnDataSource(dict(x=x, y=y, size_list=size_list, color_list=color_list, actual_size=actual_size))
mapper = linear_cmap(field_name='size_list', palette=Spectral11, low=min(size_list), high=max(size_list))
renderer = p.circle(source=source, x='x', y='y', size='color_list', fill_color=mapper)
hover_tool = HoverTool(tooltips=[
    ('tests', '@color_list')
], renderers=[renderer])
p.add_tools(hover_tool)
color_bar = ColorBar(title='Deaths', color_mapper=mapper['transform'], width=10)
relation = {3: 0, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8}
months = {3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November'}
event_legend2 = Legend(items=[LegendItem(label='1500', renderers=[renderer])],
                       location=(21, 118), label_standoff=10, title="Tests per 250")
event_legend3 = Legend(items=[LegendItem(label='3000', renderers=[renderer])],
                       location=(5, 80), label_standoff=5)
event_legend4 = Legend(items=[LegendItem(label='8000', renderers=[renderer])],
                       location=(-2, 42), label_standoff=0)
event_legend5 = Legend(items=[LegendItem(label='150000', renderers=[renderer])],
                       location=(-14, -10), label_standoff=-5)
# event_legend6 = Legend(items=[LegendItem(label="fff", renderers=[renderer])],
#                       location=(-20, -15), label_standoff=-10)
event_legend_list = [event_legend2, event_legend3, event_legend4, event_legend5]
for legend in event_legend_list:
    p.add_layout(legend)
size_list = [26, 59, 75, 100]
index_list = [0, 1, 2, 3, 4]
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
    global actual_size
    test = []
    test2 = []
    for k in deathsByState:
        test.append(float(deathsByState[k][relation[month]]))
    for l in testsByState:
        test2.append((float(testsByState[l][relation[month]])/final_population[l])*250)
    p.title.text = "COVID-19 Number of Deaths vs Testing: " + str(months[month])
    source.data['size_list'] = test
    source.data['color_list'] = test2
    hover_tool = HoverTool(tooltips=[
        ('tests', '@color_list')
    ], renderers=[renderer])
    color_list = test
    mapper = test


slider = Slider(title='Month:', start=3, end=11, step=1, value=9)
slider.on_change('value', update_plot)
layout = column(p, slider)
p.add_layout(color_bar, 'right')
show(layout)
curdoc().add_root(layout)
