import re
import html
import time
from pathlib import Path
from urllib.request import Request, urlopen

import yaml
import pandas
import camelot
import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

from menustat.log import *
from menustat.utils import *
# most_frequent, loop_string_replace, strip_col_from_col, find_rows_with_val, remove_rows_with_val, one_value_in_df,
from menustat.settings import YEAR, ANALYST, engine, session, config
from menustat.exceptions import ColumnReadingError, RowReadingError, RowAdjustError


class Scraper():
    """ Abstract class for all data collection classes.
    Subclasses include Pdf, SiteNav, and WebTable.

    Attributes
    ----------
    name : string
        Franchise's name, pulled from database.
    nutr_url : string
        Franchise's nutr_url, pulled from database.
    nutr_df : pandas dataframe
        Dataframe of scraped menu data, produced by either reading a csv or
        executing the "produce_nutr_df" method set by Scraper subclasses.
    f_id : int
        Franchise's database id, pulled from database.
    nutr_columns : list
        standard nutrition column names
    csv_file : string
        path prefix for csv.

    Methods
    -------
    collect_clean_sequence()
    make_corrections()
    standardize_col_names(df)
    separate_serving_unit_from_serving_colname(df)
    remove_cater_rows(drop="section", flags=False)
    get_method(method_name, args=None)
    click_and_wait(element, seconds, script=False)
    """

    def __init__(self, name, f_id, nutr_url, **kwargs):
        self.name = name
        self.nutr_url = nutr_url
        self.nutr_df = pandas.DataFrame()
        self.f_id = f_id
        self.nutr_columns = ['calories', "total_fat", "saturated_fat",
                "trans_fat", "cholesterol", "sodium", "potassium",
                "carbohydrates", "protein", "sugar", "dietary_fiber"]
        self.__dict__.update(kwargs)
        self.csv_file = "./data/{}/".format(YEAR)
        logger.info(f"name:{name} url:{nutr_url}\n{self.__dict__}")


    @wrap(writelog, writelog)
    def collect_clean_sequence(self):
        if not Path(self.csv_file).exists():
            self.produce_nutr_df()
            self.nutr_df.to_csv(self.csv_file, index=False)
        self.nutr_df = pandas.read_csv(self.csv_file)
        self.make_corrections()


    @wrap(writelog, writelog)
    def make_corrections(self):
        #remove all items with catering in menu_section
        self.remove_cater_rows(drop="item", flags=re.IGNORECASE)
        self.nutr_df = self.standardize_col_names(self.nutr_df)


    @wrap(writelog, writelog)
    def standardize_col_names(self, df):
        """Edit strings and/or replace using dict to change column names.
        1. strip spaces and replace newlines and asterisks
        2. add "g" as "serving_size_unit" value if serving_size column has
        (g) or (oz) in name
        3. remove all gram/milligram values from columns
        4. strip any spaces and replace remaining spaces with underscores
        5. use nutr_col_dict to replace column values requiring
         further correction
        6. add columns for any values not collected from the source
        """
        df = self.separate_serving_unit_from_serving_colname(df)
        standard_cols = ["item_name","item_description","serving_size",\
        "serving_size_household","serving_size_unit","notes"]
        standard_cols.extend(self.nutr_columns)

        logger.debug(f"df cols: {df.columns.values}")
        logger.debug("standard_cols:{}".format(standard_cols))

        rename_dict = {}
        for col in df.columns.values.tolist():
            col2 = col
            col2 = loop_string_replace(config['col_replace_dict'], col2)
            rename_dict[col] = col2.strip(":_ ").rstrip("s").lower()
        logger.debug(f"rename_dict: {rename_dict}")
        df = df.rename(columns=rename_dict)

        logger.debug("final col revision: {}".format(df.columns.values))
        if "serving_size" in df.columns and "weight" in df.columns:
            df = df.rename(columns={"serving_size":"serving_size_household"})
        df = df.rename(columns=config['nutr_col_dict'])
        add_cols = np.setdiff1d(standard_cols, df.columns.values.tolist())
        for value in add_cols:
            df[value] = ''
        logger.debug("colnames:{}".format(df.columns.values))
        logger.debug(f"df3:\n {df}")
        return df

    @wrap(writelog, writelog)
    def separate_serving_unit_from_serving_colname(self, df):
        ss_rn = ["serving size (g) or (fl oz)", "serving size (g)",
                "serving weight (g)", "serving size (oz)", "weight (g)",
                "(g) serving size", "(oz) serving size",
                "weight (g.)", "serving size (oz. )", "serving size* (ml)"]
        for i in ss_rn:
            if i in df.columns:
                u_search = re.search(r"\((.*)\)", i)
                u = u_search.group(1)
                logger.debug(f"u_search results:{u}")
                r_i = i.replace(f"({u})", "").strip("* ")
                df.rename(columns={i:r_i}, inplace=True)
                df["serving_size_unit"] = u.strip(". ")
        return df


    def remove_cater_rows(self, drop="section", flags=False):
        cater = find_rows_with_val(self.nutr_df, '(CATERING|PARTY PLATTER)', rex=True, flags=flags)
        if not cater.empty:
            logger.info(f"cater rows:\n{cater}")
            if drop == "section":
                dropsection = self.nutr_df.index[cater.index[0]:]
            elif drop == "item":
                dropsection = cater.index.values.tolist()
            self.nutr_df.drop(dropsection, inplace=True)


    def get_method(self, method_name, args=None):
        """Return method with the specified name.
        """
        method = getattr(self, method_name)
        return method(args)


    def click_and_wait(self, element, seconds, script=False):
        if script == True:
            self.driver.execute_script("arguments[0].click();", element)
        else:
            element.click()
        time.sleep(seconds)



class Calculator(Scraper):
    """
    Abstract class for franchises which use a calculator format and/
    or require the user to select individual items from a dropdown menu.

    Attributes
    ----------
    csv_file: string
        Path of CSV of raw scraped data. CSV name is the franchise's f_id.
    driver: object
        The driver controlling the running selenium session

    Methods
    -------
    produce_nutr_df() - calls all functions needed to produce
    return_add_rm_buttons()
    scrape_calculator()
    return_opts(opt_drop_css)
    collect_nutrition_facts(item_name, item_row, n_dict, df)
    combine_fields(field)
    generate_description(cust_div, cust_item, item_name)
    """

    def __init__(self, name, f_id, nutr_url, driver, **kwargs):
        self.driver = driver
        super().__init__(name, f_id, nutr_url, **kwargs)
        self.csv_file += "calculator/{}.csv".format(self.f_id)


    def produce_nutr_df(self):
        self.scrape_calculator()


    def return_add_rm_buttons(self):
        add_button = self.driver.find_element_by_css_selector(\
            self.nav['add_button'])
        remove_button = self.driver.find_element_by_css_selector(\
            self.nav['rm_button'])
        return (add_button, remove_button)


    def scrape_calculator(self):
        self.driver.get(self.nutr_url)
        time.sleep(2)
        return pandas.DataFrame()


    def return_opts(self, opt_drop_css):
        opt_drop = self.driver.find_element_by_css_selector(opt_drop_css)
        return opt_drop.find_elements_by_css_selector("option")


    def collect_nutrition_facts(self, item_name, item_row, n_dict, df):
        for n, css in n_dict.items():
            logger.debug("nutrient:{}".format(n))
            nval = self.driver.find_element_by_css_selector(css).\
                    get_attribute('innerText')
            item_row[n] = nval
        logger.debug("item_row:\n{}".format(item_row))
        item_row["item_description"] = self.generate_description(self.\
        nav['cust_div_css'], self.nav["cust_item_sect"], item_name)
        df = df.append(item_row, ignore_index = True)
        return df


    def combine_fields(self, field):
        dicta = {}
        for iname, msect in zip(self.nutr_df.item_name,self.nutr_df[field]):
            if iname not in dicta.keys():
                dicta[iname] = [msect]
            else:
                dicta[iname].append(msect)
        dicta = {k:set(v) for k, v in dicta.items()}
        dictb = {key:", ".join(v for v in val) for key, val in dicta.items()}
        self.nutr_df[field] = self.nutr_df['item_name'].map(dictb)
        self.nutr_df.drop_duplicates(keep="first", inplace=True)


    def generate_description(self, cust_div, cust_item, item_name):
        """ Generate item description using values in an item's side menu.
        """
        default_list = []
        opt_list = []
        customize_menu = self.driver.find_element_by_css_selector(cust_div)
        customizes = customize_menu.\
                find_elements_by_css_selector(cust_item)
        for customize in customizes:
            check = customize.find_element_by_css_selector("input")
            span = customize.get_attribute("innerText")
            check_attr = check.get_attribute("checked")
            if check_attr == "checked" or check_attr == "true":
                default_list.append(span)
            else:
                opt_list.append(span)
        defaults = ', '.join(default_list)
        opts = ", ".join(opt_list)
        description = f"{item_name} with {defaults}; options of {opts}"
        return description



