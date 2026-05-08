
from importlib import import_module

from app.api.routes.students import router as students_router


global_router = import_module("app.api.routes.global").router
routers = [global_router, students_router]
