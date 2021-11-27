import requests
from bs4 import BeautifulSoup

class Periodo():
    def __init__(self, ano):
        self.ano = ano
    def extrair(self):
        global tabela
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        titulos = soup.find_all("div", class_="pn-ranking-livro-nome")
        titulos_separado = [titulo.text.strip() for titulo in titulos]
        autores = soup.find_all("div", class_="pn-ranking-livro-autor")
        autores_separado = [autor.text.strip() for autor in autores]
        editoras = soup.find_all("div", class_="pn-ranking-livro-editora")
        editoras_separado = [editora.text.strip() for editora in editoras]
        resumos = soup.find_all("div", class_="pn-ranking-livro-resumo")
        resumos_separado = [resumo.text.strip() for resumo in resumos]
        isbns = soup.find_all("div", class_="pn-ranking-livro-isbn")
        isbns_separado = [isbn.text.strip() for isbn in isbns]
        categorias = soup.find_all("div", class_="pn-ranking-livro-categoria")
        categorias_separado = [categoria.text.strip() for categoria in categorias]
        paginas = soup.find_all("div", class_="pn-ranking-livro-paginas")
        paginas_separado = [pagina.text.strip() for pagina in paginas]
        tabela = {
            'titulo': titulos_separado,
            'autor': autores_separado,
            'editora': editoras_separado,
        #    'resumo': resumos_separado,
            'isbn': isbns_separado,
            'categoria': categorias_separado,
            'paginas': paginas_separado
        }
    def tabela(self):
        return tabela

class Semanal(Periodo):
    def __init__(self, ano, mes, dia):
        super().__init__(ano)
        self.mes = mes
        self.dia = dia
    def puxar(self):
        global url
        url = "https://www.publishnews.com.br/ranking/semanal/0/2020/12/18/0/0"
        a = list(url)
        a[49:53] = str(self.ano)
        a[54:56] = str(self.mes)
        a[57:59] = str(self.dia)
        url = "".join(a)

class Mensal(Periodo):
    def __init__(self, ano, mes):
        super().__init__(ano)
        self.mes = mes
    def puxar(self):
        global url
        url = "https://www.publishnews.com.br/ranking/mensal/0/2020/12/0/0"
        a = list(url)
        a[48:52] = str(self.ano)
        a[53:55] = str(self.mes)
        url = "".join(a)

class Anual(Periodo):
    def __init__(self, ano):
        super().__init__(ano)
    def puxar(self):
        global url
        url = "https://www.publishnews.com.br/ranking/anual/0/2020/0/0"
        a = list(url)
        a[47:51] = str(self.ano)
        url = "".join(a)
