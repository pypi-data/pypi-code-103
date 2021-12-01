import configparser
import pathlib
import getpass

def get_parameters() -> list:
    """This funciton gets parameters from user

    Returns:
        list: a list of all parameters that are required for config
    """
    github_token = getpass.getpass("GitHub access token: ")
    repo_name= str(input("Please enter your repo name: "))
    repo_owner = str(input("Please enter your repo owner: "))
    action_name = str(input("Please enter the name of the action you would like to use: "))
    harbor_username = str(input("Please enter your harbor username: "))
    harbor_token = getpass.getpass("Harbor access token: ")
    config_list = [github_token,repo_name,repo_owner,action_name,harbor_username,harbor_token]
    return config_list

def write_to_config(config : configparser.ConfigParser , values_to_write : "list[str]") -> None:
    """This functions creates a config file from parameters supplied

    Args:
        config (configparser.ConfigParser): The config tempalte that is used to create config
        values_to_write (list[str]): the values to populate config with
    """
    new_path = pathlib.Path.cwd() / "config" / "config.ini"
    count = -1 # this count is used to enumerate thought the nested loop of options
    for section in config.sections():
        for option in config.options(section):
            count += 1
            config.set(section,option,values_to_write[count])
    with open(new_path,"w") as f:
        config.write(f)

def main(path_to_config_template) -> None:
    """Main function

    Args:
        path_to_config_template (pathlib.Path): the path to the config template
    """
    config = configparser.ConfigParser()
    path = pathlib.Path.cwd() / path_to_config_template
    config.read(path)
    values_to_write = get_parameters()
    write_to_config(config,values_to_write)
