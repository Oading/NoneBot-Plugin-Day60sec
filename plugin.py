from nonebot import on_command, get_driver, get_bots
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.params import CommandArg
from pathlib import Path
from datetime import datetime
import asyncio
import yaml
from nonebot_plugin_apscheduler import scheduler
from . import request, merge
from nonebot.log import logger

driver = get_driver()
GROUP_IDS = getattr(driver.config, "daily_report_groups", [])
BASE_DIR = Path(__file__).parent

reqday60s = on_command("reqday60s", aliases={"!reqday60s", "！reqday60s", "每日早报"}, priority=5)

@reqday60s.handle()
async def handle_reqday60s(bot: Bot, event: Event, arg=CommandArg()):
    await reqday60s.send("正在向API请求数据,请稍候...")
    try:
        await asyncio.to_thread(request.fetch_and_save_json)
        image_path = await asyncio.to_thread(merge.generate_image_from_json)
        await reqday60s.send(MessageSegment.image(f"file:///{Path(image_path).resolve()}"))
        logger.info(f"推送图片成功：{image_path}")
    except Exception as e:
        await reqday60s.send(f"推送失败：{str(e)}")
        logger.info(f"推送图片失败：{str(e)}")


async def _generate_daily_image() -> str:
    await asyncio.to_thread(request.fetch_and_save_json)
    image_path = await asyncio.to_thread(merge.generate_image_from_json)
    return image_path


async def _send_image_to_group(bot: Bot, group_id: int, image_path: str):
    try:
        await bot.send_group_msg(
            group_id=int(group_id),
            message=MessageSegment.image(
                f"file:///{Path(image_path).resolve()}")
        )
        logger.info(f"向群 {group_id} 推送图片成功：{image_path}")
    except Exception as e:
        logger.exception(f"向群 {group_id} 推送图片失败: {e}")


def load_daily_report_groups_from_yaml() -> list:
    config_path = BASE_DIR / "config.yaml"
    if not config_path.exists():
        logger.warning(f"{config_path} 不存在，无法读取 daily_report_groups")
        return []
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        raw = data.get("daily_report_groups", [])
        groups = [int(g) for g in raw]
        return groups
    except Exception as e:
        logger.exception(f"读取 config.yaml 时出错: {e}")
        return []


@scheduler.scheduled_job("cron", hour=7, minute=30)
async def _daily_push_job():
    groups = load_daily_report_groups_from_yaml()
    if not groups:
        logger.warning(
            "Daily push被触发，但 config 中没有配置 daily_report_groups，跳过本次推送。")
        return
    try:
        image_path = await _generate_daily_image()
    except Exception as e:
        logger.exception(f"生成每日图片失败：{e}")
        return
    bots = get_bots()
    if not bots:
        logger.warning("没有可用的 bot 实例，无法推送每日图片。")
        return
    for bot in bots.values():
        for gid in groups:
            try:
                await _send_image_to_group(bot, gid, image_path)
            except Exception:
                continue
    logger.info("每日推送任务完成。")
