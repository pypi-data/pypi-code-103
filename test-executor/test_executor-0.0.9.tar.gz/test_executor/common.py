import datetime
import os

DEFAULT_LOGS_FOLDER = os.path.join(os.getcwd(), "logs",
                                   datetime.datetime.today().strftime("%d-%m-%Y_%H-%M-%S-%f"))
