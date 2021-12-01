from rats.modules import rats_parser
from rats.modules.RATS_CONFIG import Packet
import numpy as np
import pandas as pd
import plotly.express as px
pd.options.mode.chained_assignment = None

def decimate_bp_plot(df):
    # Something might be going wrong with decimate...
    if 'ERRORS' in df['state'].values:
        return df
    else:
        first = df.drop_duplicates(subset='function_number', keep='first')
        last = df.drop_duplicates(subset='function_number', keep='last')

        return pd.concat([first,last])

def assign_erroneous_edbs(df):
    # Hand me a df from a single LLC
    errors = ' '.join(df[df['state'] == 'ERRORS'][Packet.ACTIVE_EDBS.field_name].astype(str).to_list())
    df['EDBs in error'] = errors
    return(df)


# function to run on initial upload
def bigpictureplot(df, decimate=True, timescale=1000000):
    title = df.board.unique()[0]
    df = df[[Packet.FUNCTION.field_name, Packet.PACKET_COUNT.field_name, Packet.LLC_COUNT.field_name,
             Packet.ACTIVE_EDBS.field_name, 'anomalous', Packet.TIME_STAMP.field_name]]

    df.drop_duplicates(subset=[Packet.LLC_COUNT.field_name, Packet.ACTIVE_EDBS.field_name, 'anomalous'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['state'] = np.where(df['anomalous'] == 0, 'GOOD', 'ERRORS')
    # df['time'] = df['time'] / df['timescale']

    if decimate:
        # problem is grouping by state here.
        # need here to pull the erroneous EDBs  before decimation....
        df = df.groupby('state').apply(decimate_bp_plot)
        df[Packet.FUNCTION.field_name] = df[Packet.FUNCTION.field_name].astype('category')
        errors = df[df['state'] == 'ERRORS']

        df = df.groupby(Packet.LLC_COUNT.field_name).apply(assign_erroneous_edbs)

        fig = px.scatter(df, x=Packet.LLC_COUNT.field_name, y=Packet.FUNCTION.field_name, color='state',
                         hover_data=[Packet.LLC_COUNT.field_name, 'EDBs in error'],
                         title=title, render_mode='webgl', template='simple_white')

        fig.update_traces(mode='lines+markers')

        # must find a way here to include the EDB number responsible for the error state...
        if len(errors) > 0:
            fig.data[0].mode = 'markers'
            fig.data[1].mode = 'lines'
            fig.data[0].marker.color = 'red'
            fig.data[1].marker.color = 'blue'
            fig.data[1].marker.opacity = 0.5


    else:
        df['EDBs in error'] = np.where(df['state'] == 'ERRORS', df[Packet.ACTIVE_EDBS.field_name], 'NA')
        df = df.groupby(Packet.LLC_COUNT.field_name).apply(assign_erroneous_edbs)
        fig = px.scatter(df, x=Packet.LLC_COUNT.field_name, y=Packet.FUNCTION.field_name, color='state',
                         hover_data=[Packet.LLC_COUNT.field_name, 'EDBs in error'],
                         title=title, render_mode='webgl', template='simple_white')
        errors = df[df['state'] == 'ERRORS']


        if len(errors) > 0:
            fig.data[0].mode = 'markers'
            fig.data[0].marker.color = 'red'
            fig.data[1].marker.color = 'blue'

    fig.update_layout(showlegend=True)
    fig.update_traces(marker=dict(size=12))
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)

    return fig

def test_case(absolutepath):
    parser_class = rats_parser.RatsParser(absolutepath)
    parser_class.parse()

    fig = bigpictureplot(parser_class.dataframe,decimate=True)
    fig.write_html('test1.html')
# filename = 'C:\\Users\\uksayr\\AppData\\Roaming\\JetBrains\\PyCharm2021.2\\scratches\\gds_000C00_30_14092021_1520.txt'
# test_case(filename)


class BigPictureView:

    required_columns: [] = ['EDBs in error', 'state','']
    valid: bool

    def __init__(self,df: pd.DataFrame):

        self.dataframe = df.copy()
        # use copy of dataframe for now... maybe only pass the relevant, stripped dataframe to this function
        # only need a few columns...

    def decimate_data(self):

        def decimate(frame):
            if 'ERRORS' in self.df['state'].values:
                return frame
            else:
                first = frame.drop_duplicates(subset='function_number', keep='first')
                last = frame.drop_duplicates(subset='function_number', keep='last')

                return pd.concat([first, last])

        self.dataframe = self.dataframe.groupby('state').apply(decimate)
