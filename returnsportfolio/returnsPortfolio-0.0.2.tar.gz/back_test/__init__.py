import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import logging


# Weights and Returns Framework
def return_portfolio(returns, rebal_weights=None, rebal_freq=None, value0=10000, include_info=False):
    """using a time series of returns and a time series of weights for each asset, 
        the function calculates the returns of a portfolio with the same periodicity of the returns data

    :param returns: a time series dataframe of returns
    :param rebal_weights: A time series or single-row matrix/vector containing asset weights, as decimal percentages, 
        treated as beginning of period weights.
    :param rebal_freq: desired rebalancing frequency of the portfolio, i.e: 3BM means rebalance every three business month 
    :param value0: a float denoting the beginning of period total portfolio value
    :param include_info: Boolean, if include_info is TRUE, return a list of intermediary calculations

    :return: port_ret, a dataframe that stores the returns of a portfolio
    """

    all_dates = returns.index.unique()
    start_dt = all_dates[0]
    end_dt = all_dates[-1]
    all_assets = returns.columns

    N = len(all_assets)

    # check if rebal_weights is a constant list
    if isinstance(rebal_weights, pd.DataFrame):
        pass
    elif rebal_weights is None or isinstance(rebal_weights, list):
        logging.info('Rebalance weights are constant')
        # if null weights, generate equal weights
        if rebal_weights == None:
            weights = np.ones(N) / N
        else:
            weights = rebal_weights
        rebal_weights = pd.DataFrame(index=all_dates, columns=all_assets)
        # if no rebalance freq, only rebalance at beginning of period
        if rebal_freq == None:
            logging.info('Portfolio is only rebalanced at beginning')
            rebal_weights.iloc[0, :] = weights
            rebal_weights.dropna(inplace=True)
        else:
            logging.info('Portfolio is rebalanced every {}'.format(rebal_freq))
            rebal_weights.loc[:, :] = weights
            rebal_weights = rebal_weights.resample(rebal_freq).first()
            # Note that for stocks, use business days to resample. eg. '3BM' instead of '3M', 'BY' instead of 'Y'

    # trim rebal_weight timeframe to match returns timeframe
    rebal_weights = rebal_weights.loc[start_dt:end_dt]
    rebal_dates = rebal_weights.index.unique()

    # rebal_weights should not have weights if security does not exist in returns
    rebal_weights.mask(returns.shift(-1).isna(), np.nan, inplace=True)

    # rescale weights for each row (date) back to 1
    rebal_weights = rebal_weights.div(abs(rebal_weights.sum(axis=1)), axis=0)

    # check to see if rebal_weights has weights for first date
    rebal_weights_start = rebal_weights.index.unique()[0]
    if start_dt != rebal_weights_start:
        logging.info('Earliest portfolio weights is on {}.'.format(rebal_weights_start))
        # slice returns data to earliest rebalancing weights date
        returns = returns.loc[rebal_weights_start:]
        start_dt = rebal_weights_start
        all_dates = returns.index.unique()

    # make sure the columns line up
    assert returns.columns.equals(
        other=rebal_weights.columns), "The columns of returns and rebalancing weights does not match"

    # calculate portfolio returns
    # beginning of period values for each asset
    bop_value = pd.DataFrame(index=all_dates, columns=all_assets)
    # end of period values for each asset
    eop_value = bop_value.copy()

    # beginning of period weights for each asset
    bop_weights = bop_value.copy()
    # end of period weights for each asset
    eop_weights = bop_value.copy()

    # contribution to change in weights for each asset
    period_contrib = bop_value.copy()

    # overall portfolio returns
    port_ret = pd.DataFrame(index=all_dates, columns=['returns'])
    # beginning of period total value
    bop_value_total = port_ret.copy()
    # end of period total value
    eop_value_total = port_ret.copy()

    end_value = value0

    # loop through the rebalance periods
    idx = 1
    for i in range(rebal_weights.shape[0]):
        from_dt = rebal_dates[i]
        logging.info('Rebalancing portfolio on {}'.format(all_dates[idx - 1]))
        from_dt += datetime.timedelta(days=1)  # do not include the beginning date
        # no more rebalancing after this; go to end of dates
        if i == len(rebal_dates) - 1:
            to_dt = end_dt
        else:
            to_dt = rebal_dates[i + 1]

        ret_period = returns.loc[from_dt:to_dt]

        first_day = True

        # make sure our filtered period has data
        for j in range(ret_period.shape[0]):
            if first_day:
                # logging.info('Rebalancing portfolio on {}'.format(all_dates[idx]))
                bop_value.iloc[idx, :] = end_value * rebal_weights.iloc[i, :]
                first_day = False
            else:
                bop_value.iloc[idx, :] = eop_value.iloc[idx - 1, :]

            bop_value_total.iloc[idx] = bop_value.iloc[idx, :].sum()

            # calculate end of period values
            eop_value.iloc[idx, :] = (1 + ret_period.iloc[j, :]) * bop_value.iloc[idx, :]
            eop_value_total.iloc[idx] = eop_value.iloc[idx, :].sum()

            # calculate period contribution of each asset
            period_contrib.iloc[idx, :] = ret_period.iloc[j, :] * bop_value.iloc[idx, :] / bop_value_total.iloc[
                idx].values

            # calculate weights of each asset
            bop_weights.iloc[idx, :] = bop_value.iloc[idx, :] / bop_value_total.iloc[idx].values
            eop_weights.iloc[idx, :] = eop_value.iloc[idx, :] / eop_value_total.iloc[idx].values

            port_ret.iloc[idx] = eop_value_total.iloc[idx] / end_value - 1

            end_value = eop_value_total.iloc[idx].values

            idx += 1

    port_ret.dropna(inplace=True)

    if include_info:
        logging.info(
            "Returning portfolio returns, bop values, eop values, bop weights, eop weights, period contribution")
        return [port_ret, bop_value, eop_value, bop_weights, eop_weights, period_contrib]

    return port_ret


