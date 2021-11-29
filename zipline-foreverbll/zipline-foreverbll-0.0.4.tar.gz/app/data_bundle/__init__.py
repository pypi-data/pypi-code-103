from zipline.data.bundles import register

from app.data_bundle.yahoo_demo_bundle import yahoo_demo_bundle

# Most popular histrocial data pages as per 2021-11-02 20:57
# source: https://www.nasdaq.com/market-activity/quotes/historical
register(
    "yahoo_demo_bundle",
    yahoo_demo_bundle("AAPL", "SBUX", "MSFT", "CSCO", "QCOM", "FB", "AMZN", "TSLA", "AMD", "ZNGA"),
    calendar_name="NYSE",
)
