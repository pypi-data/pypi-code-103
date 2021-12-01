from openpyxl.styles.colors import COLOR_INDEX

def get_color_rgb(color):
    # Only support rgb
    if color.type == 'rgb':
        color = '00' + color.rgb[2:]
    else:
        color = '00000000'
    return color

def get_color_index_by_rgb(color):
    return COLOR_INDEX.index(color)

def get_color_rgb_by_index(index):
    if index == 32767:
        index = 0
    return COLOR_INDEX[index % 64]