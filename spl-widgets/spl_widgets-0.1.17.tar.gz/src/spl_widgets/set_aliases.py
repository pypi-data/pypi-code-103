import os
modules_to_alias=["update_widgets", "widgets_help", "gorilla_clean", "stk_swx", "tuner"]
for n in modules_to_alias:
    os.system(f'alias {n}="python3 -m spl_widgets {n}')