from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap
import datetime
import json
from lunardate import LunarDate


def generate_image_from_json():
    BASE_DIR = Path(__file__).parent
    IMG_WIDTH = 1920
    IMG_LENGTH = 2500
    NEWS_START_Y = 900
    LINE_SPACING = 16
    NEWS_SPACING = 35
    TEXT_COLOR = (0, 0, 0)
    LEFT_MARGIN = 100
    RIGHT_MARGIN = 100
    X1, Y1 = 1487, 287  # 星期
    X2, Y2 = 1159, 335  # 农历
    X3, Y3 = 1501, 393  # 日期
    week_map = ["一", "二", "三", "四", "五", "六", "日"]
    lunar_month_map = {
        1:  "正月", 2:  "二月", 3:  "三月",
        4:  "四月", 5:  "五月", 6:  "六月",
        7:  "七月", 8:  "八月", 9:  "九月",
        10: "十月", 11: "冬月", 12: "腊月",
    }
    lunar_day_map = {
        1: "初一",  2: "初二",  3: "初三",  4: "初四",  5: "初五",
        6: "初六",  7: "初七",  8: "初八",  9: "初九",  10: "初十",
        11: "十一", 12: "十二", 13: "十三", 14: "十四", 15: "十五",
        16: "十六", 17: "十七", 18: "十八", 19: "十九", 20: "二十",
        21: "廿一", 22: "廿二", 23: "廿三", 24: "廿四", 25: "廿五",
        26: "廿六", 27: "廿七", 28: "廿八", 29: "廿九", 30: "三十",
    }

    today = datetime.date.today()

    lunar = LunarDate.fromSolarDate(today.year, today.month, today.day)
    month_cn = lunar_month_map[lunar.month]
    day_cn = lunar_day_map[lunar.day]
    date_str = today.strftime("%Y-%m-%d")
    today_str = f"今天是 {date_str}"
    week_str = "星期" + week_map[today.weekday()]
    lunar_str = f"农历 {month_cn}{day_cn}"

    json_path = BASE_DIR / "archive/json" / f"{date_str}.json"
    with json_path.open("r", encoding="utf-8") as f:
        json_data = json.load(f)

    bg_path = BASE_DIR / "assets/background.png"
    news_list = json_data["data"]["news"]
    font_path = BASE_DIR / "assets/fonts/SourceHanSansCN-Regular.otf"
    font_size = 30
    font = ImageFont.truetype(font_path, font_size)

    img = Image.open(bg_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    font_size_weekday = 100
    font_size_lunarday = 50
    font_size_today = 35
    font1 = ImageFont.truetype(
        str(font_path), font_size_weekday)
    font2 = ImageFont.truetype(
        str(font_path), font_size_lunarday)
    font3 = ImageFont.truetype(
        str(font_path), font_size_today)
    draw.text((X1, Y1), week_str, fill=(0, 0, 0), font=font1)
    draw.text((X2, Y2), lunar_str, fill=(0, 0, 0), font=font2)
    draw.text((X3, Y3), today_str, fill=(0, 0, 0), font=font3)

    y = NEWS_START_Y
    for news in news_list:
        lines = textwrap.wrap(news, width=70)
        for line in lines:
            draw.text((LEFT_MARGIN, y), line, fill=TEXT_COLOR, font=font)
            y += font_size + LINE_SPACING
            if y > IMG_LENGTH:
                break
        y += NEWS_SPACING
        if y > IMG_LENGTH:
            break

    save_path = BASE_DIR / "archive/image"
    save_path.mkdir(parents=True, exist_ok=True)
    save_path = save_path / f"{date_str}.png"
    img.save(save_path)
    return str(save_path)
