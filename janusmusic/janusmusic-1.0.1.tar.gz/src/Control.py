class Control:

    def __init__(self, msg_type=None, tempo=None, control=None, value=None, instrument=None, time=None):
        """ Constructor for the Control message class.

        Args:
            msg_type (String): Contains what type of control message the object represents. Currently supported
                messages are: 'program_change', 'set_tempo', and 'control_change'. Defaults to None.

            tempo (int, optional): For "set_tempo" messages. The tempo value (in microseconds per tick). Lower
                values are faster tempos. Defaults to None.

            control (int, optional): For "control_change" type messages. Stores information about what effect will be
                applied to the given track. Defaults to None. (For more information on control values, see:
                https://beatbars.com/blog/what-does-cc-stand-for-in-midi.html )

            value (int, optional): For "control_change" type messages. Represents the amount of the above effect that
                will be applied. Defaults to None.

            instrument (String, optional): For "program_change" type messages. Instrument of the track.
                Defaults to None. (For more information on program change values, see:
                https://beatbars.com/blog/what-is-program-change.html )

            time (int, optional): For all control messages. The absolute time (in ticks) from the start of the
                song where this message occurs. Defaults to None.
        """
        self.msg_type = msg_type
        self.tempo = tempo
        self.control = control
        self.value = value
        self.instrument = instrument
        self.time = time

    def duplicate_control(self):
        return Control(msg_type=self.msg_type, tempo=self.tempo, control=self.control, value=self.value,
                       instrument=self.instrument, time=self.time)
