# Trains and Updates Ultralytics HUB Models

from .auth import Auth
from .config import BY_PASS_LOGIN
from .trainer import Trainer
from .utils.general import colorstr
from .yolov5_wrapper import clone_yolo

AUTH = Auth()
CONNECTED = False
PREFIX = colorstr('Ultralytics: ')


def train_model() -> None:
    """Starts training from next in queue"""
    clone_yolo()
    connect_to_hub()
    trainer = Trainer(None, AUTH)  # No model so next in train queue is fetched
    if trainer.model is not None:
        trainer.start()


def connect_to_hub(password=False, verbose=False) -> bool:
    """Authenticates user with Ultralytics HUB"""
    global CONNECTED

    if CONNECTED and verbose:
        print(f'{PREFIX}Already logged in.')
    elif not CONNECTED:
        CONNECTED = AUTH.attempt_signin() if password else AUTH.attempt_api_key()

    return CONNECTED


def main():
    # Deprecated
    clone_yolo()
    if BY_PASS_LOGIN:
        AUTH.sign_in_with_email_and_password("kalen.michael@ultralytics.com", "7654321")
        if AUTH.idToken:
            train_model()
        else:
            print(f"{PREFIX}Incorrect Login Details.")
    elif connect_to_hub():
        train_model()
