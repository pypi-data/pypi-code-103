import ipywidgets as widgets
from IPython.core.display import clear_output
from ipywidgets import interactive, fixed, HBox, Layout, VBox
from replifactory.culture.culture_functions import increase_stress_drug1

widget_layout = Layout(align_items='center', width='90px')
box_layout = Layout(display='flex',
                    flex_flow='row',
                    align_items='center',
                    border='solid',
                    width='720px')
style = {'description_width': '0px'}


class StirrerWidget:
    def __init__(self, device, vial_number):
        self.device = device
        self.vial_number = vial_number
        self.slider = widgets.FloatSlider(0, min=0, max=1, step=0.01,
                                          orientation="vertical",
                                          description="Mix %d" % vial_number,
                                          continuous_update=False,
                                          layout=Layout(width='30px'))
        self.slider.observe(self.handle_slider_change, names="value")
        self.max_button = widgets.Button(description="max", layout=Layout(width='60px'))
        self.max_button.on_click(self.handle_max_button)
        self.high_button = widgets.Button(description="high", layout=Layout(width='60px'))
        self.high_button.on_click(self.handle_high_button)
        self.low_button = widgets.Button(description="low", layout=Layout(width='60px'))
        self.low_button.on_click(self.handle_low_button)
        self.stop_button = widgets.Button(description="STOP", layout=Layout(width='60px'))
        self.stop_button.on_click(self.handle_stop_button)
        self.calibrate = widgets.Checkbox(description="learn", layout=Layout(width='60px'),
                                          style={"description_width": "initial"})
        self.buttons = widgets.VBox([self.max_button, self.high_button, self.low_button,
                                     self.stop_button, self.calibrate])
        self.widget = HBox([self.slider, self.buttons], layout=Layout(align_items='center', width='100px'))

    def handle_stop_button(self, button):
        self.slider.value = 0

    def handle_max_button(self, button):
        if self.calibrate.value:
            self.device.calibration_fan_speed_to_duty_cycle[self.vial_number][3] = self.slider.value
            self.calibrate.value = False
        else:
            self.slider.value = self.device.calibration_fan_speed_to_duty_cycle[self.vial_number][3]

    def handle_high_button(self, button):
        if self.calibrate.value:
            self.device.calibration_fan_speed_to_duty_cycle[self.vial_number][2] = self.slider.value
            self.calibrate.value = False
        else:
            self.slider.value = self.device.calibration_fan_speed_to_duty_cycle[self.vial_number][2]

    def handle_low_button(self, button):
        if self.calibrate.value:
            self.device.calibration_fan_speed_to_duty_cycle[self.vial_number][1] = self.slider.value
            self.calibrate.value = False
        else:
            self.slider.value = self.device.calibration_fan_speed_to_duty_cycle[self.vial_number][1]

    def handle_slider_change(self, change):
        new_speed = change.new
        self.device.stirrers._set_duty_cycle(vial=self.vial_number, duty_cycle=new_speed)


class StirrerWidgets:
    def __init__(self, device):
        self.device = device
        self.max_all = widgets.Button(description="max RPM")
        self.max_all.on_click(self.handle_all_max_button)

        self.high_all = widgets.Button(description="high RPM")
        self.high_all.on_click(self.handle_all_high_button)

        self.low_all = widgets.Button(description="low RPM")
        self.low_all.on_click(self.handle_all_low_button)

        self.stop_all = widgets.Button(description="STOP stirrers", button_style="danger")
        self.stop_all.on_click(self.handle_all_stop_button)

        self.control_all = HBox([self.max_all, self.high_all, self.low_all, self.stop_all])
        self.stirrer_widgets = [StirrerWidget(self.device, i) for i in range(1, 8)]
        stirrer_widgets_box = HBox([w.widget for w in self.stirrer_widgets])
        self.widget = VBox([self.control_all, stirrer_widgets_box],layout=Layout(display='flex',
                    flex_flow='column',
                    align_items='center',
                    border='solid',
                    width='720px'))

    def handle_all_max_button(self, button):
        for w in self.stirrer_widgets:
            w.calibrate.value = False
            w.max_button.click()

    def handle_all_high_button(self, button):
        for w in self.stirrer_widgets:
            w.calibrate.value = False
            w.high_button.click()

    def handle_all_low_button(self, button):
        for w in self.stirrer_widgets:
            w.calibrate.value = False
            w.low_button.click()

    def handle_all_stop_button(self, button):
        for w in self.stirrer_widgets:
            w.stop_button.click()


