import click
import os
from simple_term_menu import TerminalMenu
import shutil
import pathlib
import tempfile
import pkg_resources

@click.group()
def main():
    pass


@main.command()
@click.argument('name')
def create_project(name):
    path = os.getcwd()
    path_project = os.path.join(path, name)
    # create_readme(name,path_project)
    # os.chdir(path_project)
    with tempfile.TemporaryDirectory() as directory_name:
        the_dir = pathlib.Path(directory_name)
        the_dir_proyect = os.path.join(the_dir,'dashboard-template')
        os.chdir(the_dir)
        os.system('git clone --depth 1 -b master https://JohanBustos@bitbucket.org/imperiums/dashboard-template.git')
        shutil.copytree(the_dir_proyect, path_project)
    os.chdir(path_project)
    os.system('git remote rm origin')
    create_readme(name,path_project)
    print('''

    ---------------------

    🚀 launch project

    ---------------------
    cd {}
    pipenv shell
    python main.py
    '''.format(name))
    # create_conexion_origen(path_project)

@main.command()
@click.argument('path_project')
def create_conexion(path_project):
    create_conexion_origen(path_project)

# @main.command()
# def get_path():
#     new_path = pkg_resources.resource_filename(__name__,'files_template')
#     print(new_path)



def create_conexion_origen(path_project):
    print('Seleccione los origenes de datos')
    options_db = ["Postgres", "Oracle", "Mysql", "Excel", "CSV"]
    terminal_menu = TerminalMenu(
        options_db,
        multi_select=True,
        show_multi_select_hint=True,
    )
    optiondb = terminal_menu.show()
    for option in optiondb:
        if option == 0:
            path_file = os.path.join(path_project, 'data','dbPostgress.py')
            with open(path_file, 'w', encoding='utf-8') as f:
                f.close()
        if option == 1:
            path_file = os.path.join(path_project, 'data','dbOracle.py')
            with open(path_file, 'w', encoding='utf-8') as f:
                f.close()
        if option == 2:
            path_file = os.path.join(path_project, 'data','dbMysql.py')
            with open(path_file, 'w', encoding='utf-8') as f:
                f.close()
        if option == 3:
            path_file = os.path.join(path_project, 'data','dbExcel.py')
            with open(path_file, 'w', encoding='utf-8') as f:
                f.close()
        if option == 4:
            path_file = os.path.join(path_project, 'data','dbCsv.py')
            with open(path_file, 'w', encoding='utf-8') as f:
                f.close()

def create_readme(name_project, path_project):
    path_file =  os.path.join(path_project,'README.md')
    name_developer = input('Name Developer:')
    email_developer = input('E-mail Developer:')
    message_to_write = '''

# IMPERIUMS DASHBOARD :rocket:
<a href="https://python.org/pypi/pipenv" rel="nofollow"><img alt="image" src="https://warehouse-camo.ingress.cmh1.psfhosted.org/6b118bbaf88878b4a18939f6b4e040207d87f3b5/68747470733a2f2f696d672e736869656c64732e696f2f707970692f707976657273696f6e732f706970656e762e737667"></a>

 > This project is a dashboard created by imperiums for {}

# :file_folder: Files

Below you will see the structure of the project
```
        {}
        │   README.md
        │   Pipfile    
        │	main.py
        |   .env
        │	callbacks.py
        └───src
        │   └─── components (private library -- Imperiums)
        │   └─── data
        │   └─── app.py
        │   └─── callbacks.py
        │   └─── layout.py
```
## :computer: Execution

- Firts time
    ```bash
        $ cd name_project
        $ python main.py
    ```
- Anytime

    ```bash
        $ cd name_project
        $ pipenv shell
        $ python main.py
    ```

# Authors

- [Imperiums Company](imperiums.com.co)
- Developers 
    :bust_in_silhouette:  {} ({})
    '''.format(name_project, name_project, name_developer, email_developer)
    with open(path_file,'w') as file:
        file.write(message_to_write)
        file.close()

if __name__ == '__main__':
    main()
