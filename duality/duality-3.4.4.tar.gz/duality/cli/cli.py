def menu():
    print('AVAILABLE FEATURES')
    print(' 1 | Monte Carlo Simulation.')
    print(' 2 | Dijkstra algorithm.')
    print(' 3 | Economic Order Quantity.')
    print(' 4 | Exit.')


def dualityCLI():
    from duality.objects import MonteCarlo
    from duality.objects import Dijkstra
    from duality.objects import EOQ
    import pandas as pd
    while True:
        menu()
        choice = input('Choose an option: ')
        if choice == '4':
            break
        file_des = input('File destination (without quotation marks): ')
        file_type = input('Enter file type csv/xlsx/json): ')
        if file_type == 'xlsx':
            data = pd.read_excel(file_des)
        elif file_type == 'csv':
            data = pd.read_csv(file_des)
        elif file_type == 'json':
            data = pd.read_json(file_des)
        else:
            print('Only csv, xlsx and json files supported.')
            break
        file_col = input('Enter column name (without quotation marks): ')
        data = data[file_col]
        MC = MonteCarlo()
        simulations = int(input('Enter number of simulations: '))
        period = int(input('Enter desired period: '))
        MC.execute(data, simulations, period)
        action = input('Actions: graph, change, stats, risk, hist, menu, help: ')
        if action == 'graph':
            MC.graph()
        if action == 'change':
            print('Unavailable outside of IPython Notebook.')
            MC.get_change()
        if action == 'stats':
            print('Unavailable outside of IPython Notebook.')
            MC.get_stats()
        if action == 'risk':
            sample = int(input('Number of iterations: '))
            MC.get_risk(sample)
        if action == 'hist':
            MC.hist()
        if action == 'menu':
            menu()
            print('Exiting.')
            break
        if action == 'help':
            print('Execute print(help(duality)) function.')

'''
funcs = {
"json": some_func,
"csv": other_func
}
#other code
data = funcs[file_type](file_des)
'''

if __name__ == '__main__':
    dualityCLI()