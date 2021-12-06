from llcsciencesdk.llc_api import ScienceSdk

llc_api = ScienceSdk(environment="production")
llc_api.login("username", "password")
model_input = llc_api.get_model_input_as_json(11, legacy_parameters=True)
print(model_input)