__version__ = '0.0.40'  # print(ultralytics.__version__)


def checks(verbose=True):
    # Checks YOLOv5 software and hardware
    print('Checking setup...')

    import os
    import shutil
    from .utils.general import emojis, check_requirements
    from .utils.torch_utils import select_device  # imports

    if verbose:
        check_requirements(('psutil', 'IPython'))
        import psutil
        from IPython import display  # to display images and clear console output

        # System
        # gb = 1 / 1000 ** 3  # bytes to GB
        gib = 1 / 1024 ** 3  # bytes to GiB
        ram = psutil.virtual_memory().total
        total, used, free = shutil.disk_usage("/")
        display.clear_output()
        s = f'({os.cpu_count()} CPUs, {ram * gib:.1f} GB RAM, {(total - free) * gib:.1f}/{total * gib:.1f} GB disk)'
    else:
        s = ''

    select_device(newline=False, version=__version__)
    print(emojis(f'Setup complete ✅ {s}'))


def login():
    # Login to Ultralytics HUB
    from .main import connect_to_hub
    connect_to_hub(verbose=True)


def start():
    # Start training models with Ultralytics HUB
    from .main import train_model
    train_model()
