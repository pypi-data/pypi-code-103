import os
from ingradient_library.data_organizer import Data_Organizer

def medical_decathlon_organizer(SAVE_PATH, LOAD_PATH, id = 'Task'):
    TR_LOAD_PATH = os.path.join(LOAD_PATH, 'imagesTr')
    SEG_LOAD_PATH = os.path.join(LOAD_PATH, 'labelsTr')

    img_file = [e for e in os.listdir(TR_LOAD_PATH) if e[0] != '.']
    seg_file = [e for e in os.listdir(SEG_LOAD_PATH) if e[0] != '.']

    img_file = sorted(img_file)
    seg_file = sorted(seg_file)    
    organizer = Data_Organizer(SAVE_PATH, id)

    for i in range(len(img_file)):
        seg_file_path = os.path.join(SEG_LOAD_PATH, seg_file[i])
        img_file_path = os.path.join(TR_LOAD_PATH, img_file[i])
        organizer.run(seg_file_path, [img_file_path], i)


