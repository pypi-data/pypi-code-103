from browser import bind, document


@bind("#main_menu_burger", "click")
def burger_click(ev):
    document["main_menu"].classList.toggle('is-active')
    document["main_menu_burger"].classList.toggle('is-active')
