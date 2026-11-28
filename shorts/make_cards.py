"""Render 1080x1920 cards for a YouTube Short from menu photos."""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H = 1080, 1920
BLACK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
KR = 1  # Korean face index inside the .ttc
RED = (200, 30, 40)
OUT = "/home/claude/shorts"


def font(path, size):
    return ImageFont.truetype(path, size, index=KR)


def centered(draw, y, text, fnt, fill, stroke=0, stroke_fill=None):
    w = draw.textlength(text, font=fnt)
    draw.text(((W - w) / 2, y), text, font=fnt, fill=fill,
              stroke_width=stroke, stroke_fill=stroke_fill)


def photo_card(src, title, sub, idx, tag):
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    # blurred, darkened background filling the frame
    bg = ImageOps.fit(im, (W, H)).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), 0.45)
    # main photo, full width, centred vertically
    ph = ImageOps.contain(im, (W, 1300))
    bg.paste(ph, ((W - ph.width) // 2, 330 + (1300 - ph.height) // 2))
    d = ImageDraw.Draw(bg)
    # top tag pill
    tf = font(BOLD, 44)
    tw = d.textlength(tag, font=tf)
    d.rounded_rectangle(((W - tw) / 2 - 36, 110, (W + tw) / 2 + 36, 190), 40, fill=RED)
    centered(d, 118, tag, tf, "white")
    # caption block at the bottom
    centered(d, 1640, title, font(BLACK, 82), "white", stroke=8, stroke_fill="black")
    centered(d, 1768, sub, font(BOLD, 52), (255, 222, 90), stroke=6, stroke_fill="black")
    # small brand mark at top-left
    centered(d, 215, "맛있는밥집 쌍촌본점", font(BOLD, 40), (235, 235, 235))
    bg.save(f"{OUT}/card{idx}.png")


def end_card(idx):
    bg = Image.new("RGB", (W, H), (250, 246, 238))
    logo = Image.open(f"{OUT}/logo.png").convert("RGB").resize((620, 620))
    bg.paste(logo, ((W - 620) // 2, 380))
    d = ImageDraw.Draw(bg)
    centered(d, 1080, "맛있는밥집 쌍촌본점", font(BLACK, 86), (60, 40, 30))
    centered(d, 1210, "광주 서구 쌍촌동 1325번지", font(BOLD, 54), (90, 80, 70))
    d.rounded_rectangle((190, 1340, 890, 1450), 55, fill=RED)
    centered(d, 1357, "매장 · 포장 · 배달 OK", font(BLACK, 58), "white")
    centered(d, 1560, "구독하고 오늘의 메뉴 받아보세요", font(BOLD, 48), (90, 80, 70))
    bg.save(f"{OUT}/card{idx}.png")


if __name__ == "__main__":
    cards = [
        ("/mnt/user-data/uploads/8171bc2b-image.jpg",
         "짜파게티가 사천 출장 다녀옴", "계란후라이 두 개는 기본입니다", "오늘의 메뉴 1"),
        ("/mnt/user-data/uploads/6921fb42-image.jpg",
         "고등어 형제, 선탠 완료", "겉은 바삭 · 속은 촉촉 · 밥도둑", "오늘의 메뉴 2"),
        ("/mnt/user-data/uploads/c3173974-image.jpg",
         "오늘의 반찬 8종 출전", "밥 한 공기 추가는 책임 못 져요", "오늘의 반찬"),
    ]
    for i, (src, t, s, tag) in enumerate(cards, 1):
        photo_card(src, t, s, i, tag)
    end_card(len(cards) + 1)
    print("ok")
