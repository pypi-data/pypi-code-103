import configparser


def db_config() -> dict[str, str]:
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['database']

def reporting_to_dashboard() -> bool:
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config.getboolean('dashboard', 'report_to_dashboard')

def save_to_config(db_config: dict, report_to_dashboard=False):
    config = configparser.ConfigParser()
    config.add_section('dashboard')
    config.set('dashboard', 'report_to_dashboard', str(report_to_dashboard))
    
    config.add_section('database')
    config.set('database', 'host', db_config['host'])
    config.set('database', 'user', db_config['user'])
    config.set('database', 'password', db_config['password'])
    config.set('database', 'database', db_config['database'])

    with open('config.ini', 'w+') as configfile:
        config.write(configfile)

if __name__ == '__main__':
    print(db_config())
