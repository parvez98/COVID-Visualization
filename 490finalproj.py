import pandas as pd
import math
import numpy as np
from datetime import date
from bokeh.sampledata.us_states import data as states
from bokeh.plotting import figure, curdoc, show
from bokeh.transform import factor_cmap, linear_cmap
from bokeh.server.server import Server
from bokeh.client import push_session, pull_session
from bokeh.palettes import Spectral11, Spectral3, Viridis256
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider, DateRangeSlider, ColorBar, FixedTicker, Legend, LegendItem, HoverTool
from bokeh.io import curdoc, output_file, show
from bokeh.models import Select, Column, Spacer
from bokeh.client import push_session, pull_session
from bokeh.server.server import Server
import pandas as pd
from bokeh.layouts import row
from bokeh.plotting import figure

df1 = pd.read_csv('state_and_county_fips_master.csv')
df2 = pd.read_csv('mask-use-by-county.csv')

result = pd.merge(df1, df2, on='countyfp')
state = result['state'].drop_duplicates().to_list()
df = pd.DataFrame()
df['AL'] = result['name'].loc[result['state'] == 'AL']
dfx = pd.DataFrame()
counter = [0,0,0,0,0]
for x in df['AL']:
    counts = result.loc[(result['state'] == 'AL') & (result['name'] == x)]
    never = counts.drop(columns=['countyfp', 'name','state', 'RARELY', 'SOMETIMES', 'FREQUENTLY', 'ALWAYS'])
    rarely = counts.drop(columns=['countyfp', 'name','state', 'NEVER', 'SOMETIMES', 'FREQUENTLY', 'ALWAYS'])
    sometimes = counts.drop(columns=['countyfp', 'name','state', 'NEVER', 'RARELY', 'FREQUENTLY', 'ALWAYS'])
    frequently = counts.drop(columns=['countyfp', 'name','state', 'NEVER', 'RARELY', 'SOMETIMES', 'ALWAYS'])
    always = counts.drop(columns=['countyfp', 'name','state', 'NEVER', 'RARELY', 'SOMETIMES', 'FREQUENTLY'])
    counter[0]+=never.values[0]/len(df['AL'])
    counter[1] +=rarely.values[0]/len(df['AL'])
    counter[2] += sometimes.values[0]/len(df['AL'])
    counter[3] += frequently.values[0]/len(df['AL'])
    counter[4] += always.values[0]/len(df['AL'])