class WebTable(Scraper):
    """Class for franchises which present nutrition data in an html table.
    Subclasses: WebTableReactive

    Attributes
    ----------
    csv_file : scraper

    Methods
    -------
    produce_nutr_df()
    normalize_column_names()
    make_corrections()
    scrape_webtable(page_dfs)
    add_header_categories(cats)
    """

    def __init__(self, name, f_id, nutr_url, **kwargs):
        # self.cat_dict = {}
        super().__init__(name, f_id, nutr_url, **kwargs)
        self.csv_file += "webtable/{}.csv".format(self.f_id)


    def produce_nutr_df(self):
        page_dfs = webtable_to_df(self.nutr_url)
        self.scrape_webtable(page_dfs)


    @wrap(writelog, writelog)
    def normalize_column_names(self):
        """ Format existing column names.
        """
        # case-insensitive return col for normalized_nutrition_cols value with " " as "_"
        c_n = list(self.nutr_df.columns.values)
        column_names = [x.lower().replace(" ", "_") for x in c_n]
        self.nutr_df.columns=column_names
        for val in self.nutr_columns:
            cmatch = [s for s in column_names if val in s]
            if cmatch:
                self.nutr_df.rename(columns = {cmatch[0]:val}, inplace=True)


    def make_corrections(self):
        self.nutr_df = delete_all_na(self.nutr_df, subset=0)
        if "mymenuhd" not in self.nutr_url:
            cats = self.nutr_df.loc[self.nutr_df["item_name"] == self.\
                    nutr_df["calories"]]
            logger.info("cat_headers:{}".format(cats))
            try:
                self.add_header_categories(cats)
            except IndexError:
                pass
        super().make_corrections()


    @wrap(writelog, writelog)
    def scrape_webtable(self, page_dfs):
        """combine dataframes in an array into one dataframe.
        1. remove dfs with "egg" in column values and < 15 columns
            (indicates df is allergen menu)
        2. rename ambiguous dataframe columns
        3. if df
        Parameters
        ----------
        page_dfs: dataframe array
        """
        for df in page_dfs:
            # turn category headers into category column values
            first_tuple_elements = [str(i).lower() for i in df.columns.values]
            # ignore tables that are allergy tables
            if "egg" in first_tuple_elements and len(df.columns) < 15:
                pass
            elif df.columns.values[0] == "item_name":
                rename_dict = {"weight":"serving_size",
                            "serving":"serving_size_household"}
                df = df.rename(columns=rename_dict)
                self.nutr_df = self.nutr_df.append(df, ignore_index = True)
            elif not one_value_in_df(df):
                rename_dict = {}
                if "mymenuhd" not in self.nutr_url:
                    menu_section = df.columns[0] if df.columns.\
                            values[0] != "Unnamed: 0" else None
                    rename_dict.update({df.columns[0]: 'item_name'})
                    df['menu_section'] = menu_section
                rename_dict.update({"Parent Section":"menu_section",
                        "Menu Item": "item_name", "CALS":"calories"})
                df = df.rename(columns=rename_dict)
                if df.columns.values[1] == "Unnamed: 1":
                    df["Unnamed: 1"].fillna("", inplace=True)
                    for index, row in df.iterrows():
                        add = row["item_name"]+", "+str(row["Unnamed: 1"])
                        df.loc[index, "item_name"] = add.strip(", ")
                    df.drop(columns="Unnamed: 1", inplace=True)
                self.nutr_df = self.nutr_df.append(df, ignore_index=True)
        nutr_df = del_colnames_from_colvals(self.nutr_df)
        self.nutr_df = nutr_df.rename(columns=lambda x: x.lower())


    @wrap(writelog, writelog)
    def add_header_categories(self, cats):
        """
        Assign value of category title row as the "menu_section" column
        value for all items under it, then remove row from dataframe.
        """
        sections = create_sections(self.nutr_df, cats.index)
        self.nutr_df['menu_section'].fillna("", inplace=True)
        for k,v in sections.items():
            self.nutr_df.loc[k:v, "menu_section"] += ", {}".format(self.nutr_df.loc[k]["calories"])
        self.nutr_df["menu_section"] = self.nutr_df["menu_section"].str.strip(", ")
        self.nutr_df = self.nutr_df.drop(cats.index).copy()
        logger.info("cat_headers end:{}".format(cats))


class WebTableReactive(WebTable):
    def __init__(self, name, f_id, nutr_url, driver, **kwargs):
        self.driver = driver
        super().__init__(name, f_id, nutr_url, **kwargs)


    def produce_nutr_df(self):
        page_dfs = self.webtable_to_df(self.nutr_url)
        self.scrape_webtable(page_dfs)


    def webtable_to_df(self, nutr_url, type="default"):
        self.driver.get(nutr_url)
        time.sleep(10)
        logger.debug("USING SELENIUM")
        html = self.driver.find_element_by_css_selector(\
            "div.NutritionalInformation").get_attribute('innerHTML')

        page_dfs = pandas.read_html(html, header=None)
        return page_dfs


    def scrape_webtable(self, dfs):
        dfs = [df for df in dfs if "treenuts" not in [str(i).lower() for i in df.columns.values]]
        for df in dfs:
            df.dropna(axis=1, how='all', inplace=True)
            logger.debug("Header:\n{}\nvalues:{}".format(df, [str(i).strip() for i in df.columns.values]))
            # dfs_noheader.append(df)
            df = rename_cols_by_index(df)
            # else:
            #     logger.debug("Added:\n{}".format(df))
            #     self.nutr_df = self.nutr_df.append(df,ignore_index = True)
        # for df in dfs_noheader:
        #     logger.debug("Noheader Added:\n{}".format(df))
            # new_cols = {x: y for x, y in zip(df.columns, self.nutr_df.columns)}
            self.nutr_df = self.nutr_df.append(df)

        self.nutr_df = del_colnames_from_colvals(self.nutr_df)
        self.nutr_df.columns = self.nutr_df.iloc[1]
        self.nutr_df.columns.values[0] = "item_name"
        self.normalize_column_names()
        self.nutr_df.fillna('', inplace=True)
        nc = self.nutr_df.loc[pandas.notna(self.nutr_df['calories'])]
        nc = nc.astype("string")
        nutr_cols = nc.loc[nc["calories"].str.\
                contains("calories", flags=re.IGNORECASE, regex=True)]
        self.nutr_df.drop(nutr_cols.index, inplace=True)
        self.nutr_df["menu_section"] = None


    def make_corrections(self):
        self.nutr_df.fillna('', inplace=True)
        logger.debug("nutr_df:\n{}".format(self.nutr_df.head(40)))
        cat_headers = self.nutr_df.loc[(self.nutr_df["calories"] == "")|\
                (self.nutr_df["calories"] == "Unnamed: 2")]
        self.add_header_categories(cat_headers)
        super().make_corrections()


    def add_header_categories(self, cat_headers):
        self.nutr_df.loc[self.nutr_df.index.isin(cat_headers.\
                index), "calories"] = self.nutr_df["item_name"]
        super().add_header_categories(cat_headers)



