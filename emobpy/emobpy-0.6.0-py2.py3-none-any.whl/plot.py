"""
This module contains a class that can be used to visualise the data. There are different visualisation functions.
"""

import pandas as pd
import os

try:
    import plotly.graph_objects as go
    from plotly.offline import iplot
    from plotly.subplots import make_subplots
    from IPython.display import display, HTML
    import cufflinks as cf
    cf.go_offline()
except ImportError:
    raise Exception("This plotly code only works within a jupyter notebook")

from .functions import balance
from .constants import CWD
from .tools import display_all
from .logger import get_logger

logger = get_logger(__name__)

class NBplot:
    
    """
    Work in Jupyter notebooks only.
    Set of plots for a single time series and groups.
    Three kind of plots:

    - self.sgplot_dp(tscode) for driving profiles
    - self.sgplot_ga(tscode) for grid availability profiles
    - self.sgplot_ged(tscode) for grid electricity demand profiles
    - tscode: time series code (string of profile name)

    self.__init__(db)
        db is an instance of a DataBase class that contains the time series.

    """

    def __init__(self, db):
        self.db = db
        try:
            display_all()
        except:
            pass

    def sgplot_dp(self, tscode, rng=None, to_html=False, path=None):
        """
        Plot of a single driving profile.

        Args:
            tscode (str): Time series code. Eg. 'ev_user_W3_85e59_avai_65t2p'
            rng (tuple): (a,b) index if only part of timeseries should be copied. Defaults to None.
            to_html (bool): Save as a html file. Defaults to False.
            path (str): Path if plot should be saved to file. Defaults to None.

        Returns:
            plotly.plot: Plot object.
        """
        self.db.update()
        if rng is None:
            df = self.db.db[tscode]["timeseries"].copy()
        else:
            df = self.db.db[tscode]["timeseries"].iloc[rng[0]: rng[1]].copy()
        if self.db.db[tscode]["kind"] != "driving":
            raise Exception(
                "code '{}' does not correspond to a driving profile".format(tscode)
            )

        cnt = df.groupby([df.index, "state"])["state"].count()
        cn = (
            pd.DataFrame(cnt)
                .rename(columns={"state": "count"})
                .unstack(level=-1)
                .fillna(0)
        )
        cn.columns = cn.columns.droplevel()
        rr = (cn.T / cn.T.sum(axis=0)).T
        figa = rr.iplot(kind="area", fill=True, asFigure=True)
        figb = df["distance"].iplot(asFigure=True)
        fig = cf.subplots([figa, figb], shape=(2, 1), shared_xaxes=True)
        fig["layout"]["yaxis"].update(
            {"title": "Location", "rangemode": "tozero", "domain": [0.7, 1.0], 'tickformat':".1%"}
        )
        fig["layout"]["yaxis2"].update(
            {"title": "Distance (km)", "rangemode": "tozero", "domain": [0.0, 0.65]}
        )

        fig = go.Figure(data=fig["data"], layout=fig["layout"])
        if to_html:
            if path is None:
                raise Exception(
                    """when to_html is True then path must be given with .html extension"""
                )
            else:
                fig.write_html(file=path)
        return fig

    def sgplot_ga(self, tscode, rng=None, to_html=False, path=None):
        """
        Plot of a single grid availability profile.

        Args:
            tscode (str): Time series code. Eg. 'ev_user_W3_85e59_avai_65t2p'
            rng (tuple): (a,b) index if only part of timeseries should be copied. Defaults to None.
            to_html (bool): Save as a html file. Defaults to False.
            path (str): Path if plot should be saved to file. Defaults to None.

        Returns:
            plotly.plot: Plot object.
        """
        self.db.update()
        if rng is None:
            df = self.db.db[tscode]["timeseries"].copy()
        else:
            df = self.db.db[tscode]["timeseries"].iloc[rng[0]: rng[1]].copy()
        if self.db.db[tscode]["kind"] != "availability":
            raise Exception(
                "code '{}' does not correspond to a grid availability profile".format(
                    tscode
                )
            )

        dt = df[["state", "consumption", "charging_point", "charging_cap", "soc"]]
        cnt = dt.groupby([dt.index, "state"])["state"].count()
        cn = (
            pd.DataFrame(cnt)
                .rename(columns={"state": "count"})
                .unstack(level=-1)
                .fillna(0)
        )
        cn.columns = cn.columns.droplevel()
        rr = (cn.T / cn.T.sum(axis=0)).T
        figa = rr.iplot(kind="area", fill=True, asFigure=True)
        dk = dt[["consumption", "charging_cap"]]
        figb = dk.iplot(asFigure=True)
        dd = dt["soc"]
        figc = dd.iplot(asFigure=True)
        fig = cf.subplots([figa, figb, figc], shape=(3, 1), shared_xaxes=True)
        fig["layout"]["xaxis"].update(
            {"tickfont": {"family": "Arial, sans-serif", "size": 13, "color": "black"}}
        )
        fig["layout"]["yaxis"].update(
            {
                "title": "Location",
                "titlefont": {"size": 12},
                "showgrid": False,
                "showline": True,
                "rangemode": "tozero",
                "zeroline": True,
                "domain": [0.75, 1.0],
                "tickformat":".1%",
                "tickfont": {
                    "family": "Arial, sans-serif",
                    "size": 12,
                    "color": "black",
                },
                "linewidth": 2,
            }
        )
        fig["layout"]["yaxis2"].update(
            {
                "title": "Grid Availability (kW)",
                "titlefont": {"size": 12},
                "showgrid": True,
                "showline": True,
                "rangemode": "tozero",
                "domain": [0.4, 0.7],
                "tickfont": {
                    "family": "Arial, sans-serif",
                    "size": 12,
                    "color": "black",
                },
                "linewidth": 2,
            }
        )
        fig["layout"]["yaxis3"].update(
            {
                "title": "SOC",
                "titlefont": {"size": 12},
                "showgrid": True,
                "showline": True,
                "rangemode": "tozero",
                "domain": [0.0, 0.35],
                "tickformat": ".1%",
                "tickfont": {
                    "family": "Arial, sans-serif",
                    "size": 12,
                    "color": "black",
                },
                "linewidth": 2,
            }
        )
        fig["layout"].update(
            {
                "paper_bgcolor": "white",
                "plot_bgcolor": "white",
                "margin": dict(l=10, r=10, t=20, b=10, pad=0),
            }
        )  # ,'width': 800,'height': 450,'showlegend': True

        fig = go.Figure(data=fig["data"], layout=fig["layout"])
        if to_html:
            if path is None:
                raise Exception(
                    """when to_html is True then path must be given with .html extension"""
                )
            else:
                fig.write_html(file=path)
        return fig

    def sgplot_ged(self, tscode, rng=None, to_html=False, path=None):
        """
        Plot of grid electricity demand profiles associated with the same grid availability profile.

        Args:
            tscode (str): Time series code. Eg. 'ev_user_W3_85e59_avai_65t2p'
            rng (tuple): (a,b) index if only part of timeseries should be copied. Defaults to None.
            to_html (bool): Save as a html file. Defaults to False.
            path (str): Path if plot should be saved to file. Defaults to None.

        Returns:
            plotly.plot: Plot object.
        """
        self.db.update()
        if self.db.db[tscode]["kind"] != "charging":
            raise Exception(
                "code '{}' does not correspond to a grid electricity demand profile".format(
                    tscode
                )
            )
        df = pd.DataFrame()
        availcode = self.db.db[tscode]["input"]
        for k in self.db.db.keys():
            if self.db.db[k]["kind"] == "charging":
                if self.db.db[k]["input"] == availcode:
                    tmp = self.db.db[k]["timeseries"].copy()
                    tmp.loc[:, "option"] = self.db.db[k]["option"]
                    df = df.append(tmp, sort=False)

        if rng is None:
            pass
        else:
            df = df.iloc[rng[0] : rng[1]].copy()

        dt = df[["state", "actual_soc", "charge_grid", "option"]]
        dt = dt.astype(dtype={'actual_soc':float, 'charge_grid':float})
        cnt = dt.groupby([dt.index, "state"])["state"].count()
        cn = (
            pd.DataFrame(cnt)
            .rename(columns={"state": "count"})
            .unstack(level=-1)
            .fillna(0)
        )
        cn.columns = cn.columns.droplevel()
        rr = (cn.T / cn.T.sum(axis=0)).T
        figc = rr.iplot(kind="area", fill=True, asFigure=True)
        dff = dt.pivot_table(
            index=dt.index, columns="option", values="actual_soc", aggfunc="sum"
        )
        figa = dff.iplot(asFigure=True)
        dg = dt.pivot_table(
            index=dt.index, columns="option", values="charge_grid", aggfunc="sum"
        )
        figb = dg.iplot(asFigure=True)
        fig = cf.subplots([figa, figb, figc], shape=(3, 1), shared_xaxes=True)
        fig["layout"]["xaxis"].update(
            {"tickfont": {"family": "Arial, sans-serif", "size": 14, "color": "black"}}
        )
        fig["layout"]["yaxis"].update(
            {
                "title": "SOC",
                "titlefont": {"size": 14},
                "showgrid": False,
                "showline": True,
                "rangemode": "tozero",
                "zeroline": True,
                "domain": [0.7, 1.0],
                "tickformat": ".1%",
                "tickfont": {
                    "family": "Arial, sans-serif",
                    "size": 14,
                    "color": "black",
                },
                "linewidth": 2,
            }
        )
        fig["layout"]["yaxis2"].update(
            {
                "title": "Actual charge (kW)",
                "titlefont": {"size": 14},
                "showgrid": True,
                "showline": True,
                "rangemode": "tozero",
                "domain": [0.25, 0.65],
                "tickfont": {
                    "family": "Arial, sans-serif",
                    "size": 12,
                    "color": "black",
                },
                "linewidth": 2,
            }
        )
        fig["layout"]["yaxis3"].update(
            {
                "title": "Location",
                "titlefont": {"size": 14},
                "showgrid": True,
                "showline": True,
                "rangemode": "tozero",
                "domain": [0.0, 0.2],
                "tickformat": ".1%",
                "tickfont": {
                    "family": "Arial, sans-serif",
                    "size": 12,
                    "color": "black",
                },
                "linewidth": 2,
            }
        )
        fig["layout"].update(
            {
                "paper_bgcolor": "white",
                "plot_bgcolor": "white",
                "margin": dict(l=10, r=10, t=20, b=10, pad=0),
                "showlegend": True,
            }
        )  # 'width': 800,'height': 450

        FIG = go.Figure(data=fig["data"], layout=fig["layout"])
        if to_html:
            if path is None:
                raise Exception(
                    """when to_html is True then path must be given with .html extension"""
                )
            else:
                FIG.write_html(file=path)
        return FIG


    def sankey(self, tscode, include=None, to_html=False, path=None):
        """
        Plot of sankey diagram which shows the energy consumption flows.

        Args:
            tscode (str): Time series code. Eg. 'ev_user_W3_85e59_avai_65t2p'
            include (int): Index which part to include. Defaults to None.
            to_html (bool): Save as a html file. Defaults to False.
            path (str): Path if plot should be saved to file. Defaults to None.

        Returns:
            plotly.plot: Plot object.
        """
        self.db.update()
        distance, consumption, rate, label, source, target, value = balance(
            self.db, tscode, include=include
        )

        link = dict(source=source, target=target, value=value)
        node = dict(label=label, pad=50, thickness=10)
        data = go.Sankey(link=link, node=node)
        fig = go.Figure(data)
        if to_html:
            if path is None:
                raise Exception(
                    """when to_html is True then path must be given with .html extension"""
                )
            else:
                fig.write_html(file=path)
        logger.info(f"Consumption [kWh]: {round(consumption,3)}")
        logger.info(f"Distance [km]: {round(distance,3)}")
        logger.info(f"Specific consumption [kWh/100 km]: {round(rate,3)}")
        return fig

    def overview(self, tscode, date_range=None, to_html=False, path=None, share_x=True):
        """
        Plot overview of all time series of a vehicle. Give one charging name profile and it collects upstream related profile names.
        
        args:
        
            tscode(string): Time series code. Eg. 'ev_user_W3_85e59_avai_65t2p'
            date_range(list): List of two datetime objects. Defaults to None. E.g. [datetime.datetime(2019, 1, 1, 0, 0), datetime.datetime(2019, 1, 31, 23, 59)]
            to_html(bool): Save as a html file. Defaults to False.
            path(string): Path if plot should be saved to file. Defaults to None.
            share_x(bool): Share x axis. Defaults to True.
            
        returns:
            plotly.plot: Plot object.

        """
        self.db.update()
        gavailability_name = self.db.db[tscode]['input']
        # logger.info(gavailability_name)
        consumption_name = self.db.db[gavailability_name]['input']

        ts = self.db.db[gavailability_name]['timeseries'].reset_index(drop=False).rename(
            columns={'date': 'datetime', 'hh': 'hr'})

        logger.info(f"Actual time-series date range = [{ts.datetime.min()},{ts.datetime.max()}]")
        if date_range is None:
            start = ts.datetime.min()
            end = ts.datetime.max()
        else:
            start = date_range[0]
            end = date_range[1]

        cons = self.db.db[consumption_name]

        from .consumption import include_weather, Weather
        wt = Weather()
        D = wt.humidair_density
        temp_arr = wt.temp(cons['weather_country'], cons['weather_year'])
        pres_arr = wt.pressure(cons['weather_country'], cons['weather_year'])
        dp_arr = wt.dewpoint(cons['weather_country'], cons['weather_year'])
        hum_arr = wt.calc_rel_humidity(dp_arr, temp_arr)
        r_ha = wt.humidair_density(temp_arr, pres_arr, h=hum_arr)
        dfs = include_weather(ts, cons['refdate'], temp_arr, pres_arr, dp_arr, hum_arr, r_ha)

        cdf = self.db.db[consumption_name]['profile'].copy()
        dfg = pd.merge_asof(dfs, cdf[['datetime', 'speed km/h']], on="datetime", tolerance=pd.Timedelta("900s"),
                            direction="nearest").fillna(0.0).set_index('datetime')  
        df = pd.DataFrame()
        availcode = self.db.db[tscode]["input"]
        for k in self.db.db.keys():
            if self.db.db[k]["kind"] == "charging":
                if self.db.db[k]["input"] == availcode:
                    tmp = self.db.db[k]["timeseries"].copy()
                    tmp.loc[:, "option"] = self.db.db[k]["option"]
                    df = df.append(tmp, sort=False)

        dt = df[["state", "actual_soc", "charge_grid", "option"]]
        dt = dt.astype(dtype={'actual_soc':float, 'charge_grid':float})
        dff = dt.pivot_table(index=dt.index, columns="option", values="actual_soc", aggfunc="sum")
        dg = dt.pivot_table(index=dt.index, columns="option", values="charge_grid", aggfunc="sum")

        dg.loc[:, 'Grid Availability'] = dfg["charging_cap"]
        cnt = dfg.groupby([dfg.index, "state"])["state"].count()
        cn = (
            pd.DataFrame(cnt)
                .rename(columns={"state": "count"})
                .unstack(level=-1)
                .fillna(0)
        )
        cn.columns = cn.columns.droplevel()
        rr = (cn.T / cn.T.sum(axis=0)).T

        # imput is the name of grid demand time series (charging class) and database 'db'
        # rr, dfg, dff, dg are dataframes resulting from a preprocessing step

        fig1 = rr[start:end].iplot(kind="area", fill=True, asFigure=True)
        fig2 = dfg[start:end][["distance", "consumption"]].iplot(colors=['green', 'pink'], asFigure=True)
        fig3 = dfg[start:end][["temp_degC", "speed km/h"]].iplot(colors=['purple', '#9c8830'], asFigure=True)
        fig4 = dg[start:end].iplot(yTitle='Power rating (kW)', asFigure=True)
        fig5 = dff[start:end].iplot(yTitle='SOC', asFigure=True)

        for trace in fig5['data']:
            trace['showlegend'] = True

        fig = make_subplots(rows=5, cols=1,shared_xaxes= True if share_x else False,
                            specs=[[{"secondary_y": True}], [{'secondary_y': True}], [{'secondary_y': True}],
                                [{'secondary_y': True}], [{'secondary_y': True}]])

        [fig.add_trace(trace, secondary_y=False, row=1, col=1) for trace in fig1['data']]
        fig.add_trace(fig2['data'][0], secondary_y=False, row=2, col=1)
        fig.add_trace(fig2['data'][1], secondary_y=True, row=2, col=1)
        fig.add_trace(fig3['data'][0], secondary_y=False, row=3, col=1)
        fig.add_trace(fig3['data'][1], secondary_y=True, row=3, col=1)
        [fig.add_trace(trace, secondary_y=False, row=4, col=1) for trace in fig4['data']]
        [fig.add_trace(trace, secondary_y=False, row=5, col=1) for trace in fig5['data']]

        renames = {'distance': ('Distance', 2.2),
                    'consumption': ('Consumption', 1.2),
                    'temp_degC': ('Temperature', 2),
                    'speed km/h': ('Average speed', 2),
                #    'from_23_to_8_at_any': ('Charge at night', 2),
                #    'immediate': ('Charge immediate', 1.5),
                #    'home': ('Home', 0.6), 'driving': ('Driving', 0.6), 'workplace': ('Workplace', 0.6),
                #    'errands': ('Errands', 0.6), 'leisure': ('Leisure', 0.6), 'shopping': ('Shopping', 0.6),
                    }

        for trace in fig['data']:
            if trace['name'] in renames:
                name = trace['name']
                trace['name'] = renames[name][0]
                trace['line']['width'] = renames[name][1]
            else:
                trace['line']['width'] = 0.6

        fig["layout"].update({'yaxis': dict(title="Location", 
                                            title_font=dict(color='black',
                                                            # size=18,
                                                            ), 
                                            showgrid=False,
                                            zeroline=True, linecolor='black', gridcolor='#bdbdbd', tickformat=".1%",
                                            # tickfont={"size": 12},
                                            ),
                                'yaxis3': dict(title='Distance (km)', 
                                            title_font=dict(color='green',
                                                            # size=18,
                                                            ),
                                            showgrid=True, zeroline=True, linecolor='black', gridcolor='#bdbdbd',
                                            #  tickfont={"size": 12},
                                            ),
                                'yaxis4': dict(title='Consumption (kWh)', 
                                            title_font=dict(color='pink'
                                                            # size=18, 
                                                            ),
                                            showgrid=False, zeroline=True, linecolor='black', gridcolor='#bdbdbd',
                                            #  tickfont={"size": 12},
                                            ),
                                'yaxis5': dict(title='Temp (C)', 
                                            title_font=dict(color='purple',
                                                            #  size=18,
                                                            ),
                                            showgrid=True, zeroline=True, linecolor='black', gridcolor='#bdbdbd',
                                            zerolinecolor='black', 
                                            #  tickfont={"size": 12},
                                            ),
                                'yaxis6': dict(title='Speed (km/h)', title_font=dict(color='#9c8830'
                                                                                #   size=18, 
                                                                                    ),
                                            showgrid=False, zeroline=True, linecolor='black', gridcolor='#bdbdbd',
                                            #  tickfont={"size": 12},
                                            ),
                                'yaxis7': dict(title='Power rating (kW)', title_font=dict(color='black',
                                                                                    #   size=18, 
                                                                                        ),
                                            showgrid=True, zeroline=True, linecolor='black', gridcolor='#bdbdbd',
                                            #  tickfont={"size": 12},
                                            ),
                                'yaxis9': dict(title='SOC', title_font=dict(color='black',
                                                                        #   size=18,
                                                                        ), 
                                            showgrid=True, zeroline=True, linecolor='black', gridcolor='#bdbdbd', tickformat=".1%",
                                            #  tickfont={"size": 12},
                                            ),
                                            })

        fig.update_xaxes(showgrid=True, zeroline=True, linecolor='black', gridcolor='#bdbdbd')
        fig.update_yaxes(rangemode='tozero')

        fig["layout"].update(
            {
                "paper_bgcolor": "white",
                "plot_bgcolor": "white",
                "margin": dict(l=10, r=10, t=20, b=10, pad=0),
                # 'width': 1300,
                'height': 1000, 
                'showlegend': True
            }
        )

        if to_html:
            if path is None:
                raise Exception("""when to_html is True then path must be given with .html extension""")
            else:
                fig.write_html(file=path)

        return fig

