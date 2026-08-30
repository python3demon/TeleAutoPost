from aiogram import Router
from .common import router as common_router
from .send_post import router as send_post_router
from .save_draft import router as save_draft_router
from .callbacks import router as callback_router

handlers_router = Router()

handlers_router.include_routers(
    common_router,
    send_post_router,
    save_draft_router,
    callback_router
)