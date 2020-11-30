from bokeh.io import curdoc, output_file, show
from bokeh.models import Select, Column
import pandas as pd
from bokeh.client import push_session, pull_session
from bokeh.server.server import Server
import pandas as pd
from bokeh.plotting import figure

df1 = pd.read_csv('state_and_county_fips_master.csv')
df2 = pd.read_csv('mask-use-by-county.csv')

result = pd.merge(df1, df2, on='countyfp')
state = result['state'].drop_duplicates().to_list()
df = pd.DataFrame()
df['AL'] = result['name'].loc[result['state'] == 'AL']
#df['Italy'] = ['Rome','Milan', 'Rimini']
#df['Spain'] = ['Madrid', 'Barcelona', 'Bilbao']
#df['Country']   = ['France', 'Italy', 'Spain']


def bkapp(doc):

    select_state= Select(title="State",  options=state, value = 'AL')
    select_county = Select(title = 'Counties', value = 'Autauga County', options = list(df['AL']))

    #doc.theme = Theme(filename="theme.yaml")
    def update_layout(attr, old, new):
        state_selected = select_state.value
        df5 = pd.DataFrame()
        df5[state_selected] = result['name'].loc[result['state'] == state_selected]
        select_county.options = list(df5[state_selected])
        county_selected = select_county.value

        ranges = ['Never', 'Rarely', 'Sometimes', 'Frequently', 'Always']
        counts = result.loc[(result['state'] == state_selected) & (result['name'] == county_selected)]
        counts = counts.drop(columns=['countyfp', 'name','state'])
        x = counts.values.tolist()
        if(len(x) > 0):
            p = figure(x_range=ranges, plot_height=500, title="Mask Usage in %s, %s" %(county_selected, state_selected),
                toolbar_location=None, tools="")

            p.vbar(x=ranges, top=x[0], width=0.9)

            p.xgrid.grid_line_color = None
            p.y_range.start = 0

            show(p)

    select_state.on_change('value', update_layout)
    select_county.on_change('value', update_layout)
    layout = Column(select_state, select_county)
    doc.add_root(layout)

server = Server({'/': bkapp}, num_procs=1)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')

    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()