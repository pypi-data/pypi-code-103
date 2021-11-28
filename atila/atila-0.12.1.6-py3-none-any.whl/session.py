from .secured_cookie_value import SecuredDictValue
import time

class Session (SecuredDictValue):
	DEFAULT_SESSION_TIMEOUT = 1200 # 20 min.
	KEY = "ATLSES"
	VALIDS = "_valids"

	def __init__ (self, name, cookie, request, secret_key, session_timeout = 0, extend = True):
		self.__session_timeout = session_timeout or self.DEFAULT_SESSION_TIMEOUT
		self.__extend = extend
		self.__new_session_timeout = None
		self.__deadline = None
		self.__now = time.time ()
		self.__real_ip = request.real_ip
		SecuredDictValue.__init__ (self, name, cookie, request, secret_key)

	def use_time (self):
		return self.__session_timeout - (self.__deadline - self.__now)

	def _recal_expires (self, expires):
		if expires is None:
			if self.__new_session_timeout is not None:
				expires = self.__new_session_timeout
			else:
				return self.__session_timeout
		if expires == "now":
			return 0
		if expires == "never":
			raise ValueError("session must be specified expires seconds")
		return int (expires)

	def validate (self):
		if self.VALIDS not in self.data:
			self.data = {}
			return

		if type (self.data [self.VALIDS]) is tuple:
			deadline, addr = self.data [self.VALIDS]
			self._source_verified = (addr == self.__real_ip)
		else:
			deadline = self.data [self.VALIDS]

		if self.__now > deadline: # expired
			self.data = {}
			return

		self.__deadline = deadline

	def getv (self, k, default = None, expire_if_error = False):
		val = self.get (k, default)
		if not self._source_verified:
			if expire_if_error:
				self.expire ()
			raise ValueError ('session error: source verification failed')
		return val

	def touch (self):
		self.set_expiry (self.__session_timeout)

	def set_expiry (self, timeout):
		self.__new_session_timeout = timeout
		self.dirty = True

	def get_expiry (self):
		if not self.data.get (self.VALIDS):
			return
		return self.data [self.VALIDS][0]

	def impending (self):
		if not self.__deadline:
			return False
		if (self.__deadline - self.__now) > max (10, self.__session_timeout * 0.2):
			return False
		return True

	def expire (self):
		self.clear ()
		self.__new_session_timeout = 'now'

	def commit (self, expires = None):
		if self.data and len (self.data) == 1 and self.VALIDS in self.data: # only have _expires, expire now
			self.expire ()

		if not self.data and self.__new_session_timeout is None:
			# just new mounted but no data, no need extending
			return

		if not self.dirty:
			if not self.__extend or not self.impending ():
				return

		expires = self._recal_expires (expires)
		if not expires:
			self [self.VALIDS] = (int (time.time ()), self.__real_ip)

		else:
			new = int (time.time () + expires)
			if "_expire" not in self.data: # old session
				self [self.VALIDS] = (new, self.__real_ip)
			else:
				current = self [self.VALIDS][0]
				if self.__new_session_timeout or new > current:
					#already set_expiry
					self [self.VALIDS] = (new, self.__real_ip)
				else:
					expires = current - time.time ()

		self.set_cookie (expires)
		self.dirty = False
