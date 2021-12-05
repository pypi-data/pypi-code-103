import time
# from ..networking import epoll, EPOLLIN, EPOLLHUP

class ClusterServer:
	"""
	TODO:
	Implementation of a cluster-share-service.
	This class listens for other nodes and can connect to other nodes.
	The purposes is to share states, machines, evacuate a node etc.
	"""
	pass

	def poll(self) -> bool:
		time.sleep(0.25)
		return True