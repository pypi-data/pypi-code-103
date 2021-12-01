#!/usr/bin/env python
# coding: utf-8

# # <strong>Motivaçãoo</strog>
# A nossa motivação do projeto é analisar as informações dos pricipais vestibulares do país.

# # Importando bibliotecas

# In[26]:


from selenium import webdriver
from time import sleep 
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import pandas as pd
import csv
from datetime import date
import re
import numpy as np


# In[27]:


pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)


# # Extração

# ## Definindo Super Classe

# In[28]:
def help():
        '''  
        Mostra ao usuário a lista de comando possíveis e suas funcionalidades.
        '''
        print(f'''Lista de comandos:
    .ObterTabela() -> extrai os dados de todas as universidades, junta ao banco de daos, trata e possibilita que sejam exbidos na tela de forma correta.
    .ruf(\"parametro\") -> Ordena as universidade de acordo com o a RUF 2019, da mais bem colocada para a menos
    \tparâmetros:
    \t\t'Posição em Ensino', 'Posição em Pesquisa',  'Posição em Mercado',  'Posição em Inovação', 
    \t\t'Posição em Internacionalização', 'Nota em Internacionalização', 'Nota'.
    .publica() -> Exibe apenas as universidades públicas (Federais, Estaduais ou Municipais).
    .privada() -> Exibe apenas as universidades privadas.
    .estado(\"estado\") -> Exibe as faculdades do estado passado como parâmetro.
    .coincide(\"etapa\") -> Mostra as universidades que tem datas coincidentes no processo passado em \"etapa\".
    \tparâmetros:
    \t\t'Inicio incrição', 'Fim inscrição', 'Início isenção ', 'Fim isenção', 'Primiera fase', 
    \t\t'Primeira fase (segundo dia)', 'Segunda fase', 'Segunda fase (segundo dia)', 'Resultado'
    .processo(\"etapa\", \"periodo\") -> Ordena a tabela da data mais antiga para a mais recente de acordo com o processo escolhido.
    \tparâmetros: 
    \t\tetapa = \"ins\" (inscrição), \"ise\" (Isenção), \"pri\" (Primeira fase), \"seg\" (Segunda Fase), \"res\" (Resultado)
    \t\tperido = \"i\" (início), \"f\" (fim), \"p\" (primeiro dia), \"s\" (segundo dia)''')

class CarregarPagina:
    """
    O CarregarPagina é uma Super classe utilitária que facilita o acesso a páginas da web   

    driver = define o caminho do drive
    url = indica a url a ser visitada
    """
    def __init__(self, url, driver=None):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(chrome_options=options) if not driver else driver
        self.url = url
        self.driver.get(self.url)


# ## Definindo Classes
# Nessa sessão definimos as classes específicas para cada uma das páginas das universidades das quais queremos extrair informações. Essas classes extraem e fazem o pré tratamento dos dados que julgamos importantes para nosso resultado final.

# ### Extrator UEPG

# In[29]:


