import pandas
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#------------------------------------- for CVR line
def cvr_line(df):
  df = df.replace({'Year' : {22:2022,21:2021,20:2020,19:2019,18:2018,17:2017}})
  df["YM"] = pandas.to_datetime(df['Year'].astype(str)+ df['Month'].astype(str), format='%Y%m')

  pivot_for_channel=df.pivot_table(aggfunc='sum', values = ['Debug_Estimated_Purcheses','Debug_Estimated_Visits'], index = ['YM'])
  pivot_for_channel1=pivot_for_channel.reset_index()

  # Create figure with secondary y-axis
  fig = make_subplots(specs=[[{"secondary_y": True}]])

  # Add traces
  fig.add_trace(
      go.Scatter(x=pivot_for_channel1['YM'], y=pivot_for_channel1['Debug_Estimated_Visits'], name="Estimated Visits"),
      secondary_y=False,
  )

  fig.add_trace(
      go.Scatter(x=pivot_for_channel1['YM'], y=pivot_for_channel1['Debug_Estimated_Purcheses'], name="Estimated Purcheses"),
      secondary_y=True,
  )

  # Set x-axis title
  fig.update_xaxes(title_text="Channel Conversion Results")

  # Set y-axes titles
  fig.update_yaxes(title_text="<b>Estimated</b> Visits", secondary_y=False)
  fig.update_yaxes(title_text="<b>Estimated</b> Purcheses", secondary_y=True)

  return fig.show()



#--------- for oss bar
def oss_bar(df):
  #to transform inserted df
  df = df.replace({'Year' : {22:2022,21:2021,20:2020,19:2019,18:2018,17:2017}})
  df["YM"] = pandas.to_datetime(df['Year'].astype(str)+ df['Month'].astype(str), format='%Y%m')
  pivot_table=df.pivot_table(aggfunc='count', values = 'Search_Term', index=['YM'])
  pivot_table1=pivot_table.reset_index()
  
  #find index of min element in results
  min_element=int(pivot_table1[['Search_Term']].idxmin())
  
  colors = ['lightslategray'] * 40
  colors[min_element] = 'crimson'
  
  fig = go.Figure(data=[go.Bar(
    x=pivot_table1['YM'],
    y=pivot_table1['Search_Term'],
    marker_color=colors, # marker color can be a single color value or an iterable
    text=pivot_table1['Search_Term'],
    textposition='auto')])
  return fig.update_layout(title_text='OSS')



def oss_line(df):
  #to transform inserted df
  df = df.replace({'Year' : {22:2022,21:2021,20:2020,19:2019,18:2018,17:2017}})
  df["YM"] = pandas.to_datetime(df['Year'].astype(str)+ df['Month'].astype(str), format='%Y%m')
  pivot_table=df.pivot_table(aggfunc='count', values = 'Search_Term', index=['YM'])
  pivot_table1=pivot_table.reset_index()
  
  #to get a min value to highlight it on a graph
  min_element=int(pivot_table1[['Search_Term']].idxmin())
  date_min=pivot_table1["YM"][min_element] #for x axis
  value_min=pivot_table1["Search_Term"][min_element] #for y axis


  fig = go.Figure()

  fig.add_trace(go.Scatter(
    x=pivot_table1['YM'],
    y=pivot_table1['Search_Term'],
    name='OSS line',
    connectgaps=True # override default to connect the gaps
  ))
  fig.add_trace(go.Scatter(x=[date_min],y=[value_min],name='Min value',marker=dict(color='red',size=12,line=dict(color='MediumPurple',width=4)))) #add a dot to hightlight a min value

  return fig.show()