from bokeh.io import curdoc, output_file, show
from bokeh.models import Select, Column
import pandas as pd
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

    select_state= Select(title="State",  options=state, value = 'AL')
    select_county = Select(title = 'County', value = 'Autauga County', options = list(df['AL']))

    ranges = ['Never', 'Rarely', 'Sometimes', 'Frequently', 'Always']
    counts = result.loc[(result['state'] == 'AL') & (result['name'] == 'Autauga County')]
    counts = counts.drop(columns=['countyfp', 'name','state'])
    x = counts.values.tolist()

    p1 = figure(x_range=ranges, plot_height=250, title="Mask Usage in AL",
                toolbar_location=None, tools="")

    p1.vbar(x=ranges, top=counter, width=0.9)

    p1.xgrid.grid_line_color = None
    p1.y_range.start = 0

    p = figure(x_range=ranges, plot_height=250, title="Mask Usage in Autauga County, AL",
                toolbar_location=None, tools="")

    p.vbar(x=ranges, top=x[0], width=0.9)

    p.xgrid.grid_line_color = None
    p.y_range.start = 0

    #doc.theme = Theme(filename="theme.yaml")
    def update_layout(attr, old, new):
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
        p1.vbar(x=ranges, top=counter, width=0.9)
        p1.title.text = "Mask Usage in %s" %(state_selected)
        if(len(x) > 0):
            p.vbar(x=ranges, top=x[0], width=0.9)
            p.title.text = "Mask Usage in %s, %s" %(county_selected, state_selected)

    select_state.on_change('value', update_layout)
    select_county.on_change('value', update_layout)
    layout = Column(row(select_state, select_county), row(p1, p))
    doc.add_root(layout)

server = Server({'/': bkapp}, num_procs=1)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')

    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()