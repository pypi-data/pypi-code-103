import urllib.error
from fastapi import Depends, FastAPI, Security
from fastapi_resource_server import JwtDecodeOptions, OidcResourceServer
from pydantic import BaseModel
from typing import Dict, Any
from ...storage import storage

if storage['arguments'].api:
	decode_options = JwtDecodeOptions(verify_aud=False)

	try:
		auth_scheme = OidcResourceServer(
			f"http://{storage['arguments'].auth_server}:8080/auth/realms/{storage['arguments'].auth_realm}",
			scheme_name=storage['arguments'].auth_schema,
			jwt_decode_options=decode_options,
		)
	except urllib.error.URLError as err:
		auth_scheme = None
		print(f"Warning: Could not initiate auth schema http://{storage['arguments'].auth_server}:8080/auth/realms/{storage['arguments'].auth_realm}: {err}")

	app = FastAPI()

	class User(BaseModel):
		username: str
		given_name: str
		family_name: str
		email: str

	def get_current_user(claims: Dict[str, Any] = Security(auth_scheme)) -> User:
		claims.update(username=claims["preferred_username"])
		user = User.parse_obj(claims)
		return user

	@app.get("/users/me")
	def read_current_user(current_user: User = Depends(get_current_user)) -> User:
		"""
		This API call will return the current (logged in) user information.
		"""
		return current_user

	@app.get("/clusters")
	def list_all_clusters(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
		"""
		List all available clusters (if any).
		"""
		return {}