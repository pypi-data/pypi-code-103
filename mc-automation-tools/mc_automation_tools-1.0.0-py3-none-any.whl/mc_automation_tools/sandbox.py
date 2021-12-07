from mc_automation_tools.ingestion_api import overseer_api
url = 'https://discrete-ingestion-qa-overseer-route-raster.apps.v0h0bdx6.eastus.aroapp.io'
overseer = overseer_api.Overseer(url)
overseer.get_class_params