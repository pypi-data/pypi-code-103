import re
import csv
import sys
import glob
import string
import warnings
import subprocess
import faulthandler
import datetime as dt
from pathlib import Path

import yaml
import pandas
import sqlalchemy
import numpy as np
import chromedriver_binary
from tqdm import tqdm
from selenium import webdriver
from rapidfuzz import fuzz, process
from sqlalchemy import or_, update
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from selenium.common.exceptions import SessionNotCreatedException
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from menustat.log import *
from menustat.utils import *
# add_meta, loop_string_replace, return_range,
from menustat.orm import Base, Franchise, MenuItem, AnnualItemData, return_largest_id_plusone
from menustat.settings import YEAR, ANALYST, engine, session, config
from menustat.scraper import Calculator, WebTable, WebTableReactive, Pdf, MultiPdf, WebSite, SiteNav
from menustat.collecteddf import CollectedDf, check_df_for_issues


class ClassMapper:
    classmapper = {
            "calculator":Calculator,
            "pdf":Pdf,
            "pdf.multi":MultiPdf,
            "webtable":WebTable,
            "webtable.reactive":WebTableReactive,
            "website":WebSite,
        }

    def run_factory(f, driver):
        classargs = {"name":f.name, "f_id":f.id, "headquarters":f.headquarters,
            "nutr_url":f.nutr_url, "menu_url":f.menu_url,
            "nutr_scraper":f.nutr_scraper, "driver":driver, "year":YEAR
        }
        nav_args = config['scrapers']['web_scrapers'][f.name] if f.name\
                in config['scrapers']['web_scrapers'] else {}
        logger.info("nav_args:{}".format(nav_args))
        classargs.update(nav_args)
        aClass = ClassMapper.classmapper[f.nutr_scraper]
        return aClass(**classargs)



def start_selenium(headless=True):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = headless
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')
    try:

        # driver = webdriver.Remote("http://host.docker.internal:4444/wd/hub",
        #             DesiredCapabilities.CHROME, options=chrome_options)
        driver = webdriver.Chrome(chrome_options=chrome_options)

    except Exception as e:
        # try:
        #     logger.warning("selenium driver startup failed. Using chromedriver"
        #             " autoinstaller instead; this may take a moment.\n"
        #             "Error:{}".format(e), exc_info=True)
        #     chromedriver_autoinstaller.install()
        # except:
        logger.warning("Selenium driver startup failed. Skipping unscraped"
            " franchises requiring selenium-based web scraping."
            "\nError:{}".format(e), exc_info=True)
        driver = None
    return driver



### COLLECTION METHODS ###
@wrap(writelog, writelog)
def collect_and_clean_annualitemdata(headless_conf=True, dryrun=False, subset=None):
    """ Scrape all menu items from sources listed in franchise table.
    Parameters
    ----------
    headless_conf : bool, optional
        Run Selenium without visible browser window (default is True)
    dryrun : bool, optional
        Execute method without writing to database (default is False)
    subset : int or list, optional
        Execute method on franchise subset (default is None)
        If int, select only franchise with matching id.
        If list, select franchises with ids equal to and between listed ints.
    """

    driver = start_selenium(headless=headless_conf)
    menustat_query = session.query(Franchise).\
        filter(sqlalchemy.not_(Franchise.nutr_scraper == "")).\
        filter(sqlalchemy.not_(Franchise.nutr_scraper.like('%.manual')))
    if type(subset) is int:
        menustat_query = menustat_query.filter(Franchise.id == subset)
    elif type(subset) is list:
        menustat_query = menustat_query\
                .filter(Franchise.id >= subset[0])\
                .filter(Franchise.id <= subset[1])
    t = tqdm(menustat_query.all())
    for f in t:
        t.set_postfix_str("{} {}: {}".format(f.id, f.name, f.nutr_scraper))
        try:
            scraped = ClassMapper.run_factory(f, driver)
            scraped.collect_clean_sequence()
            logger.debug("pre-clean, in collect_and_clean_annualitemdata")
        except Exception as e:
            logger.warning("\nFAILURE TO COLLECT FRANCHISE\n----------------------------\nfranchise {}, name {}, scraper {}; passed without"
                " entry\nError:\n{}".format(f.id, f.name, f.nutr_scraper, e), exc_info=True)
            continue
        try:
            df_obj = CollectedDf(f.name, f.id, scraped.nutr_df)
            df_obj.clean()
            df_obj.nutr_df = df_obj.nutr_df.where(pandas.notnull(df_obj.nutr_df), None)
            df_obj.add_df_to_db(dryrun=True)
            df_obj.nutr_df.insert(2, 'mi_name', None)
            df_obj.nutr_df["mi_name"] = df_obj.nutr_df['menu_item_id'].\
                apply(lambda x: return_menuitem_name(x))
            # df_obj.nutr_df.drop(columns="aid_objects", inplace=True)
            save_to_csv_for_review(df_obj.nutr_df, f.name, f.nutr_url, f.id, f.nutr_scraper, f.menu_scraper)
        except Exception as e:
            logger.warning("\nFAILURE TO CLEAN FRANCHISE\n--------------------------\nfranchise {}, name {}, scraper {}; passed without"
                " entry\nError:\n{}".format(f.id, f.name, f.nutr_scraper, e), exc_info=True)
    driver = None if driver == None else driver.quit()


