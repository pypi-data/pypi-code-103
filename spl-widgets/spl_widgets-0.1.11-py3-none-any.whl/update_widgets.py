import os
modules_to_alias=["update_widgets","widgets_help","gorilla_clean","stk_swx","tuner"]

def main():
    os.system("pip -qq install spl_widgets --upgrade")
    zprofile = f"{os.getenv('HOME')}/.zprofile"
    with open(zprofile,"r") as reader:
        lines = reader.readlines()

        for module in modules_to_alias:
            to_find = "python3 -m spl_widgets set_aliases\n"
            
            for i, line in enumerate(lines): 
                if "spl_widgets" in line and "alias" in line and not any([module in line for module in modules_to_alias]):
                    print(f"Removed old alias: {line[:-1]}")
                    lines[i]="KILL"+line
            
            if to_find not in lines:
                lines.append(to_find)
                print(lines)

    with open(zprofile, "w") as writer:
        writer.writelines([line for line in lines if not line.startswith("KILL")])