from .start import router as start_router
from .profile import router as profile_router
from .water import router as water_router
from .food_handler import router as food_router
from .workout import router as workout_router
from .progress import router as progress_router
from .recommendations import router as recommendations_router
from .graphs import router as graphs_router
from .help import router as help_router
from .default import router as default_router


def setup_routers(dp):
    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(water_router)
    dp.include_router(food_router)
    dp.include_router(workout_router)
    dp.include_router(progress_router)
    dp.include_router(recommendations_router)
    dp.include_router(graphs_router)
    dp.include_router(help_router)
    dp.include_router(default_router)