class Pdf(Scraper):
    """ Data collection class for franchise nutrition information pdfs.

    Attributes
    ----------
    cleaner_conf
    scraper_conf
    src_file
    csv_file: string
        Path of csv where uncleaned scraped data is stored. The csv's name
        is the franchise's f_id.

    Methods
    -------
    produce_nutr_df()
    return_src_file(srcfile, url)
    dfs_from_pdf(url)
    autoread_pdf(url)
    in_operations(val)
    concatenate_pdf_dfs(dfs)
    make_corrections()
    id_rowtypes()
    identify_cats(df)
    return_rowtype(df, string, rex=False, nun=False)
    id_last_item_row()
    remove_rows_by_content()
    set_column_header()
    colnames_from_config(serving=0, fat_cal=1,
    potassium=0, switch_sodium_carb=False)
    autoname_cols(df, nutr_rows)
    split_headers_cats(df, headercats)
    reassign_rows()
    add_name_to_sizes(cats, separate_notes=True)
    add_section_labels(df, sect_starts, target_col,src_row_idx, to_labels=None, src_col=None, separator=" ")
    add_notes_to_categories()
    separate_value_and_note(value, re_string=string)
    """

    def __init__(self, name, f_id, nutr_url, **kwargs):
        try:
            self.cleaner_conf = config["cleaners"]["pdf_cleaners"]
        except (KeyError, TypeError):
            self.cleaner_conf = {}
        try:
            self.scraper_conf = config['scrapers']['pdf_scrapers'][name]
        except (KeyError, TypeError):
            self.scraper_conf = {}
        # self.cat_dict = {}
        super().__init__(name, f_id, nutr_url)
        y = YEAR
        self.csv_file += f"pdf_scrapes/{self.f_id}.csv"
        self.src_file = f"./data/{y}/pdf_source/{self.f_id}.pdf"


    @wrap(writelog, writelog)
    def produce_nutr_df(self):
        """Save pdf, select/automate camelot config, read pdf, concat dfs.

        Returns
        -------
        self.nutr_df: DataFrame
            columns are named after their index number
            item_name corresponds to column 0
            if menu_section is present, it must correspond to column 1
        """
        self.return_src_file(self.src_file, self.nutr_url)
        dfs = self.dfs_from_pdf(self.src_file)
        logger.info("dfs: {}".format(dfs))
        nutr_df = self.concatenate_pdf_dfs(dfs)
        self.nutr_df = nutr_df.replace(r'\\n','', regex=True)


    def return_src_file(self, srcfile, url):
        """Return pdf src_file if file exists; if not, save to filepath
        """
        if not Path(srcfile).exists():
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urlopen(req)
            with open(srcfile, 'wb') as f:
                f.write(response.read())


    @wrap(writelog, writelog)
    def dfs_from_pdf(self, url):
        """ Determines the correct method for reading a pdf.
        Parameters
        ----------
        url : string
            String representing web address or file location of pdf

        Returns
        -------
        final_dfs : list
            List of dataframes taken from the pdf
        """
        camelot_args = None if not self.scraper_conf or "readconf" not in\
                self.scraper_conf else self.scraper_conf["readconf"]
        if camelot_args is None:
            logger.info("No camelot_args present; using basic conf")
            dfs = self.autoread_pdf(url)
        elif type(camelot_args) is list:
            logger.info("using readconf to read pdf")
            dfs = self.read_from_config(camelot_args, url)
        else:
            logger.warning("ISSUE: camelot_args type is not list")
        final_dfs = [df for df in dfs if len(df.columns) > 3 or self.\
                        in_operations("allow_small_df")]
        return final_dfs


    def read_from_config(self, camelot_args, url):
        dfs = []
        for conf in camelot_args:
            c = conf if type(conf) is dict else conf[1]
            tables = camelot.read_pdf(url, **c)
            dfcollect = [t.df for t in tables]
            logger.debug(f"read_from_config dfcollect:\n{dfcollect}")
            if not self.in_readconf(conf, "columns"):
                logger.debug("read_from_config - deleting empty cols")
                dfcollect = [delete_all_na(df, subset=1) for df in dfcollect]

            if type(conf) is list:
                dfs.append([conf[0], dfcollect])
            elif type(conf) is dict:
                dfs.extend(dfcollect)
        logger.debug(f"read_from_config end dfs:\n{dfs}")
        return dfs

    def in_readconf(self, conf, val):
        """Confirm that a value is in the config "readconf" list.
        """
        if type(conf) is list:
            return True if val in conf[1] else False
        elif type(conf) is dict:
            return True if val in conf else False
        else:
            logger.warning(f"ISSUE: readconf entry datatype unrecognized\nconf:{conf}")


    @wrap(writelog, writelog)
    def autoread_pdf(self, url):
        """
        Parameters
        ----------
        url : string
            String representing web address or file location of pdf

        Returns
        -------
        final_dfs : list
            dataframes of pdf table information
        """
        tables = camelot.read_pdf(url, pages="1-end", shift_text=[''])
        logger.debug("tables: {}".format(tables))
        try:
            col_num = [len(t.df.columns) for t in tables]
            newline_ct = lambda x: x.str.count("\n").sum()
            df_newlines = [t.df.apply(newline_ct).sum() for t in tables]
            if max(col_num) < 4:
                if not self.in_operations("allow_small_df"):
                    raise ColumnReadingError
            elif sum(df_newlines)/len(df_newlines) > 200:
                raise RowReadingError
            elif sum(df_newlines)/len(df_newlines) > 20:
                raise RowAdjustError
        except (ColumnReadingError, RowReadingError):
            tables = camelot.read_pdf(url, pages="1-end", flavor="stream")
            logger.info("ERROR:too few col/rows\ntables:{}".format(tables))
        except RowAdjustError:
            tables = camelot.read_pdf(url, shift_text=[''], pages="1-end",\
                    line_scale=50)
            logger.info("ERROR: rows too close\ntables: {}".format(tables))
        except ValueError:
            logger.info("ERROR: issue w/ table read, trying stream")
            tables = camelot.read_pdf(url, pages="1-end", flavor="stream")
        dfs = [delete_all_na(t.df, subset=1) for t in tables]
        return dfs


    def in_operations(self, val):
        """Confirm that a value is in the config "operations" list.
        Parameters
        ----------
        val : string
            value to search for in "operations" list
        Returns
        -------
        boolean value
            True if val is in the "operations" list, False if it's not there
            or no "operations" list can be found
        """
        try:
            return True if val in self.scraper_conf['operations'] else False
        except (KeyError,TypeError):
            return False


    @wrap(writelog, writelog)
    def concatenate_pdf_dfs(self, dfs):
        frames = []
        # add warning for tables that don't have same number of cols
        for i, df in enumerate(dfs):
            if df.columns.values.tolist() != list(range(len(df.columns.values))):
                dfs[i] = rename_cols_by_index(df)
                dfs[i].drop(0, inplace=True)
            frames.append(df)
            dfcols = df.columns.values.tolist()
            logger.debug(f"dataframe cols:\n{dfcols}")
        c_df = pandas.concat(frames, ignore_index=True)
        # rename columns by their indexes
        if c_df.columns.values.tolist() != list(range(len(c_df.columns.values))):
            c_df = rename_cols_by_index(c_df)

        logger.info("result:{}".format(c_df))
        return c_df


    @wrap(writelog, writelog)
    def make_corrections(self):
        """ Make a series of corrections to pdf dataframe.

        1. remove rows representing content that appears before or after
        the pdf table.
        2. set column names by locating line with "Calories/Cals" or by
        manually setting the column names
        3. delete duplicate column name rows
        4. change cat header rows into values in the menu_section column
        """
        # make all changes needed for set_column_header to work
        self.nutr_df = delete_all_na(self.nutr_df, fill=True)
        self.id_format_header_rows()
        if self.in_operations("delete_newlined"):
            newlined = find_rows_with_val(self.nutr_df, r'\\n', flags=re.MULTILINE)
            logger.debug(f"deleting all characters after \\n:\n{newlined}")
            self.nutr_df['calories'] = self.nutr_df['calories'].str.replace(r'\n.*', "", regex=True, flags=re.MULTILINE)
            logger.debug(f"deleted all characters after \\n:\n{newlined}")
        self.remove_rows_by_content()
        # after remove_rows_by_content, all NaN must be filled with empty strings
        self.detect_and_split_multisize_rows()
        self.id_rowtypes()
        self.nutr_df = self.nutr_df.reset_index(drop=True)
        self.reassign_rows()

        self.move_notes()
        logger.debug(f"self.nutr_df.item_name:\n{self.nutr_df.item_name}")
        super().make_corrections()


    def id_format_header_rows(self):
        header_idx_list = self.id_all_header_rows(self.nutr_df)
        self.nutr_df = recombine_header_rows(self.nutr_df, header_idx_list)
        self.nutr_df['rowtype'] = ''
        self.nutr_df.loc[0, 'rowtype'] = "rowtype"
        if self.in_operations("headers_cats_combined"):
            hdrs_cats = find_rows_with_val(self.nutr_df,\
                    self.cleaner_conf['header_match'], flags=re.IGNORECASE)
            self.nutr_df = self.split_headers_cats(self.nutr_df, hdrs_cats)
            hdrs = find_rows_with_val(self.nutr_df,\
                    self.cleaner_conf['header_match'], flags=re.IGNORECASE)
            cats = [i+1 for i in hdrs.index.tolist()]
            self.nutr_df.loc[self.nutr_df.index.isin(cats), "rowtype"] = "cat"
        # set_column_header
        self.set_column_header()
        if self.in_operations("headers_cats_combined"):
            self.reassign_rows()
        self.detect_and_remove_allergy_cols()


    def id_all_header_rows(self, df):
        """
        Identify "main" header rows (those containing the most relevant
        headers) as those containing the substrings "cal", "fat", and
        "carb" or "prot".
        If rows immediately before or after main header rows contain
        strings characteristic of fragmented header rows - specifically,
        "total", "(g)", or "grams" in spaces after the first two columns -
        put them into a list with their associated main header row.

        Returns
        -------
        nutr_row_idxs : list
            list of either numbers representing the indexes of header rows
            or lists containing the
        """

        nutr_rows = find_rows_with_val(df,\
                self.cleaner_conf['header_match'], flags=re.IGNORECASE)
        nutr_row_idxs = nutr_rows.index.values.tolist()

        def find_row_fragments(df, re_string, nutr_row_idxs):
            rows = find_rows_with_val(df, re_string, flags=re.IGNORECASE)
            row_idxs = rows.index.values.tolist()
            row_idxs = [i for i in row_idxs if i not in nutr_row_idxs]
            row_idxs_final = [i for i in row_idxs for n in nutr_row_idxs if i in range(n-2, n+3)]
            logger.debug(f"row_idxs:{row_idxs} row_idxs2:{row_idxs_final}")
            return row_idxs_final

        gram_idxs = find_row_fragments(df, r"((\(m?g\)+|Grams).*)", nutr_row_idxs)
        logger.debug(f"gram_idxs: {gram_idxs}")
        outlier_idxs = find_row_fragments(df, r"^((Total)+|OPTIONS)(DietaryTotalAdded)?$|Sugars|CHOLESTEROL", nutr_row_idxs)
        logger.debug(f"outlier_idxs: {outlier_idxs}")

        for idx, i in enumerate(nutr_row_idxs):
            ilist = [i]
            ilist.extend([n for n in gram_idxs if n in range(i-2, i+3)])
            ilist.extend([n for n in outlier_idxs if n in range(i-2, i+3)])
            if len(ilist) > 1:
                ilist.sort()
                nutr_row_idxs[idx] = [ilist[0], ilist[-1]]

        return nutr_row_idxs


    # @wrap(writelog, writelog)
    def set_column_header(self):
        """Set colnames using colnames_from_config() or autoname_cols().
        Rename columns using colnames_from_config() if args are
        manually set in scraper_conf['col_setter'].
        If no args are set for the franchise, make a best guess at
        column names with autoname_cols().
        """
        # identify header column equivalents, if there are any
        headers = find_rows_with_val(self.nutr_df, self.cleaner_conf['header_match'],\
                flags=re.IGNORECASE)
        # if "col_setter" value exists, use it to manually set colnames
        try:
            colvals = {"0":"item_name", "1":"menu_section"}
            rename_args = self.scraper_conf["col_setter"]
            if type(rename_args) is list:
                self.colnames_from_config(name_list=rename_args)
            elif type(rename_args) is dict:
                self.colnames_from_config(**rename_args)
            self.nutr_df = self.nutr_df.rename(columns=colvals)
        # if "col_setter" doesn't exist, use "headers" rows to set values
        except Exception as e:
            logger.debug("{}; autosetting columns".format(e))
            self.nutr_df = self.autoname_cols(self.nutr_df, headers)
        # delete headers rows from self.nutri_df
        self.nutr_df = self.nutr_df.loc[~self.nutr_df.index.isin(headers.\
                        index)]
        # standardize header column names
        for col in ["menu_section","serving_size_unit","rowtype","notes"]:
            if col not in self.nutr_df:
                self.nutr_df[col] = ""
        self.nutr_df = self.standardize_col_names(self.nutr_df)
        self.order_col_names()


    @wrap(writelog, writelog)
    def detect_and_remove_allergy_cols(self):
        """
        If a dataframe has more than 19 columns, search for "allergy"
        label. If "allergy" label found in a given column, delete that
        column and all columns after it.
        """
        potential_drop = ['egg', 'milk', 'soy', 'wheat', 'fish', 'tree nut',
                    'tree nuts', 'peanut','peanuts', 'shellfish','allergen',
                    'added_sugar']
        dropcols = [x for x in potential_drop if x in self.nutr_df.columns]
        logger.info(f"dropcols:{dropcols}")
        self.nutr_df.drop(columns=dropcols, inplace=True)


    # @wrap(writelog, writelog)
    def colnames_from_config(self, m_s=0, serving=0, fat_cal=1,
    potassium=0, switch_sodium_carb=False, name_list=None):
        """ Rename columns based on manually set parameters.
        Parameters:
        ----------
        nutr_df: dataframe
        m_s: int, optional, defaults to 0
            Index of menu_section column. '0' means no column will be relabeled
            as menu_section. col must come before all nutrition columns.
        serving: int, optional, defaults to 0
            Index of column containing serving_size value. Set to 0 if no
            serving_size column is present.
        fat_cal: int, optional, defaults to 1
            If a fat_calories column is present, set to 1; set to 0 if not.
        potassium: int, optional, defaults to 0
            If a potassium column is present, set value to 1.
        switch_sodium_carb: boolean, optional, defaults to False
            If carbohydrates column comes before sodium column, set to True.
        name_list: list
            An alternative approach. Simply list the names of all columns in order.
        """
        if name_list != None:
            col_names = dict(enumerate(name_list))
            col_names = {str(k):v for k, v in col_names.items()}
        else:
            six_seven = ["sodium", "carbohydrates"] if switch_sodium_carb == \
                    False else ["carbohydrates", "sodium"]
            col_names = {
            "{}".format(str(1+m_s+serving)):"calories",
            "{}".format(str(2+m_s+fat_cal+serving)):"fat",
            "{}".format(str(3+m_s+fat_cal+serving)):"saturated_fat",
            "{}".format(str(4+m_s+fat_cal+serving)):"trans_fat",
            "{}".format(str(5+m_s+fat_cal+serving)):"cholesterol",
            "{}".format(str(6+m_s+fat_cal+serving)):six_seven[0],
            "{}".format(str(7+m_s+fat_cal+serving+potassium)):six_seven[1],
            "{}".format(str(8+m_s+fat_cal+serving+potassium)):"dietary_fiber",
            "{}".format(str(9+m_s+fat_cal+serving+potassium)):"sugar",
            "{}".format(str(10+m_s+fat_cal+serving+potassium)):"protein"
            }
            if potassium == 1:
                col_names["{}".format(str(7+m_s+fat_cal+serving))] = "potassium"
            if serving > 0:
                col_names["{}".format(str(0+m_s+serving))] = "serving_size"
            logger.debug(f"colnames_from_config rename dict:{col_names}")
        self.nutr_df = self.nutr_df.rename(columns=col_names)


    @wrap(writelog, writelog)
    def autoname_cols(self, df, nutr_rows):
        """ Automatically set df column names using nutr_rows subset.
        Set first nutr_rows row as header, then format as lowercase and
        strip stray spaces.

        Parameters
        ----------
        df : pandas DataFrame
        nutr_rows :

        Returns
        -------
        df : pandas DataFrame
        """
        logger.debug("nutrirows:{}".format(nutr_rows))
        ### TO DO!!!: fix the occasional occurrence of row names lumping
        ### into the same column, as with franchise 101
        try:
            dict = {"  +|\\n|\n":" "}
            for k, v in dict.items():
                hedit = lambda x: x.str.replace(k, v, regex=True)
                nutr_rows = nutr_rows.apply(hedit, axis=1)
            col_dict = nutr_rows.to_dict('records')[0]
            col_dict = {k:v.lower().strip(" *‡") for k, v in col_dict.items() if v != ""}
            col_dict['0'] = "item_name"
            logger.debug("calorie_cols:\n{}".format(col_dict))
            df.rename(columns=col_dict, inplace=True)

        except Exception as e:
            logger.warning("method failed. Error:\n{}\nhead:\n{}".\
                    format(e, self.nutr_df.head(10)), exc_info=True)
        return df

    @wrap(writelog, writelog)
    def order_col_names(self):
        sc = ["item_name","menu_section","serving_size","serving_size_unit"]
        sc.extend(self.nutr_columns)
        sc.extend(["serving_size_household","notes","rowtype"])

        # make list of colnames that aren't part of the standard set
        col_list = self.nutr_df.columns.values.tolist()
        diff_list = list(set(col_list) - set(sc))
        # append diff_list to end of standard_cols
        sc.extend(diff_list)
        self.nutr_df = self.nutr_df[sc]


    def id_rowtypes(self):
        """Identify and assign rowtype values.
        """
        # straightforward identification
        # 1. id cats
        catstest = self.nutr_df.drop(columns=["serving_size_unit","menu_section"])
        cats = return_rows_with_one_value(catstest)
        self.nutr_df.loc[self.nutr_df.index.isin(cats.\
                    index), "rowtype"] += "cat "
        # 2. id notes


    def return_rowtype(self, df, string, rex=False, nun=False):
        return df.loc[df['rowtype'].str.contains(string, regex=rex, na=nun)]


    # @wrap(writelog, writelog)
    def remove_rows_by_content(self):
        """ Remove empty rows and rows with unneeded data.
        """

        self.remove_cater_rows()
        last_item = self.id_last_item_row()
        self.nutr_df.loc[self.nutr_df.index == last_item, "rowtype"] += "last_itemrow "
        # remove all lines with no calorie data after the last line with calorie data
        e_row = self.return_rowtype(self.nutr_df, "last_itemrow")
        logger.debug("e_row:{}".format(e_row))
        if len(self.nutr_df.iloc[e_row.index[0]:]) > 1:
            self.nutr_df.drop(self.nutr_df.index[e_row.index[-1] + 1:],\
                inplace=True)
        for s in self.cleaner_conf['single_junkrows']:
            self.nutr_df = remove_rows_with_val(self.nutr_df, s, rex=False)
        self.nutr_df = remove_rows_with_val(self.nutr_df, \
                self.cleaner_conf['single_junkrows_re'])
        self.nutr_df.drop_duplicates(inplace=True)
        self.nutr_df.reset_index(drop=True, inplace=True)


    def id_last_item_row(self):
        kargs = {"regex":True, "na":False}
        e = self.nutr_df.loc[(self.nutr_df["calories"].astype("string").str\
                            .contains("\d+", **kargs)) & (
                            self.nutr_df["total_fat"].astype("string").str\
                            .contains("\d+", **kargs))]
        logger.debug("e:{}\ne.tail:{}".format(e, e.tail(1)))
        li = e.tail(1).index[0]
        return li


    @wrap(writelog, writelog)
    def split_headers_cats(self, df, headercats):
        """return dataframe with header and menu_section in different rows

        Parameters
        ----------
        df : dataframe
            Dataframe in which to split headers and categories.
        headercats : dataframe
            df slice containing rows which contain both headers and categories
        """
        logger.debug("headers_cats:\n{}".format(headercats))
        # make new rows with just the value of the first column
        cat_rows = headercats[['0']].copy()
        cat_rows.index = cat_rows.index + .6
        logger.debug("cat_rows\n{}".format(cat_rows))
        cat_rows.rename(columns={"0":"iname"}, inplace=True)
        new_df = pandas.concat([df, cat_rows], axis=1)
        new_df.index = new_df.index.astype(float)
        new_df.sort_index(inplace=True)
        df = new_df.reset_index(drop=True)
        df.fillna("", inplace=True)
        logger.debug("dfcheck\n{}\n{}".format(df.head(), df.columns.values))
        df['0'] = df['0'] + df['iname']
        df.drop(columns="iname", inplace=True)
        return df


    @wrap(writelog, writelog)
    def reassign_rows(self):
        # make all rows with rowtype "cats" into columns for those below
        # logger.debug("TRYING 0: self.nutr_df:\n{}".format(self.nutr_df['item_name']))
        cats = self.return_rowtype(self.nutr_df,"cat")
        logger.debug("cat_headers:\n{}".format(cats))
        if self.in_operations("add_name_to_sizes"):
            self.add_name_to_sizes(cats)
            condition = self.nutr_df.index.isin(cats.index)
            self.nutr_df.loc[~condition, 'item_description'] = self.\
                            nutr_df['item_name'] + self.nutr_df['notes']
            cats = self.return_rowtype(self.nutr_df,"cat")
        if cats.empty:
            pass
        else:
            self.nutr_df = align_vals(self.nutr_df, cats)
            truecats = cats.loc[~cats['rowtype'].str.contains("namecat")]
            self.nutr_df = self.add_section_labels(self.nutr_df, cats.index\
                    .tolist(), "menu_section", [0], separator=", ",\
                    to_labels=truecats.index.tolist(), src_col="item_name")
            self.nutr_df = self.nutr_df.drop(cats.index)


    @wrap(writelog, writelog)
    def add_name_to_sizes(self, cats, separate_notes=True, n=None):
        """Add item_name of 'names' rows to item_names below.
        """
        if type(n) == type(None):
            n = ((self.nutr_df['total_fat']=="") & ~(self.\
                    nutr_df["item_name"].str.isupper()))
        # self.nutr_df.loc[n, "rowtype"] += "superitem "
        self.nutr_df.loc[n, "rowtype"] += "namecat "
        names = self.nutr_df.loc[n]
        logger.debug("name rows:\n{}".format(names))
        names_and_cats = self.nutr_df.loc[(self.nutr_df.index.isin(names.\
                    index))|(self.nutr_df.index.isin(cats.index))]

        self.nutr_df = align_vals(self.nutr_df, names)
        self.nutr_df = self.add_section_labels(self.nutr_df,\
                names_and_cats.index, "item_name", [0], to_labels=names.\
                index.tolist(), separator=", ")
        self.nutr_df = self.nutr_df.drop(names.index).reset_index(drop=True)


    def add_section_labels(self, df, sect_starts, target_col,\
        src_row_idx, to_labels=None, src_col=None, separator=" "):
        """Add value from one cell to all columns in a given section of rows
        Parameters
        ----------
        df : DataFrame (default: None)
            The dataframe upon which the operation is performed. Will use \
            self.nutr_df if no value is specified.
        sect_starts : list
            indexes marking the beginnings of sections. The ends of
            sections are calculated by subtracting 1 from the next highest
            sect_start value.
        target_col : int or string
            name of the column into which values will be inserted.
        src_row_idx : list of ints
            What number to add to the sect_start row indexes to get the
            source row value.
        to_labels : list of ints, optional (default None)
            assign labels to subset of sections with key vals in this list.
        src_col : int or string, optional (default None)
            name of the column from which values will be taken. If None,
            target_col value will be used.
        separator : string, optional (default " ")
            join value to place between source cell values.

        Returns
        -------
        df : DataFrame
        """
        logger.debug("add_section_labels start df head:\n{}".format(df.head(15)))
        sections = create_sections(df, sect_starts)
        if to_labels != None:
            sections = {k:v for k, v in sections.items() if k in to_labels}
        src_col = target_col if src_col == None else src_col
        logger.debug("add_section_labels mid df:\n{}".format(df))
        for k, v in sections.items():
            labels = [str(df.loc[k + r][src_col]) for r in src_row_idx]
            label = separator.join([l for l in labels])
            df.loc[k:v, target_col] += separator + label
            df.loc[k:v, target_col] = df.loc[k:v][target_col].str.strip(", ")
        logger.debug("add_section_labels END df head:\n{}".format(df))
        return df


    # @wrap(writelog, writelog)
    def add_notes_to_categories(self):
        """
        Identify menu_section attached to "notes" values, then assign
        item_names to all "notes" columns of rows with the same "menu_section" value.
        """
        notes = self.return_rowtype(self.nutr_df, "notes")
        logger.debug(f"notes:\n{notes}")
        notedict = pandas.Series(notes.item_name.values, index=notes\
                .menu_section.values).to_dict()
        logger.debug("notesdict: {}".format(notedict))
        self.nutr_df['notes'] = self.nutr_df.menu_section.map(notedict)

    @wrap(writelog, writelog)
    def detect_and_split_multisize_rows(self):
        """
        Find rows that display multiple sizes for one item in the
        same row by separating the values with a "/" and split each row
        into multiple rows.

        """
        tester_df = self.nutr_df.replace("", np.nan, regex=False)
        tester_df = tester_df.drop(columns=["rowtype"])
        split_rows = self.detect_multisize_rows(self.nutr_df)
        self.nutr_df = self.nutr_df.fillna("")
        logger.info(f"rows to split:\n{split_rows}")
        if not split_rows.empty:
            logger.info(f"rows to split:\n{split_rows}")
            split_row_idxs = split_rows.index.tolist()
            self.nutr_df = self.split_df_items(self.nutr_df, split_row_idxs)


    def detect_multisize_rows(self, df, name_split=True):
        """
        ID rows suiting the following criteria as multisize rows:
        - has at least 7 non-na fields (avoids false positives from lines
            with dates or without nutrition information)
        - ratio of total "/"s in row to non-na fields is at least 3:4
        - 'item_name' column has a "/" character in it (if not present,
            presumes that the flagged row uses "/" to denote a range)

        Parameters
        ----------
        df : DataFrame
        name_split : boolean opt, default True
            If true, make presence of a "/" in the name a condition for
            recognizing a multisize row.

        Returns
        -------
        split_rows : DataFrame
        """
        multisize_rows = count_occurrences_in_rows(df, "/")
        # detect rows by number of "/" in non-na columns for each
        # row. If count >= 75% non-na columns, do split_rows.
        if "rowtype" in multisize_rows.columns:
            multisize_rows = multisize_rows.drop(columns="rowtype")
        multisize_rows = multisize_rows.loc[multisize_rows['count'] != 0]
        multisize_rows['non_na'] = multisize_rows.replace("", np.nan).count(axis=1)
        multisize_rows['occurrence'] = multisize_rows['count'] / multisize_rows['non_na']

        occ_over_75pc = (multisize_rows['occurrence'] > .75)
        non_na_over_6ct = (multisize_rows['non_na'] > 6)
        logger.debug(f"multisize_rows:\n{multisize_rows}")
        if name_split == True:
            name_split = (multisize_rows['item_name'].str.contains("/"))
            split_rows = multisize_rows.loc[occ_over_75pc & non_na_over_6ct & name_split]
        else:
            split_rows = multisize_rows.loc[occ_over_75pc & non_na_over_6ct]
        return split_rows


    @wrap(writelog, writelog)
    def split_df_items(self, df, split_row_idxs, sizelist=None):
        """

        Parameters
        ----------
        df : DataFrame
            df item_name col must be named item_name.
        split_rows : DataFrame
            slice of df containing the rows

        Returns
        -------
        df : DataFrame
        """
        rows_to_split = df.loc[df.index.isin(split_row_idxs)]
        new_df = df.copy()
        for index, row in rows_to_split.iterrows():
            if sizelist == None:
                sizes = self.return_size_list(row)
            else:
                sizes = sizelist
            subdf = self.split_items_in_subdf(index, row, sizes)
            logger.info(f"subdf split:\n{subdf}")
            new_df = new_df.drop(index)
            new_df = pandas.concat([new_df, subdf])
            new_df.index = new_df.index.astype(float)
            logger.info(f"new_df split:\n{new_df}")
            new_df = new_df.sort_index()
        df = new_df.reset_index(drop=True)
        logger.info(f"df product:\n{df.head(50)}")
        return df


    def return_size_list(self, row):
        """Identify list of sizes in self.nutr_df['0'].
        """
        size_str = r'\(?(\w+\s?\/\s?\w+(\/\s?\w+)?(\/\s?\w+)?)\)?'
        m = re.search(size_str, row['item_name'])
        sizes = m.group(1).split("/") if m else None
        return sizes



    def split_items_in_subdf(self, index, row, sizes):
        subdf = pandas.DataFrame()
        val_list = [v for v in row if str(v).lower() != "nan" and v != ""]
        sizecount = most_frequent([v.count('/') +1 for v in val_list])
        for k, v in row.items():
            if k == "item_name":
                for s in sizes:
                    v = v.replace(s, "")
                sv = [v.strip(" -,()/")] * sizecount
            elif str(v).lower() != "nan":
                sv = v.split("/") if "/" in v else [v] * sizecount
            for i, v in enumerate(sv):
                subdf.loc[index + i/10, k] = v
            for i, size in enumerate(sizes):
                subdf.loc[index + i/10, "size"] = size
        subdf["item_name"] += ", " + subdf["size"]
        subdf.drop(columns=["size"], inplace=True)
        logger.debug(f"split_items_in_subdf product:\n{subdf}")
        return subdf


    def move_notes(self):
        for match in self.cleaner_conf['note_matches']:
            m_string = match
            logger.debug(f"m_string:{m_string}")
            lv = lambda x: Pdf.separate_value_and_note(x, m_string)
            for c in ["item_name", "menu_section"]:
                self.nutr_df["notes"] += ", " + self.nutr_df[c].apply(lv)
                self.nutr_df["notes"] = self.nutr_df["notes"].str.strip(" ,")
                self.nutr_df[c] = strip_col_from_col(self.nutr_df, c,\
                        'notes')

    def separate_value_and_note(value, m_string):
        m = re.search(m_string, str(value))
        notes =  m['notes'] if m else ""
        if m:
            logger.debug(f"separate_value_and_notes:  {notes}")
        return notes

    def recombine_cell(self, df, indexes, col):
        """
        For row w/ index in indexes, append next row's colval to each col.
        """
        df.fillna("", inplace=True)
        for i in indexes:
            df.loc[df.index == i, col] += " " + df.loc[i + 1][col]
            df.loc[df.index - 1 == i, col] = df.loc[i][col]
        logger.debug("recombine_cell\n{}".format(df))
        return df


