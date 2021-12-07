"""Module for controlling the Isoplot notebook"""

import io
import os
import logging
from pathlib import Path

import ipywidgets as widgets

mod_logger = logging.getLogger(f"isoplot.isoplot_notebook")

class IsoplotNb:

    def __init__(self, verbose=False):
        """ Initialize the widgets used in the dashboard and initial parameters """

        # Get home directory
        self.home = Path(os.getcwd())

        # Initiate child logger for class instances
        self.logger = logging.getLogger("isoplot.isoplot_notebook.IsoplotNb")
        handler = logging.StreamHandler()

        if verbose:
            handler.setLevel(logging.DEBUG)
        else:
            handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)

        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)

        # Initiate all the widgets

        self.metabolite_selector = widgets.SelectMultiple(options=self.metabolite_list,
                                                          value=self.metabolite_list[0],
                                                          description="Metabolites",
                                                          disabled=True)

        self.condition_selector = widgets.SelectMultiple(options=self.condition_list,
                                                        value=self.condition_list[0],
                                                        description="Conditions",
                                                        disabled=True)

        self.time_selector = widgets.SelectMultiple(options=[""],
                                                    value=("", ""),
                                                    description="Times",
                                                    disabled=True)

        self.mode_selector = widgets.Dropdown(options=["Static", "Interactive"],
                                              value="Static",
                                              description="Mode",
                                              disabled=True)

        self.plot_selector = widgets.Dropdown(options="",
                                              value="",
                                              description="Plot Type",
                                              disabled=True)

        self.run_name = widgets.Text(value="",
                                     placeholder="Input run name",
                                     description="Run Name",
                                     disabled=True)

        # Build layout

        pressed_btns = [self.generate_template_btn, self.submit_template_btn]
        pressed_btns_layout = widgets.HBox(pressed_btns)
        initial_btns = widgets.VBox(upload_btns_layout, pressed_btns_layout)

        selectors = [self.metabolite_selector, self.condition_selector, self.time_selector]
        selectors_layout = widgets.HBox(selectors)

        dropdowns = [self.plot_selector, self.mode_selector]
        dropdowns_layout = widgets.HBox(dropdowns)

        self.log_console = widgets.Output()

        self.preview_window = widgets.Output()

        self.layout = widgets.VBox(initial_btns, selectors_layout, dropdowns_layout, self.preview_window,
                                   self.log_console)

    def initialize_upload_btns(self):

        upload_data = widgets.FileUpload(
            accept='',  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
            multiple=False,  # True to accept multiple files upload else False
            description="Upload Datafile"
        )
        upload_template = widgets.FileUpload(accept="",
                                                  multiple=False,
                                                  description="Upload Template")
        generate_template_btn = widgets.Button(description='Create Template')
        submit_template_btn = widgets.Button(description='Submit Template')
        upload_btns = [upload_data, upload_template]
        self.upload_btns_layout = widgets.HBox(upload_btns)

        display(self.upload_btns_layout)

    def make_gui(self):

        display(self.layout)