def bkapp(doc):
    col_list = ["date", "state", "deathIncrease", "totalTestResultsIncrease"]
    og_df = pd.read_csv('all-states-history.csv', usecols=col_list, sep=",")

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
    test_df = og_df.copy(deep=True)
    for i, j in test_df.iterrows():
        if j['state'] == 'TX' and math.isnan(j['deathIncrease']) == False:
            summ = summ + j['deathIncrease']

    deathsByState = {}
    testsByState = {}
    for i in state_order:
        new_df = og_df.copy(deep=True)
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

    p = figure(title="COVID-19 Number of Deaths vs Testing: September",
            plot_width=1000, plot_height=650)
    p.patches(state_xs, state_ys, line_color="#000000",
            line_width=2, fill_color="#ffffff")
    source = ColumnDataSource(dict(
        x=x, y=y, size_list=size_list, color_list=color_list, actual_size=actual_size))
    mapper = linear_cmap(field_name='size_list', palette=Spectral11,
                        low=min(size_list), high=max(size_list))
    renderer = p.circle(source=source, x='x', y='y',
                        size='color_list', fill_color=mapper)
    hover_tool = HoverTool(tooltips=[
        ('tests', '@color_list')
    ], renderers=[renderer])
    p.add_tools(hover_tool)
    color_bar = ColorBar(
        title='Deaths', color_mapper=mapper['transform'], width=10)
    relation = {3: 0, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8}
    months = {3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July',
            8: 'August', 9: 'September', 10: 'October', 11: 'November'}
    event_legend2 = Legend(items=[LegendItem(label='10', renderers=[renderer])],
                        location=(21, 118), label_standoff=10, title="Tests per 250")
    event_legend3 = Legend(items=[LegendItem(label='30', renderers=[renderer])],
                        location=(5, 80), label_standoff=5)
    event_legend4 = Legend(items=[LegendItem(label='40', renderers=[renderer])],
                        location=(-2, 42), label_standoff=0)
    event_legend5 = Legend(items=[LegendItem(label='50', renderers=[renderer])],
                        location=(-14, -10), label_standoff=-5)
    event_legend_list = [event_legend2,
                        event_legend3, event_legend4, event_legend5]
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

    select_state= Select(title="State",  options=state, value = 'AL')
    select_county = Select(title = 'County', value = 'Autauga County', options = list(df['AL']))

    ranges = ['Never', 'Rarely', 'Sometimes', 'Frequently', 'Always']
    counts = result.loc[(result['state'] == 'AL') & (result['name'] == 'Autauga County')]
    counts = counts.drop(columns=['countyfp', 'name','state'])
    x = counts.values.tolist()

    p1 = figure(x_range=ranges, title="Mask Usage in AL",plot_height=250,
                toolbar_location=None, tools="")

    p1.vbar(x=ranges, top=counter, width=0.9)

    p1.xgrid.grid_line_color = None
    p1.y_range.start = 0

    p2 = figure(x_range=ranges, title="Mask Usage in __, AL", plot_height=250,
                toolbar_location=None, tools="")

    p2.vbar(x=ranges, top=[0,0,0,0,0], width=0.9)

    p2.xgrid.grid_line_color = None
    p2.y_range.start = 0
    
    def update_plot(attr, old, new):
        month = int(slider.value)
        test = []
        test2 = []
        for k in deathsByState:
            test.append(float(deathsByState[k][relation[month]]))
        for l in testsByState:
            test2.append(
                (float(testsByState[l][relation[month]])/final_population[l])*250)
        p.title.text = "COVID-19 Number of Deaths vs Testing: " + \
            str(months[month])
        source.data['size_list'] = test
        source.data['color_list'] = test2
        hover_tool = HoverTool(tooltips=[
            ('tests', '@color_list')
        ], renderers=[renderer])
        color_list = test
        mapper = test
    
    def update_layout(attr, old, new):
        counter = [0,0,0,0,0]
        state_selected = select_state.value
        df5 = pd.DataFrame()
        df5[state_selected] = result['name'].loc[result['state'] == state_selected]
        select_county.options = list(df5[state_selected])
        county_selected = select_county.value
        counts = result.loc[(result['state'] == state_selected) & (result['name'] == county_selected)]
        counts = counts.drop(columns=['countyfp', 'name','state'])
        x = counts.values.tolist()
        for county in df5[state_selected]:
            curr_state = result.loc[(result['state'] == state_selected) & (result['name'] == county)]
            never = curr_state.drop(columns=['countyfp', 'name','state', 'RARELY', 'SOMETIMES', 'FREQUENTLY', 'ALWAYS'])
            rarely = curr_state.drop(columns=['countyfp', 'name','state', 'NEVER', 'SOMETIMES', 'FREQUENTLY', 'ALWAYS'])
            sometimes = curr_state.drop(columns=['countyfp', 'name','state', 'NEVER', 'RARELY', 'FREQUENTLY', 'ALWAYS'])
            frequently = curr_state.drop(columns=['countyfp', 'name','state', 'NEVER', 'RARELY', 'SOMETIMES', 'ALWAYS'])
            always = curr_state.drop(columns=['countyfp', 'name','state', 'NEVER', 'RARELY', 'SOMETIMES', 'FREQUENTLY'])
            counter[0]+=never.values[0]/len(df5[state_selected])
            counter[1] +=rarely.values[0]/len(df5[state_selected])
            counter[2] += sometimes.values[0]/len(df5[state_selected])
            counter[3] += frequently.values[0]/len(df5[state_selected])
            counter[4] += always.values[0]/len(df5[state_selected])
        if(select_state.value == new):
            p4 = figure(x_range=ranges, title="Mask Usage in %s" %(state_selected), plot_height=250,
                        toolbar_location=None, tools="")
            p4.vbar(x=ranges, top=counter, width=0.9)
            p4.xgrid.grid_line_color = None
            p4.y_range.start = 0
            layout.children[1] = p4

            p3 = figure(x_range=ranges, title="Mask Usage in __, %s" %(state_selected), plot_height=250,
                toolbar_location=None, tools="")
            p3.vbar(x=ranges, top=[0,0,0,0,0], width=0.9)
            p3.xgrid.grid_line_color = None
            p3.y_range.start = 0
            layout.children[2] = p3
        if(select_county.value == new):
            x[0] = np.round(x[0], 2)
            p3 = figure(x_range=ranges, title="Mask Usage in %s, %s" %(county_selected, state_selected), plot_height=250,
                toolbar_location=None, tools="")
            p3.vbar(x=ranges, top=x[0], width=0.9)
            p3.xgrid.grid_line_color = None
            p3.y_range.start = 0
            layout.children[2] = p3

    slider = Slider(title='Month', start=3, end=11, step=1, value=9)
    slider.on_change('value', update_plot)
    select_state.on_change('value', update_layout)
    select_county.on_change('value', update_layout)
    layout = Column(row(select_state, Spacer(width = 300, height = 1, sizing_mode='fixed'), select_county), p1, p2, Spacer(width=10, height=40, sizing_mode='fixed'), column(p, slider))
    p.add_layout(color_bar, 'right')
    #show(layout)
    doc.add_root(layout)

server = Server({'/': bkapp}, num_procs=1)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')

    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
