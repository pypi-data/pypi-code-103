import click
from meu_contracheque.mg_last_period import scraping_mg_last_period_cli
from meu_contracheque.mg_all_periods import scraping_mg_all_periods_cli

@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
  """
    Conjunto de comandos criados para extração de informações de contracheques.
  """
  pass

@cli.group()
def mg():
  """
    Funções responsáveis pela extração de informações de contracheques dos servidores do Estado de Minas Gerais.
  """
  pass

mg.add_command(scraping_mg_last_period_cli)
mg.add_command(scraping_mg_all_periods_cli)

