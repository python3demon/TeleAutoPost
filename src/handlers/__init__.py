from aiogram import Router
from .common import router as common_router
from .send_post import router as send_post_router
from .drafts import router as drafts_router

handlers_router = Router()

handlers_router.include_routers(
    common_router,
    drafts_router,
    send_post_router
)