def performance_metrics(returns, annualization=1, quantile=0.05):
    metrics = pd.DataFrame(index=returns.columns)
    metrics['Mean'] = returns.mean() * annualization
    metrics['Vol'] = returns.std() * np.sqrt(annualization)
    metrics['Sharpe'] = (returns.mean() / returns.std()) * np.sqrt(annualization)

    metrics['Min'] = returns.min()
    metrics['Max'] = returns.max()
    return metrics


def maximum_drawdown(returns):
    """calculate the maximum drawdown of the given return time series"""
    returns['returns'] = pd.to_numeric(returns['returns'])
    cum_returns = (1 + returns).cumprod()
    rolling_max = cum_returns.cummax()
    drawdown = (cum_returns - rolling_max) / rolling_max

    max_drawdown = drawdown.min()
    end_date = drawdown.idxmin()
    summary = pd.DataFrame({'Max Drawdown': max_drawdown, 'Bottom': end_date})

    for col in drawdown:
        summary.loc[col, 'Peak'] = (rolling_max.loc[:end_date[col], col]).idxmax()
        recovery = (drawdown.loc[end_date[col]:, col])

        try:
            summary.loc[col, 'Recover'] = pd.to_datetime(recovery[recovery >= 0].index[0])
        except:
            summary.loc[col, 'Recover'] = pd.to_datetime(None)

        summary['Peak'] = pd.to_datetime(summary['Peak'])
        try:
            summary['Duration (to Recover)'] = (summary['Recover'] - summary['Peak'])
        except:
            summary['Duration (to Recover)'] = None

        summary = summary[['Max Drawdown', 'Peak', 'Bottom', 'Recover', 'Duration (to Recover)']]

    return summary


def tail_metrics(returns, quantile=.05, mdd=True):
    """calculate Skewness, Kurtosis, VaR, and CVaR of given return time series"""
    metrics = pd.DataFrame(index=returns.columns)
    metrics['Skewness'] = returns.skew()
    metrics['Kurtosis'] = returns.kurtosis()

    VaR = returns['returns'].quantile(quantile)
    CVaR = (returns[returns['returns'] < returns['returns'].quantile(quantile)]).mean()

    metrics['VaR ({})'.format(quantile)] = VaR
    metrics['CVaR ({})'.format(quantile)] = CVaR

    if mdd:
        mdd_stats = maximum_drawdown(returns)
        metrics = metrics.join(mdd_stats)

    return metrics


def cumulative_plot(returns, save_path=""):
    """plot the cumulative returns graph of given return time series"""
    cum_ret = (1 + returns).cumprod()
    cum_ret.plot()
    plt.savefig(save_path)