class ExtratorUEPG(CarregarPagina):
    """
    O ExtratorUEPG é uma classe utilitária que facilita a extração das informações sobre o vestibular de verão atual da Univesidade Estadual de Ponta Grossa (UEPG)   
    """
    def __init__(self,  url = "https://cps.uepg.br/inicio/"):
        """
        Inicializador

        url = endereço da página desejada
        lst_informações = armazena as iformações coletadas
        qntd_linhas = define o número de linhas a serem percorridas pelo nosso extrator
        """
        super().__init__(url)
        self.lst_informações = []
        self.qntd_linhas = 9

   
    def pagina_vestibular(self):
        """
        Seleciona o último vestibular para visualizar mais detalhes sobre

        vestibular = localiza o elemento web que direciona para a página que contem as iformações sobre os vestibulares
        """
        # Clica no ùltimo vestibular postado
        vestibular = self.driver.find_element_by_xpath("""//*[@id="content-1column"]/section/div/article/table/tbody/tr[3]/td[1]/a[1]""")
        vestibular.click()

    def informações_vestibular(self):
        """
        Extrai as informações do vestibular

        vestibular_atual = localiza o último post da página e clica nele
        """
        # Grava o nome do vestibular
        vestibular_atual = self.driver.find_element_by_xpath("""//*[@id="content-1column"]/article/table/tbody/tr[2]/td/p[1]/span""")
        self.lst_informações.append(vestibular_atual.text)
        
        # Extrai as informações como data de abertura e encerramento de inscrições, data de liberação dos resultados, taxa de inscrição etc.
        for i in range (1, self.qntd_linhas):
            xpath_linhas = f'//*[@id="content-1column"]/article/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/tr[{i}]'
            informações = self.driver.find_element_by_xpath(xpath_linhas)
            self.lst_informações.append(informações.text)

    def atribuir_datas(self):
        '''
        correlaciona e formata a lista de datas e de títulos

        inicio_das_insc = armazena a data em que se inicia o período de inscrições
        termino_das_insc = armazena a data em que termina o período de inscrições
        primeira_fase = armazena a data em que ocorrerá a primeira fase do vestibular
        '''
        for linha in self.lst_informações:
            if 'Período de inscrição' in linha:
                texto = linha.split(':')
                texto = str(texto[1])
                data = texto.split('a')
                self.inicio_das_insc = data[0]
                self.termino_das_insc = data[1]
            elif 'Aplicação das provas' in linha:
                texto = linha.split(':')
                texto = str(texto[1])
                self.primeira_fase = texto

    def extrair_informacoes(self):
        '''
        Reúne todos os métodos anteriores em apenas um
        '''
        print('Carregando página UEPG...')
        self.pagina_vestibular()
        self.informações_vestibular()
        self.atribuir_datas()
        print('concluído!')


# ### Extrator Nucvest

# In[30]:



class ExtratorNUCVEST(CarregarPagina):
    """
    O ExtratorNUCVEST é uma classe utilitária que facilita a extração das informações sobre o atual vestibular de verão realizado pela NUCVEST  
    """
    def __init__(self, url = 'https://www.nucvest.com.br/'):
        """
        Inicializador

        url = endereço da página desejada
        elem_pag = guarda o número de linhas da tabela de datas
        inscricao = armazena informações sobre a inscrição no vestibular
        """
        super().__init__(url)
        self.elem_pag = 20
        self.inscricao = []
        
    def aceitarcookies(self):
        ''' 
        Aceita os cookies da página

        btn_cookie = botão para aceitar os cookies da página
        '''
        self.btn_cookie = self.driver.find_element_by_class_name("""fundasp-lgpd-button-accept""")
        self.btn_cookie.click()
    
    def cronograma(self):
        '''
        abre a página que contem os dados referente ao cronograma 

        btn = botão para abrir os dados de cronograma
        '''
        btn = self.driver.find_element_by_class_name("""calendar""")
        btn.click()
        
    def extrair_info_páginas(self):
        ''' 
        coleta as informações uteis para nosso framework
        '''
        informacoes = []
        for i in range(1, self.elem_pag+1):
            data = self.driver.find_element_by_xpath(f"""//*[@id="collapseTwo"]/div/ul/li[{i}]/div[1]""")
            data = data.text
            try:
                conteudo = self.driver.find_element_by_xpath(f"""//*[@id="collapseTwo"]/div/ul/li[{i}]/div[2]""")
                conteudo = conteudo.text
            except:
                conteudo = ''
            dados = {'Data':data,
                    'Conteudo':conteudo}
            informacoes.append(dados)
        self.inscricao = informacoes

    def formatar_dados(self):
        ''' 
        Faz uma formatação incial dos dados para que possam ser armasenado em nosso banco de dados

        
        inicio_das_insc = armazena a data em que se inicia o período de inscrições
        termino_das_insc = armazena a data em que termina o período de inscrições
        primeira_fase = armazena a data em que ocorrerá a primeira fase do vestibular
        '''
        for linha in self.inscricao:
            if 'Período de Inscrições' in str(linha['Conteudo']):
                data = str( linha['Data']).split('a')
                self.inicio_das_insc = data[0]
                self.termino_das_insc = data[1]
            elif 'Aplicação da prova' in str(linha['Conteudo']):
                self.primeira_fase = str(linha['Data']).split('a')

    def extrair_informacoes(self):
        ''' 
        Junta todos os métodos anteriores em apenas um
        '''
        print('Carregando página Nucvest...')
        self.aceitarcookies()
        self.cronograma()
        self.extrair_info_páginas()
        self.formatar_dados()
        print('concluído!')


# ### Unifesp

# In[31]:


