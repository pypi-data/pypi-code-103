from pathlib import Path
from dotenv import load_dotenv
from meu_contracheque.mg_last_period import scraping_mg_last_period
from meu_contracheque.mg_all_periods import scraping_mg_all_periods
load_dotenv(dotenv_path=Path('.', '.env'))
