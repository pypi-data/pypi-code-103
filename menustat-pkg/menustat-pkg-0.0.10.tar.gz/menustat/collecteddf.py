import re
import string
import subprocess

import yaml
import pandas
from rapidfuzz import fuzz, process
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from menustat.log import *
from menustat.utils import *
# add_meta, loop_string_replace, return_range,
from menustat.orm import Base, MenuItem, AnnualItemData, return_largest_id_plusone
from menustat.settings import YEAR, ANALYST, engine, session, config


class CollectedDf():
    """Class for dataframes of collected data to prepare for db entry.

    Attributes
    ----------
    name: string
        Franchise's name, collected from database.
    nutr_url: string
        Franchise's nutr_url, collected from database.
    nutr_df: pandas dataframe
        Dataframe of scraped menu data.
    year: int
        Year of data collection.

    Methods
    -------
    add_df_to_db() - Creates AnnualItemData ORM objects from dataframe
        rows and inserts them into the database.
    """

    def __init__(self, name, f_id, nutr_df, **kwargs):
        self.name = name
        self.f_id = f_id
        self.nutr_df = nutr_df
        self.year = YEAR
        self.cleaner = config['cleaners']['gen_cleaners']
        self.__dict__.update(kwargs)
        self.nutr_columns = ['calories', "total_fat", "saturated_fat",
                "trans_fat", "cholesterol", "sodium", "potassium",
                "carbohydrates", "protein", "sugar", "dietary_fiber"]
        self.all_menu_items = session.query(MenuItem.id, MenuItem.item_name).\
                filter(MenuItem.franchise_id == self.f_id).all()
        self.all_annual_items = session.query(AnnualItemData.id,
                    AnnualItemData.menu_item_id,
                    AnnualItemData.year,
                    AnnualItemData.item_name,
                    AnnualItemData.calories,
                    AnnualItemData.protein,
                    AnnualItemData.total_fat,
                    AnnualItemData.carbohydrates).\
                join(MenuItem).\
                filter(MenuItem.franchise_id == self.f_id)
        logger.debug("{}".format(self.__dict__))
        logger.info("# items: {}".format(self.all_annual_items.count()))


    @wrap(writelog, writelog)
    def clean(self):
        # logger.debug("Clean: menu_section start:\n{}".format(self.nutr_df['menu_section']))
        self.nutr_df = self.nutr_df.dropna(how="all")
        self.nutr_df["item_name"] = self.nutr_df["item_name"].\
            apply(lambda x: self.clean_item_name(str(x)))
        if len(self.nutr_df[self.nutr_df["serving_size"] == '']) > 10:
            self.nutr_df["serving_size"] = self.nutr_df["item_name"].\
                apply(lambda x: self.name_to_serving(str(x)))
        logger.debug("autogenerate_description BEGIN:\n{}".format(self.nutr_df.head()))
        self.nutr_df['item_description'] = self.nutr_df.apply(lambda r: self.autogenerate_description(r), axis=1)

        self.nutr_df['item_name'] = self.nutr_df['item_name'].str.strip()
        self.combine_duplicate_rows()
        # self.pair_with_MenuItems()
        self.remove_unneeded_cols()
        self.standardize_df_contents()
        self.nutr_df['menu_item_id'] = self.nutr_df.apply(lambda x: self.\
                pair_with_menu_ids(x), axis=1)
        logger.debug("Clean: item_description end:\n{}".format(self.nutr_df.item_description))
        check_df_for_issues(self.name, self.nutr_df)


    def pair_with_menu_ids(self, aid_row,):
        """
        input: collected AID item (aid_row)
        1. Search db for AID entry using year, f_id, aid_row.item_name. If
        item found, return AID id and mi_id. If multiple items
        returned, flag issue.
        2. If no items returned, run self.return_MenuItem() to find correct
        menu_item and return mi_id of returned menu_item.
        """

        if aid_row.item_name == "":
            logger.warning("empty item_name string detected - ending "
                "return_MenuItem method")
            return
        aid_query = session.query(AnnualItemData).\
        join(MenuItem).\
        filter(AnnualItemData.item_name == aid_row.item_name).\
        filter(AnnualItemData.year == YEAR).\
        filter(MenuItem.franchise_id == self.f_id)
        try:
            matched_db_entry = aid_query.one()
        except MultipleResultsFound:
            logger.warning("WARNING: multiple matches for annual_item_"
            "data search:{}\nreturned items:".format(row['item_name']))
            matched_db_entries = aid_query.all()
            for e in matched_db_entries:
                logger.info("item:{} cals:{} carbs:{} add_date:{}".format(\
                e.item_name, e.calories, e.carbohydrates, e.created_at))
            mi_id = ",".join([e.id for e in matched_db_entries])
        except NoResultFound:
            logger.info("No AnnualItemData entry found.")
            mi_id = self.return_MenuItem(aid_row)
        else:
            mi_id = str(matched_db_entry.menu_item_id)
        return mi_id


    @wrap(writelog, writelog)
    def remove_unneeded_cols(self):
        standard_cols = ["item_name","menu_item_id","item_description",\
            "serving_size_household", "serving_size","serving_size_unit",
            "notes", "iurl"]
        standard_cols.extend(self.nutr_columns)
        logger.info("cols:{}".format(self.nutr_df.columns))
        not_in_df = [c for c in standard_cols if c not in self.nutr_df]
        logger.info("not_in_df:{}".format(not_in_df))
        for col in not_in_df:
            self.nutr_df[col] = ""
        self.nutr_df = self.nutr_df[standard_cols]


    def return_range_search_list(self, aid_item):
        logger.debug("return_range_search_list: {}".format(aid_item))
        ranges = {}
        for item in ["calories", "protein", "total_fat", "carbohydrates"]:
            val = getattr(aid_item, item, None)
            if val is not None:
                try:
                    ranges[item] = return_range(val)
                except TypeError:
                    pass
        logger.debug("return_range_search_list ranges: {}".format(ranges))
        return ranges


    def match_by_nutrition(self, row):
        """Return best-guess AID match using nutrition data and name.
        1. Try exact match for macronutrients, see if name is 75% match.
        2. If exact match fails, select best match from query of all
            franchise AID entries with ±5% macronutrient levels and >85%
            fuzzy match on name.
        3. If either match succeeds, return menu_item_id of AID match.
        """
        logger.debug("START: {}".format(row))
        returned_items = self.all_annual_items.filter(AnnualItemData.year < YEAR)
        try:
            returned_items = self.all_annual_items.\
                filter(AnnualItemData.calories == row.calories).\
                filter(AnnualItemData.protein == row.protein).\
                filter(AnnualItemData.total_fat == row.total_fat).\
                filter(AnnualItemData.carbohydrates == row.carbohydrates)
            logger.debug("returned_items1 query: {}".format(returned_items))
            if returned_items.count() == 0:
                raise ValueError('No returned_items for exact match')
        except Exception as e:
            logger.debug("{}; trying range match".format(e))
            # need light conditional for these - use if range exists, don't if not.
            range_dict = self.return_range_search_list(row)

            range_search_dict = {getattr(AnnualItemData, k):v for k, v in range_dict.items()}
            for k, v in range_search_dict.items():
                returned_items = returned_items.filter(k > v[0]).\
                        filter(k < v[1])
            logger.debug("returned_items query: {}".format(returned_items))

        logger.info("returned_items #: {}".format(returned_items.count()))
        if returned_items.count() == 1:
            aid_item = returned_items.one()
            plain_ratio = fuzz.ratio(row.item_name, aid_item.item_name)
            token_ratio = fuzz.token_set_ratio(row.item_name, aid_item.item_name)
            partial_ratio = fuzz.token_set_ratio(row.item_name, aid_item.item_name)
            if plain_ratio > 75 or token_ratio > 75:
                menu_item_id = aid_item.menu_item_id
                logger.debug("returned result:{}, {}, ratio={}, token_set_ratio={}".format(row.item_name, aid_item.item_name, plain_ratio, token_ratio))
            else:
                logger.debug("single result didn't pass 75%:{}, {}, ratio={}, token_set_ratio={}".format(row.item_name, aid_item.item_name, plain_ratio, token_ratio))
                menu_item_id = None
        elif returned_items.count() > 1:
            logger.info("too many returned items!")
            for item in returned_items.all():
                logger.info("{}, {}".format(item.id, item.item_name))
                item.menu_item_id = self.return_closest_match(item)
        elif returned_items.count() == 0:
            logger.info("no returned items!")
            menu_item_id = None
        logger.debug("END menu_item_id:{}".format(menu_item_id))
        return menu_item_id


    def clean_item_name(self, name):
        """Remove unneeded data from item name and restructure serving data.
        """
        logger.debug("preclean: {}".format(name))
        name = loop_string_replace(self.cleaner['nd_cleaner'], name, regex=False)
        name = loop_string_replace(self.cleaner['nd_cleaner_re'], name)
        count_re = re.search(r'\((\d+)\)$', name)
        if count_re:
            name = "{} {}".format(str(count_re.group(1)), name)
            name = name.replace(str(count_re.group(0)), "")
        count_counter_re = re.search(r' \((\d+ \w+)\)$', name)
        if count_counter_re:
            name = "{}, {}".format(name, str(count_counter_re.group(1)))
            name = name.replace(str(count_counter_re.group(0)), "")
        name = name.strip("+ ")
        logger.debug("cleaned: {}".format(name))
        return name


    def name_to_serving(self, name):
        """Place any serving_size values in item_name in serving_size field.
        """
        logger.debug(name)
        for pattern in self.cleaner["serving_in_name"]:
            count_re = re.search(pattern, name)
            if count_re:
                serving = str(count_re.group(1))
                break
        else:
            serving = None
        logger.debug(serving)
        return serving


    @wrap(writelog, writelog)
    def combine_duplicate_rows(self):
        """ If any rows have same nutrition facts and name, combine rows.
        1. ID all rows of same item
        2. ID the duplicates to appear second, add its menu_section to
        first row's menu_section.
        """
        colnames = ['item_name']
        colnames.extend(self.nutr_columns)
        logger.debug("platonic colnames: {}".format(colnames))
        dupecheck = self.nutr_df[self.nutr_df.duplicated(subset=colnames,
                                            keep=False)].fillna("")
        if not dupecheck.empty:
            dicta = {}
            # make dict of item_name: menu_section pairs
            for iname, msect in zip(self.nutr_df.item_name, self.nutr_df["menu_section"]):
                if iname not in dicta.keys():
                    dicta[iname] = [msect]
                else:
                    dicta[iname].append(msect)
            dictb = {key:", ".join(v for v in value) for key, value in dicta.items()}
            self.nutr_df['menu_section'] = self.nutr_df['item_name'].map(dictb)
            self.nutr_df.drop_duplicates(keep="first", inplace=True)
            # logger.debug(dupecheck.groupby(by=colnames)['menu_section'].apply(', '.join))
            # dupecheck.groupby(by=colnames).agg({'menu_section': ','.join, "index": list()})



    def add_df_to_db(self, dryrun=True):
        """ Insert df of AnnualItemData entries into database.
        1. Create AnnualItemData ORM objects from dataframe rows
        2. Search AnnualItemData entries w/ matching item_name, f_id, & year
        2A. If one entry returned, update entry.
        3. If multiple AnnualItemData entries returned, default to first.
        4. If existing AnnualItemData entry not found, search for
            accompanying MenuItem entry in the database.
        5. If MenuItem entry found, link new AnnualItemData object to it;
            if not, create new MenuItem entry.
        6. Insert new AnnualItemData objects into database.
        """
        new_id = return_largest_id_plusone(AnnualItemData, session)
        aid_objects = self.nutr_df.apply(lambda x: self.\
                produce_aid_object(x), axis=1)
        new_db_entries = aid_objects.tolist()
        if dryrun == True:
            pass
        else:
            session.add_all(new_db_entries)
            session.commit()


    def produce_aid_object(self, row):
        aid_args = {k:v for k, v in row.to_dict().items() if k != "iurl"}
        annual_item = AnnualItemData(**aid_args)
        # annual_item = add_meta(annual_item, created=False)
        annual_item.updated_by = ANALYST
        annual_item.updated_at = dt.datetime.now()
        return annual_item


    def return_MenuItem(self, annual_item):
        """ Return MenuItem match for AnnualItemData object.
        1. Attempt direct match using item name.
        2. If direct match returns multiple results, return closest match.
        3. If direct match returns no results, return match using
            match_by_nutrition method.
        4. If match_by_nutrition fails, use fuzzy string matching.
        5. If no match satisfying any prior conditions found, create a new
            Menu_Item object and insert it into the database.
        """
        item_name = f"{annual_item.item_name}"
        logger.info(f"namesearch: {item_name}")
        menu_item_query = session.query(MenuItem.id).\
                filter(MenuItem.item_name.ilike(f'{item_name}')).\
                filter(MenuItem.franchise_id == self.f_id)
        try:
            menu_item_id = menu_item_query.one()[0]
            logger.info(f"MenuItem match: {item_name}")
        except MultipleResultsFound:
            logger.info(f"ISSUE: multiple matches for: {annual_item.__dict__}")
            menu_item_id = self.fuzzy_match_menu_item(annual_item)
        except NoResultFound:
            logger.info(f"No exact match: {item_name}\nTrying match_by_nutrition")
            try:
                menu_item_id = self.match_by_nutrition(annual_item)
                if menu_item_id is None:
                    raise TypeError("no match found")
            except Exception as e:
                logger.info("match_by_nutrition fail\n{}".format(e))
                try:
                    logger.info("trying name-only fuzzy match")
                    menu_item_id = self.fuzzy_match_menu_item(annual_item)
                except TypeError as e:
                    logger.info("fuzzy match failed: {}".format(e))
                    menu_item_id = None
                except Exception as e:
                    logger.info(f"fuzzy match failed: {e}", exc_info=True)
                    logger.info("adding new Menu_Item entry")
                    menu_item_id = self.add_new_menuitem(annual_item)

        logger.info("menu_item_id:{}".format(menu_item_id))
        return menu_item_id


    def fuzzy_match_menu_item(self, annual_item, match_pct=91):
        """ Use fuzzy match to find MenuItem for new AnnualItemData entry.
        1. Create list of menu_item item_name values
        2. Return item_name values that match self.item_name at ≥ 91%
        3. Select first entry.
        """
        logger.info("fuzzy_match: {}".format(annual_item.item_name))
        # plain_ratio = fuzz.ratio(self.item_name, aid_item.item_name)
        # token_ratio = fuzz.token_set_ratio(self.item_name, aid_item.item_name)
        # partial_ratio = fuzz.token_set_ratio(self.item_name, aid_item.item_name)
        all_franchise_item_names = [i[1] for i in self.all_menu_items]
        returned = process.extractOne(annual_item.item_name,\
                all_franchise_item_names, score_cutoff=match_pct)
        if not returned:
            desc = f"{annual_item.item_name} {annual_item.item_description}"
            returned = process.extractOne(annual_item.item_description,\
                    all_franchise_item_names, score_cutoff=match_pct)
        logger.info("returned pair: {}::{}".format(annual_item.item_name,\
                returned))
        returned_id = [i[0] for i in self.all_menu_items if i[1] ==\
                returned[0]]
        menu_item_id = None if not returned_id else str(returned_id[0])
        logger.info("menu_item_id: {}".format(menu_item_id))
        return menu_item_id


    def add_new_menuitem(self, annual_item):
        logger.debug("START {}".format(annual_item))
        new_menu_items = []
        try:
            new_mi_id = return_largest_id_plusone(MenuItem, session)
            new_mi_id += 1
        except Exception as e:
            logger.info("method failed:\n{}".format(e), exc_info=True)
        else:
            meta = add_meta({}, created=True)
            new_entry = MenuItem(
                    id=new_mi_id,
                    franchise_id=self.f_id,
                    item_name=annual_item.item_name,
                    **meta)

            new_menu_items.append(new_entry)
        return new_mi_id

    def autogenerate_description(self, row):
        """
        Generate description using item_name, menu_section and description.
        1. if "description" exists, add  ", " + "menu_section"
        2. if not, "description" = "item_name" + ", " + "menu_section"
        """
        desc_base = row.item_description if row.item_description != "" else\
                row.item_name
        desc = "{}, {}".format(desc_base, row["menu_section"]).\
                replace(", nan", "")
        logger.debug("item_description:{}".format(desc))
        desc = re.sub(self.cleaner['remove_from_desc'], "", desc, flags=re.IGNORECASE)
        desc = loop_string_replace(self.cleaner['nd_cleaner'], desc, regex=False)
        desc = loop_string_replace(self.cleaner['nd_cleaner_re'], desc)

        return desc


    @wrap(writelog, writelog)
    def standardize_df_contents(self):
        """ Make column contents conform with intended format & datatype.
        1. Move non-digit nutrition columns to "_text" cells
        2. add numeric serving amounts in names ("24 oz") to serving size
        3. separate serving size value into numeric amount and measure. If
            measure isn't a standard measure, assign to "household"
        """
        df = self.nutr_df
        # column contents to address: '4130/7140','43 g',"<1","-"
        df.drop_duplicates(inplace=True)
        df.fillna("", inplace=True)
        df.loc[df['serving_size'].notnull(), 'serving_size'] = df['serving_size'].astype(str)
        df = df.replace("^-$", "", regex=True)
        df['serving_size'] = df['serving_size'].str.strip()

        df.loc[df['serving_size'].str.contains(self.cleaner["ss_text"], \
                regex=True), "serving_size_text"] = df['serving_size']

        ssu_re = "\d+\s*({})".format("|".join(u for u in self.cleaner["serving_units"]))
        df.loc[df['serving_size'].str.contains(ssu_re, regex=True),\
                "serving_size_unit"] = df['serving_size']

        df.loc[(df['item_name'].str.contains(self.cleaner["serving_in_name"\
            ][0], regex=True)) & (df['item_name'].str.contains("(small|medium"
            "|large)", regex=True, flags=re.IGNORECASE)), "item_name"] = df['item_name'].str.replace(self.cleaner['serving_in_name'][0], "", regex=True)

        df.loc[df['serving_size'].str.contains(self.cleaner["ss_house"\
        ],regex=True), "serving_size_household"] = df['serving_size']
        df['serving_size_unit'] = df['serving_size_unit'].str.\
            replace(r"([1234567890\.\/])+", "", regex=True).str.strip()
        df['serving_size'] = df['serving_size'].str.\
        replace(r"([^1234567890\.\/])+", "", regex=True)
        isnum = r"^\d+([\.\/]\d{1,3})?$"
        for col in self.nutr_columns:
            logger.debug(f"colname:{col}\ndata overview:\n{df[col]}")
            df[col] = df[col].astype(str).apply(lambda x: re.sub(r'(\d+),(\d+)', r'\1\2', x))
            text_col = col + "_text"
            df[text_col] = None
            df[text_col] = df[col].astype(str)
            df[text_col] = df[text_col].str.replace("(m?g| cal|,)$", "",\
                    regex=True, flags=re.IGNORECASE).str.strip()
            is_num = df[text_col].str.contains(isnum, regex=True)
            df.loc[~is_num, col] = ""
            df.loc[is_num, col] = df[text_col]
            df.loc[is_num, text_col] = ""
            is_perc = df[text_col].str.contains("%", regex=False)
            deformatted_field = col.replace("_", " ")
            df[col] = df[col].str.replace("{}".format(deformatted_field),\
                "", regex=True, flags=re.IGNORECASE)
        caps_func = lambda x: " ".join(s if s in self.cleaner['keepcap'] else\
            string.capwords(s) for s in x.split(" "))
        df['item_name'] = df['item_name'].apply(caps_func)
        df['item_description'] = df['item_description'].apply(caps_func)
        self.nutr_df = df



def check_df_for_issues(name, df):
    """Run series of checks on dataframe and record red flags in log file.

    The following characteristics are flagged:
    - Empty item_name column
    - Empty item_name column entries
    - Empty calories column
    - Empty calories column entries

    Parameters
    ----------
    name : string
        Name of the franchise.
    df : DataFrame
        Dataframe with the structure of those produced by the
        collect_and_clean_annualitemdata method.
    """
    issue_list = []
    null_valued = df.replace(r'^\s*$', np.nan, regex=True)
    if df.empty:
        issue_list.append("Empty DF")
    valuecheck = ["calories", "item_name"]
    for value in valuecheck:
        if null_valued[value].isnull().all():
            issue = "No {} values".format(value)
            issue_list.append(issue)
        elif null_valued[value].isnull().any():
            missing = null_valued.loc[null_valued[value].isnull()]
            if value == "calories":
                missing = missing.loc[missing["calories_text"].isnull()]
            missing_len = str(len(missing.index))
            issue = "Missing {} values: {}".format(value, missing_len)
            issue_list.append(issue)
    if issue_list:
        issues = '\n'.join('{}' for _ in range(len(issue_list))).format(*issue_list)
        logger.warning(f"ISSUES FOUND FOR {name}\nissues:\n{issues}")
