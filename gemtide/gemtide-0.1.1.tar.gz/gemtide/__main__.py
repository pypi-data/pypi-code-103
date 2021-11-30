import yaml, sys
from jetforce import GeminiServer
from .GemTideApplication import GemTideApplication

def main():
	config_file = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
	
	with open(config_file, "r") as c:
		config_yaml = yaml.safe_load(c)
	
	config_app = { "api_key": config_yaml["api_key"] }
	
	if "station_prefix" in config_yaml:
		config_app["station_prefix"] = config_yaml["station_prefix"]
	
	if "menu" in config_yaml:
		config_app["menu"] = config_yaml["menu"]
	
	config_server = {}
	
	if "server" in config_yaml:
		config_server = config_yaml["server"]
		
	app = GemTideApplication(**config_app)
	server = GeminiServer(app, **config_server)
	server.run()

if __name__ == "__main__":
	main()
