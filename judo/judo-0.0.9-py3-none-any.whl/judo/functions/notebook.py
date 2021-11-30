AVAILABLE_FUNCTIONS = {"running_in_ipython", "remove_notebook_margin"}


def running_in_ipython() -> bool:
    """Return ``True`` if the code is this function is being called from an IPython kernel."""
    try:
        from IPython import get_ipython

        return get_ipython() is not None
    except ImportError:
        return False


def remove_notebook_margin(output_width_pct: int = 80):
    """Make the notebook output wider."""
    from IPython.core.display import HTML

    html = (
        "<style>"
        ".container { width:" + str(output_width_pct) + "% !important; }"
        ".input{ width:70% !important; }"
        ".text_cell{ width:70% !important;"
        " font-size: 16px;}"
        ".title {align:center !important;}"
        "</style>"
    )
    return HTML(html)
