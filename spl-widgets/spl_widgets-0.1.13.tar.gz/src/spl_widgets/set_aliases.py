import os
modules_to_alias=["update_widgets","widgets_help","gorilla_clean","stk_swx","tuner"]

def main():
    for module in modules_to_alias:
        alias_str = f'alias {module}="python3 -m spl_widgets {module}"'
        os.system(alias_str)

if __name__ == "__main__": main()