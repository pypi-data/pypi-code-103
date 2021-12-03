from cvat_reader import open_cvat

with open_cvat(
    "/Users/koen/PycharmProjects/eyedle-training/tests/test_data/task_20210516_random_backup_2021_08_06_06_40_07.zip",
    load_video=False,
) as dataset:

    for frame in dataset:
        frame.annotations[0].occluded
        print(frame)