class ExtratorUnifesp(CarregarPagina):
    """
    O ExtratorUnifesp é uma classe utilitária que facilita a extração das informações sobre o atual vestibular de verão da Universidade Federal do Estado de São Paulo  

    inscricao = armazena os dados referentes a inscrição 
    """
    def __init__(self, url = 'https://ingresso.unifesp.br/informacoes-fixas/informacoes-fixas-misto/cronograma-sistema-misto'):
        super().__init__(url)
        self.inscricao = []
        
    def extrair_info_páginas(self):
        '''
        Coleta da página os dados relevantes para o nosso projeto
        '''
        dados_lst = []
        for k in range(1, 12):
            data = self.driver.find_element_by_xpath(f"""//*[@id='g-main']/div/div/div/div/div/div/div/div[2]/table/tbody/tr[{k}]/td[1]""")
            data = data.text
            try:
                conteudo = self.driver.find_element_by_xpath(f"""//*[@id='g-main']/div/div/div/div/div/div/div/div[2]/table/tbody/tr[{k}]/td[2]""")
                conteudo = conteudo.text
            except:
                conteudo = ''
            dados = {'Data':data,
                    'Conteudo':conteudo}
            dados_lst.append(dados)
        self.inscricao = dados_lst
        
    def formatar_dados(self):
        '''
        Realiza a pré-formatação dos dados para serem adicionados ao nosso banco de dados 

        inicio_isencao = armazena a data em que se inicia o período de pedido de isenção de taxa
        termino_isencao = armazena a data em que se termina o período de pedido de isenção de taxa
        inicio_das_insc = armazena a data em que se inicia o período de inscrições
        termino_das_insc = armazena a data em que termina o período de inscrições
        primeira_fase = armazena a data em que ocorrerá a primeira fase do vestibular
        primeira_fase_dia2 = armazena a data em que ocorrerá o segundo dia de provas da primeira fase do vestibular
        '''
        for linha in self.inscricao:
            if  'Período para pedido de isenção de taxa de inscrição do vestibular' in str(linha['Conteudo']):
                data = str( linha['Data']).split('às')
                self.inicio_isencao = data[0]
                self.termino_isencao = data[1]
            elif 'Período de inscrição para as provas complementares' in str(linha['Conteudo']):
                data = str( linha['Data']).split('às')
                self.inicio_das_insc = data[0]
                self.termino_das_insc = data[1]
            elif 'Provas Complementares:\n' in str(linha['Conteudo']):
                data = str(linha['Data']).split('\n')
                self.primeira_fase = data[0]
                self.primeira_fase_dia2 = data[1]
    
    def extrair_informacoes(self):
        ''' 
         Junta todos os métodos anteriores em apenas um
        '''
        print('Extraindo informações Unifesp...')
        self.extrair_info_páginas()
        self.formatar_dados()
        print('Concluído!')
            


# ### Acafe

# In[32]:


