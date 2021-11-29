import datetime
from client import BloombergClient
import pandas as pd
import os
import calendar

NON_SALES_COLS = ['Ticker','quarter_end','date', 'eps_estimate',
       'eps_reported', 'gaap_eps', 'quarter', 'reported_revenue',
       'revenue_estimate', 'symbol', "total_dollars", "eps","profit","revenue", "ann_date", "SALES_REV_TURN","GROSS_PROFIT","ARD_GROSS_PROFITS","IS_EPS", "IS_COMP_EPS_ADJUSTED", "IS_BASIC_EPS_CONT_OPS", "ARD_ADJUSTED_EPS","IS_ADJUSTED_EPS_AS_REPORTED", "BEST_SALES","BEST_EPS"]

def get_quarter_end(date, calendar_type):

    fiscal_months = [calendar_type + x for x in [0, 3, 6, 9]]
    for month in fiscal_months:
        if date.month <= month:
            last_day = calendar.monthrange(date.year, month)[1]
            return datetime.datetime(date.year, month, last_day)
    last_day = calendar.monthrange(date.year + 1, fiscal_months[0])[1]
    return datetime.datetime(date.year + 1, fiscal_months[0], last_day)

def create_dataset(ew_data):

    ew_data = ew_data[(ew_data["Ticker"] != 'All Other (Suppressed)') & (~ew_data["Ticker"].str.contains(".", regex=False))]
    tickers = list(ew_data["Ticker"].unique())
    bclient = BloombergClient()
    bdata = bclient.get_quarterly_financials(tickers)
    bdata["q_datetime"] = pd.to_datetime(bdata["date"])
    
    #construct financial calendar map
    ticker_quarters = {}
    for ticker in bdata["symbol"].unique():
        qdate = bdata[bdata["symbol"] == ticker]["q_datetime"].sample().item()
        if qdate.month in [3,6,9,12]:
            ticker_quarters[ticker] = 3
        elif qdate.month in [2,5,8,11]:
            ticker_quarters[ticker] = 2
        elif qdate.month in [1,4,7,10]:
            ticker_quarters[ticker] = 1

    ew_data["Month"] = ew_data["Time Periods"].apply(lambda x: datetime.datetime.strptime(x, "%b %Y"))
    ew_data["calendar_type"] = ew_data["Ticker"].apply(lambda x: ticker_quarters[x])
    ew_data["quarter_end"] = ew_data.apply(lambda x: get_quarter_end(x["Month"], x["calendar_type"]), axis=1)

    bdata["calendar_type"] = bdata["symbol"].apply(lambda x: ticker_quarters[x])
    bdata["quarter_end"] = bdata.apply(lambda x: get_quarter_end(x["q_datetime"], x["calendar_type"]), axis=1)

    ew_data = ew_data.groupby(["Ticker","quarter_end","Category"])["Dollars Adjusted"].sum().reset_index()
    ew_data = ew_data.pivot(index=["Ticker","quarter_end"], columns="Category", values="Dollars Adjusted").reset_index()
    ew_data.index.name = None

