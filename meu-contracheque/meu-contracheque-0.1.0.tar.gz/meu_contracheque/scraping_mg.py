# Documento inicial
# https://github.com/gabrielbdornas/projetos-antigos-testes/blob/main/vpn-fhemig/app/controllers/contracheque_importations_controller.rb
from meu_contracheque.time_reader import find_last_month, find_today, find_last_period
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from pathlib import Path
from dotenv import load_dotenv
import csv
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
load_dotenv(dotenv_path=Path('.', '.env'))

def clean_full_process():
  os.system('rm -rf .temp/')
  os.system('rm -rf contracheques.csv')

def clean_process():
  os.system('rm -rf .temp/')

def scraping_process_begin():
  try:
    driver = driver_initiate()
    today = find_today()
    last_month = find_last_month(today)
    period = get_period(last_month)
  except:
    print('Não foi possível iniciar o processo de busca de contracheque.')
    sys.exit(1)
  return driver, period

def driver_initiate():
  try:
    chrome_options = Options()
    chrome_options.headless = True
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(3)
    driver.get('https://www.portaldoservidor.mg.gov.br/azpf/broker2/?controle=ContraCheque')
  except:
    print('Não foi possível iniciar o driver. Tente acesso mais tarde pois portal pode estar fora do ar.')
    sys.exit(1)
  return driver

def scraping_login_process(driver, period, masp, senha):
  try:
    masp_field = driver.find_element(By.ID, 'inputMasp')
    senha_field = driver.find_element(By.ID, 'inputSenha')
    masp_field.send_keys(masp)
    senha_field.send_keys(senha)
    # Clica no botão para entrar e selecionar o mês desejado
    driver.find_element(By.XPATH, "//input[@type='submit' and @value='Entrar']").click()
    # Imprime resultado em pdf
    # time.sleep(5) # Pode ser necessário aumentar este tempo durante processo de extração
    # driver.find_element(By.XPATH, "//a[@class='botao' and text()='SALVAR EM PDF']").click()
  except:
    print('Não foi possível realizar login para busca do contracheque')
    sys.exit(1)

def scraping_full_process(driver, period, last_period):
  found_period = True
  while found_period:
    mes = driver.find_element(By.ID, 'mesAno')
    # Seleciona o mês desejada e clica no botão consultar
    period = normalize_period(period)
    mes.send_keys(period)
    driver.find_element(By.XPATH, "//input[@type='submit' and @value='Consultar']").click()
    try:
      driver.find_element(By.XPATH, f"//b[text()='Nao possui contracheque no mes/ano {period}']")
      found_period = False
      print(f'Fim da busca. Nao possui contracheque no mes/ano {period}.')
    except NoSuchElementException:
      try:
        voltar = driver.find_element(By.XPATH, "//a[@class='botao' and text()='VOLTAR']")
        print(f'Baixando informações contracheque {period}')
        get_page_source(driver, period, 'normal')
        period = get_period(find_last_period(period))
        voltar.click()
        found_period = (True, False)[last_period] # para execução se desejado for último período
      except NoSuchElementException:
        driver.find_element(By.XPATH, "//input[@type='submit' and @value='Consultar']").click()
        print(f'Baixando informações contracheque {period}')
        get_page_source(driver, period, 'normal')
        driver.find_element(By.XPATH, "//a[@class='botao' and text()='VOLTAR']").click()
        mes = driver.find_element(By.ID, 'mesAno')
        mes.send_keys(period)
        driver.find_element(By.XPATH, "//input[@type='submit' and @value='Consultar']").click()
        driver.find_element(By.XPATH, "//input[@id='folha1']").click()
        driver.find_element(By.XPATH, "//input[@type='submit' and @value='Consultar']").click()
        print(f'Baixando informações contracheque gratificação {period}')
        get_page_source(driver, period, 'gratificacao')
        period = get_period(find_last_period(period))
        voltar = driver.find_element(By.XPATH, "//a[@class='botao' and text()='VOLTAR']")
        voltar.click()
        found_period = (True, False)[last_period] # para execução se desejado for último período
  driver.quit()

