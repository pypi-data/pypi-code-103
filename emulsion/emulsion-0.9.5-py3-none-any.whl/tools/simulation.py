"""A Python implementation of the EMuLSion framework.
(Epidemiologic MUlti-Level SImulatiONs).

Tools for providing a generic simulation class.

"""

import abc
from   pathlib        import Path
from   os.path        import exists

import progressbar
import numpy          as     np
import pandas         as     pd

from   sqlalchemy     import create_engine

from   emulsion.model import EmulsionModel

#   ____        _               _   __  __
#  / __ \      | |             | | |  \/  |
# | |  | |_   _| |_ _ __  _   _| |_| \  / | __ _ _ __   __ _  __ _  ___ _ __
# | |  | | | | | __| '_ \| | | | __| |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
# | |__| | |_| | |_| |_) | |_| | |_| |  | | (_| | | | | (_| | (_| |  __/ |
#  \____/ \__,_|\__| .__/ \__,_|\__|_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|
#                  | |                                        __/ |
#                  |_|                                       |___/

class OutputManager(object):
    """Manager to handle different outputs (csv, database,... etc)

    """
    def __init__(self, model=None, output_dir=''):
        """Initialize the output manager, specifying the model and the
        directory where outputs will be stored.

        """
        self.model = model
        self.output_dir = output_dir

        # database engine
        self.engine = None
        self.counts_filename = None
        # We choose csv file by default
        self.output_type = 'csv'
        self.update_output_type()
        self.update_output_information()

    def update_output_type(self):
        """Update output type if specified in model

        """
        if 'type' in self.model.outputs:
            self.output_type = self.model.outputs['type']

    def update_output_information(self):
        """Update csv file path or database connection engine

        """
        if self.output_type == 'database':
            database_information = self.model.outputs['database_information']

            host = database_information['server_name']
            port = database_information['port']
            host = '{}:{}'.format(host, port) if port else host

            # dialect+driver://username:password@servername:port/database
            connection = '{}+{}://{}:{}@{}/{}'.format(
                database_information['dialect'],
                database_information['driver'],
                database_information['username'],
                database_information['password'],
                host,
                database_information['database'])
            self.engine = create_engine(connection)
            # self.engine.raw_connection()
            self.output_dir = self.output_dir.replace('/', '_')

        elif self.output_type == 'csv':
            filename = 'counts.csv'
            self.counts_filename = str(Path(self.output_dir, filename))
        else:
            print('unknown output type !!!{]!!!')

    def update_outputs(self, df=None):
        """Update outputs: writing in csv file or in database

        """
        if self.output_type == 'csv':
            header = not exists(self.counts_filename)
            with open(self.counts_filename, 'a') as f:
                df.to_csv(f, header=header, index=False)
        elif self.output_type == 'database':
            df.to_sql(self.output_dir, self.engine, if_exists='append',
                      index=False, chunksize=10000)


#           _         _                  _    _____ _                 _
#     /\   | |       | |                | |  / ____(_)               | |
#    /  \  | |__  ___| |_ _ __ __ _  ___| |_| (___  _ _ __ ___  _   _| | __ _
#   / /\ \ | '_ \/ __| __| '__/ _` |/ __| __|\___ \| | '_ ` _ \| | | | |/ _` |
#  / ____ \| |_) \__ \ |_| | | (_| | (__| |_ ____) | | | | | | | |_| | | (_| |
# /_/    \_\_.__/|___/\__|_|  \__,_|\___|\__|_____/|_|_| |_| |_|\__,_|_|\__,_|

class AbstractSimulation(object):
    """Abstract class of any Simulation class. Nothing special.

    """
    def __init__(self, start_id=0, model_path='', model=None, stock_agent=True,
                 output_dir='outputs/', target_agent_class=None,
                 save_results=True, **_):
        # ID of simulation
        self.start_id = start_id
        self.model = EmulsionModel(filename=model_path) if model is None else model
        self.stock_agent = stock_agent
        self.target_agent_class = target_agent_class
        self.output_manager = OutputManager(model=self.model, output_dir=output_dir)
        self.save_results = save_results

        filename = 'counts.csv'
        self.counts_filename = str(Path(output_dir, filename))

    @abc.abstractmethod
    def evolve(self, steps=1):
        """Operations to perform at each time step."""
        pass
    @abc.abstractmethod
    def run(self):
        """Entry point to simulation execution."""
        pass

    def update_csv_counts(self, df, header=True, dparams={}):
        """Update the CSV recording of populations in each state."""
        if self.save_results:
            for name, value in dparams.items():
                df.insert(0, name, value)
            # with open(self.counts_filename, 'a') as f:
            #     df.to_csv(f, header=header, index=False)
            self.output_manager.update_outputs(df=df)

    def counts_to_csv(self):
        """Record the counts into a CSV file."""
        self.counts.to_csv(self.counts_filename, index=False)

