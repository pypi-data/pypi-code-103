import sys
import click
from meu_contracheque.scraping_mg import (scraping_process_begin,
                                         scraping_login_process,
                                         csv_register,
                                         clean_full_process,
                                         find_last_period,
                                         scraping_full_process,
                                         clean_process)


def scraping_mg_all_periods(masp, senha):
  """
  Função responsável pela busca de informações de todos os contracheques dos servidores do Estado de Minas Gerais.
  Parâmetros:
  -------
  masp: string
    Masp do servidor do Estado de Minas Gerais
  senha: string
    Senha de acesso ao Portal do servidor do Estado de Minas Gerais
  Retorna:
  -------
  Arquivo "contracheques.csv" atualizado com as informações de todos os contracheque disponíveis no Portal do Servidor.
  """
  try:
    print('Iniciando processo de extração de todos contracheques...')
    clean_full_process()
    start = scraping_process_begin()
    driver = start[0]
    period = start[1]
    scraping_login_process(driver, period, masp, senha)
    scraping_full_process(driver, period, False)
    csv_register()
    clean_process()
  except:
    print('Não foi possível finalizar o processo de busca de todos contracheques.')
    sys.exit(1)

@click.command(name='todos')
@click.option('--masp', '-m', envvar='MASP', required=True,
              help="Masp do servidor do Estado de Minas Gerais")
@click.option('--senha', '-s', envvar='PORTAL_PWD', required=True,
              help="Senha de acesso ao Portal do servidor do Estado de Minas Gerais")
def scraping_mg_all_periods_cli(masp, senha):
  """
  Função CLI responsável pela busca de informações de todos os contracheques dos servidores do Estado de Minas Gerais.
  Por padrão, função buscará masp e senha nas variáveis de ambiente MASP e PORTAL_PWD cadastradas na máquina ou
  em arquivo .env.
  Parâmetros:
  ----------
  masp: string
      Masp do servidor do Estado de Minas Gerais
    senha: string
      Senha de acesso ao Portal do servidor do Estado de Minas Gerais
    Retorna:
    -------
    Arquivo "contracheques.csv" atualizado com as informações de todos os contracheques disponíveis no Portal do Servidor.
  """
  scraping_mg_all_periods(masp, senha)
