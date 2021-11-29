import threading

import requests
import time

from .config import HUB_API_ROOT
from .utils.general import colorstr

PREFIX = colorstr('Ultralytics: ')


class HUBLogger:
    def __init__(self, model_id, auth):
        self.model_id = model_id
        self.auth = auth
        self.rate_limit = 60.0  # minimum seconds between checkpoint uploads
        self.t = time.time()  # last upload time

    def on_model_save(self, *args, **kwargs):
        """
        Runs after each model save

        Args:
             *args     last, epoch, final_epoch, best_fitness, fi
        """

        # Set args
        last, epoch, final_epoch, best_fitness, fi = args[:5]
        is_best = best_fitness == fi

        if (time.time() - self.t) > self.rate_limit:
            print(f"{PREFIX}Uploading checkpoint for " + self.model_id)
            threading.Thread(target=self._upload_model, args=(epoch, is_best, last), daemon=True).start()
            self.t = time.time()

    def _upload_model(self, epoch, is_best, weights):
        api_url = HUB_API_ROOT + "model-checkpoint"
        payload = {"modelId": self.model_id, "epoch": epoch, "isBest": bool(is_best)}
        payload.update(self.auth.get_auth_string())

        with open(weights, "rb") as last:
            r = requests.post(api_url, data=payload, files={"last.pt": last})
            if r.status_code != 200:
                print(f"{PREFIX}Unable to upload checkpoint!")

    def on_train_end(self, *args, **kwargs):
        """"
        Args:

            *args   last, best, plots, epoch
        """
        # Set args
        last, best, plots, epoch, results = args[:5]

        # mAP0.5:0.95
        map_new = results[3]

        api_url = HUB_API_ROOT + "model-final"
        payload = {"modelId": self.model_id, "epoch": epoch, "map": map_new}
        payload.update(self.auth.get_auth_string())

        print(f"{PREFIX}Uploading final models for " + self.model_id)
        with open(last, "rb") as last, open(best, "rb") as best:
            r = requests.post(api_url, data=payload, files={"last.pt": last, "best.pt": best})
            if r.status_code != 200:
                print(f"{PREFIX}Unable to upload final models!")
