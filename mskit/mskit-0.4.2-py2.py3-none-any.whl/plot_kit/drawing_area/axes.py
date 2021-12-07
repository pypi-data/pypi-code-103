import matplotlib.pyplot as plt


def isometric_axes(
        left_init=0.05, bottom_init=0.05, right_end=0.9, top_end=0.9,
        ax_col_gap=0.1, ax_row_gap=0.1,
        row_num=2, col_num=5,
        total_num=None,
        container=None,
        *figure_args
):  # TODO support new ax args
    if container is None:
        container = plt.figure(*figure_args)
    if isinstance(container, plt.Figure):
        new_ax_method = container.add_axes
    elif isinstance(container, plt.Axes):
        new_ax_method = container.inset_axes
    else:
        raise ValueError(f'container should be `Figure` or `Axes` or `None`, now {type(container)}')

    if isinstance(ax_col_gap, (float, int)):
        ax_col_gap = [ax_col_gap] * (col_num - 1)
    if isinstance(ax_row_gap, (float, int)):
        ax_row_gap = [ax_row_gap] * (row_num - 1)
    else:
        ax_row_gap = ax_row_gap[::-1]
    if not total_num:
        total_num = row_num * col_num

    fig_length = right_end - left_init
    fig_height = top_end - bottom_init

    row_height = (fig_height - sum(ax_row_gap)) / row_num
    col_length = (fig_length - sum(ax_col_gap)) / col_num

    ax_x = [left_init + sum(ax_col_gap[:i]) + col_length * i for i in range(col_num)]
    ax_y = [top_end - sum(ax_row_gap[:i]) - row_height * (i + 1) for i in range(row_num)]

    ax_num = 0
    axes_list = []
    for row_index, y in enumerate(ax_y):
        for col_index, x in enumerate(ax_x):
            if ax_num == total_num:
                break
            ax = new_ax_method([x, y, col_length, row_height])
            axes_list.append(ax)
            ax_num += 1

    return container, axes_list