class SiteNav(Scraper):
    """

    Attributes
    ----------
    cleaner_conf: dict
    csv_file : string
    driver: object
        The driver controlling the running selenium session

    Methods
    -------
    produce_nutr_df()
    capture_webpage_urls()
    capture_nutrition()
    collect_nutrition(row)
    nav_sizes_customizations(df, row)
    loop_customizations(row, df, cust_opts)
    extract_table_nutrition(item_row, table_nav_css)
    remove_wrong_menu_cats()
    create_cat_dict()
    catch_nested_cats()
    click_page_for_link(item, driver)
    return_item_name(item)
    make_corrections()
    """

    def __init__(self, name, f_id, nutr_url, driver, **kwargs):
        self.driver = driver
        self.cleaner_conf = config["cleaners"]["web_cleaners"]
        super().__init__(name, f_id, nutr_url, **kwargs)
        self.csv_file += "webpage_scrapes/{}.csv".format(f_id)
        logger.info("sitenav nutr_df:\n{}".format(self.nutr_df))


    def produce_nutr_df(self):
        self.capture_webpage_urls()
        self.capture_nutrition()


    def capture_webpage_urls(self):
        """ Scrape item urls; open each page, collect nutrition data in df.
        1. if self has no cat_urls, run function to retrieve them
        2. make df of item page urls
        """
        self.driver.get(self.nutr_url)
        if not hasattr(self, "cat_dict"):
            self.create_cat_dict()
            self.remove_wrong_menu_cats()
        self.nutr_df = self.website_to_df()


    def capture_nutrition(self):
        """ Choose correct scraper for item nutrition; add data to nutr_df.
        """
        df = pandas.DataFrame()
        for index, row in self.nutr_df.iterrows():
            self.driver.get(row['iurl'])
            if "sizes_customizations" in self.vars:
                df = self.nav_sizes_customizations(df, row)
                logger.debug("QUICKCHECK df:\n{}".format(df))
            else:
                new_row = self.collect_nutrition(row)
                df = df.append(new_row)
        self.nutr_df = df


    def collect_nutrition(self, row):
        new_row = self.extract_table_nutrition(row, self.table_nav_css)
        if self.nfacts_method == "table":
            if "two_part_table" in self.vars:
                row_addition = self.extract_table_nutrition(row, self.table_nav_css_2)
                new_row += row_addition
        elif self.nfacts_method == "table_with_extra":
            for key, value in self.other_nfacts.items():
                new_row[key] = self.driver.find_element_by_css_selector(\
                        value).get_attribute('innerHTML')
        logger.debug("new_row: {}".format(new_row))
        return new_row


    def nav_sizes_customizations(self, df, row):
        """
        Scan page for size and customization links; collect data if present.
        """
        logger.debug("START:{}".format(row['item_name']))
        to_collect = []
        try:
            time.sleep(2)
            size_div = self.driver.find_element_by_css_selector(self.size_nav[0])
            logger.debug("innerHTML:\n{}".format(size_div.get_attribute("innerHTML")))
            size_opts = size_div.find_elements_by_css_selector(self.size_nav[1])
            to_collect.append("size")
        except Exception as e:
            logger.debug("size collection Exception: {}".format(e))
        try:
            cust_div = self.driver.find_element_by_css_selector(self.cust_nav[0])
            cust_opts = cust_div.find_elements_by_css_selector(self.cust_nav[1])
            to_collect.append("customization")
        except Exception as e:
            logger.info("customization collection Exception: {}".format(e))

        if "size" in to_collect:
            logger.debug("COLLECTING SIZE")
            if self.size_nav[2] == "switcher":
                for option in reversed(size_opts):
                    time.sleep(1)
                    self.click_and_wait(option, 1, script=True)
                    new_row = self.collect_nutrition(row.copy(deep=True))
                    new_row["item_name"] += ", {}".format(option.\
                            get_attribute('innerHTML').strip())
                    df = df.append(new_row)
                    logger.debug("COLLECTING SIZE ROW: {}".format(new_row))
        if "customization" in to_collect:
            if self.cust_nav[2] == "switcher":
                df = self.loop_customizations(row, df, cust_opts)
                for option in cust_opts:
                    time.sleep(1)
                    self.click_and_wait(option, 2, script=True)
                    df = self.loop_customizations(row, df, cust_opts)
        if not to_collect:
            logger.debug("NOTHING FOUND")
            new_row = self.collect_nutrition(row)
            df = df.append(new_row)

        logger.debug("END df:\n{}".format(df))
        return df


    def loop_customizations(self, row, df, cust_opts):
        new_row = self.collect_nutrition(row.copy(deep=True))
        new_row["item_name"] += " w/"
        options = []
        for option in cust_opts:
            active = option.get_attribute("class")
            if active == "active":
                options.append(option.get_attribute('innerHTML'))
            else:
                pass
        if options:
            opt_string = ', '.join(options)
            new_row["item_name"] += opt_string
        new_row["item_name"] = re.sub(r' (w\/|&)$','', new_row["item_name"])
        logger.debug("new_row:{}".format(new_row))
        df = df.append(new_row)
        return df


    def extract_table_nutrition(self, item_row, table_nav_css):
        """ Open menu_item url, collect nutrition data from table area.
        """
        # open the item page
        try:
            if "click_for_item_nutrition" in self.vars:
                self.driver.find_elements_by_link_text(self.nfacts_click).click()
            table = self.driver.find_element_by_css_selector(table_nav_css[0]).get_attribute('innerHTML')
            soup = BeautifulSoup(table, 'html.parser')
            keys = [re.sub(r"\(\d{1,}% Daily Value\)", "", item.text.\
                    strip()) for item in soup.select(table_nav_css[1])]
            vals = [i.text.strip() for i in soup.select(table_nav_css[2])]
        #     keys =[i.text for i in table_soup.find_all('tr').find('td', {'class':'nutrient-key'})]
        #     vals = [i.text for i in table_soup.find_all('tr').find('td', {'class':'nutrient-value'})]
            nutr_dict = dict(zip(keys, vals))
            logger.info("nutr_dict: {}".format(nutr_dict))
            rm_sp = lambda x: re.sub(r'(\s|\\t){2,}', ' ', x)
            nutr_dict = {rm_sp(k):rm_sp(v) for k, v in nutr_dict.items()}
            for k, v in nutr_dict.items():
                item_row[k] = v
            logger.info("final row:{}".format(item_row))
            if len(nutr_dict) == 0:
                raise ValueError('Empty nutrition_dict')
        except NoSuchElementException:
            to_error_csv(item_row['item_name'],item_row['iurl'], "can't locate nutrition table (NoSuchElementException)")
            item_row = None
        except ValueError:
            to_error_csv(item_row['item_name'],item_row['iurl'], "can't locate nutrition table (ValueError)")
            item_row = None
        return item_row


    def remove_wrong_menu_cats(self):
        """ Remove unwanted menu sections, e.g. catering or grocery.
        """
        logger.debug("cat_dict:\n{}".format(self.cat_dict))
        self.cat_dict = {k:v for k,v in self.cat_dict.items() if not re.match(self.cleaner_conf['bad_cat_names'], k)}
        # remove specific categories from various franchises
        self.cat_dict = {k:v for k, v in self.cat_dict.items() if not re.\
        match(self.cleaner_conf['bad_cat_urls'], v)}


    def create_cat_dict(self):
        """Produce dict of category names and urls from scraped webpage.
        """
        # cat_menu is the section of the webpage that contains all sub-menus
        logger.info("self.__dict__ = {}".format(self.__dict__))
        cat_menu = self.driver.find_element_by_css_selector(self.cat_menu_css)
        # categories are the divs that contain name & url of each category
        cats = cat_menu.find_elements_by_css_selector(self.categories_css)
        self.cat_dict = {}
        for category in cats:
            cat_name = category.find_element_by_css_selector(self.\
                    cat_name_css).get_attribute('innerHTML')
            cat_name = cat_name.strip("\n\t ")
            try:
                cat_url = category.find_element_by_css_selector("a").\
                    get_attribute('href')
                if cat_url is None:
                    raise TypeError("Empty String; error with cat_url")
            except TypeError:
                cat_url = category.get_attribute('href')
                logger.info("cat_url: {}".format(cat_url))
            except NoSuchElementException:
                cat_url = category.get_attribute('href')
            self.cat_dict[html.unescape(cat_name)] = cat_url
            logger.info("self.cat_dict:{}".format(self.cat_dict))
        if "subcats" in self.vars:
            logger.info("subcats somewhere...")
            self.cat_dict = self.catch_nested_cats()
            logger.info("postmethod self.cat_dict:{}".format(self.cat_dict))


    def catch_nested_cats(self):
        """ Identify pages consisting of links to subcategory pages.
        Prompted by Culver's.
        """
        new_cats = {}
        for cat, url in self.cat_dict.items():
            logger.info("cat: {}".format(cat))
            self.driver.get(url)
            try:
                subcat_div = self.driver\
                        .find_element_by_css_selector(self.cat_menu_css)
                subcats = subcat_div\
                        .find_elements_by_css_selector(self.categories_css)
                for subcat in subcats:
                    subcat_name = "{}:{}".format(cat, subcat\
                        .find_element_by_css_selector(self.cat_name_css)\
                        .get_attribute('innerHTML'))
                    subcat_url = subcat.find_element_by_tag_name("a")\
                        .get_attribute('href')
                    new_cats[subcat_name] = subcat_url
            except NoSuchElementException:
                new_cats[cat] = url
        logger.info("new cat_dict: {}".format(new_cats))
        self.cat_dict = new_cats


    def click_page_for_link(self, item, driver):
        """ Collect item urls by navigating to item page.
        Click on item link, collect page url, and navigate back to menu
        page. Useful when webpage urls aren't available as href values.
        """
        item.find_element_by_css_selector(self.iurl_css).click()
        iurl = driver.current_url
        driver.back()
        return iurl


    def return_item_name(self, item):
        """ Return menu item name from website menu.
        """
        try:
            item_name = item.find_element_by_css_selector(self.item_name_css)
            item_name_text = item_name.text
            if item_name_text == "":
                raise TypeError("Empty String")
        except TypeError as e:
            logger.info("TypeError:{}".format(e))
            item_name = item.find_element_by_css_selector(self.item_name_css).get_attribute('innerHTML')
        except AttributeError as e:
            logger.info("AttributeError:{}".format(e))
            item_name_text = item.find_element_by_css_selector(self.item_name_alt_css).get_attribute('innerHTML')
            logger.info("alt_itemname:{}".format(item_name_text))
        item_name_text_prepared = html.unescape(item_name_text)
        return item_name_text_prepared


    def make_corrections(self):
        if self.f_id == 55:
            cols_to_clean = {'carbohydrates':"Total Carbs", "total_fat":"Total Fat"}

            for k, v in cols_to_clean.items():
                cols = self.nutr_df[self.nutr_df.columns[self.nutr_df.\
                        columns.to_series().str.contains(v)]]
                subset = self.nutr_df.loc[: , cols.columns.values.tolist()]
                self.nutr_df.insert(2, k, None)
                self.nutr_df = align_vals(self.nutr_df, subset, cols=list(subset.columns.values))
                self.nutr_df.drop(columns=list(subset.columns.values), inplace=True)

            # self.nutr_df.insert(0, 'total_fat', None)
            # fat_cols = self.nutr_df.loc[self.nutr_df.columns[self.\
            #     nutr_df.columns.to_series().str.contains('Total Fat')]]
            # align_vals(self.nutr_df, fat_cols)

            # df[df.columns[df.columns.to_series().str.contains('Total Fat')]]
        super().make_corrections()


