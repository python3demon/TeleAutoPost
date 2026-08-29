import asyncio
from aiogram import BaseMiddleware

class GroupPhotoMiddleware(BaseMiddleware):
    def __init__(self, latency: float = 0.5):
        self.cache: dict[str, list] = {}
        self.latency = latency
    
    async def __call__(self, handler, event, data):
        if not event.photo:
            return await handler(event, data)
        if not event.media_group_id:
            data["post"] = event.caption
            data["group_photo"] = [event.photo[-1].file_id]
            return await handler(event, data)
        
        try:
            self.cache[event.media_group_id].append(event)
            return
        except KeyError:
            self.cache[event.media_group_id] = [event]
            await asyncio.sleep(self.latency)
            msgs = self.cache.pop(event.media_group_id)
            data["group_photo"] = [msg.photo[-1].file_id for msg in msgs]
            data["post"] = None
            for msg in msgs:
                if msg.caption:
                    data["post"] = msg.caption
                    break
            return await handler(event, data)