#   _____ _                 _       _   _
#  / ____(_)               | |     | | (_)
# | (___  _ _ __ ___  _   _| | __ _| |_ _  ___  _ __
#  \___ \| | '_ ` _ \| | | | |/ _` | __| |/ _ \| '_ \
#  ____) | | | | | | | |_| | | (_| | |_| | (_) | | | |
# |_____/|_|_| |_| |_|\__,_|_|\__,_|\__|_|\___/|_| |_|

class Simulation(AbstractSimulation):
    """Simulation class can do a 'single' run (one repetition) of a given
    model (Intra or Inter herd).  For several repetition, please check
    out MultiSimulation class.

    """
    def __init__(self, steps=300, simu_id=0, **others):
        """Create an instance of simulation."""
        super().__init__(**others)
        self.simu_id = simu_id
        self.steps = steps

        self.agent = self.target_agent_class(**others)

        self.outputs_period = self.model.outputs[self.agent.level]['period']\
                                if self.agent.level in self.model.outputs else 1

    def init_agent(self, **others):
        """Create an agent from the target class."""
        return self.target_agent_class(**others)

    def evolve(self, steps=1):
        """Make the target agent evolve."""
        for _ in range(steps):
            self.agent.evolve()

    def run(self, dparams={}):
        """Make the simulation progress."""
        bar_run = progressbar.ProgressBar(widgets=[
            ' [ Simulation #%s] '%(self.simu_id,),
            progressbar.Bar(),
        ])
        for step in bar_run(range(self.steps)):
            if step % self.outputs_period == 0 and step != 0:
                header = not exists(self.counts_filename)
                self.update_csv_counts(self.counts, header=header, dparams=dparams)
            self.agent.evolve()

    @property
    def counts(self):
        """Return a pandas DataFrame contains counts of each process if existing.
        TODO: column steps need to be with one of process
        and NO column steps for inter herd

        """
        res = self.agent.counts
        res.insert(0, 'simu_id', self.simu_id)
        return res
        # res = None
        # for comp in self.agent:
        #     try:
        #         counts = pd.DataFrame(comp.counts)
        #         res = res.join(counts, lsuffix='res', rsuffix='counts')\
        #                                         if not res is None else counts
        #     except AttributeError:
        #         pass
        #     except Exception as e:
        #         raise e
        # if not res is None:
        #     res.insert(0, 'steps', res.index)
        #     res.insert(0, 'simu_id', self.simu_id)
        # return res

#  __  __       _ _   _  _____ _                 _       _   _
# |  \/  |     | | | (_)/ ____(_)               | |     | | (_)
# | \  / |_   _| | |_ _| (___  _ _ __ ___  _   _| | __ _| |_ _  ___  _ __
# | |\/| | | | | | __| |\___ \| | '_ ` _ \| | | | |/ _` | __| |/ _ \| '_ \
# | |  | | |_| | | |_| |____) | | | | | | | |_| | | (_| | |_| | (_) | | | |
# |_|  |_|\__,_|_|\__|_|_____/|_|_| |_| |_|\__,_|_|\__,_|\__|_|\___/|_| |_|