class MultiPdf(Pdf):
    """
    Collect from a webpage source that has links to multiple pdfs.

    prep_unaligned_table() - not called on object. Used in
        concatenate_pdf_dfs method for pdfs where number of recognized
        columns might vary from table to table. Ensures
        that columns are properly aligned before concatenation.
    """

    def __init__(self, name, f_id, nutr_url, driver, **kwargs):
        self.driver = driver
        super().__init__(name, f_id, nutr_url, **kwargs)


    def produce_nutr_df(self):
        """
        1. go to mainpage
        2. collect pdf links in page
        3. run super.produce_nutr_df on all pages
        """
        self.driver.get(self.nutr_url)
        main = self.driver.find_element_by_css_selector('main')
        soup = BeautifulSoup(main.get_attribute("innerHTML"), 'html.parser')
        hrefs = soup.find_all('a')
        drop = ["Allergens", "Catering"]
        links = [h for h in hrefs if not any(s in h.text for s in drop)]
        urls = ["https:"+link['href'] for link in links]
        nest_tables = [self.dfs_from_pdf(url) for url in urls]
        tables_raw = [i for sublist in nest_tables for i in sublist]
        tables = self.prepare_tables(tables_raw)
        self.nutr_df = self.concatenate_pdf_dfs(tables)
        self.nutr_df.loc[0, 0] = ""
        self.nutr_df = self.nutr_df.replace(r'\\n','', regex=True)


    def prepare_tables(self, tables):
        return tables

    def prep_unaligned_table(self, df, serving_size=True):
        """
        Parameters
        ----------
        df : DataFrame
            dataframe
        serving_size :

        Returns
        -------
        final_dfs : list
            dataframes of pdf table information
        """
        df.fillna('', inplace=True)
        try:
            colnames = ["item_name","serving_size_add","serving_size",
            "calories","fat_cals","total_fat","saturated_fat","trans_fat",
            "cholesterol","sodium","carbohydrates","dietary_fiber","sugar",
            "protein"]
            if len(df.columns) < 14:
                del colnames[1]
            if len(df.columns) == 12:
                df.insert(1, "serving_size", "")
            rename_dict = dict(zip(df.columns.values.tolist(), colnames))
            df.rename(columns=rename_dict, inplace=True)
            if len(df.columns) == 14:
                df["serving_size_add"] += " " + df["serving_size"]
                df["serving_size"] = df["serving_size_add"]
                df.drop(columns="serving_size_add", inplace=True)
        except Exception as e:
            logger.warning("df not 12-14:{}\n{}".format(len(df.columns), df))
        return df