def export_csv(csv_path, table, overwrite=False):
    """Export a database table to csv.

    Parameters
    ----------
    csv_path : string
        Filepath for exported csv.
    table :
    overwrite : (optional) boolean, default False
    """
    if not overwrite:
        if Path(csv_path).exists():
            print("File already exists! Please change the name of the existing file or the file to be created.")
            sys.exit(1)
    else:
        check = input("\nATTENTION: This function will overwrite the file at the current path ({}). Is this okay?"+' (y/n): ').lower().strip()
        if check == 'y':
            print("y -- writing table to csv.")
        elif check == 'n':
            print("n -- ending program without writing to csv")
            sys.exit(1)
        else:
            print("input not recognized; closing the program.")
            sys.exit(1)

    fmt = '%Y-%m-%d'
    table_df = pandas.read_sql_table(table, engine,
            parse_dates={"created_at": fmt, "updated_at": fmt})
    table_df.to_csv(csv_path, index=False)


def update_franchise_table_from_csv(csv_import):
    """Add rows from selected csv to franchise database table
    Try updating existing entry; if no entry exists, add new entry.

    Parameters
    ----------
    csv_import : filepath
        file must have identical layout and structure to db table.
    """
    new_db_entries = []
    new_id = return_largest_id_plusone(Franchise, session)
    with open(csv_import, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                q = session.query(Franchise).get(row['id'])
                if not q:
                    raise NoResultFound("no result found")
                elif q.name == row["name"]:
                    ud = {k:v for k, v in row.items() if v != getattr(q, k)}
                    ud = add_meta(ud)

                    session.query(Franchise).\
                            filter(Franchise.id == row['id']).\
                            update(ud, synchronize_session = False)
                else:
                    raise ValueError("franchise name-id mismatch!")
            except NoResultFound:
                logger.info("No match:{}\nAdding row".format(row["name"]))
                entryargs = {k:v for k, v in row.items()}
                entryargs = add_meta(entryargs, created=True)
                entryargs['id'] = new_id
                new_db_entries.append(Franchise(**entryargs))
                new_id += 1
            except ValueError as e:
                warning = "{} id {}:{}; skipping row.".format(row["name"],\
                        row['id'], e)
                logger.warning(warning)
    session.add_all(new_db_entries)
    session.commit()


### REVIEW FUNCTIONS ###
def check_dfs_for_issues():
    """ Run check_df_for_issues method on all csvs in dfs_for_review directory.
    """
    fpath = "./data/dfs_for_review/"
    csvs = glob.glob("./data/dfs_for_review/*")
    for csv in csvs:
        df = pandas.read_csv(csv)
        name = str(df.loc[3, "name"])
        check_df_for_issues(name, df)

    # add condition to check number of entries without matches

def save_to_csv_for_review(nutr_df, name, url, f_id, nutr_scraper, menu_scraper):
    to_csv_df = nutr_df.copy()
    to_csv_df['name'] = name
    if "iurl" not in to_csv_df:
        to_csv_df['iurl'] = url
    to_csv_df['f_id'] = f_id
    to_csv_df['nutr_scraper'] = nutr_scraper
    to_csv_df['menu_scraper'] = menu_scraper
    prepped_id = "{}{}".format("0"*(3-len(str(f_id))),f_id)
    to_csv_df.to_csv("data/dfs_for_review/{}-{}.csv".format(prepped_id,\
            name.lower().replace("/", "_")), index=False)

def return_menuitem_name(mi_id):
    if mi_id != None:
        try:
            menu_item = session.query(MenuItem).filter(MenuItem.id == mi_id).one()
            return menu_item.item_name
        except Exception as e:
            return None
    else:
        return None