def run_summary_cat_report(output_dir, df):

    rev_corr_data = most_corr_by_ticker_yy(df, "SALES_REV_TURN", measure_est="BEST_SALES")
    profit_corr_data = most_corr_by_ticker_yy(df, "GROSS_PROFIT", measure_est=None)
    eps_corr_data = most_corr_by_ticker_yy(df, "IS_COMP_EPS_ADJUSTED", measure_est="BEST_EPS")

    writer = pd.ExcelWriter(output_dir + "YYcorr.xlsx")
    rev_corr_data[["symbol","category","category_corr","total_dollars_corr","share_of_total_dollars","estimate_corr"]].to_excel(writer, sheet_name="Rev YY", index=False)
    profit_corr_data[["symbol","category","category_corr","total_dollars_corr","share_of_total_dollars"]].to_excel(writer, sheet_name="Profit YY", index=False)
    eps_corr_data[["symbol","category","category_corr","total_dollars_corr","share_of_total_dollars","estimate_corr"]].to_excel(writer, sheet_name="EPS YY", index=False)
    workbook = writer.book
    rev_sheet = writer.sheets["Rev YY"]
    profit_sheet = writer.sheets["Profit YY"]
    eps_sheet = writer.sheets["EPS YY"] 

    beat_consensus_format = workbook.add_format({"bg_color":"#6ADF41"})
    beat_total_dollars_format = workbook.add_format({"bg_color":"#5897FE"})
    percent_format = workbook.add_format({'num_format': '0.0%'})

    rev_sheet.conditional_format(1, 2, len(rev_corr_data), 2, {"type":"formula","criteria":"=$C2>$F2", "format":beat_consensus_format})
    rev_sheet.conditional_format(1, 2, len(rev_corr_data), 2, {"type":"formula","criteria":"=$C2>$D2", "format":beat_total_dollars_format})
    rev_sheet.set_column(4, 4, cell_format=percent_format)

    profit_sheet.conditional_format(1, 2, len(profit_corr_data), 2, {"type":"formula","criteria":"=$C2>$D2", "format":beat_total_dollars_format})
    profit_sheet.set_column(4, 4, cell_format=percent_format)

    eps_sheet.conditional_format(1, 2, len(eps_corr_data), 2, {"type":"formula","criteria":"=$C2>$F2", "format":beat_consensus_format})
    eps_sheet.conditional_format(1, 2, len(eps_corr_data), 2, {"type":"formula","criteria":"=$C2>$D2", "format":beat_total_dollars_format})
    eps_sheet.set_column(4, 4, cell_format=percent_format)

    writer.save()
    writer.close()


def most_corr_by_ticker_yy(data, measure, measure_est):

    yy_corr_df = pd.DataFrame()
    df = data.copy()
    for s in df["symbol"].unique():
        
        sdf = df[df["symbol"] == s]
        sdf = sdf.dropna(axis=1, thresh=len(sdf)-1)
        if measure not in sdf.columns:
            continue
        use_cols = ["total_dollars",measure]
        if measure_est != None and measure_est in sdf.columns:
            use_cols.append(measure_est)
        share_percs = {}
        for x in sdf.columns:
            if x not in NON_SALES_COLS:
                sdf[x] = sdf[x].apply(lambda x: 0 if pd.isnull(x) else x)
                share_perc = (sdf[x] / sdf["total_dollars"]).mean()
                share_percs[x] = share_perc
                if share_perc > 0.01:
                    use_cols.append(x)
        for x in sdf.columns:
            if x not in NON_SALES_COLS or x in ["total_dollars",measure, measure_est]:
                sdf[x] = sdf[x].pct_change(periods=4)
        sdf = sdf.iloc[4:, :]
        if len(sdf) < 2:
            continue
        #print(sdf[[measure, measure_est]])
        cor = sdf[use_cols].corr()
        cor = cor.sort_values(measure, ascending=False)
        total_cor = cor.loc["total_dollars",measure]
        if measure_est in use_cols:
            est_cor = cor.loc[measure_est, measure]
        else:
            est_cor = None
        cor = cor.reset_index().rename(columns={"index":"category"})
        cor = cor[~cor["category"].isin(["total_dollars",measure, measure_est])].reset_index(drop=True)
        yy_corr_df = yy_corr_df.append({"symbol":s, "category":cor.loc[0, "category"], "category_corr":cor.loc[0, measure], "total_dollars_corr":total_cor, "share_of_total_dollars":share_percs[cor.loc[0,"category"]], "estimate_corr":est_cor}, ignore_index=True)
    return yy_corr_df.sort_values("category_corr", ascending=False)


def run_cat_report(output_dir, ticker, df):

    if ticker not in df["symbol"].unique():
        raise Exception("Ticker not in data")
    if len(df[df["symbol"] == ticker]) < 7:
        raise Exception("Not enough data for ticker")

    writer = pd.ExcelWriter( output_dir + ticker + "_category_correlation.xlsx")
    try:
        ticker_excel(writer, df, ticker)
    except:
        writer.close()
        os.remove(output_dir + ticker + "_category_correlation.xlsx")
        


def get_k_best(df, k, measure):

    cor = df.corr()
    cor_target = abs(cor[measure])
    cor_target = cor_target.sort_values(ascending=False)
    cols = list(cor_target.index)
    cols.remove(measure)
    cols = [x for x in cols if not pd.isnull(cor_target[x])]
    return cols[:k]

