from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.params import CommandArg
from pathlib import Path
from datetime import datetime
import asyncio

from . import request, merge

reqday60s = on_command("reqday60s", aliases={"！reqday60s"}, priority=5)


@reqday60s.handle()
async def handle_reqday60s(bot: Bot, event: Event, arg=CommandArg()):
    await reqday60s.send("...")

    try:

        await asyncio.to_thread(request.fetch_and_save_json)

        image_path = await asyncio.to_thread(merge.generate_image_from_json)

        await reqday60s.send(MessageSegment.image(f"file:///{Path(image_path).resolve()}"))
    except Exception as e:
        await reqday60s.send(f"处理失败：{str(e)}")
