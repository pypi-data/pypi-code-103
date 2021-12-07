from json import JSONDecodeError

from locust import HttpUser, between, task

from leximpact_socio_fisca_simu_etat.config import Configuration

config = Configuration()

# Without Quantile
# payload = {
#     "base": 2021,
#     "plf": 2022,
#     "amendement": {
#         "prelevements_sociaux.contributions_sociales.csg.activite.deductible.taux": 0.0001,
#     },
#     "output_variables": [
#         "csg_imposable_salaire",
#     ],
#     "quantile_nb": 0,
# }

# With Quantile
payload = {
    "base": 2021,
    "plf": 2022,
    "amendement": {
        "prelevements_sociaux.contributions_sociales.csg.activite.deductible.taux": 0.0001,
    },
    "output_variables": [
        "assiette_csg_abattue",
        "csg_imposable_salaire",
        "csg_deductible_salaire",
    ],
    "quantile_nb": 10,
    "quantile_base_variable": ["assiette_csg_abattue"],
    "quantile_compare_variables": [
        "csg_imposable_salaire",
        "csg_deductible_salaire",
    ],
}


class ApiBudgetTest(HttpUser):
    host = "https://api-simu-etat-integ.leximpact.dev"
    # host = "http://0.0.0.0:8000"

    # Set the time to wait between two requests for one user
    wait_time = between(1, 5)

    def on_start(self):
        """
        On start we clear the API cache
        """
        self.clear_cache()

    @task
    def index(self):
        self.client.get("/")

    @task
    def status(self):
        self.client.get("/status")

    def clear_cache(self):
        """
        Clear the API cache
        """
        passwd = config.get("ADMIN_PASSWORD")
        with self.client.get(f"/clear_cache?secret={passwd}") as response:
            if response.status_code != 200:
                # response.failure(f"Response code not 200 : {response.status_code}")
                print(f"Response code not 200 : {response.status_code}")

    @task(5)
    def simu_csg(self):
        """
        Ask API for a simulation
        """
        header = {"jwt-token": config.get("TOKEN_FOR_LOAD_TESTING")}
        payload["amendement"][
            "prelevements_sociaux.contributions_sociales.csg.activite.deductible.taux"
        ] += 0.0001
        with self.client.post(
            "/state_simulation", json=payload, catch_response=True, headers=header
        ) as response:
            if response.status_code != 200:
                response.failure(f"Response code not 200 : {response.status_code}")
            try:
                if (
                    int(
                        response.json()["result"]["base"]["state_budget"][
                            "csg_imposable_salaire"
                        ]
                    )
                    < 50_000_000
                ):  # fmt: off
                    response.failure(
                        f'Did not get expected value for csg_imposable_salaire : {response.json()["result"]["base"]["state_budget"]["csg_imposable_salaire"]}'
                    )
            except JSONDecodeError:
                response.failure(
                    f"Response could not be decoded as JSON: {response.text}"
                )
            except KeyError:
                response.failure(
                    f"Response did not contain expected key : {response.json()}"
                )
