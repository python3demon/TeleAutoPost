import asyncio
from middlewares.media_group import GroupPhotoMiddleware
from handlers import handlers_router
from config import bot, dp

async def main() -> None:
    dp.message.middleware(GroupPhotoMiddleware())
    dp.include_router(handlers_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
