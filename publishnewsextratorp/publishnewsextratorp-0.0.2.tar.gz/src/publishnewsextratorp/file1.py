#para verificar a versão das libs
#pip freeze

#atualiza o selenium para versão 4 ou posterior
#pip install selenium --upgrade --use-feature=2020-resolver

#atualiza o chardet para dependencia do selenium (remover warning)
#pip install chardet --upgrade --use-feature=2020-resolver

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd

class IniciarDriver:
    
    #classe construtor
    def __init__(self):
        '''
        Esta é uma classe construtora. Inicializa o Chrome
        A classe ExtracaoPublishNews está usando a classe IniciarDriver como relação de herança para iniciar o construtor.
        '''
        #valida a versão do Chrome, atualiza o driver ou instala caso não exista
        s=Service(ChromeDriverManager().install())
        #executa o serviço acima
        self.driver = webdriver.Chrome(service=s)
        #abre o site publish news 
        self.driver.get('https://www.publishnews.com.br/ranking/')
        #clica em aceitar cookies para sair o banner do site
        self.driver.find_element(by='xpath', value='/html/body/div[1]/div/a[2]').click()

#classe de exceção para tratamento de erro
class ExcecaoAnoInvalido(Exception):
    pass

#a classe ExtracaoPublishNews está usando a classe IniciarDriver como relação de herança para iniciar o construtor.
class ExtracaoPublishNews(IniciarDriver):
    '''
    A classe ExtracaoPublishNews está usando a classe IniciarDriver como relação de herança para iniciar o construtor.
    '''
    #aqui não temos o construtor pois estamos inicializando o driver na classe IniciarDriver
    def seleciona_anual(self):
        '''
        Seleciona a aba ano no site.
        '''
        #método para selecionar a aba de ano no site
        self.driver.find_element(by='xpath', value='//*[@id="pn-orelha-anual"]').click()
        
    def seleciona_xpath(self, ano): 
        '''
        Recebe como parâmetro o ano.
        Disponíveis os anos entre 2010 e 2021.
        ''' 
        sleep(2)
        #cria o dicionário com os anos para contorlar o xpath de cada ano
        self.listaDict = {}
        #o xpath de cada ano possui uma sequencia de 1 a 13, atraves do decremento da variavel inc consigo indicar o ano correto
        self.inc = 13
        #adicionando ao dicionario o ano e seu respectivo xpath
        for i in range(2010, 2022):
            self.listaDict[i] = '//*[@id="pn-selecao-anual"]/div/a['+str(self.inc)+']'
            self.inc = self.inc - 1
                   
        #para escolher o ano; se não estiver na lista retorna erro personalizado
        try:
            #atraves do ano escolhido busca o xpath correspondente dentro do dicionario
            self.driver.find_element(by='xpath', value=self.listaDict[ano]).click()
            
        except:
            #executa a classe de exceção para exibir o erro
            raise ExcecaoAnoInvalido(f'O ano digitado {ano}, não é um ano válido ou não está na lista de anos que vão de 2010 à 2021.')   
    
    #método para coletar todas as informações disponíveis no site
    def coleta_dados(self):
        '''
        Método para extrair as informações de posição, título, autor, editora, categoria, isbn, número de páginas e volumes vendidos.
        Cria o dataframe com as informações extraídas.
        Retorna o dataframe criado.
        É necessário passar como parâmetro o nome do dataframe.
        '''
        #listas para guardar as informações do site, necessário para criar o dataframe
        self.posicao   = []
        self.titulo    = []
        self.autor     = []
        self.editora   = []
        self.categ     = []
        self.categoria = []
        self.isbnPn    = []
        self.isbn      = []
        self.pag       = []
        self.paginas   = []
        self.vendidos  = []
        
        #aqui clicamos em cada livro para exibir outras informações necessárias para a extração
        for item in self.driver.find_elements(by='class name', value='pn-ranking-livro-nome'):
            item.click()
            #tempo de espera necessário, não abre todos os detalhes quando o tempo é inferior a 1.5s
            sleep(1.5)
        
        #para pegar posição de venda do livro 
        for item in self.driver.find_elements(by='class name',value='pn-ranking-livros-posicao-numero'):
            self.posicao.append(item.text)
        
        #para o titulo do livro
        for item in self.driver.find_elements(by='class name',value='pn-ranking-livro-nome'):
            self.titulo.append(item.text)
        
        #para a editora do livro
        for item in self.driver.find_elements(by='class name',value='pn-ranking-livro-editora'):
            self.editora.append(item.text)
        
        #para o autor do livro
        for item in self.driver.find_elements(by='class name',value='pn-ranking-livro-autor'):
            self.autor.append(item.text)
        
        #para a categoria do livro
        for itemC in self.driver.find_elements(by='class name',value='pn-ranking-livro-categoria'):
            self.categ.append(itemC.text)
            #tratando as informações retornadas do site
            for x in self.categ:
                itemC = x
            for y in ['Categoria ']:
                itemC = itemC.replace(y, "")
                self.categoria.append(itemC) 
        
        #para o isbn do livro
        for itemISBN in self.driver.find_elements(by='xpath', value='//div[@class="pn-ranking-livro-isbn"]'):
            self.isbnPn.append(itemISBN.text)
            #tratando as informações retornadas do site
            for x in self.isbnPn:
                itemISBN = x
            for y in ['ISBN ']:
                itemISBN = itemISBN.replace(y, "")
            for a in ['-']:
                itemISBN = itemISBN.replace(a, "")
                self.isbn.append(itemISBN)
        
        #para quantidade de paginas do livro
        for item in self.driver.find_elements(by='class name',value='pn-ranking-livro-paginas'):
            self.pag.append(item.text)
            for x in self.pag:
                item = x
            for y in ['Páginas ']:
                item = item.replace(y, "")
                self.paginas.append(item)
        
        #para número de volumes vendidos do livro
        for item in self.driver.find_elements(by='class name',value='pn-ranking-livros-posicao-volume'):
            self.vendidos.append(item.text)

        #criando dataframe e definindo nome e ordem das colunas
        self.dataframe = pd.DataFrame(list(zip(self.posicao, self.titulo, self.autor, self.editora, self.categoria, self.isbn, self.paginas, self.vendidos)),
                      columns=['posicao', 'titulo', 'autor', 'editora', 'categoria', 'isbn', 'numero de paginas', 'volumes vendidos'])

        return self.dataframe

    def salvar_dataframe(self, dataframe, nome_arquivo):
        '''
        Salva o dataframe em arquivo xlsx
        Necessário passar como parâmetro o nome do arquivo.
        '''
        self.dataframe.to_excel(nome_arquivo+'.xlsx')
        
    #fecha a janela após concluir a extração
    def fecha_browser(self):
        '''
        Fecha a janela após concluir a extração
        '''
        self.driver.close()