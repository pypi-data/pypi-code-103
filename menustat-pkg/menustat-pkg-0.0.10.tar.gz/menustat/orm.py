from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, PrimaryKeyConstraint
from sqlalchemy import Column, Integer, DateTime, Boolean, String, ForeignKey

Base = declarative_base()


def connect_to_db(db):
    try:
        engine = create_engine(db)
    except AttributeError as e:
        print("A problem was encountered while creating the db engine.\nThis "
        "may be the result of an incorrect 'DEV_DB' variable in your .env file."
        "\nError: {}".format(e))
        raise
    Session = sessionmaker(bind=engine)
    session = Session()
    return (engine, session)



def return_largest_id_plusone(table, session):
    largest_id = session.query(table.id).order_by(table.id.\
            desc()).first()[0]
    new_id = largest_id + 1 #return largest id in table + 1
    return new_id


class Franchise(Base):
    """ ORM class for interacting with MenuStat db "franchises" table."""

    __tablename__ = "franchises"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    nutr_scraper = Column(String)
    nutr_url = Column(String)
    menu_scraper = Column(String)
    menu_url = Column(String)
    headquarters = Column(String)
    url_publish_date = Column(String)
    nx_id = Column(String)
    nx_url = Column(String)
    nx_menu_last_updated = Column(String) #Column(DateTime)
    nx_alias = Column(String)
    notes = Column(String)
    created_at = Column(String) # Column(DateTime)
    updated_at = Column(String) # Column(DateTime)
    updated_by = Column(String)

    # sets up bidirectional one-to-many relationship with MenuItem class objs
    menu_items = relationship("MenuItem",
                 back_populates="franchises",
                 primaryjoin="(Franchise.id==MenuItem.franchise_id)")



class MenuItem(Base):
    """ ORM class for interacting with MenuStat db's "menu_items" table."""

    __tablename__ = 'menu_items'
    id = Column(Integer, primary_key=True)
    franchise_id = Column(Integer, ForeignKey("franchises.id"))
    item_name = Column(String, nullable=False)
    food_category = Column(String)
    regional = Column(Boolean)
    shareable = Column(Boolean)
    limited_time_offer = Column(Boolean)
    combo_meal = Column(Boolean)
    kids_meal = Column(Boolean)
    created_at = Column(String) # Column(DateTime)
    updated_at = Column(String) # Column(DateTime)
    updated_by = Column(String)

    # sets up bidirectional many-to-one relationship with Franchise class
    franchises = relationship("Franchise", back_populates="menu_items")
    # sets up bidirectional one-to-many relationship with AnnualItemData class objs
    annual_item_data = relationship("AnnualItemData", back_populates="menu_item",
                primaryjoin="(MenuItem.id==AnnualItemData.menu_item_id)")


    def clean_names():
        menu_items = pandas.read_sql_table('menu_items', con=engine, columns = ["id","franchise_id", 'item_name','food_category','regional','shareable','limited_time_offer','kids_meal'])

        string_replacement_dict = {
            ' with ':" w/ ",
            "for 1 Topping Build Your Own Deep Dish Pizza":"Topping, Pizza",
            " and ":" & "
        }
        add_meta(menu_items, created=True)
        for pat, repl in string_replacement_dict.items():
            menu_items['item_name'] = menu_items['item_name'].str.replace(pat, repl)

        menu_items.to_csv('menu_items_corrected.csv')
        menu_items.to_sql('menu_items_corrected', con=engine,
                if_exists='replace', index_label='id', index=False)



class AnnualItemData(Base):
    """ORM class for interacting with MenuStat db "annual_item_data" table."""

    __tablename__ = "annual_item_data"
    id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    year = Column(Integer)
    item_name = Column(String, nullable=False)
    item_description = Column(String)
    serving_size = Column(String)
    serving_size_text = Column(String)
    serving_size_unit = Column(String)
    serving_size_household = Column(String)
    calories = Column(Integer)
    total_fat = Column(Integer)
    saturated_fat = Column(Integer)
    trans_fat = Column(Integer)
    cholesterol = Column(Integer)
    sodium = Column(Integer)
    potassium = Column(Integer)
    carbohydrates = Column(Integer)
    protein = Column(Integer)
    sugar = Column(Integer)
    dietary_fiber = Column(Integer)
    calories_text = Column(String)
    total_fat_text = Column(String)
    saturated_fat_text = Column(String)
    trans_fat_text = Column(String)
    cholesterol_text = Column(String)
    sodium_text = Column(String)
    potassium_text = Column(String)
    carbohydrates_text = Column(String)
    protein_text = Column(String)
    sugar_text = Column(String)
    dietary_fiber_text = Column(String)
    notes = Column(String)
    created_at = Column(String) # Column(DateTime)
    updated_at = Column(String) # Column(DateTime)
    updated_by = Column(String)
    __table_args__ = (PrimaryKeyConstraint("id", sqlite_on_conflict='REPLACE'),)

# sets up bidirectional many-to-one relationship with MenuItem class
    menu_item = relationship("MenuItem", back_populates="annual_item_data")


    def return_closest_match(self, items):
        """ Return menu_item_id of AID item with closest name match
        """
        all_item_names = [i[3] for i in items]
        returned_choice_name = process.extractOne(self.item_name,\
                all_item_names, score_cutoff=65, scorer=fuzz.token_sort_ratio)
        if returned_choice_name:
            returned_choice = [i[1] for i in items if i[3] == returned_choice_name[0]][0]
        else:
            returned_choice = None

        return returned_choice