class ExtratorAcafe(CarregarPagina):
    def __init__(self, url = 'https://acafe.org.br/site/', periodo = 'Verão 2022'):
        '''
        O ExtratorAcafe é uma classe utilitária que facilita a extração das informações sobre o atual vestibular de verão fornecido pela Acafe  


        periodo = Qual edição da prova queremos (ex:'Verão 2022', 'Inverno 2022', ...)
        '''
        super().__init__(url)
        self.periodo =  periodo


    def abrir_calendario(self):
        '''  
        Abre o elemento html que possui o calendário do vestibular

        banner = elemento web do banner que precisa ser fechado 
        aceitar_cookies = elemento web para aceitar os cookies
        abrir_calendario = botão que possibilita a abertura do calendário
        '''
        #fechar banner
        try:
            sleep(15)
            banner = self.driver.find_element_by_xpath(f'''/html/body/div[3]/div/div/div[3]/button''')
            banner.click()
        except:
            pass
        #Aceita os cookies e abre o calendário 
        aceitar_cookies = self.driver.find_element_by_class_name(f'''btn-cookies''')
        abrir_calendario = self.driver.find_element_by_xpath(f'''/html/body/div[5]/div/div[2]''')
        sleep(5)
        aceitar_cookies.click()
        sleep(3)
        abrir_calendario.click()    

    def extrair_conteudo(self):
        '''  
        Extrai da página o conteúdo que julgamos relevante para nosso trabalho

        titulos_element = armazena os elementos dos títulos da tabela de calendários
        linhas_element = armazena os elementos das linhas com as informações sobre as datas de calendários
        linhas = armazena as linhas com as informações sobre as datas de calendários
        titulo = armazena os títulos da tabela de calendários
        '''
        #extrai o conteúdo do calendário (os acontecimentos que queremos para o nosso banco de dados e suas respectivas datas)
        self.abrir_calendario()
        self.titulos_element = self.driver.find_elements_by_tag_name(f'''th''')
        self.linhas_element = self.driver.find_elements_by_tag_name(f'''td''')

        #organizando conteúdo em listas
        linhas = []
        for linha in self.linhas_element:
            linhas.append(linha.text)
        self.linhas = linhas
        titulos = []
        for titulo in self.titulos_element:
            if titulo.text != '':
                titulos.append(titulo.text)
        self.titulos = titulos

    def atribuir_datas(self):
        '''
        pré-formata e atribui as datas a cada acontecimento importante refernte às provas, para adicionarmos a nossa base de dados

        indice_do_perido = armazena o indice em que o nome do período se encontra na lista
        inicio_das_insc = armazena a data em que se inicia o período de inscrições
        termino_das_insc = armazena a data em que termina o período de inscrições
        primeira_fase = armazena a data em que ocorrerá a primeira fase do vestibular
        '''
        #correlacionando e formatando a lista de datas e de títulos(acontecimento)
        self.indice_do_perido = int(self.titulos.index(self.periodo))
        for i in range(0,len(self.linhas), len(self.titulos)):
            if self.linhas[i] == 'Aplicação da prova':
                self.primeira_fase = self.linhas[(i+self.indice_do_perido)]
            elif self.linhas[i] == 'Inscrição':
                datas = (self.linhas[(i+self.indice_do_perido)]).split('a')
                self.inicio_das_insc = datas[0]
                self.termino_das_insc = datas[1]  
    def extrair_informacoes(self):
        '''
        método que ao ser chamado, executa todas os anteriores.
        '''
        print('Carregando página Acafe...')
        self.extrair_conteudo()
        self.atribuir_datas()
        print('Concluído')



# ## Definindo classe
# Aqui foi definida a classe que reliza o trabalho de incluir os novos dados à tabela principal.
class ObterDados:
    ''' 
    Adicona os dados coletados à tabela principla
    '''
    def __init__(self, file = 'ranking_universidades.csv'):
        '''   
        abre a tabela


        ranking = dataset com a tabela principal
        '''
        self.ranking = pd.read_csv(file, dtype = str, encoding = 'latin-1', sep = ';')
        self.ranking.fillna('', inplace = True)
    
    def adicionar_a_tabela(self, acafe, uepg, unifesp, nucvest):
        ''' 
        adicona os dados coletados ao dataset
        ''' 
        for index, row in self.ranking.iterrows():
            if row['Extrator'] == 'ExtratorAcafe':
                row['link site'] = acafe.url
                row['Inicio incrição'] = acafe.inicio_das_insc
                row['Fim inscrição'] = acafe.termino_das_insc
                row['Primiera fase'] = acafe.primeira_fase
            elif row['Extrator'] == 'ExtratorUepg':
                row['link site'] = uepg.url
                row['Inicio incrição'] = uepg.inicio_das_insc
                row['Fim inscrição'] = uepg.termino_das_insc
                row['Primiera fase'] = uepg.primeira_fase
            elif row['Extrator'] == 'ExtratorUnifesp':
                row['link site'] = unifesp.url
                row['Inicio incrição'] = unifesp.inicio_das_insc
                row['Fim inscrição'] = unifesp.termino_das_insc
                row['Primiera fase'] = unifesp.primeira_fase
                row['Primeira fase (segundo dia)'] = unifesp.primeira_fase_dia2
            elif row['Extrator'] == 'ExtratorNucvest':
                row['link site'] = nucvest.url
                row['Inicio incrição'] = nucvest.inicio_das_insc
                row['Fim inscrição'] = nucvest.termino_das_insc
                row['Primiera fase'] = nucvest.primeira_fase

    def salvar(self):
        '''  
        salva o dataset em csv
        '''
        self.ranking.to_csv('rankingteste.csv', sep = ',', encoding = 'utf-8', index = False, quoting = csv.QUOTE_ALL)


