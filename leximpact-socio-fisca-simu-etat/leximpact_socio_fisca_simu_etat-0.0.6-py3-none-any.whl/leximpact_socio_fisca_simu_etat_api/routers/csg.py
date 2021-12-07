from random import random

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from leximpact_socio_fisca_simu_etat.cache import Cache
from leximpact_socio_fisca_simu_etat.config import Configuration
from leximpact_socio_fisca_simu_etat.csg_simu import compute_all_simulation
from leximpact_socio_fisca_simu_etat.schema import (
    AllSimulationResult,
    OneSimulationResult,
    ReformeSocioFiscale,
)
from leximpact_socio_fisca_simu_etat_api.security import get_token_header

config = Configuration()

router = APIRouter()


def get_random_result():
    return OneSimulationResult(
        state_budget={"csg": random() * 1e9},
        quantiles=[
            {
                "fraction": float((i + 1) / 10),
                "csg": random() * 1_000 * -(10 ** i),
            }
            for i in range(10)
        ],
    )


@router.post("/state_simulation_random", response_model=AllSimulationResult)
def reform_csg_fake(reform: ReformeSocioFiscale):
    montant_csg_etat = AllSimulationResult(
        result={
            "base": get_random_result(),
            "plf": get_random_result(),
            "amendement": get_random_result(),
        },
        error="WARNING : FAKE DATA",
    )
    return montant_csg_etat


@router.post(
    "/state_simulation",
    response_model=AllSimulationResult,
    dependencies=[Depends(get_token_header)],
)
def reform_csg(reform: ReformeSocioFiscale):
    montant_csg_etat = compute_all_simulation(reform)
    return montant_csg_etat


@router.get("/clear_cache")
def clear_cache_db(secret: str):
    if secret == config.get("ADMIN_PASSWORD"):
        return {"cache_cleared": Cache().clear_cache()}
    else:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )
