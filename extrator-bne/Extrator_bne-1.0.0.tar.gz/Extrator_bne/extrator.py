from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.keys import Keys
from time import sleep

class Extrator_bne:

    def __init__(self,caminho):
        self.driver = webdriver.Chrome(caminho)
        self.driver.get("https://www.bne.com.br/vagas-de-emprego-para-vendedor/?Page=1&Function=vendedor&Area=Com%C3%A9rcio&Sort=0")
        self.lista_local = []
        self.lista_salario = []
        self.lista_empresa = []
        self.lista_forma = []
        self.lista_candidatura = []
        self.INTERVALO_ENTRE_PÁGINAS = 1
        self.df = pd.DataFrame()

    #CLica na próxima página
    def extrair_infos_paginas(self, n_paginas=5, autosave=""):
        for x in range(1,n_paginas+1):
            xpath_clique = f'//*[@id="pagination"]/ul/li[{x}]'
            clique = self.driver.find_element_by_xpath(xpath_clique)
            self.driver.execute_script("arguments[0].scrollIntoView()", clique)  # Scroll to element
            sleep(self.INTERVALO_ENTRE_PÁGINAS)
            clique.click()

    #Busca as informações
            for z in range(1,4):
                xpath_local = f'/html/body/div[5]/section/div[3]/div[{z}]/div[1]/dl[1]/dd'
                local = self.driver.find_element_by_xpath(xpath_local)
                self.lista_local.append(local.text)
                xpath_salario = f'/html/body/div[5]/section/div[3]/div[{z}]/div[1]/dl[2]/dd'
                salario = self.driver.find_element_by_xpath(xpath_salario)
                self.lista_salario.append(salario.text)
                xpath_empresa = f'/html/body/div[5]/section/div[3]/div[{z}]/div[1]/dl[3]/dd'
                empresa = self.driver.find_element_by_xpath(xpath_empresa)
                self.lista_empresa.append(empresa.text)
                try:
                    xpath_home_office = f'/html/body/div[5]/section/div[3]/div[{z}]/div[2]/h4[3]/span'
                    home_office = self.driver.find_element_by_xpath(xpath_home_office)
                    self.lista_forma.append(home_office.text)
                except:
                    self.lista_forma.append('Trabalho Presencial')
                try:
                    xpath_candidatura_livre = f'//*[@id="job-3206490"]/div[2]/h[{z}]'
                    candidatura_livre = self.driver.find_element_by_xpath(xpath_candidatura_livre)
                    self.lista_candidatura.append(candidatura_livre.text)
                except:
                    self.lista_candidatura.append('Candidatura Paga')

    #Busca as informaçôes
            for k in range(5,8):

                xpath_local2 = f'/html/body/div[5]/section/div[3]/div[{k}]/div[1]/dl[1]/dd'
                local2 = self.driver.find_element_by_xpath(xpath_local2)
                self.lista_local.append(local2.text)
                xpath_salario2 = f'/html/body/div[5]/section/div[3]/div[{k}]/div[1]/dl[2]/dd'
                salario2 = self.driver.find_element_by_xpath(xpath_salario2)
                self.lista_salario.append(salario2.text)
                xpath_empresa2 = f'/html/body/div[5]/section/div[3]/div[{k}]/div[1]/dl[3]/dd'
                empresa2 = self.driver.find_element_by_xpath(xpath_empresa2)
                self.lista_empresa.append(empresa2.text)
                try:
                    xpath_home_office = f'/html/body/div[5]/section/div[3]/div[5]/div[2]/h4[2]/span'
                    home_office = self.driver.find_element_by_xpath(xpath_home_office)
                    self.lista_forma.append(home_office.text)
                except:
                    self.lista_forma.append('Trabalho Presencial')
                try:
                    xpath_candidatura_livre = f'/html/body/div[5]/section/div[3]/div[2]/div[2]/h3'
                    candidatura_livre = self.driver.find_element_by_xpath(xpath_candidatura_livre)
                    self.lista_candidatura.append(candidatura_livre.text)
                except:
                    self.lista_candidatura.append('Candidatura Paga')

        self.driver.quit()

    #Cria o dataframe e gera o csv
        df=pd.DataFrame({'Candidatura':self.lista_candidatura,'Localização':self.lista_local,'Salario':self.lista_salario,'Empresa':self.lista_empresa,'Forma de Trabalho':self.lista_forma})
        df['Empresa'] = df['Empresa'].map(lambda x: x.lstrip('+-').rstrip('O que é isso?'))

        self.df = df

        if len(autosave)>0:
            self.salvar_csv(autosave)

    def salvar_csv(self, nome ,sep = ','):
            self.df.to_csv(nome, sep = ',', index=False)