# # <strong>Tratamento</strong>
# ## Definindo Classe
# Definimos a clase que trata todos os campos de data passando-os para o padrõa aaaa-mm-dd. É importante ressaltar que foram tratadas as exceções que encontramos durante nossa coleta de dados, mas conforme forem obtidas mais amostras a atualização desse código pode se fazer necessária.

class Tratando():
    ''' 
    Classe que trata todos os campos de data passando-os para o padrõa aaaa-mm-dd
    '''
    def __init__(self,df, colunas_data = ['Inicio incrição', 'Fim inscrição', 'Início isenção ', 'Fim isenção',
    'Primiera fase', 'Primeira fase (segundo dia)', 'Segunda fase',
    'Segunda fase (segundo dia)', 'Resultado']):
        '''  
        df = datframe a ser tratado
        colunas_datas = armazena o nome das colunas que possuem datas
        coluna_metadados = armazena o nome da coluna que possui metadados
        '''
        self.df = df
        self.colunas_data = colunas_data
        self.coluna_metadados = 'metadados'
    
    
    def tratar_datas(self):
        '''
        Aplica as regras para o tratamento das exceções

        coluna = define a coluna atual que está sendo trabalhada
        proxima_coluna = define a próxima coluna que será trabalhada
        data = é a data do evento que está sendo trabalhado
        proximo_ano = armazena o ano do próximo evento que será relizado naquela univerisdade
        '''
        for index, row in self.df.iterrows():
            for i in range(len(self.colunas_data)):
                self.coluna = self.colunas_data[i] 
                try:
                    self.proxima_coluna = self.colunas_data[i+1] #caso a data não tenha o ano, pegamos da próxima data (ex: incrições de 20/10 a 20/11/2021)
                    self.adicionar_ano(row[self.proxima_coluna])
                except:
                    self.proxima_coluna = ''
                self.metadados = ''
                self.encontrar_datas(row[self.coluna])
                if self.data != '':
                    if str(self.data)[0] == '-':
                        self.data = str(self.proximo_ano) + str(self.data)
                self.df.loc[index, self.coluna_metadados] += self.metadados
                self.df.loc[index, self.coluna] = self.data

    def info_adicional(self, texto):
        ''' 
        Reconhece os eventos importante que podem estra presentes nas informações adicionais 

        texto = texto presente na coluna de metadados da linha trabalhada atualmente
        '''
        info_adicional = [ 
        'ENEM'
        'EAD'
        'SISU'
        'Cancelado'
        ]
        texto_final = ''
        for info in info_adicional:
            if info in texto:
                texto_final += f'''{info}\n''' 
        return f'''{self.coluna}: {texto_final}''' if texto_final != '' else ''

    def encontrar_datas(self, texto):
        ''' 
        Encontra, de acordo com os padrões observados, nos campos onde devem haver datas, as datas dos eventos e passa elas para o padrão aaaa-mm-dd.

        dia = armazena o dia do evento
        mes = armazena o mes do evento
        ano = armazena o ano do evento
        data = armazena a data final do evento
        metadados = caso o campo analisado não possua datas nos padrões estabelecidos, o métodos info_adicional procura informções adicionais relevantes sobre ele e, se for o caso, às adicona ao campo de metadados.
        '''
        r = re.compile(r'\d{2}/\d{2}/\d{4}')
        s =  re.compile(r'(\d{2}/\d{2}[^/0-9])')
        texto = str(texto)
        r = str(r.findall(texto))[2:-2]
        s = str(s.findall(texto))[2:-3]
        if r != '':
            self.dia = r[:2]
            self.mes = r[3:5]
            self.ano = r[6:]
            self.data = f'''{self.ano}-{self.mes}-{self.dia}'''
        elif s != '':
            self.dia = s[:2]
            self.mes = s[3:5]
            self.data = f'''-{self.mes}-{self.dia}'''
        else:
            self.data = ''
            self.metadados = self.info_adicional(texto)
    
    def adicionar_ano(self, texto):
        '''  
        armazena as datas do proxímo evento que ocorrerá nessa universidade, pois em alguns casos encontramos datas como "incrições do dia 11/10 a 11/11/2021", o que faz necessário obter ano do término das incrições para definir o ano de seu inicio.

        proximo_dia = armazena o dia do próximo evento
        proximo_mes = armazena o mes do próximo evento
        proximo_ano = armazena o ano do próximo evento
        '''
        r = re.compile(r'\d{2}/\d{2}/\d{4}')
        r = str(r.findall(texto))[2:-2]
        if r != '':
            self.proximo_dia = r[:2]
            self.proximo_mes = r[3:5]
            self.proximo_ano = r[6:]
        else:
            self.proximo_dia = ''
            self.proximo_mes = ''
            self.proximo_ano = ''

    def salvar(self):
        '''  
        salva o dataset em csv
        '''
        self.df = self.df.drop(columns=['Extrator'])
        self.df.to_csv('ranking_tratado.csv', sep = ',', encoding = 'utf-8', index = False, quoting = csv.QUOTE_ALL)



