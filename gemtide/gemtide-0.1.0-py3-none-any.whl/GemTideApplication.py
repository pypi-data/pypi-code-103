import asyncio
import datetime
import typing

from jetforce import JetforceApplication, Response, Status, RoutePattern
from ukhotides import UkhoTides
from aiohttp import ClientSession
from jinja2 import Environment, PackageLoader
from slugify import slugify

class GemTideApplication(JetforceApplication):

	async def fetch_stations(self, query=""):
		async with ClientSession() as session:
			client = UkhoTides(session, self.api_key)
			return await client.async_get_stations(query)
	
	async def fetch_station(self, stationid=""):
		async with ClientSession() as session:
			client = UkhoTides(session, self.api_key)
			return await client.async_get_station(stationid)
	
	async def fetch_tidal_events(self, stationid=""):
		async with ClientSession() as session:
			client = UkhoTides(session, self.api_key)
			return await client.async_get_tidal_events(stationid)
	
	def get_station_uri(self, name, ext):
		return self.station_uri_prefix + slugify(name) + "." + ext

	def __init__(self, api_key, station_prefix = "location/", menu = []):
		super().__init__()
		
		self.api_key = api_key
		self.station_uri_prefix = station_prefix
		self.menu = menu

		self.env = Environment(
			loader = PackageLoader("gemtide"),
			trim_blocks = True,
			lstrip_blocks = True
		)

		self.env.filters["slugify"] = slugify
		self.env.filters["station_uri"] = self.get_station_uri
	
		self.station_slugs = {
			slugify(station.name): station.id
			for station in asyncio.get_event_loop().run_until_complete(self.fetch_stations())
		}
		
		self.station_exts = [t[8:] for t in self.env.list_templates() if "station." in t]
		
		self.routes.append((RoutePattern("/search"), self.search))
		self.routes.append((RoutePattern("/{}(?P<station_name>.*)\.(?P<ext>({}))".format(self.station_uri_prefix, "|".join(self.station_exts))), self.station))
		self.routes.append((RoutePattern(""), self.index))

	def index(self, request):
		template = self.env.get_template("index")
		return Response(Status.SUCCESS, "text/gemini", template.render(menu=self.menu))

	def station(self, request, station_name, ext):
		if not ext:
			return Response(Station.NOT_FOUND, "Invalid file type, .gmi or .txt only")
		elif station_name not in self.station_slugs.keys():
			return Response(Status.NOT_FOUND, "Location not found")
		else:
			dates = {
				"today": datetime.date.today(),
				"tomorrow": datetime.date.today() + datetime.timedelta(days=1)
			}
			station_id = self.station_slugs[station_name]
			station = asyncio.get_event_loop().run_until_complete(self.fetch_station(station_id))
			events = asyncio.get_event_loop().run_until_complete(self.fetch_tidal_events(station_id))
			for event in events:
				# event date_time needs to be truncated to seconds in case it's invalid for datetime.isoformat
				event.datetime = datetime.datetime.fromisoformat(event.date_time[:19])
			template = self.env.get_template("station.{}".format(ext))
			return Response(Status.SUCCESS, "text/gemini",
				template.render(station=station, events=events, dates=dates)
				)

	def search(self, request):
		if request.query and len(request.query) >= 3:
			stations = asyncio.get_event_loop().run_until_complete(self.fetch_stations(request.query))
			if len(stations) > 50:
				return Response(Status.INPUT, "Too many results, please enter a more specific location (minimum 3 characters)")
			sorted_stations = stations.sort(key= lambda s : s.name)
			template = self.env.get_template("search")
			return Response(Status.SUCCESS, "text/gemini", template.render(stations=stations))
		else:
			return Response(Status.INPUT, "Enter a location (minimum 3 characters)")

