import os

if "OKATESTING" in os.environ:
    # user:pass@http://localhost:5000
    default_url = "http://localhost:5000"  # os.environ['OKATESTING'].split("@")[1]
    default_user, default_password = os.environ["OKATESTING"].split("@")[0].split(":")
else:
    default_url = "https://oka.icmc.usp.br"
    default_user, default_password = None, None