# In[33]:

class ObterTabela():
    def __init__(self):

        # ## Realizando Extração
        # aqui chamamos as classes extratoras de cada universidade para cumprir suas fucionalidades.
        self.uepg = ExtratorUEPG()
        self.uepg.extrair_informacoes()
        self.nucvest = ExtratorNUCVEST()
        self.nucvest.extrair_informacoes()
        self.unifesp = ExtratorUnifesp()
        self.unifesp.extrair_informacoes()
        self.acafe = ExtratorAcafe()
        self.acafe.extrair_informacoes()

        # # Incluir informações no dataset
        # Nessa etapa adicionamos as informações coletadas à nossa tabela principal. 
        self.ranking = ObterDados()
        self.ranking.adicionar_a_tabela(self.acafe, self.uepg, self.unifesp, self.nucvest)
        self.ranking.salvar() 

        # ## Chamando Classe
        df_compl = self.ranking.ranking
        self.df_tratado = Tratando(df_compl)
        self.df_tratado.tratar_datas()
        self.df_tratado.salvar()


# # <strong>Visualização</strong>
# Aqui possibilitamos que a visualização dos dados fosse personalizada pelo usuário de acordo com sua preferência. Por exemplo, é possível organizar a exibição das universidades por estado, por datas de incrições mais antigas para as mais recentes, apenas privadas ou apenas públicas, dentre muitas outras.

# ## Definindo Classe
# Aqui definimos a classe e seus métodos, que quando chamdos pelo usuário, exibirão as tabelas de forma específica. 

# In[41]:


