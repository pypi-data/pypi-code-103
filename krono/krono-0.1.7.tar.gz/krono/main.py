import json
import typer
import sys
import csv
import pathlib
import pandas as pd
from typing import Optional
from datetime import datetime, date
from time import sleep

app = typer.Typer()


@app.command()
def track(activity: str,
          hourly_rate: Optional[float] = typer.Option(None, "--hourly_rate", "-h",
                                                      help="Hourly rate. "
                                                           "Must be either provided by arguments "
                                                           "or in configuration file")):
    file_path = pathlib.Path.cwd() / "rastreador.json"

    if file_path.is_file():
        with open(file_path, mode='r+') as fid:
            data = json.load(fid)

            if hourly_rate is None:
                if "hourly_rate" not in data:
                    print("Hourly rate must be either provided by arguments or in configuration file.")
                    sys.exit()
                hourly_rate = data["hourly_rate"]

    start_time = datetime.now()
    print("Press CTRL+C to stop timer")
    while True:
        try:
            sleep(1)
            current_time = datetime.now() - start_time
            billed_time = round(current_time.total_seconds() * (hourly_rate/3600), 2)
            report_path = pathlib.Path.cwd() / "database.csv"
            if report_path.is_file():
                df = pd.read_csv(report_path.name)
                df.index = pd.to_datetime(df['date'], format='%Y-%m-%d')
                time_df = df.groupby(pd.Grouper(freq='M')).mean()
                estimated_monthly_earnings = round(time_df["billed_time"].mean() * 30, 2)
            else:
                estimated_monthly_earnings = "N/A"
            print(f"Activity: {activity} "
                  f"- Current time tracked: {current_time} "
                  f"- Billed time: ${billed_time}"
                  f"- Estimated Monthly Earnings: ${estimated_monthly_earnings}", end="", flush=True)
            print("\r", end="", flush=True)
        except KeyboardInterrupt:
            with open('database.csv', 'a+', newline='') as file:
                fieldnames = ['activity', 'current_time', 'billed_time', 'date']
                writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction='ignore')

                if file.tell() == 0:
                    writer.writeheader()

                writer.writerow({'activity': activity, 'current_time': current_time, 'billed_time': billed_time,
                                 'date': date.today()})

            print("\nGood job!")
            sys.exit()


@app.command()
def report(starting_date: str = typer.Option(None, "--starting_date", "-s",
                                             help="[REQUIRED] Starting date for the report (format %Y-%m-%d)"),
           ending_date: Optional[str] = typer.Option(None, "--ending_date", "-e",
                                                     help="Ending date for the report (format %Y-%m-%d)"),
           currency: Optional[str] = typer.Option("USD", "--currency", "-c", help="Currency used"),
           requested_from: Optional[str] = typer.Option(None, "--requested_from", "-r",
                                                        help="Developer/Company requesting payment"),
           bill_to: Optional[str] = typer.Option(None, "--bill_to", "-b", help="Company to bill to"),
           due_date: Optional[str] = typer.Option(None, "--due_date", "-d", help="Due date for payment")):
    file_path = pathlib.Path.cwd() / "rastreador.json"
    if file_path.is_file():
        with open(file_path, mode='r+') as fid:
            data = json.load(fid)

            if requested_from is None:
                requested_from = data["requested_from"]

            if bill_to is None:
                bill_to = data["bill_to"]

    now = datetime.now()
    timestamp = datetime.timestamp(now)

    report_path = pathlib.Path.cwd() / "database.csv"

    if report_path.is_file():
        df = pd.read_csv(report_path.name)
        after_start_date = df["date"] >= starting_date
        ending_date = ending_date if ending_date else now.strftime("%Y-%m-%d")
        before_end_date = df["date"] <= ending_date
        between_two_dates = after_start_date & before_end_date
        filtered_report = df.loc[between_two_dates]
        filtered_report.to_csv(f"report_{timestamp}.csv", index=False)
    else:
        print("No entries yet")
        sys.exit()

    with open(f"report_{timestamp}.csv", "r") as fi:
        reader = csv.DictReader(fi)
        total = round(sum(float(row["billed_time"]) for row in reader), 2)

    with open(f"report_{timestamp}.csv", "a+", newline='') as fd:
        writer = csv.writer(fd)
        writer.writerow(['currency', currency])
        writer.writerow(['requested_from', requested_from])
        writer.writerow(['bill_to', bill_to])
        writer.writerow(['total', total])
        writer.writerow(['date', date.today()])
        writer.writerow(['due_date', due_date])

    print(f"Generated report: report_{timestamp}.csv")


if __name__ == "__main__":
    app()
