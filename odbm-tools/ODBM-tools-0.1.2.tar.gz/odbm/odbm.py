import pandas as pd
from odbm.utils import extractParams, fmt

from odbm.mechanisms import *
from odbm.modifiers import *
DEFAULT_MECHANISMS = [  MichaelisMenten, OrderedBisubstrateBiproduct, MassAction, simplifiedOBB,
                        TX_MM,
                        LinearCofactor, HillCofactor, ProductInhibition
                    ]

class ModelBuilder:
    """
    A class used to keep species and reaction information and compile them into an Antamony model

    Attributes
    ----------
    mech_dict : str
        a dictionary with available Mechanisms
    species : pd.DataFrame
        dataframe where each row is a different species
    rxns : pd.DataFrame
        dataframe where each row is a different reaction

    Methods
    -------
    addMechanism(self, new_mechanism: Mechanism):
        Adds a new Mechanism to the internal mechanism dictionary 

    addSpecies(self, Label, StartingConc, Type = np.nan, Mechanism = np.nan, Parameters = np.nan):
        Adds a new species to the internal species dataframe 

    addReaction(self, Mechanism, Substrate, Product, Parameters, Enzyme = np.nan, Cofactor = np.nan, Label = np.nan):
        Adds a new reaction to the internal reaction dataframe
    
    applyMechanism(self, mechanism, species):
        WRITE DESCR

    writeSpecies(self, rxn):
        WRITE DESCR

    writeReaction(self, rxn):
        WRITE DESCR

    writeParameters(self, rxn):
        WRITE DESCR

    get_substrates(self, id: int or str, cofactors = True):
        Returns a list of susbtrates given a reaction index
    
    get_products(self, id: int or str):
        Returns a list of products given a reaction index
    
    compile():
        Iterates through all species and reactions and generates an Antimony string
    
    saveModel(self, filename:str):
        Saves the Antimony model to a text file

    """

    def __init__(self, species, reactions):
        self.mech_dict = {}
        [self.addMechanism(m) for m in DEFAULT_MECHANISMS]
        self.species = species
        self.rxns = reactions

    def addMechanism(self, new_mechanism: Mechanism):
        """Adds a new Mechanism to the internal mechanism dictionary 

        Parameters
        ----------
        new_mechanism (Mechanism): Mechanism class 
        """
        self.mech_dict[new_mechanism.name] = new_mechanism

    def addSpecies(self, Label, StartingConc, Type = np.nan, Mechanism = np.nan, Parameters = np.nan):
        """
        Adds a new species to the internal species dataframe

        Parameters
        ----------
        Label : str
        StartingConc : str
        Type : str, optional, by default np.nan
        Mechanism : str, optional, by default np.nan
        Parameters : str, optional, by default np.nan
        """
        args = locals()
        args.pop('self')
        # maybe check inputs??
        if not self.species['Label'].str.contains(Label).any():
            self.species = self.species.append(args,ignore_index = True) 

    def addReaction(self, Mechanism, Substrate, Product, Parameters, Enzyme = np.nan, Cofactor = np.nan, Label = np.nan):
        """
        Adds a new reactions to the internal reaction dataframe

        Parameters
        ----------
        Mechanism : str
        Substrate : str
        Product : str
        Parameters : str
        Enzyme : str, optional, by default np.nan
        Cofactor : str, optional, by default np.nan
        Label : str, optional, by default np.nan
        """
        args = locals()
        args.pop('self')
        # maybe check inputs??
        # maybe do something about the Label        
        self.rxns = self.rxns.append(args,ignore_index = True)

    def applyMechanism(self, mechanism, species):
        """[summary]

        Args:
            mechanism ([type]): [description]
            species ([type]): [description]

        Returns:
            [type]: [description]
        """        
        M = self.mech_dict[mechanism]
        substrate = fmt(species['Label'])
        label = M.generate_label(substrate)
        product = M.generate_product(substrate)
        parameters = species['Parameters']
        pdict = extractParams(parameters)

        def lookup(lbl:str):
            K = '0'
            for k in pdict.keys():
                if lbl in k:
                    K = pdict[k]
            return K

        if M.nS > 1:
            substrate = substrate +';'+ M.required_substrates
            for s in M.required_substrates.split(';'):
                self.addSpecies(s, lookup(s))

        if not np.isnan(M.nE):
            enzyme = M.required_enzyme
            for e in enzyme.split(';'):
                self.addSpecies(e, lookup(e))
        else:
            enzyme = np.nan

        if not np.isnan(M.nC):
            cofactor = M.required_cofactor
            for c in cofactor.split(';'):
                self.addSpecies(c, lookup(c))
        else:
            cofactor = np.nan

        for p in product.split(';'):
            self.addSpecies(p, lookup(p))

        self.addReaction(mechanism, substrate, product, parameters, enzyme, cofactor, Label = label)

    def writeSpecies(self, species):
        """[summary]

        Args:
            species ([type]): [description]

        Returns:
            [type]: [description]
        """        
        label = fmt(species['Label'])
        species['Label'] = label
        
        s_str = (label +'=' + str(species['StartingConc']) + '; \n')

        return s_str

    def writeReaction(self, rxn):
        """[summary]

        Args:
            rxn ([type]): [description]

        Raises:
            KeyError: [description]

        Returns:
            [type]: [description]
        """        
        m = rxn['Mechanism'].split(';')

        try:
            M = self.mech_dict[m[0].strip()](rxn)
        except KeyError:
            # bug here: throws error for no mechanism found even if issue is incorrect parameters
            raise KeyError('No mechanism found called '+m[0])
        
        rate_str = M.writeRate()
        for mod in m[1:]:
            MOD = self.mech_dict[mod.strip()](rxn)
            rate_str = MOD.apply(rate_str)

        return '\n' + M.writeEquation() + '; \n' + rate_str+'; '

    def writeParameters(self, rxn):
        """[summary]

        Args:
            rxn ([type]): [description]

        Returns:
            [type]: [description]
        """        
        p_str = ''
        if not pd.isnull(rxn['Parameters']):
            #initialize value
            kdict = extractParams(rxn['Parameters'])
            for key, value in kdict.items():
                p_str += (key+'_'+rxn['Label'] +'=' + str(value) + '; \n')
        else:
            raise('No parameters found for reaction '+rxn['Label'])
            # Diego: what about default parameters? say if we want to set all transcription rates to be the same

        return p_str

    def compile(self) -> str:
        """
        Iterates through all species and reactions and generates an Antimony string

        Returns
        -------
        str
            Antimony model string
        """
        s_str = '# Initialize concentrations \n'
        p_str = '\n# Initialize parameters \n'
        r_str = '# Define specified reactions \n'

        S = self.species.copy()
        for _,s in S.iterrows():
            if not pd.isnull(s['Mechanisms']):
                mechanisms = s['Mechanisms'].split(';')
                for m in mechanisms:
                        self.applyMechanism(m,s)

        for _, sp in self.species.iterrows():
            s_str += self.writeSpecies(sp)

        for _, rxn in self.rxns.iterrows():
            p_str += self.writeParameters(rxn) + '\n'
            r_str += self.writeReaction(rxn) + '\n'

        return s_str + p_str + r_str

    def saveModel(self, filename:str):
        """
        Saves the Antimony model to a text file

        Parameters
        ----------
        filename : str
        """
        with open(filename, 'w') as f:
            f.write(self.compile())

    def get_reaction(self, id):
        if type(id) is int:
            r = self.rxns.iloc[id]
        elif type(id) is str:
            r = self.rxns[self.rxns['Label'] == id]
        return r
    
    def get_substrates(self, id: int or str, cofactors = True) -> list:
        """
        Returns a list of susbtrates given a reaction index

        Parameters
        ----------
        id : int or str
            Reaction number or label
        cofactors : bool, optional
            Also return cofactors, by default True

        Returns
        -------
        List
        """
        r = self.get_reaction(id)

        if cofactors and (str(r['Cofactor']) != 'nan'):
            X = [*r['Substrate'].split(';'), *r['Cofactor'].split(';')]
        else:
            X = r['Substrate'].split(';')

        return list(map(fmt, X))

    def get_products(self, id: int or str) -> list:
        """
        Returns a list of products given a reaction index

        Parameters
        ----------
        id : int or str
            Reaction number or label

        Returns
        -------
        List
        """
        r = self.get_reaction(id)
        return list(map(fmt, r['Product'].split(';')))
