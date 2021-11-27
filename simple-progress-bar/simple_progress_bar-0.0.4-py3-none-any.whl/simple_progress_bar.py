
def print_progressbar(value: int, max_value: int, char: str = '|', blank: str = ' ', show_value: bool = True, description: str = '', width_bar: int = 100, multiply_char: int = 1):
    """
    This function will print a progress bar
    It should be used inside a for loop 

    Parameters
    ----------

    value : int
        current value of the progress bar
    max_value : int
        max value of the progress bar
    char : str, optional
        char printed as the progress bar is updated (default is |)
    blank : str, optional
        char printed for empty spaces in progress bar (default is [space])
    show_value : bool, optional
        define if current value should be printed alongside progress bar (default is True)
    description : str, optional
        text description for each increment (default is '')
    width_bar : int, optional
        width of the progress bar - char count (default is 100)
    multiply_char : int, optional
        multiply char for each increment in the progress bar (default is 1)

    """
    char_base = char * multiply_char
    char_blank = blank * multiply_char
    bars = []
    limit = width_bar 

    for i in range(limit):
        
        base = i * char_base
        blank = (limit - i) * char_blank
        bar = base + blank
        bars.append(bar)

    bars.append(width_bar * char_base)
    
    bar_constant = 100 / width_bar
    p = value * 100 / max_value 
    b_index = int(int(p) / bar_constant)  
    b = bars[b_index] if p/bar_constant >= b_index and p/bar_constant < (b_index + 1) else ''
    final_string = f'|{b}| -> {int(p)} % {description}' if show_value else f'|{b}|'
    
    print(f'\r {final_string}', end='')
    if value == max_value:
        print('\n')


if __name__ == "__main__":
    print("Should not be called directly")