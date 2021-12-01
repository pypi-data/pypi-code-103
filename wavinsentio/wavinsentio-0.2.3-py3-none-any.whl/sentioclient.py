from wavinsentio import WavinSentio 
#pipsys.path.append(".")
#from wavinsentio import wavinsentio 

sentio = WavinSentio("djerik@gmail.com","TLPW2wavin")
locations = sentio.get_locations()
print(locations)
rooms = sentio.get_rooms(locations[1]["ulc"])
print(rooms)
#room = sentio.set_temperature(601893689,22)
#room = sentio.set_profile(601893689,"comfort")
#room = sentio.set_profile(601893689,"extracomfort")