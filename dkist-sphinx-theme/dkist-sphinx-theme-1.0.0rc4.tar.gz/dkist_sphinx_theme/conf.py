import os
from . import get_html_theme_path

html_theme_path = get_html_theme_path()

html_theme = "dkist"

html_theme_options = {
    'navbar_links': [
        ("Documentation", "https://dkistdc-public-documentation.readthedocs-hosted.com", 1),
        # ("Data Portal", "https://d3a6qbwties1ot.cloudfront.net/dashboard", 1),
        ("User Tools", "https://dkistdc-dkist.readthedocs-hosted.com", 1),
        # ("Help Desk", "https://nso.atlassian.net/wiki/spaces/DHDT/pages/1738180434/DEV+DKIST+Data+Center+Archive+Help+Desk", 1),
        ("Calibration", "https://dkistdc-public-documentation.readthedocs-hosted.com/en/latest/calibration.html", 1),
        ("DKIST", "https://nso.edu/telescopes/dki-solar-telescope/", 1),
    ]
}
html_favicon = os.path.join(html_theme_path[0], html_theme, "static",
                            "img", "favico.ico")

html_sidebars = {
    '**': ['localtoc.html'],
    'search': [],
    'genindex': [],
    'py-modindex': [],
}