class ValveButtons:
    def __init__(self, device):
        self.layout = Layout(align_items='center', width='90px', height="30px")
        self.device = device
        self.valve_buttons = []
        self.open_all = widgets.Button(description="OPEN all valves")
        self.close_all = widgets.Button(description="CLOSE all valves")
        self.open_all.on_click(self.handle_open_all_button)
        self.close_all.on_click(self.handle_close_all_button)
        for v in range(1, 8):
            button = widgets.ToggleButton(value=self.device.valves.is_open[v],
                                          description="Valve %d" % v, layout=self.layout, style=style)
            button.observe(handler=self.handle_valve_button, names=["value", "description"])

            self.valve_buttons += [button]
        box_valves = HBox(self.valve_buttons, layout=Layout(display='flex',
                                                            flex_flow='row',
                                                            align_items='stretch',
                                                            # height='120px',
                                                            width='720px'))
        all_valves = HBox([self.open_all, self.close_all])
        self.widget = VBox([box_valves, all_valves], layout=Layout(display='flex',
                                                                   flex_flow='column',
                                                                   align_items='stretch',
                                                                   border='solid',
                                                                   width='720px'))

    def handle_valve_button(self, change):
        valve = int(change.owner.description[-1])
        if self.device.locks_vials[valve].locked():
            print("ERROR: LOCKED")
        else:
            self.device.locks_vials[valve].acquire()
            self.device.valves.set_state(valve=valve, is_open=change.owner.value)
            # if is_open:
            #     print("Open")
            # else:
            #     print("Closed")
            self.device.locks_vials[valve].release()

    #
    # def make_valve_button(self, valve_number):
    #     button = widgets.ToggleButton(value=is_open, description="Valve %d" % valve_number,
    #                                   layout=self.layout, style=style)
    #
    #     is_open = self.device.valves.is_open[valve_number]
    #     button = widgets.ToggleButton(value=is_open, description="Valve %d" % valve_number,
    #                                   layout=self.layout, style=style)
    #     widget = interactive(self.valve_button, valve=fixed(valve_number), is_open=button, layout=self.layout)
    #     return widget

    def handle_open_all_button(self, b):
        self.open_all.disabled = True
        # self.device.valves.open_all()
        for v in range(1, 8):
            if not self.device.valves.is_open[v] is True:
                self.valve_buttons[v-1].value = True
        self.close_all.disabled = False

    def handle_close_all_button(self, b):
        self.close_all.disabled = True
        # self.device.valves.close_all()
        for v in range(1, 8):
            if not self.device.valves.is_open[v] is False:
                self.valve_buttons[v-1].value = False
        self.open_all.disabled = False

# def valve_button(self, valve, is_open=False):
#     if self.device.locks_vials[valve].locked():
#         print("ERROR: LOCKED")
#     else:
#         self.device.locks_vials[valve].acquire()
#         self.device.valves.set_state(valve=valve, is_open=is_open)
#         # if is_open:
#         #     print("Open")
#         # else:
#         #     print("Closed")
#         self.device.locks_vials[valve].release()


class DilutionWidget:
    def __init__(self, device):
        self.device = device
        self.vial = widgets.Dropdown(options=[1, 2, 3, 4, 5, 6, 7], index=None, description="Vial")
        self.target_concentration = widgets.FloatSlider(disabled=True, description="concentration")
        self.vial.observe(self.handle_vial_change, names="value")
        self.button = widgets.Button(description="make dilution")
        self.button.on_click(self.handle_button)
        self.widget = VBox([self.vial, self.target_concentration, self.button])

    def handle_button(self, button):
        self.button.disabled = True
        self.button.description = "diluting..."
        c = self.device.cultures[self.vial.value]
        increase_stress_drug1(culture=c, target_concentration=self.target_concentration.value)
        self.button.disabled = False
        self.button.description = "make dilution"

    def handle_vial_change(self, change):
        c = self.device.cultures[change["new"]]
        dilution_factor = (c.default_dilution_volume + c.dead_volume) / c.dead_volume
        self.target_concentration.min = c.medium2_concentration / dilution_factor
        stock_c = c.device.pump2.stock_concentration
        self.target_concentration.value = c.medium2_concentration
        self.target_concentration.max = (
                                                    c.medium2_concentration * c.dead_volume + c.default_dilution_volume * stock_c) / (
                                                    c.dead_volume + c.default_dilution_volume)
        self.target_concentration.disabled = False


