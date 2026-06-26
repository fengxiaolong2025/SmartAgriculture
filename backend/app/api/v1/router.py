from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.devices import router as devices_router
from app.api.v1.sensor_data import router as sensor_data_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.irrigation import router as irrigation_router
from app.api.v1.fertilization import router as fertilization_router
from app.api.v1.pest_control import router as pest_control_router
from app.api.v1.ventilation import router as ventilation_router
from app.api.v1.harvest import router as harvest_router
from app.api.v1.statistics import router as statistics_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.system import router as system_router
from app.api.v1.data_ingest import router as data_ingest_router
from app.api.v1.alert_rules import router as alert_rules_router
from app.api.v1.crops import router as crops_router
from app.api.v1.plots import router as plots_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(devices_router)
api_router.include_router(sensor_data_router)
api_router.include_router(alerts_router)
api_router.include_router(alert_rules_router)
api_router.include_router(irrigation_router)
api_router.include_router(fertilization_router)
api_router.include_router(pest_control_router)
api_router.include_router(ventilation_router)
api_router.include_router(harvest_router)
api_router.include_router(crops_router)
api_router.include_router(plots_router)
api_router.include_router(statistics_router)
api_router.include_router(dashboard_router)
api_router.include_router(system_router)
api_router.include_router(data_ingest_router)
