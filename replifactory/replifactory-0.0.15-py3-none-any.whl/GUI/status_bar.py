import os
import glob
import ipywidgets as widgets

from ipywidgets import Layout, VBox, HBox

from replifactory.GUI.device_tab import get_ftdi_addresses
from IPython.display import clear_output, display

# class ExperimentWidget:
#     def __init__(self, status_bar):
#         self.status_bar = status_bar
#         print("output made")
#         with self.status_bar.output:
#             self.status_bar.main_gui.experiment = Experiment("NewExperiment")
#         # if self.status_bar.main_gui.experiment is not None:
#         #     with self.status_bar.output:
#         #         self.status_bar.main_gui.experiment.status()
# box_layout = Layout(display='flex',
#                     flex_flow='column',
#                     align_items='stretch',
#                     border='solid 1px gray', )


class StatusBar:
    config_paths = glob.glob("../**/device_config.yaml")
    config_paths = [os.path.relpath(p) for p in config_paths]
    experiment_directories = [os.path.relpath(os.path.join(p, "..")) for p in config_paths]
    layout_width = "350px"

    def __init__(self, main_gui):
        self.main_gui = main_gui
        ftdi_addresses = get_ftdi_addresses()
        ndev = len(ftdi_addresses)
        self.title = widgets.HTML('<b><font size=2>Status:</b><br>Devices available: %d' % ndev)
        self.subtitle = widgets.Output()
        self.output_title = widgets.HTML("Output:")
        self.output = widgets.Output()
        self.output.layout.width = self.layout_width
        self.widget = None
        self.check_button = widgets.Button(description="CHECK")
        self.run_button = widgets.Button(description="RUN", disabled=True)
        self.stop_button = widgets.Button(description="STOP", disabled=True)
        self.check_button.on_click(self.handle_check_button)
        self.run_button.on_click(self.handle_run_button)
        self.stop_button.on_click(self.handle_stop_button)
        self.input = None
        self.update()

    # def ask_question(self, question):
    #     input_label = widgets.Label("How can i help you? ")
    #     input_text = widgets.Text()

    def handle_check_button(self, b):
        with self.output:
            clear_output()
            assert not self.main_gui.experiment.is_running()
            self.main_gui.experiment.device.check_all()
            self.run_button.disabled = False
            # self.update()

    def handle_run_button(self, b):
        with self.output:
            clear_output()
            self.main_gui.experiment.run()
            self.run_button.disabled = True
            self.stop_button.disabled = False
            # self.update()

    def handle_stop_button(self, b):
        with self.output:
            clear_output()
            self.main_gui.experiment.stop()
            self.stop_button.disabled = True
            self.run_button.disabled = False
            # self.update()

    def update(self):
        with self.subtitle:
            clear_output()
            try:
                print("    EXPERIMENT: %s" % self.main_gui.experiment.directory)
            except:
                print("    EXPERIMENT: None")
            try:
                if self.main_gui.device.__class__ is type(None):
                    print("  DEVICE CLASS: None")
                else:
                    print("  DEVICE CLASS: %s" % str(self.main_gui.device.__class__).split(".")[-1][:-2])
            except:
                print("  DEVICE CLASS: None")
            try:
                print("DEVICE ADDRESS: %s" % self.main_gui.device.ftdi_address)
            except:
                print("DEVICE ADDRESS: None")

        widget_list = [self.title, self.subtitle, self.check_button, HBox([self.run_button, self.stop_button]),
                       self.output_title, self.output]
        self.widget = VBox(widget_list, layout=Layout(width=self.layout_width))

    def user_input(self,question):
        with self.output:
            clear_output()
            self.input = InputWidget("How many ml?")
            display(self.input.widget)


class InputWidget:
    def __init__(self, q):
        self.name = q
        self.input = widgets.FloatText(description=q, style={'description_width': 'initial'})
        self.submit = widgets.Button(description="submit")
        self.widget = HBox([self.input, self.submit])


class UserInputFloat:
    def __init__(self, status_bar, question, action=None):
        self.status_bar = status_bar
        self.question = question
        self.action = action
        with self.status_bar.output:
            clear_output()
            q = widgets.FloatText(description=question)
            display(q)
        q.observe(self.on_answer, names="value")

    def on_answer(self, change):
        with self.status_bar.output:
            clear_output()
            print(self.question, "\nuser input:", change.new)
            if self.action is callable:
                self.action(change.new)


class UserInputConfirm:
    def __init__(self, status_bar, question, action=None):
        self.status_bar = status_bar
        self.question = question
        self.action = action
        with self.status_bar.output:
            clear_output()
            y = widgets.Button(description="Yes", button_style="success")
            n = widgets.Button(description="No", button_style="danger")
            q = HBox([y, n])
            display(q)
        y.on_click(self.on_yes)
        n.on_click(self.on_no)

    def on_yes(self, button):
        with self.status_bar.output:
            clear_output()
            print("yass")

    def on_no(self, button):
        with self.status_bar.output:
            clear_output()
            print("nope")
