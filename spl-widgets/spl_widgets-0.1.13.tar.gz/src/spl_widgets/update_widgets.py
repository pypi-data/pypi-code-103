import os
modules_to_alias=["update_widgets","widgets_help","gorilla_clean","stk_swx","tuner"]

def main():
    os.system("pip -qq install spl_widgets --upgrade")
    zprofile = f"{os.getenv('HOME')}/.zprofile"
    with open(zprofile,"r") as reader:
        
        lines = reader.readlines()
        to_find = "python3 -m spl_widgets set_aliases\n"
        newlines = []
        
        for line in lines: 
            if not ( "spl_widgets" in line and "alias" in line ):
                newlines.append(line)
        
        if to_find not in newlines:
            newlines.append(to_find)

    with open(zprofile, "w") as writer:
        writer.writelines(newlines)

if __name__ == "__main__": main()