class WebSite(SiteNav):

    def __init__(self, name, f_id, nutr_url, driver, **kwargs):
        super().__init__(name, f_id, nutr_url, driver, **kwargs)


    def website_to_df(self):
        """
        """
        nutr_df = pandas.DataFrame(columns = ["franchise_id", "iurl",
                "menu_section", "item_name"])
        driver = self.driver
        logger.info("self.cat_dict: {}".format(self.cat_dict))
        for cat, url in self.cat_dict.items():
            logger.info("cat: {}, url: {}".format(cat, url))
            self.driver.get(url)
            time.sleep(2)
            # menu_div is the webpage div containing all menu item page urls
            menu_div = self.driver.find_element_by_css_selector(self.menu_div_css)
            # item_divs are the page elements containing both menu item names and their page urls.
            item_divs = menu_div.find_elements_by_css_selector(self.item_divs_css)
            logger.info("CATEGORY: {}".format(cat))
            for item in item_divs:
                time.sleep(1)
                try:
                    iurl = self.click_page_for_link(item, self.driver)\
                            if "click_page_for_link" in self.vars else \
                            item.find_element_by_css_selector(self.\
                            iurl_css).get_attribute('href')
                    item_name = self.return_item_name(item)
                    if "append_cat_to_name" in self.vars and cat != 'Fresh Fit Choices™':
                        item_name += " {}".format(cat.rstrip("se"))
                    nutr_df = nutr_df.append({  "iurl": iurl,
                                                "item_name": item_name,
                                                "menu_section": cat
                                            }, ignore_index=True)
                    nutr_df = nutr_df.drop_duplicates()
                    nutr_df['menu_section'] = nutr_df.groupby(['iurl','item_name'])\
                    ['menu_section'].transform(lambda x: ','.join(x))
                    nutr_df = nutr_df.drop_duplicates()
                    nutr_df['franchise_id'] = self.f_id

                except Exception as e:
                    logger.warning("Exception for website item div collection: {}\nitem innerHTML:\n{}".format(e, item.get_attribute("innerHTML")), exc_info=True)
        return nutr_df


