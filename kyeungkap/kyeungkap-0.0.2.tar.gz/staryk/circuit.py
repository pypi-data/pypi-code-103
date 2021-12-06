import planet, flight
import earth
import dimension

mtcycl = planet.meetingCycle()
mtcycl.set( "1 _ "+ str((272/542)*2) )
cycleOfPlanet = mtcycl.get()

kepler3 = planet.kepler3()
kepler3.set( "_ "+str(cycleOfPlanet) )
radiusOfPlanet = kepler3.get()

hohmann = flight.hohmann()
hohmann.set(1, radiusOfPlanet)
flightRadius = hohmann.radius()

vis_viva = planet.visViva()
vis_viva.set( str(flightRadius)+" "+str(earth.mass)+" 1" )
velocityOfShuttle = vis_viva.get()

velocityOfLaunching = velocityOfShuttle - dimension.KM_M(earth.v_orbital)
print(velocityOfLaunching)