def ticker_excel(writer, df, ticker):

    sdf = df[df["symbol"] == ticker]
    sdf = sdf.drop(columns=["IS_EPS","IS_ADJUSTED_EPS_AS_REPORTED","ARD_ADJUSTED_EPS","ARD_GROSS_PROFITS","IS_BASIC_EPS_CONT_OPS"])
    sdf = sdf.dropna(axis=1, how="all")
    for x in sdf.columns:
        if x not in NON_SALES_COLS:
            sdf[x] = sdf[x].apply(lambda x: 0 if pd.isnull(x) else x)
    
    valid_categories = []
    for x in sdf.columns:
        if x not in NON_SALES_COLS:
            if sdf[x].mean() / sdf["total_dollars"].mean() >= 0.01:
                valid_categories.append(x)

    sdf_yy = sdf.copy()
    for x in sdf_yy.columns:
        if x not in NON_SALES_COLS or x in ["total_dollars","SALES_REV_TURN","BEST_SALES","GROSS_PROFIT","IS_COMP_EPS_ADJUSTED","BEST_EPS"]:
            sdf_yy[x] = sdf_yy[x].pct_change(periods=4)
    sdf_yy = sdf_yy.iloc[4:,:]
    
    workbook = writer.book
    yy_visuals_sheet = workbook.add_worksheet(ticker + " YY")
    #raw_visuals_sheet = workbook.add_worksheet(ticker + " Raw")
    sdf_yy.to_excel(writer, index=False, sheet_name="YY Data")
    sdf.to_excel(writer, index=False, sheet_name="Raw Data")
    yy_sheet = writer.sheets["YY Data"]
    raw_sheet = writer.sheets["Raw Data"]

    percent_format = workbook.add_format({'num_format': '0.0%'})    
    border_format = workbook.add_format({"border":2})
    percent_border_format = workbook.add_format({"num_format": "0.0%","border":2})
    beat_consensus_format = workbook.add_format({"num_format": "0.0%","border":2})
    beat_consensus_format.set_bg_color("#6ADF41")
    beat_total_dollars_format = workbook.add_format({"num_format": "0.0%","border":2})
    beat_total_dollars_format.set_bg_color("#5897FE")

    ############## YY Visuals#################

    yy_corr_df = sdf_yy.corr()

    yy_best_rev_cat = get_k_best(sdf_yy[valid_categories + ["SALES_REV_TURN"]], 1, "SALES_REV_TURN")[0]
    yy_rev_cat_corr = yy_corr_df.loc[yy_best_rev_cat, "SALES_REV_TURN"]
    yy_rev_total_corr = yy_corr_df.loc["total_dollars", "SALES_REV_TURN"]
    yy_rev_cat_share = sdf[yy_best_rev_cat].sum() / sdf["total_dollars"].sum()
    yy_rev_estimate_corr = yy_corr_df.loc["BEST_SALES", "SALES_REV_TURN"]
    yy_best_profit_cat = get_k_best(sdf_yy[valid_categories + ["GROSS_PROFIT"]], 1, "GROSS_PROFIT")[0]
    yy_profit_cat_corr = yy_corr_df.loc[yy_best_profit_cat, "GROSS_PROFIT"]
    yy_profit_total_corr = yy_corr_df.loc["total_dollars", "GROSS_PROFIT"]
    yy_profit_cat_share = sdf[yy_best_profit_cat].sum() / sdf["total_dollars"].sum()
    yy_best_eps_cat = get_k_best(sdf_yy[valid_categories + ["IS_COMP_EPS_ADJUSTED"]], 1, "IS_COMP_EPS_ADJUSTED")[0]
    yy_eps_cat_corr = yy_corr_df.loc[yy_best_eps_cat, "IS_COMP_EPS_ADJUSTED"]
    yy_eps_total_corr = yy_corr_df.loc["total_dollars", "IS_COMP_EPS_ADJUSTED"]
    yy_eps_estimate_corr = yy_corr_df.loc["BEST_EPS","IS_COMP_EPS_ADJUSTED"]
    yy_eps_cat_share = sdf[yy_best_eps_cat].sum() / sdf["total_dollars"].sum()

    yy_cols = list(sdf_yy.columns)
    for col in [yy_cols.index(x) for x in [y for y in sdf_yy.columns if y not in NON_SALES_COLS] + ["SALES_REV_TURN","IS_COMP_EPS_ADJUSTED","GROSS_PROFIT","BEST_SALES","BEST_EPS",yy_best_rev_cat, yy_best_profit_cat, yy_best_eps_cat, "total_dollars"]]:
        yy_sheet.set_column(col, col, cell_format=percent_format)

    #ticker and category table
    yy_visuals_sheet.write("A1", "Data", border_format)
    yy_visuals_sheet.write("B1", ticker + " Dollars %YY", border_format)
    yy_visuals_sheet.write("A2", "Best Category (Revenue)", border_format)
    yy_visuals_sheet.write("B2", yy_best_rev_cat, border_format)
    yy_visuals_sheet.write("A3", "Best Category (Profit)", border_format)
    yy_visuals_sheet.write("B3", yy_best_profit_cat, border_format)
    yy_visuals_sheet.write("A4", "Best Category (EPS)", border_format)
    yy_visuals_sheet.write("B4", yy_best_eps_cat, border_format)

    #correlations table
    yy_visuals_sheet.write("E1","Category Corr.", border_format)
    yy_visuals_sheet.write("F1","Total NPD Corr.", border_format)
    yy_visuals_sheet.write("G1", "Consensus Corr.", border_format)
    yy_visuals_sheet.write("D2","Revenue", border_format)
    yy_visuals_sheet.write("D3","Profit", border_format)
    yy_visuals_sheet.write("D4","EPS", border_format)
    if yy_rev_cat_corr > yy_rev_estimate_corr:
        yy_visuals_sheet.write("E2",yy_rev_cat_corr, beat_consensus_format)
    elif yy_rev_cat_corr > yy_rev_total_corr:
        yy_visuals_sheet.write("E2",yy_rev_cat_corr, beat_total_dollars_format)
    else:
        yy_visuals_sheet.write("E2",yy_rev_cat_corr, border_format)
    if yy_profit_cat_corr > yy_profit_total_corr:
        yy_visuals_sheet.write("E3",yy_profit_cat_corr, beat_total_dollars_format)
    else:
        yy_visuals_sheet.write("E3",yy_profit_cat_corr, border_format)
    if yy_eps_cat_corr > yy_eps_estimate_corr:
        yy_visuals_sheet.write("E4", yy_eps_cat_corr, beat_consensus_format)
    elif yy_eps_cat_corr > yy_eps_total_corr:
        yy_visuals_sheet.write("E4", yy_eps_cat_corr, beat_total_dollars_format)
    else:
        yy_visuals_sheet.write("E4", yy_eps_cat_corr, border_format)
    yy_visuals_sheet.write("F2", yy_rev_total_corr, border_format)
    yy_visuals_sheet.write("F3", yy_profit_total_corr, border_format)
    yy_visuals_sheet.write("F4", yy_eps_total_corr, border_format)
    yy_visuals_sheet.write("G2",yy_rev_estimate_corr, border_format)
    yy_visuals_sheet.write("G3", "N/A", border_format)
    yy_visuals_sheet.write("G4", yy_eps_estimate_corr, border_format)
    yy_visuals_sheet.write("H1", "Share of Total NPD $", border_format)
    yy_visuals_sheet.write("H2", yy_rev_cat_share, percent_border_format)
    yy_visuals_sheet.write("H3", yy_profit_cat_share, percent_border_format)
    yy_visuals_sheet.write("H4", yy_eps_cat_share, percent_border_format)
    
    for col, size in {0:22, 1:29, 4:14, 5:18, 6:15, 7:18}.items():
        yy_visuals_sheet.set_column(col, col, size)

    yy_x_axis = ["YY Data",1, yy_cols.index("quarter_end"), len(sdf_yy), yy_cols.index("quarter_end")]

    yy_rev_cat_chart = create_chart(workbook, "YY Data", list(sdf_yy.columns), yy_best_rev_cat, "SALES_REV_TURN", "Reported Revenue", yy_x_axis, len(sdf_yy))
    yy_rev_total_chart = create_chart(workbook, "YY Data", list(sdf_yy.columns), "total_dollars", "SALES_REV_TURN", "Reported Revenue", yy_x_axis, len(sdf_yy))
    yy_rev_consenesus_chart = create_chart(workbook, "YY Data", list(sdf_yy.columns), "BEST_SALES", "SALES_REV_TURN", "Reported Revenue", yy_x_axis, len(sdf_yy))
    yy_profit_cat_chart = create_chart(workbook, "YY Data", list(sdf_yy.columns), yy_best_profit_cat, "GROSS_PROFIT", "Reported Profit", yy_x_axis, len(sdf_yy))
    yy_profit_total_chart = create_chart(workbook, "YY Data", list(sdf_yy.columns), "total_dollars", "GROSS_PROFIT", "Reported Profit", yy_x_axis, len(sdf_yy))
    yy_eps_cat_chart = create_chart(workbook, "YY Data", list(sdf_yy.columns), yy_best_eps_cat, "IS_COMP_EPS_ADJUSTED", "Reported EPS", yy_x_axis, len(sdf_yy))
    yy_eps_total_chart = create_chart(workbook, "YY Data", list(sdf_yy.columns), "total_dollars", "IS_COMP_EPS_ADJUSTED", "Reported EPS", yy_x_axis, len(sdf_yy))
    yy_eps_consenesus_chart = create_chart(workbook, "YY Data", list(sdf_yy.columns), "BEST_EPS", "IS_COMP_EPS_ADJUSTED", "Reported EPS", yy_x_axis, len(sdf_yy))

    yy_visuals_sheet.insert_chart("A6", yy_rev_cat_chart)
    yy_visuals_sheet.insert_chart("E6", yy_rev_total_chart)
    yy_visuals_sheet.insert_chart("J6", yy_rev_consenesus_chart, {'x_offset': -44})
    yy_visuals_sheet.insert_chart("A21", yy_profit_cat_chart)
    yy_visuals_sheet.insert_chart("E21", yy_profit_total_chart)
    yy_visuals_sheet.insert_chart("A36", yy_eps_cat_chart)
    yy_visuals_sheet.insert_chart("E36", yy_eps_total_chart)
    yy_visuals_sheet.insert_chart("J36", yy_eps_consenesus_chart, {'x_offset': -44})


    ############## Raw Visuals#################
    '''
    raw_corr_df = sdf.corr()

    raw_best_rev_cat = get_k_best(sdf, 1, "SALES_REV_TURN")[0]
    raw_rev_cat_corr = raw_corr_df.loc[raw_best_rev_cat, "SALES_REV_TURN"]
    raw_rev_total_corr = raw_corr_df.loc["total_dollars", "SALES_REV_TURN"]
    raw_rev_estimate_corr = raw_corr_df.loc["BEST_SALES", "SALES_REV_TURN"]
    raw_best_profit_cat = get_k_best(sdf, 1, "GROSS_PROFIT")[0]
    raw_profit_cat_corr = raw_corr_df.loc[raw_best_profit_cat, "GROSS_PROFIT"]
    raw_profit_total_corr = raw_corr_df.loc["total_dollars", "GROSS_PROFIT"]
    raw_best_eps_cat = get_k_best(sdf, 1, "IS_COMP_EPS_ADJUSTED")[0]
    raw_eps_cat_corr = raw_corr_df.loc[raw_best_eps_cat, "IS_COMP_EPS_ADJUSTED"]
    raw_eps_total_corr = raw_corr_df.loc["total_dollars", "IS_COMP_EPS_ADJUSTED"]
    raw_eps_estimate_corr = raw_corr_df.loc["BEST_EPS","IS_COMP_EPS_ADJUSTED"]

    raw_cols = list(sdf.columns)

    #ticker and category table
    raw_visuals_sheet.write("A1", "Data", border_format)
    raw_visuals_sheet.write("B1", ticker + " Dollars Raw", border_format)
    raw_visuals_sheet.write("A2", "Best Category (Revenue)", border_format)
    raw_visuals_sheet.write("B2", raw_best_rev_cat, border_format)
    raw_visuals_sheet.write("A3", "Best Category (Profit)", border_format)
    raw_visuals_sheet.write("B3", raw_best_profit_cat, border_format)
    raw_visuals_sheet.write("A4", "Best Category (EPS)", border_format)
    raw_visuals_sheet.write("B4", raw_best_eps_cat, border_format)

    #correlations table
    raw_visuals_sheet.write("E1","Category Corr.", border_format)
    raw_visuals_sheet.write("F1","Total NPD Corr.", border_format)
    raw_visuals_sheet.write("G1", "Consensus Corr.", border_format)
    raw_visuals_sheet.write("D2","Revenue", border_format)
    raw_visuals_sheet.write("D3","Profit", border_format)
    raw_visuals_sheet.write("D4","EPS", border_format)
    raw_visuals_sheet.write("E2",raw_rev_cat_corr, border_format)
    raw_visuals_sheet.write("E3",raw_profit_cat_corr, border_format)
    raw_visuals_sheet.write("E4", raw_eps_cat_corr, border_format)
    raw_visuals_sheet.write("F2", raw_rev_total_corr, border_format)
    raw_visuals_sheet.write("F3", raw_profit_total_corr, border_format)
    raw_visuals_sheet.write("F4", raw_eps_total_corr, border_format)
    raw_visuals_sheet.write("G2",raw_rev_estimate_corr, border_format)
    raw_visuals_sheet.write("G3", "N/A", border_format)
    raw_visuals_sheet.write("G4", raw_eps_estimate_corr, border_format)
    
    for col, size in {0:22, 1:30, 4:14, 5:20, 6:15}.items():
        raw_visuals_sheet.set_column(col, col, size)

    raw_x_axis = ["Raw Data",1, raw_cols.index("quarter_end"), len(sdf), raw_cols.index("quarter_end")]

    raw_rev_cat_chart = create_chart(workbook, "Raw Data", list(sdf.columns), raw_best_rev_cat, "SALES_REV_TURN", "Reported Revenue", raw_x_axis, len(sdf))
    raw_rev_total_chart = create_chart(workbook, "Raw Data", list(sdf.columns), "total_dollars", "SALES_REV_TURN", "Reported Revenue", raw_x_axis, len(sdf))
    raw_profit_cat_chart = create_chart(workbook, "Raw Data", list(sdf.columns), raw_best_profit_cat, "GROSS_PROFIT", "Reported Profit", raw_x_axis, len(sdf))
    raw_profit_total_chart = create_chart(workbook, "Raw Data", list(sdf.columns), "total_dollars", "GROSS_PROFIT", "Reported Profit", raw_x_axis, len(sdf))
    raw_eps_cat_chart = create_chart(workbook, "Raw Data", list(sdf.columns), raw_best_eps_cat, "IS_COMP_EPS_ADJUSTED", "Reported EPS", raw_x_axis, len(sdf))
    raw_eps_total_chart = create_chart(workbook, "Raw Data", list(sdf.columns), "total_dollars", "IS_COMP_EPS_ADJUSTED", "Reported EPS", raw_x_axis, len(sdf))
    
    raw_visuals_sheet.insert_chart("A6", raw_rev_cat_chart)
    raw_visuals_sheet.insert_chart("E6", raw_rev_total_chart)
    raw_visuals_sheet.insert_chart("A21", raw_profit_cat_chart)
    raw_visuals_sheet.insert_chart("E21", raw_profit_total_chart)
    raw_visuals_sheet.insert_chart("A36", raw_eps_cat_chart)
    raw_visuals_sheet.insert_chart("E36", raw_eps_total_chart)
    '''

    writer.save()
    writer.close()

