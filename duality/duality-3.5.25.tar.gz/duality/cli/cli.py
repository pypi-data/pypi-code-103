#dualityCLI version.
__CLIversion__ = 'v1.14'

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
            print('=== ENTERING MONTECARLO CLIENT... ===\n')
            MonteCarloCLI()
        elif choice == '2':
            print('=== ENTERING DIJKSTRA CLIENT... ===\n')
            DijkstraCLI()
        elif choice == '3':
            print('=== ENTERING EOQ CLIENT... ===\n')
            EOQCLI()
        elif choice == '4':
            print('Exiting...')
            break
        else:
            print('=== OPTION NOT EXISTENT OR AVAILABLE, PLEASE WRITE THE EXISTING NUMBER FROM THE MENU TO CONTINUE. ===')

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
        print('=== ONLY CSV, XLSX AND JSON FILES SUPPORTED, RESTARTING... ===\n')
        MonteCarloCLI()
    file_col = input('\nEnter column name: ').replace("'", '"').strip('"')
    try:
        data = data[file_col]
    except KeyError:
        print('=== INVALID COLUMN NAME, RESTARTING... ===\n')
        MonteCarloCLI()
    MC = MonteCarlo()
    simulations = int(input('Enter number of simulations: '))
    period = int(input('Enter desired period: '))
    executed = MC.execute(list_of_values = data, num_sims = simulations, time_seq = period)
    while True:
        action = input('ACTIONS: graph, change, values, stats, risk, hist, home, help: ')
        if action == 'graph':
            title = input('Title: ')
            x_axis = input('X axis title:')
            y_axis = input('Y axis title:')
            MC.graph(graph_title = title, x_title = x_axis, y_title = y_axis)
        elif action == 'change':
            print('1 | csv')
            print('2 | xlsx')
            print('3 | json')
            file_type = input('\nEnter the number or name of file type:')
            output = MC.get_change()
            try:
                save_to(output, 'change', choice = file_type)
            except:
                raise Exception('=== UNABLE TO SAVE, PLEASE RUN THE TERMINAL AS AN ADMINISTRATOR. ===\n')
        elif action == 'values':
            print('1 | csv')
            print('2 | xlsx')
            print('3 | json')
            file_type = input('\nEnter the number or name of file type:')
            try:
                save_to(executed, 'values', choice = file_type)
            except:
                raise Exception('=== UNABLE TO SAVE, PLEASE RUN THE TERMINAL AS AN ADMINISTRATOR. ===\n')
        elif action == 'stats' or action == 'statistics':
            MC.get_stats()
        elif action == 'risk':
            sample = int(input('Number of iterations to measure risk on: '))
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
                print('=== INVALID METHOD. ===\n')
        elif action == 'home':
            break
            CLI()
        elif action == 'help':
            print('https://github.com/dkundih/duality\n')
        else:
            print('=== INVALID ACTION. ===\n')

#save helper for cleaner code.
def save_to(file, func_name, choice):
    import pandas as pd
    import os
    if choice == '1' or choice == 'csv':
        extension = '.csv'
        file.to_csv('duality.MonteCarlo - ' + func_name + extension)
        print(os.path.join(os.getcwd() + '\duality.MonteCarlo - ' + func_name + extension))
    elif choice == '2' or choice == 'xlsx':
        extension = '.xlsx'
        file.to_excel('duality.MonteCarlo - ' + func_name + extension)
        print(os.path.join(os.getcwd() + '\duality.MonteCarlo - ' + func_name + extension))
    elif choice == '3' or choice == 'json':
        extension = '.json'
        file.to_json('duality.MonteCarlo - ' + func_name + extension)
        print(os.path.join(os.getcwd() + '\duality.MonteCarlo - ' + func_name + extension))
    else:
        print('=== NO OPTION CHOSEN, EXITING THE MENU... =\n')
#Dijkstra client extension.
def DijkstraCLI():

    '''

    (FUNCTION INFO)
    ---------------

    duality.DijkstraCLI - Dijkstra client extension.

    '''

    from duality.objects import Dijkstra
    while True:
        action = input('ACTIONS: home, help: ')
        if action == 'home':
            break
            CLI()
        elif action == 'help':
            print('https://github.com/dkundih/duality\n')
        else:
            print('=== INVALID ACTION. ===\n')

#EOQ client extension.
def EOQCLI():

    '''

    (FUNCTION INFO)
    ---------------

    duality.EOQCLI - EOQ client extension.

    '''

    from duality.objects import EOQ
    while True:
        action = input('ACTIONS: home, help: ')
        if action == 'home':
            break
            CLI()
        elif action == 'help':
            print('https://github.com/dkundih/duality\n')
        else:
            print('=== INVALID ACTION. ===\n')

#runs client.
if __name__ == '__main__':
    CLI()