class MultiSimulation(AbstractSimulation):
    """MultiSimulation can handle multiple repetitions of a given model.
    For sensibility study (same model with different values of variables),
    please check out SensitivitySimulation.

    """
    def __init__(self, multi_id=0, nb_simu=200, set_seed=False, **others):
        super().__init__(**others)
        self.multi_id = multi_id
        self.nb_simu = nb_simu
        self.set_seed = set_seed
        self.others = others

        self.d_simu = dict()

    def __iter__(self):
        return self.d_simu.values().__iter__()

    def evolve(self, steps=1):
        for simu in d_simu.values():
            simu.evolve(steps=steps)

    def run(self, update=True, dparams={}):
        """Run all simulation one by one.
        TODO:
          - ProgressBar don't work for parallel computing

        """
        for simu_id in range(self.start_id, self.start_id+self.nb_simu):
            if self.set_seed:
                np.random.seed(simu_id)
            if 'model' not in self.others:
                self.others['model'] = self.model
            simu = Simulation(simu_id=simu_id, **self.others)

            simu.run(dparams=dparams)

            if self.stock_agent:
                self.d_simu[simu_id] = simu

            # if update:
            #     header = not exists(self.counts_filename)
            #     self.update_csv_counts(simu.counts, header=header, dparams=dparams)

    @property
    def counts(self):
        l_counts = [simu.counts for simu in self]
        return pd.concat(l_counts).reset_index(drop=True)

    def write_dot(self):
        self.model.write_dot(self.others['output_dir'])


#   _____                _ _   _       _ _          _____ _                 _
#  / ____|              (_) | (_)     (_) |        / ____(_)               | |
# | (___   ___ _ __  ___ _| |_ ___   ___| |_ _   _| (___  _ _ __ ___  _   _| |
#  \___ \ / _ \ '_ \/ __| | __| \ \ / / | __| | | |\___ \| | '_ ` _ \| | | | |
#  ____) |  __/ | | \__ \ | |_| |\ V /| | |_| |_| |____) | | | | | | | |_| | |
# |_____/ \___|_| |_|___/_|\__|_| \_/ |_|\__|\__, |_____/|_|_| |_| |_|\__,_|_|
#                                             __/ |
#                                            |___/
#        _   _
#       | | (_)
#   __ _| |_ _  ___  _ __
#  / _` | __| |/ _ \| '_ \
# | (_| | |_| | (_) | | | |
#  \__,_|\__|_|\___/|_| |_|

class SensitivitySimulation(AbstractSimulation):
    """SensitivitySimulation can handle sensibility study with a given
    pandas DataFrame of parameters or a path linked with file which contains
    scenarios of parameters. Then it will be transformed to a dictionary of
    scenario in the ```d_scenario``` attribute.

    For instance, d_scenario could be the form (QFever model example) :
        {0: {'m': 0.7, 'q': 0.02 ...},
         1: {'m': 0.5, 'q': 0.02 ...},
         2: ...,
         ... }
    """
    def __init__(self, scenario_path=None, df=None, nb_multi=None, **others):
        super().__init__(**others)
        self.others = others
        self.others['start_id'] = 0

        # Retrieving DataFrame and creation of dictionnary of simulation/scenario
        df = pd.read_csv(scenario_path) if df is None else df
        self.nb_multi = len(df) if nb_multi is None else nb_multi
        self.d_scenario = df.to_dict(orient='index')
        self.d_multi = dict()

    def run(self):
        """Make the simulation advance."""
        bar_sens = progressbar.ProgressBar(widgets=[
            ' [ Sensitivity Simulation ] ',
            progressbar.Bar(),
            ' (', progressbar.ETA(), ') ',
        ])

        # for multi_id, scenario in bar_sens(self.d_scenario.items()):
        for multi_id in bar_sens(range(self.start_id, self.start_id+self.nb_multi)):
            scenario = self.d_scenario[multi_id]
            # Copy a model
            model = self.model.copy()
            # Modify model
            for name, value in scenario.items():
                try:
                    model.set_value(name, value)
                except Exception:
                    self.others[name] = value

            # Instantiate MultiSimulation and execution
            multi = MultiSimulation(multi_id=multi_id, model=model, **self.others)
            multi.run(dparams=scenario)

            if self.stock_agent:
                self.d_multi[multi_id] = multi

            # if update:
            #     header = not exists(self.counts_filename)

            #     counts = multi.counts
            #     for name, value in self.d_scenario[multi_id].items():
            #         counts.insert(0, name, value)

            #     self.update_csv_counts(counts, header=header)

    @property
    def counts(self):
        l_counts = []
        for multi_id, multi in self.d_multi.items():
            counts = multi.counts
            for name, value in self.d_scenario[multi_id].items():
                counts.insert(0, name, value)

            counts.insert(0, 'scenario_id', multi_id)
            l_counts.append(counts)

        return pd.concat(l_counts).reset_index(drop=True)

    def write_dot(self):
        self.model.write_dot(self.others['output_dir'])