def create_chart(workbook, sheet_name, sheet_cols, npd_col, measure, measure_label, x_axis, num_rows):

    npd_col_name = "Total NPD" if npd_col == "total_dollars" else npd_col
    chart = workbook.add_chart({"type":"line"})
    chart.add_series({"name":npd_col_name,"categories":x_axis, "values":[sheet_name, 1, sheet_cols.index(npd_col), num_rows, sheet_cols.index(npd_col)], "line":{"color":"#0078BE"}})
    chart.add_series({"name":measure_label,"categories":x_axis, "values":[sheet_name, 1, sheet_cols.index(measure), num_rows, sheet_cols.index(measure)], "line":{"color":"red"}})
    chart.set_y_axis({"crossing":"min"})
    chart.set_x_axis({"name":"For Quarter Ending", "position_axis":"on_tick"})
    if npd_col == "total_dollars":
        chart.set_title({"name":"YY Total NPD {measure} Correlation".format(measure=measure_label.replace("Reported ", ""))})
    elif npd_col in ["BEST_SALES","BEST_EPS"]:
        chart.set_title({"name":"YY Consensus {measure} Correlation".format(measure=measure_label.replace("Reported ", ""))})
    else:
        chart.set_title({"name":"YY Category {measure} Correlation".format(measure=measure_label.replace("Reported ", ""))})
    chart.set_legend({"position":"bottom"})
    return chart