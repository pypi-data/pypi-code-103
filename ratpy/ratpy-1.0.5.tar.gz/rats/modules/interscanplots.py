from rats.modules import rats_parser
from rats.modules.RATS_CONFIG import Packet
import pandas as pd
import plotly.express as px
pd.options.mode.chained_assignment = None

def interscanplot(df, timescale=1000000):
    title = 'title'
    df = df[[Packet.FUNCTION.field_name, Packet.TIME_STAMP.field_name, Packet.LLC_COUNT.field_name]].drop_duplicates()
    df = df.set_index([Packet.FUNCTION.field_name, Packet.LLC_COUNT.field_name]).diff()
    df = df.reset_index()
    df = df.iloc[1:]
    df.loc[:, 'timescale'] = timescale
    df.loc[:, Packet.TIME_STAMP.field_name] = df[Packet.TIME_STAMP.field_name]/df['timescale']
    df = df.sort_values(Packet.FUNCTION.field_name, ascending=False)

    fig = px.violin(df, x=Packet.TIME_STAMP.field_name, y=Packet.FUNCTION.field_name, color=Packet.FUNCTION.field_name,
                    orientation='h', title=title).update_traces(side='positive', width=2.5)
    fig.update_yaxes(type='category')
    fig.update_layout(plot_bgcolor='#fff')
    return fig


def test_case(absolutepath):
    parsing_class = rats_parser.RatsParser(absolutepath)
    parsing_class.parse()
    fig = interscanplot(parsing_class.dataframe)
    fig.write_html('test2.html')

# test_case('gds_000C00_30_14092021_1520.txt')