def webtable_to_df(nutr_url: str, type="default"):
    """Read html table into pandas dataframes.
    Parameters
    ----------
    nutr_url : str
        weburl of html nutrition table

    Returns
    -------
    page_dfs : list of dataframes
    """
    hdr = {'User-Agent': 'Mozilla/5.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    s = requests.Session()
    r = s.get(nutr_url, headers=hdr, timeout=15)
    html = r.content
    df = pandas.DataFrame()
    try:
        page_dfs = pandas.read_html(html)
    except ValueError:
        try:
            r = s.get(nutr_url, headers=hdr, timeout=15)
            html = r.content
            page_dfs = pandas.read_html(html)
        except ValueError:
            page_dfs = interpret_div_table(nutr_url, html)
    return page_dfs


def interpret_div_table(nutr_url: str, hdr, html):
    """Produce dataframe from html table that doesn't use table/tr/td markup

    Parameters
    ----------
    nutr_url : str
        weburl of html nutrition table
    hdr : bool, default False
        If true, don't replace NaNs with empty strings before returning.

    Returns
    -------
    [df] : list containing a dataframe
    """
    # r = requests.Session().get(nutr_url, headers=hdr)
    # html = r.content
    df = pandas.DataFrame(columns=["item_name", "menu_section"])
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find(id="nutrion-results")
    items = table.findAll('div', class_="nutrition-item")
    for i in items:
        cat_div = i.find(class_="td name").find("span")
        cat = cat_div['data-category']
        iname = i.find(class_="td name").get_text().strip()
        itemrow = {"item_name": iname, "menu_section": cat}
        nutrients = i.findAll('div', class_="td")
        logger.debug("itemrow\n{}".format(itemrow))
        for n in nutrients:
            n.span.clear()
            nval = n.get_text().strip()
            logger.debug("nutrient:\n{}\nnval:{}".format(n, nval))
            nkey = n["class"][1]
            itemrow[nkey] = nval
            nkey = n['class']
        df = df.append(itemrow, ignore_index = True)
        logger.debug("df\n{}".format(df))
    return [df]


def create_sections(df, idxs):
    """
    Produce start & end indices of sections from dataframe and indexes.

    Parameters
    ----------
    df : dataframe
        Dataframe.
    idxs : dataframe index
        Selection of indexes from the given dataframe.
        example: df.loc[section_header_identifier_condition].index

    Returns
    -------
    sections : dict
        Key-value pairs representing df section start and end indices.
    """
    last_row = df.tail(1)
    last_idx = last_row.index.values[0]

    section_ends = list(idxs)
    section_ends.sort()

    sections = {n: last_idx if n == idxs[-1] else next(x for x in section_ends if x > n) - 1 for n in idxs}
    return sections


def del_colnames_from_colvals(nutr_df):
    cols = [re.escape(val) for val in nutr_df.columns.values]
    arr = sorted(cols, reverse=True, key=len)
    nutr_df = nutr_df.replace(to_replace=arr, value="", regex=True)
    return nutr_df
