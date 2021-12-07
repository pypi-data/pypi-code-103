from enum import Enum
from functools import lru_cache
from typing import Type, List, cast, Optional

import pendulum
from duckling import (load_time_zones, parse_ref_time,
                      parse_lang, default_locale_lang, parse_locale,
                      parse_dimensions, parse, Context)
from pydantic import BaseModel, Field
from pymultirole_plugins.util import comma_separated_to_list
from pymultirole_plugins.v1.annotator import AnnotatorParameters, AnnotatorBase
from pymultirole_plugins.v1.schema import Document, Span, Annotation


class Dimension(str, Enum):
    amount_of_money = 'amount-of-money'
    credit_card_number = 'credit-card-number'
    distance = 'distance'
    duration = 'duration'
    email = 'email'
    number = 'number'
    ordinal = 'ordinal'
    phone_number = 'phone-number'
    quantity = 'quantity'
    time = 'time'
    url = 'url'
    volume = 'volume'


class DucklingParameters(AnnotatorParameters):
    time_zone: str = Field("Europe/Paris",
                           description="Reference time zone to normalize date/time, must be a valid [time zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)")
    lang: str = Field("fr", description="Reference language")
    locale: Optional[str] = Field(None, description="Reference locale, default is the default locale of the language")
    dimensions: Optional[str] = Field("amount-of-money,time",
                                      description="""Comma-separated list of [Duckling](https://github.com/facebook/duckling) dimensions to consider, to be chosen among:<br/>
        <li>`amount-of-money`: Measures an amount of money such as *$20*, *30 euros*.
        <li>`credit-card-number`: Captures a credit card number.
        <li>`distance`: Captures a distance in miles or kilometers such as *5km*, *5 miles* and *12m*.
        <li>`duration`: Captures a duration such as *30min*, *2 hours* or *15sec* and normalizes the value in seconds.
        <li>`email`: Captures an email but do not try to check the validity of the email. For example, *support@kairntech.com*.
        <li>`number`: Extrapolates a number from free text, such as *six*,*twelve*, *16*, *1.10* and *23K*.
        <li>`ordinal`: Captures the measure of an ordinal number, such as *first*, *second*, *third*... or *1st*, *2nd*, ..., *7th*, etc.
        <li>`phone-number`: Captures phone numbers, but does not try to check the validity of the number.
        <li>`quantity`: Captures the quantity of something; such as ingredients in recipes, or quantities of food for health tracking apps. Returns a numerical value, a unit, and a product (each field is optional).
        <li>`temperature`: Captures the temperature in units of celsius or fahrenheit degrees.
        <li>`time`: Captures and resolves date and time, like *tomorrow at 6pm*.
        <li>`url`: Captures an URL, but does not try to check the validity of the URL.
        <li>`volume`: Captures measures of volume like *250 ml*, *3 gal*.
        """)


time_zones = load_time_zones("/usr/share/zoneinfo")


class DucklingAnnotator(AnnotatorBase):
    """[Duckling](https://github.com/facebook/duckling) annotator.
    """

    def annotate(self, documents: List[Document], parameters: AnnotatorParameters) \
            -> List[Document]:
        params: DucklingParameters = \
            cast(DucklingParameters, parameters)
        # Create parsing context with time and language information
        context = get_context(params.time_zone, params.lang, params.locale)

        # Define dimensions to look-up for, check if they are valid names
        valid_dimensions = []
        for d in comma_separated_to_list(params.dimensions):
            try:
                Dimension(d)
                valid_dimensions.append(d)
            except ValueError:
                pass

        # Parse dimensions to use
        output_dims = parse_dimensions(valid_dimensions)

        for document in documents:
            document.annotations = []
            if not document.sentences:
                document.sentences = [Span(start=0, end=len(document.text))]
            for sent in document.sentences:
                # Parse a phrase
                dims = parse(document.text[sent.start:sent.end], context, output_dims, False)
                for dim in dims:
                    start = sent.start + dim['start']
                    end = sent.start + dim['end']
                    props = dim.get('value', {})
                    props.pop('values', None)
                    document.annotations.append(Annotation(start=start, end=end,
                                                           labelName=dim['dim'].replace('-', '_'), label=dim['dim'],
                                                           text=document.text[start:end],
                                                           properties=props))
        return documents

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return DucklingParameters


@lru_cache(maxsize=None)
def get_context(time_zone, lang, locale):
    bog_now = pendulum.now(time_zone).replace(microsecond=0)
    ref_time = parse_ref_time(time_zones, time_zone, bog_now.int_timestamp)
    # Load language/locale information
    lang = parse_lang(lang)
    default_locale = default_locale_lang(lang)
    locale = default_locale if locale is None else parse_locale(locale, default_locale)
    return Context(ref_time, locale)
