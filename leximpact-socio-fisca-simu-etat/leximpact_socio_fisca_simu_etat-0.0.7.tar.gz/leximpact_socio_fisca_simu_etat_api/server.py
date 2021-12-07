import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from leximpact_socio_fisca_simu_etat.cache import Cache
from leximpact_socio_fisca_simu_etat.csg_simu import compute_reform
from leximpact_socio_fisca_simu_etat.schema import ReformeSocioFiscale
from leximpact_socio_fisca_simu_etat_api.routers import csg

cache = Cache()
app = FastAPI()
app.include_router(csg.router)

# For Prometheus exporter
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# CORS
# Needed for Javascript Browser
# TODO: add origins in the config file
origins = [
    "https://leximpact.an.fr",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost",
    "https://budget.leximpact.an.fr",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*.leximpact.dev",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# To allow *
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=False,  # Can't be True when allow_origins is set to ["*"].
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@app.get("/", tags=["root"])
def root():
    return {"message": "please go to /docs"}


@app.get("/status", tags=["root"])
def status():
    if not cache.is_available():
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cache not available",
        )
    reform_base = ReformeSocioFiscale(
        base="2021",
        amendement={},
        output_variables=["csg"],
        quantile_nb=0,
    )
    res = compute_reform(reform_base, "2021")
    if res[0].state_budget.get("csg") is None:
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            detail="API CSG not available",
        )
    return {"cache": "OK", "simu": "OK", "status": "OK"}


def start_dev():
    """
    Launched with `poetry run start` at root level
    Only for DEV, don't use for production
    """
    uvicorn.run(
        "leximpact_socio_fisca_simu_etat_api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
