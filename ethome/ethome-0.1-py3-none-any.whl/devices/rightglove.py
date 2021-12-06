from glove import Glove

class RightGlove(Glove):
    
    attrs = [
        'Thumb_CMC',
        'Thumb_MCP',
        'Thumb_IJ',
        'Thumb_Index_ABD',
        'Index_MCP',
        'Index_PIP',
        'Index_DIP',
        'Middle_MCP',
        'Middle_PIP',
        'Middle_DIP',
        'Middle_Index_ABD',
        'Ring_MCP',
        'Ring_PIP',
        'Ring_DIP',
        'Ring_Middle_ABD',
        'Pinky_MCP',
        'Pinky_PIP',
        'Pinky_DIP',
        'Pinky_Ring_ABD',
        'Palm_Arch',
        'Wrist_FLEX',
        'Wrist_ABD',
    ]    

    def __init__(self, **kwargs):
        kwargs.update({"labels": self.attrs})
        super().__init__(**kwargs)