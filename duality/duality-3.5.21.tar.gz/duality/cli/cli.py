#dualityCLI version.
__CLIversion__ = 'v1.10'

#intro to the client.
def greet():
    print('\n - duality Command Line Interface © David Kundih -', __CLIversion__)

#menu.
def menu():
    print('-----------------------------')
    print('AVAILABLE FEATURES')
    print(' 1 | Monte Carlo simulation')
    print(' 2 | Dijkstra algorithm')
    print(' 3 | Economic Order Quantity')
    print(' 4 | Exit')
    print('-----------------------------')

#main client.
def CLI():

    '''

    (FUNCTION INFO)
    ---------------

    duality.CLI - main client that serves as an access to other module clients.

    '''

    greet()
    while True:
        menu()
        choice = input('Choose an option: ')
        if choice == '1':
            print('Entering Monte Carlo client...\n')
            MonteCarloCLI()
        elif choice == '2':
            print('Entering Dijkstra client...\n')
            DijkstraCLI()
        elif choice == '3':
            print('Entering EOQ client...\n')
            EOQCLI()
        elif choice == '4':
            print('Exiting...')
            break
        else:
            print('Option not existent or available, please write the existing number from the menu to continue.\n')

#MonteCarlo client extension.
def MonteCarloCLI():

    '''

    (FUNCTION INFO)
    ---------------

    duality.MonteCarloCLI - MonteCarlo client extension.

    '''

    import matplotlib.pyplot as plt
    from duality.objects import MonteCarlo
    import pandas as pd
    file = input('File path: ').replace("'", '"').strip('"')
    if str(file).endswith('.csv'):
        data = pd.read_csv(file)
        print('AVAILABLE COLUMNS: ')
        for col in data.columns:
            print(col)
    elif str(file).endswith('.xlsx'):
        data = pd.read_excel(file)
        print('AVAILABLE COLUMNS: ')
        for col in data.columns:
            print(col)
    elif str(file).endswith('.json'):
        data = pd.read_json(file)
        print('AVAILABLE COLUMNS: ')
        for col in data.columns:
            print(col)
    else:
        print('Only csv, xlsx and json files supported, restarting...\n')
        MonteCarloCLI()
    file_col = input('Enter column name: ').replace("'", '"').strip('"')
    try:
        data = data[file_col]
    except KeyError:
        print('Invalid column name, restarting...\n')
        MonteCarloCLI()
    MC = MonteCarlo()
    simulations = int(input('Enter number of simulations: '))
    period = int(input('Enter desired period: '))
    executed = MC.execute(list_of_values = data, num_sims = simulations, time_seq = period)
    while True:
        action = input('ACTIONS: graph, change, values, stats, risk, hist, home, restart, help: ')
        if action == 'graph':
            title = input('Title: ')
            x_axis = input('X axis title:')
            y_axis = input('Y axis title:')
            MC.graph(graph_title = title, x_title = x_axis, y_title = y_axis)
        elif action == 'change':
            print('1 | csv')
            print('2 | xlsx')
            print('3 | json')
            file_type = input('Enter the number of file type:')
            output = MC.get_change()
            try:
                save_to(output, 'change', choice = file_type)
            except:
                raise Exception('Unable to save, make sure you run the CLI in administrator mode.\n')
        elif action == 'values':
            print('1 | csv')
            print('2 | xlsx')
            print('3 | json')
            file_type = input('Enter the number of file type:')
            try:
                save_to(executed, 'values', choice = file_type)
            except:
                raise Exception('Unable to save, make sure you run the CLI in administrator mode.\n')
        elif action == 'stats' or action == 'statistics':
            MC.get_stats()
        elif action == 'risk':
            sample = int(input('Number of iterations: '))
            MC.get_risk(sample)
        elif action == 'hist' or action == 'histogram':
            x_axis = input('X axis title:')
            y_axis = input('Y axis title:')
            print('1 | Basic Histogram')
            print('2 | Empirical Rule Histogram')
            method = input('Enter histogram method: ')
            if method == '1':
                MC.hist(x_title = x_axis, y_title = y_axis)
            elif method == '2':
                MC.hist(x_title = x_axis, y_title = y_axis, method = 'e')
            else:
                print('Invalid method.')
        elif action == 'home':
            CLI()
        elif action == 'restart':
            MonteCarloCLI()
        elif action == 'help':
            print('https://github.com/dkundih/duality\n')
        else:
            print('Invalid action.\n')

#save helper for cleaner code.
def save_to(file, func_name, choice):
    import pandas as pd
    import os
    if choice == '1' or choice == 'csv':
        extension = '.csv'
        file.to_csv('duality.MonteCarlo - ' + func_name + extension)
        print(os.path.join(os.getcwd() + '\duality.MonteCarlo - ' + func_name + extension))
    if choice == '2' or choice == 'xlsx':
        extension = '.xlsx'
        file.to_excel('duality.MonteCarlo - ' + func_name + extension)
        print(os.path.join(os.getcwd() + '\duality.MonteCarlo - ' + func_name + extension))
    if choice == '3' or choice == 'json':
        extension = '.json'
        file.to_json('duality.MonteCarlo - ' + func_name + extension)
        print(os.path.join(os.getcwd() + '\duality.MonteCarlo - ' + func_name + extension))
    
#Dijkstra client extension.
def DijkstraCLI():

    '''

    (FUNCTION INFO)
    ---------------

    duality.DijkstraCLI - Dijkstra client extension.

    '''

    from duality.objects import Dijkstra
    while True:
        action = input('ACTIONS: home, restart, help: ')
        if action == 'home':
            CLI()
        elif action == 'restart':
            DijkstraCLI()
        elif action == 'help':
            print('https://github.com/dkundih/duality\n')
        else:
            print('Invalid action.\n')

#EOQ client extension.
def EOQCLI():

    '''

    (FUNCTION INFO)
    ---------------

    duality.EOQCLI - EOQ client extension.

    '''

    from duality.objects import EOQ
    while True:
        action = input('ACTIONS: home, restart, help: ')
        if action == 'home':
            CLI()
        elif action == 'restart':
            EOQCLI()
        elif action == 'help':
            print('https://github.com/dkundih/duality\n')
        else:
            print('Invalid action.\n')

#runs client.
if __name__ == '__main__':
    CLI()
