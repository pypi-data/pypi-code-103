from .extrator import Extrator_bne

class Descritor(Extrator_bne):

    def candidaturaLivre(self):
        #Busca as candidaturas livres
        return self.df.loc[self.df['Candidatura']=='Candidatura Livre']
    #    descritor.df.loc[descritor.df['Candidatura']=='Candidatura Livre']

    def candidaturaPaga(self):
        #Busca as candidaturas pagas
        return self.df.loc[self.df['Candidatura']=='Candidatura Paga']

    def homeOffice(self):
        #Busca o trabalho home_office
        return self.df.loc[self.df['Forma de Trabalho']=='Home Office']

    def presencial(self):
        #Busca o trabalho Presencial
        return self.df.loc[self.df['Forma de Trabalho']=='Trabalho Presencial']

    def combinar(self):
        #Busca salarios à combinar
        return self.df.loc[self.df['Salario']=='a combinar']
