from rats.modules import rats_parser
from rats.modules.RATS_CONFIG import Packet
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None  # get rid of SettingWithCopyWarning. Default='warn'

# define a protocol here?

def llc_handler(df ,llc):
    df[llc] = np.where(df[llc] == 0, df[Packet.DATA.field_name].min() * 1.1, df[Packet.DATA.field_name].max() * 1.1)
    llc_df = df[[Packet.LLC_COUNT.field_name, Packet.TIME_STAMP.field_name,llc]]
    llc_first = llc_df.drop_duplicates(subset=[Packet.LLC_COUNT.field_name,llc],keep='first')
    llc_last = llc_df.drop_duplicates(subset=[Packet.LLC_COUNT.field_name,llc], keep='last')
    llc_df = pd.concat([llc_first,llc_last]).sort_index()
    
    return llc_df


def scopeplot(df, llc=0, buffer=1, facet=False, timescale=1000000, show_sip = False, llc_select='SIP'):

    if llc > df[Packet.LLC_COUNT.field_name].max():
        # shouldn't really happen but might if switching between very different rats files
        llc = 0
    start = llc - buffer
    end = llc + buffer
    title = df.board.unique()[0]
    df['time'] = [i + 100 for i in range(len(df['time']))] # TODO: remove when timestamps are included in packet
    df[Packet.LLC_COUNT.field_name] = df[Packet.LLC_COUNT.field_name].astype('int')
    df[Packet.FUNCTION.field_name] = df[Packet.FUNCTION.field_name].astype('int')
    df = df[(df[Packet.LLC_COUNT.field_name] >= start) & (df[Packet.LLC_COUNT.field_name] <= end)]  # subsequent operations will throw SettingWithCopyWarning - false positive warning in this case
    df.reset_index(drop=True, inplace=True)
    df[Packet.TIME_STAMP.field_name] = df[Packet.TIME_STAMP.field_name] / timescale
    
    sip_df = llc_handler(df,llc_select)

    # Need to make this configurable somehow.. need to set a list of available LLCs from the LLCEDBFormat config.
    sip_series = df.SIP.diff()
    df.SIP = np.where(df.SIP == 0, df[Packet.DATA.field_name].min()*1.1,df[Packet.DATA.field_name].max()*1.1)
    sip_transitions = sip_series[sip_series != 0].index.to_list()[1:]

    if len(sip_transitions)%2 > 0: # this is poor logic
        sip_transitions.append(df[Packet.TIME_STAMP.field_name].max())
    # sip_data = []
    # for i in sip_transitions:


    sip_transitions = [(sip_transitions[i], sip_transitions[i + 1]) for i in range(0, len(sip_transitions) - 1, 2)]


    sip = go.Scatter(x=sip_df[Packet.TIME_STAMP.field_name], y=sip_df.SIP, name='SIP')

    sip.update(legendgroup='trendline', showlegend=False, line=dict(dash='dash', color='orange'), opacity=0.8, mode='lines', marker=dict(opacity = 0),
                      hovertemplate='sip<br>time=%{x}<extra></extra>')

    if facet:
        fig = px.line(df, x=Packet.TIME_STAMP.field_name, y=Packet.DATA.field_name, color=Packet.ACTIVE_EDBS.field_name,
                      hover_data=[Packet.LLC_COUNT.field_name, Packet.FUNCTION.field_name,
                                  Packet.PACKET_COUNT.field_name],
                      facet_row=Packet.ACTIVE_EDBS.field_name,
                      title=title,
                      template='simple_white')
        fig.update_yaxes(matches=None)

    #TODO: Change x to time when the info in the rats packets is correct
    else:
        fig = px.line(df, x=Packet.TIME_STAMP.field_name, y=Packet.DATA.field_name, color=Packet.ACTIVE_EDBS.field_name,
                      hover_data=[Packet.LLC_COUNT.field_name, Packet.FUNCTION.field_name,
                                  Packet.PACKET_COUNT.field_name],
                      title=title,
                      template='simple_white')
        fig.update_yaxes(matches=None)

    for i in sip_transitions:
        fig.add_vrect(
            x0=df.loc[i[0]:i[1], 'time'].min(),
            x1=df.loc[i[0]:i[1], 'time'].max()-1,
            fillcolor="LightSeaGreen", opacity=0.1,
            layer="below", line_width=0,
        )

    if show_sip:
        fig.add_trace(sip, row='all', col='all', exclude_empty_subplots=True)

    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)



    # make sure markers are there in case user wants a single MRM scan, which would just be a single datapoint per edb
    fig.update_traces(mode='markers+lines', marker=dict(size=4), selector=-1, showlegend=True)
    return fig

def test_case(absolutepath):
    parser_class = rats_parser.RatsParser(absolutepath)
    parser_class.parse()
    if parser_class.valid:
        df = parser_class.dataframe
        fig = scopeplot(df,llc=1,timescale=1, buffer=1, facet=False, show_sip=True)
        fig.write_html('test1.html')

    else:
        fig = px.scatter(x=[1,2,3],y=[4,5,6],title=f'Data for file {parser_class.filename} Invalid')
        fig.write_html('test1.html')

# filename = 'C:\\Users\\uksayr\\AppData\\Roaming\\JetBrains\\PyCharm2021.2\\scratches\\gds_000C00_2E_22112021_0958.txt'
# filename = 'C:\\Users\\uksayr\\AppData\\Roaming\\JetBrains\\PyCharm2021.2\\scratches\\gds_000C00_30_14092021_1520.txt'
# test_case(filename)