class DeviceControl:
    def __init__(self, device):
        self.device = device
        if self.device is None:
            self.widget = widgets.Output()
            with self.widget:
                print("No device connected.")
        else:
            self.widget = self.build_widget(self.device)

    def build_widget(self, device):
        # STIRRERS ##
        # stirrer_widgets = []
        # for stirrer in range(1, 8):
        #     slider = widgets.FloatSlider(0, min=0, max=1, step=0.01,
        #                                  orientation="vertical",
        #                                  description="Stirrer %d" % stirrer,
        #                                  continuous_update=False,
        #                                  layout=widget_layout)
        #     stirrer_slider = interactive(device.stirrers._set_duty_cycle, vial=fixed(stirrer), duty_cycle=slider)
        #     stirrer_widgets += [stirrer_slider]
        # box_stirrers = HBox(stirrer_widgets, layout=box_layout

        box_stirrers = StirrerWidgets(device).widget
    # LASERS ####
        laser_widgets = []

        def laser_trigger(vial, is_on=False):
            if is_on:
                device.lasers.switch_on(vial)
            else:
                device.lasers.switch_off(vial)

        for laser in range(1, 8):
            checkbox = widgets.Checkbox(value=False, description="Laser %d" % laser,
                                        layout=widget_layout, style=style)
            laser_checkbox = interactive(laser_trigger, vial=fixed(laser), is_on=checkbox)
            laser_widgets += [laser_checkbox]
        box_lasers = HBox(laser_widgets, layout=box_layout)

    # ADC #######
        adc_widgets = []
        outputs = {v: widgets.Output() for v in range(1, 8)}

        def make_adc_button_function(photodiode):
            def button_function(b):
                with outputs[photodiode]:
                    self.device.photodiodes.switch_to_vial(vial=photodiode)
                    clear_output()
                    mv, err = device.photodiodes.measure(gain=8, bitrate=16)
                    print(mv, "\n±%.7f" % err)
            return button_function

        for photodiode in range(1, 8):
            button = widgets.Button(description='ADC %d' % photodiode, height="20px", layout=Layout(width='90px'))
            button.on_click(make_adc_button_function(photodiode))
            sub_box = VBox([button, outputs[photodiode]],
                           layout=Layout(align_items='center', width='110px', height="70px"))
            adc_widgets += [sub_box]
        box_adc = HBox(adc_widgets, layout=box_layout)

    # OD ########
        od_widgets = []
        od_outputs = {v: widgets.Output() for v in range(1, 8)}

        def make_od_button_function(vial):
            def button_function(b):
                with od_outputs[vial]:
                    clear_output()
                    od = device.od_sensors[vial].measure_od()
                    try:
                        device.cultures[vial].od = od
                    except:
                        pass
                    print("%.4f" % od)
            return button_function

        for vial in range(1, 8):
            button = widgets.Button(description='OD %d' % vial, height="20px", layout=Layout(width='90px'))
            button.on_click(make_od_button_function(vial))
            sub_box = VBox([button, od_outputs[vial]],
                           layout=Layout(align_items='center', width='110px', height="70px"))
            od_widgets += [sub_box]
        box_od = HBox(od_widgets, layout=box_layout)

    # PUMPS #####
        pump_style = {'description_width': 'initial'}
        rotations_sliders = {pump: widgets.FloatSlider(0, min=0, max=40, step=0.001, orientation="horizontal",
                                                       description="PUMP %d rotations" % pump, continuous_update=False,
                                                       style=pump_style) for pump in range(1, 5)}
        run_buttons = {pump: widgets.Button(description="RUN pump_number %d" % pump) for pump in range(1, 5)}

        def run_pump1(b):
            device.pump1.move(n_rotations=rotations_sliders[1].value)

        def run_pump2(b):
            device.pump2.move(n_rotations=rotations_sliders[2].value)

        def run_pump3(b):
            device.pump3.move(n_rotations=rotations_sliders[3].value)

        def run_pump4(b):
            device.pump4.move(n_rotations=rotations_sliders[4].value)

        run_buttons[1].on_click(run_pump1)
        run_buttons[2].on_click(run_pump2)
        run_buttons[3].on_click(run_pump3)
        run_buttons[4].on_click(run_pump4)

        box_pumps = []
        for pump in range(1, 5):
            box_pumps += [HBox([rotations_sliders[pump], run_buttons[pump]])]

        def emergency_stop_button_action(b):
            self.device.pump1.stop()
            self.device.pump2.stop()
            self.device.pump3.stop()
            self.device.pump4.stop()
            # self.device.emergency_stop()

        def continuous_vacuum_button_action(b):
            assert self.device.valves.not_all_closed()
            self.device.pump4.run(0.1)

        emergency_stop = widgets.Button(description="STOP pumps", button_style="danger")
        continuous_vacuum = widgets.Button(description="continuous vacuum", button_style="warning")
        continuous_vacuum.on_click(continuous_vacuum_button_action)
        emergency_stop.on_click(emergency_stop_button_action)

        box_pumps += [HBox([continuous_vacuum, emergency_stop])]
        box_pumps += [DilutionWidget(self.device).widget]
        pumps_box_layout = Layout(display='flex',
                            flex_flow='column',
                            align_items='stretch',
                            border='solid',
                            width='470px')
        box_pumps = VBox(box_pumps, layout=pumps_box_layout)
    # TEMP ######
        temp_output = widgets.Output()

        def temp_measure(b):
            with temp_output:
                clear_output()
                cold, hot = device.thermometers.measure_temperature()
                print("Vials:\t%.2f °C\nBoard:\t%.2f °C" % (cold, hot))

        temp_button = widgets.Button(description="Temperature")
        temp_button.on_click(temp_measure)
        box_temps = VBox([temp_button, temp_output], layout=Layout(height="80px"))

        box_pumps_and_temps = HBox([box_pumps, box_temps])
    # TAB #######
        widget_control_whole = VBox([box_pumps_and_temps,
                                     box_stirrers,
                                     box_lasers,
                                     ValveButtons(self.device).widget,
                                     box_adc,
                                     box_od,
                                     ], disabled=True)
        return widget_control_whole