def get_page_source(driver, period, doc_type):
  if not os.path.isdir('.temp'):
    os.system('mkdir .temp')
  page_source = driver.page_source
  file_path = page_source_file_path(period, doc_type)
  write_page_source = open(file_path, "w")
  write_page_source.write(page_source)
  write_page_source.close()

def page_source_file_path(period, doc_type):
  period = period.split('/')
  month = period[0]
  year = period[1]
  file_path = f".temp/{year}_{month}_{doc_type}_page_source.html"
  return file_path

def csv_register():
  for file in os.listdir('.temp'):
    position = os.listdir('.temp').index(file) + 1
    files_len = len(os.listdir('.temp'))
    split_file = file.split('_')
    year = split_file[0]
    month = split_file[1]
    doc_type = split_file[2]
    period = f'{month}/{year}'
    print(f'Registrando {position} de {files_len} contraqueches - {period}')
    # csv header
    fieldnames = ['periodo', 'mes', 'ano', 'masp', 'tipo_contracheque', 'cpf','nome', 'cargo', 'orgao_exercicio', 'unidade_exercicio', 'verba', 'valor', 'previdencia']
    rows = find_contracheque_values(period, doc_type)
    file_path = 'contracheques.csv'
    file_exist = os.path.isfile(file_path)
    with open(file_path, 'a', encoding='UTF8', newline='') as f:
      writer = csv.DictWriter(f, fieldnames=fieldnames)
      if not file_exist:
        writer.writeheader()
      writer.writerows(rows)

def find_contracheque_values(period, doc_type):
  rows = []
  file_path = page_source_file_path(period, doc_type)
  file = open(file_path, "r").read()
  soup = BeautifulSoup(file, 'html5lib')
  value_table = soup.findAll("tbody")[8]
  lines = value_table.findAll("tr") # linhas da tabela
  for line in lines:
    row = find_contracheque_fix_information(period, doc_type)
    if lines.index(line) != 0: # Pula a primeira linha da tabela que é o cabeçalho
      columns = line.findAll("td") # colunas da tabela por linha
      for column in columns:
        if columns.index(column) == 2: # coluna da descrição da despesa
          text = column.findAll("small")
          if len(text) != 0:
            text = text[0].text.strip()
            row['verba'] = text
        elif columns.index(column) == 4:
          value = column.findAll("small")
          if len(value) != 0:
            value = float(value[0].text.strip()[3:].replace('.', '').replace(',', '.'))
            row['valor'] = value
        elif columns.index(column) == 5:
          value = column.findAll("small")
          if len(value) != 0:
            value = float(value[0].text.strip()[3:].replace('.', '').replace(',', '.')) * -1
            row['valor'] = value
    if 'verba' in row.keys() and 'valor' in row.keys():
      rows.append(row)
  return rows

def find_contracheque_fix_information(period, doc_type):
  file_path = page_source_file_path(period, doc_type)
  file = open(file_path, "r").read()
  soup = BeautifulSoup(file, 'html5lib')
  elements = soup.findAll("small")
  row = {
      'periodo': period,
      'mes': int(period.split('/')[0]),
      'ano': int(period.split('/')[1]),
      'masp': elements[23].get_text(strip=True),
      'tipo_contracheque': doc_type,
      'cpf': elements[59].get_text(strip=True),
      'nome': elements[26].get_text(strip=True),
      'cargo': elements[80].get_text(strip=True),
      'orgao_exercicio': elements[104].get_text(strip=True),
      'unidade_exercicio': elements[113].get_text(strip=True)
    }
  return row

def get_period(last_month):
  return f'{last_month.month}/{last_month.year}'

def normalize_period(period):
  split_period = period.split('/')
  month = str(split_period[0])
  if len(month) == 1:
    month = f'0{month}'
  year = split_period[1]
  period = f'{month}/{year}'
  return period