class Ordenar():
    def __init__(self, objname, tirar_sem_datas = False):
        '''
        Transforma os dados para ordenar a tabela de a cordo com a preferência do usuário

        df = dataframe utilizado
        tirar_sem_datas = tira da visualização as universidades que não possuem datas para nenhum dos processos.
        colunas_data = armazena o nome das colunas que possuem datas
        colunas_colocacao = armazen ao nome das colunas que possuem informações sobre colocação da universidade no RUF.
        colunas_int = armazena o nome das colunas que possuem número inteiros como dados.
        tirar_sem_datas = Caso definido como True, tira da exibição as universidades que não possuem nenhuma data referente ao processo seletivo. 
        estados = armazena  alista de estados em que as universidades da nossa tabela se encontram.
        objname = nome dados ao objeto ao qual foi atribuida a classe ObterTabela
        '''
        self.df = objname.df_tratado.df
        colunas_int = [
            'Nota', 'Posição em Pesquisa', 'Posição em Ensino', 'Posição em Mercado', 'Posição em Inovação', 'Posição em Internacionalização'
            ]
        self.colunas_data = [
            'Inicio incrição', 'Fim inscrição', 'Início isenção ', 'Fim isenção', 'Primiera fase', 
            'Primeira fase (segundo dia)', 'Segunda fase', 'Segunda fase (segundo dia)',	'Resultado'
            ]
        self.colunas_colocacao = [ 
            'Posição em Ensino', 'Posição em Pesquisa',  'Posição em Mercado',  'Posição em Inovação', 
            'Posição em Internacionalização', 'Nota em Internacionalização', 'Nota'
        ]

        if tirar_sem_datas == 'True':
            self.df = self.df.replace('', np.nan)
            self.df = self.df.dropna(how = 'all', subset = [self.colunas_data])
            self.df = self.df.fillna('')
            
        self.estados = self.df.Estado.unique()
        self.df = self.df.rename(columns={'metadados':'Mais Informações'})
        self.df[colunas_int] = self.df[colunas_int].astype(int)
        self.df['Nota'] = self.df['Nota'].astype(float)
        

    def ruf(self, parametro : str):
        ''' 
        exibe a tabela de acordo com a classificacão no RUF.
        '''
        if parametro in self.colunas_colocacao:
            df_ = self.df 
            df_ = df_.sort_values(by = parametro)
            return display(df_)
        else:
            print(f'''\"{parametro}\" não é válido, confia a lista de parâmetros válidos:\n{self.colunas_colocacao}''')

    def publica(self):
        ''' 
        Exibe apenas as universidade públicas (federais, estaudais ou municipais)
        '''
        df_ = self.df
        df_ = df_.loc[df_['Pública ou Privada']!='Privada']
        return display(df_)

    def privada(self):
        ''' 
        Exibe apenas as universidades privadas.
        '''
        df_ = self.df
        df_ = df_.loc[df_['Pública ou Privada']=='Privada']
        return display(df_)

    def estado(self, sigla_estado : str):
        '''  
        Exibe apenas as universidades do estado escolhido pelo usuário.
        '''
        if sigla_estado in self.estados:
            df_ = self.df
            df_ = df_.loc[df_['Estado']== sigla_estado]
            return display(df_)
        else:
            return print(f'''\"{sigla_estado}\" não é um estado válido. Confira a lista de estados válidos: \n{self.estados}''')
    
    def coincide(self, etapa : str):
        ''' 
        Mostra as universidades que tem datas coincidentes no processo especificado pelo usário.
        '''
        if  etapa in self.colunas_data:
            df_ = self.df 
            df_ = pd.concat(linha for _, linha in df_.groupby(etapa) if len(linha) > 1)
            df_ = df_.loc[df_[etapa]!= '']
            print(f'''Datas coincidentes em \"{etapa}\"''')
            return display(df_)
        else:
             print(f'''\"{etapa}\" não é válido, confia a lista de parâmetros válidos:\n{self.colunas_data}''')

    def processo(self, etapa, periodo):
        '''  
        Ordena a tabela da data mais antiga para a mais recente de acordo com o processo escolhido.
        '''
        df_ = self.df
        df_[self.colunas_data] =  df_[self.colunas_data].apply(pd.to_datetime, format='%Y-%m-%d')
        if etapa == 'ins':
            if periodo == 'i': 
                df_ = df_.sort_values(by = 'Inicio incrição')
                return df_.replace({pd.NaT: ""})
            elif periodo == 'f':
                df_ = df_.sort_values(by = 'Fim inscrição')
                return df_.replace({pd.NaT: ""})
            else:
                print(f'''\"{periodo}\" é um período inválido para Inscrição.
Use \".help()\" para verificar a lista de parâmetros possíveis para este comando.''')
        elif etapa == 'ise':
            if periodo == 'i': 
                df_ = df_.sort_values(by = 'Início isenção ')
                return df_.replace({pd.NaT: ""})
            elif periodo == 'f':
                df_ = df_.sort_values(by = 'Fim isenção')
                return df_.replace({pd.NaT: ""})
            else:
                print(f'''\"{periodo}\" é um período inválido para Isenção de Taxa.
Use \".help()\" para verificar a lista de parâmetros possíveis para este comando.''')
        elif etapa == 'pri':
            if periodo == 'p':
                df_ = df_.sort_values(by = 'Primiera fase')
                return df_.replace({pd.NaT: ""})
            elif periodo == 's':
                df_ = df_.sort_values(by = 'Primeira fase (segundo dia)')
                return df_.replace({pd.NaT: ""})
            else:
                print(f'''\"{periodo}\" é um período inválido para Primeira fase.
Use \".help()\" para verificar a lista de parâmetros possíveis para este comando.''')
        elif etapa == 'seg':
            if periodo == 'p':
                df_ = df_.sort_values(by = 'Segunda fase')
                return df_.replace({pd.NaT: ""})
            elif periodo == 's':
                df_ = df_.sort_values(by = 'Segunda fase (segundo dia)')
                return df_.replace({pd.NaT: ""})
            else:
                print(f'''\"{periodo}\" é um período inválido para Segunda fase.
Use \".help()\" para verificar a lista de parâmetros possíveis para este comando.''')
        elif etapa == 'res':
            df_ = df_.sort_values(by = 'Resultado')
            return df_.replace({pd.NaT: ""})
        else:
            print(f'''\"{etapa}\" é uma etapa inválida.\nUse \".help()\" para verificar a lista de parâmetros possíveis para este comando.''')

