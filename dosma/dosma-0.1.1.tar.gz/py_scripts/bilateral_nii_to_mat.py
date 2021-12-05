import os
import time

import scipy.io as sio

from utils import dicom_utils, io_utils

dataset_map = {
    "rep_02": ["005", "008"],
    "rep_03": ["005", "009"],
    "rep_04": ["005", "009"],
    "rep_05": ["005", "007"],
    "rep_06": ["005", "009"],
    "rep_07": ["005", "010"],
}
knee_sides = ["LEFT", "RIGHT"]

outLoc = io_utils.check_dir("/bmrNAS/people/arjun/dess_data/dess_bilateral_data/mat_files/")

dicomDir = "/bmrNAS/people/barma7/bilateral/dess_study/data/marco_study_copy/%s/%s/%s/"
segFileBase = "/bmrNAS/people/barma7/bilateral/dess_study/data/marco_study_copy/%s/data/%s/%s/fc/fc_manual.nii.gz"  # noqa

start_time = time.time()
counter = 0
for subject in dataset_map.keys():
    for scan_id in dataset_map[subject]:
        for knee in knee_sides:
            volume, _ = dicom_utils.load_dicom(dicomDir % (subject, scan_id, knee))
            volume = volume.volume
            echo1 = volume[..., 0::2]
            echo2 = volume[..., 1::2]

            seg = io_utils.load_nifti(segFileBase % (subject, scan_id, knee))
            seg = seg.volume

            save_dir = io_utils.check_dir(os.path.join(outLoc, subject, scan_id, knee))
            sio.savemat(
                os.path.join(save_dir, "matFile.mat"), {"echo1": echo1, "echo2": echo2, "seg": seg}
            )

    counter += 1
    print("Finished subject %d/%d" % (counter, len(dataset_map.keys())))

print("Time Elapsed: %0.2f seconds" % (time.time() - start_time))
