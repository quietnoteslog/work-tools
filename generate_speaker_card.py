#!/usr/bin/env python3
"""
Speaker Card Generator
이벤트/행사 연자 소개 SNS 카드 이미지 자동 생성기

레이아웃:
  - (선택) 종이질감 or 단색 배경
  - 컬러 박스 + 흑백 인물 컷아웃 레이어드
  - 인용구 바 (어두운 배경 + 흰 텍스트)
  - 이름 / 직함 하단
  - 행사명 하단 중앙

Usage:
  python3 generate_speaker_card.py \
    --photo ./photo.jpg \
    --quote "여기에 연자 인용구를 입력하세요" \
    --name "홍길동" \
    --cred "PhD / 소속 기관" \
    --event-name "MY CONFERENCE 2026" \
    --output ./output/speaker_card.png

  # 색상 변경
  python3 generate_speaker_card.py ... --accent-color "#2A9D8F"

  # 종이질감 배경 사용
  python3 generate_speaker_card.py ... --texture ./texture.jpg

  # X(Twitter) 1200x675 버전도 함께 생성
  python3 generate_speaker_card.py ... --x

Requirements:
  pip install Pillow rembg numpy
"""

import argparse
import os
import platform
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ── 기본값 ──────────────────────────────────────────────────────
W, H        = 1080, 1080
BG_COLOR    = "#EFEFEC"
DARK_BAR    = "#1A1A1A"
WHITE       = "#FFFFFF"
DARK        = "#1A1A1A"
GRAY        = "#555555"

BOX_COLORS = {
    "purple": "#7B5EA7",
    "teal":   "#2A9D8F",
    "navy":   "#264653",
    "rose":   "#C1666B",
    "slate":  "#457B9D",
    "green":  "#2D6A4F",
    "orange": "#E76F51",
}


# ── 폰트: OS별 자동 탐색 ────────────────────────────────────────
def _find_font(bold=False):
    system = platform.system()
    candidates = {
        "Darwin": {
            True:  ["/System/Library/Fonts/AppleSDGothicNeo.ttc",   # 한글 지원
                    "/System/Library/Fonts/Helvetica.ttc",
                    "/System/Library/Fonts/SFNS.ttf"],
            False: ["/System/Library/Fonts/AppleSDGothicNeo.ttc",   # 한글 지원
                    "/System/Library/Fonts/SFNS.ttf",
                    "/System/Library/Fonts/Geneva.ttf"],
        },
        "Linux": {
            True:  ["/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",  # 한글 지원
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"],
            False: ["/usr/share/fonts/truetype/nanum/NanumGothic.ttf",      # 한글 지원
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"],
        },
        "Windows": {
            True:  ["C:/Windows/Fonts/malgunbd.ttf",   # 맑은 고딕 Bold (한글 지원)
                    "C:/Windows/Fonts/arialbd.ttf"],
            False: ["C:/Windows/Fonts/malgun.ttf",     # 맑은 고딕 (한글 지원)
                    "C:/Windows/Fonts/arial.ttf"],
        },
    }
    for path in candidates.get(system, {}).get(bold, []):
        if os.path.exists(path):
            return path
    return None


def f(size, bold=False):
    path = _find_font(bold)
    try:
        return ImageFont.truetype(path, size, index=0) if path else ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def wrap(text, fnt, max_w, draw):
    lines, cur = [], []
    for para in text.split("\n"):
        for word in para.split():
            test = " ".join(cur + [word])
            if draw.textbbox((0, 0), test, font=fnt)[2] > max_w and cur:
                lines.append(" ".join(cur))
                cur = [word]
            else:
                cur.append(word)
        if cur:
            lines.append(" ".join(cur))
            cur = []
    return lines


# ── 메인 생성 함수 (1080x1080) ──────────────────────────────────
def generate(photo_path, quote, name, cred, output_path,
             event_name="MY EVENT 2026",
             accent_color=None,
             texture_path=None,
             photo_scale=1.0,
             photo_y_offset=0):

    accent = accent_color or "#7B5EA7"
    accent_rgb = _hex(accent)

    # 배경: 텍스처 or 단색
    if texture_path and os.path.exists(texture_path):
        bg = Image.open(texture_path).convert("RGB").resize((W, H), Image.LANCZOS)
    else:
        bg = Image.new("RGB", (W, H), BG_COLOR)
    img = bg.copy()

    # 레이아웃 기준값
    MARGIN       = 110
    CONTENT_W    = W - MARGIN * 2
    PHOTO_BASE_Y = 40
    PHOTO_H      = 620
    BAR_H        = 200
    BAR_Y        = PHOTO_BASE_Y + PHOTO_H - 60
    BOX_H        = int(PHOTO_H * 0.58)
    BOX_Y        = BAR_Y - BOX_H
    PHOTO_Y      = BOX_Y + photo_y_offset

    # 뉴모피즘 그림자
    BLUR_R  = 22
    PAD_S   = BLUR_R * 2
    ZONE_W  = CONTENT_W + PAD_S * 2
    ZONE_H  = (BAR_Y + BAR_H - BOX_Y) + PAD_S * 2

    dark_layer = Image.new("RGBA", (ZONE_W, ZONE_H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dark_layer)
    dd.rectangle([PAD_S + 10, PAD_S + 10, PAD_S + CONTENT_W + 10, PAD_S + (BAR_Y + BAR_H - BOX_Y) + 10],
                 fill=(40, 25, 70, 110))
    dark_layer = dark_layer.filter(ImageFilter.GaussianBlur(radius=BLUR_R))

    light_layer = Image.new("RGBA", (ZONE_W, ZONE_H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(light_layer)
    dl.rectangle([PAD_S - 10, PAD_S - 10, PAD_S + CONTENT_W - 10, PAD_S + (BAR_Y + BAR_H - BOX_Y) - 10],
                 fill=(255, 255, 255, 90))
    light_layer = light_layer.filter(ImageFilter.GaussianBlur(radius=BLUR_R))

    shadow_x = MARGIN - PAD_S
    shadow_y = BOX_Y - PAD_S
    img.paste(dark_layer,  (shadow_x, shadow_y), dark_layer)
    img.paste(light_layer, (shadow_x, shadow_y), light_layer)

    draw = ImageDraw.Draw(img, "RGBA")

    # 컬러 박스
    draw.rectangle([MARGIN, BOX_Y, MARGIN + CONTENT_W, BOX_Y + BOX_H], fill=accent)

    # 인물 컷아웃
    if photo_path and os.path.exists(photo_path):
        from rembg import remove
        src = Image.open(photo_path).convert("RGB")
        src = remove(src).convert("RGBA")
        target_h = int(BOX_H * photo_scale)
        ratio    = target_h / src.height
        nw       = int(src.width * ratio)
        src      = src.resize((nw, target_h), Image.LANCZOS)
        cx       = (W - nw) // 2
        clip_bottom = BAR_Y + BAR_H
        visible_h   = min(target_h, clip_bottom - PHOTO_Y)
        if visible_h > 0:
            img.paste(src.crop((0, 0, nw, visible_h)),
                      (cx, PHOTO_Y), src.crop((0, 0, nw, visible_h)))
    else:
        draw.text((W // 2, PHOTO_Y + PHOTO_H // 2), "PHOTO",
                  font=f(48, bold=True), fill="#AAAAAA", anchor="mm")

    # 인용구 바
    draw.rectangle([MARGIN, BAR_Y, MARGIN + CONTENT_W, BAR_Y + BAR_H],
                   fill=(*_hex(DARK_BAR), 235))

    TEXT_MAX_W = CONTENT_W - 48
    TEXT_MAX_H = BAR_H - 36
    for font_size in range(30, 14, -1):
        f_q   = f(font_size, bold=True)
        lines = wrap(quote, f_q, TEXT_MAX_W, draw)
        LH    = int(font_size * 1.45)
        if len(lines) * LH <= TEXT_MAX_H:
            break
    ty = BAR_Y + (BAR_H - len(lines) * LH) // 2
    for line in lines:
        draw.text((MARGIN + 24, ty), line, font=f_q, fill=WHITE)
        ty += LH

    # 이름 + 직함
    NAME_Y = BAR_Y + BAR_H + 30
    draw.rectangle([MARGIN, NAME_Y, MARGIN + 4, NAME_Y + 80], fill=accent)
    draw.text((MARGIN + 18, NAME_Y), name, font=f(36, bold=True), fill=DARK)
    CRED_Y = NAME_Y + 46
    for line in cred.replace("/", "\n").split("\n"):
        draw.text((MARGIN + 18, CRED_Y), line.strip().upper(), font=f(19), fill=GRAY)
        CRED_Y += 26

    # 행사명 (하단 중앙)
    draw.text((W // 2, H - 80), event_name.upper(),
              font=f(22, bold=True), fill=accent, anchor="mm")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path, "PNG", quality=95)
    print(f"Saved: {output_path}")


# ── X 버전 (1200x675) ───────────────────────────────────────────
def generate_x(photo_path, quote, name, cred, output_path,
               event_name="MY EVENT 2026",
               accent_color=None,
               texture_path=None):

    accent = accent_color or "#7B5EA7"
    XW, XH = 1200, 675
    MARGIN  = 60

    if texture_path and os.path.exists(texture_path):
        bg = Image.open(texture_path).convert("RGB").resize((XW, XH), Image.LANCZOS)
    else:
        bg = Image.new("RGB", (XW, XH), BG_COLOR)
    img = bg.copy()
    draw = ImageDraw.Draw(img, "RGBA")

    PHOTO_W = int(XW * 0.42)
    if photo_path and os.path.exists(photo_path):
        from rembg import remove
        src     = Image.open(photo_path).convert("RGB")
        cutout  = remove(src).convert("RGBA")
        ratio   = XH / cutout.height
        nw      = int(cutout.width * ratio)
        cutout  = cutout.resize((nw, XH), Image.LANCZOS)
        BOX_Y   = int(XH * 0.15)
        BOX_H   = int(XH * 0.65)
        draw.rectangle([20, BOX_Y, PHOTO_W - 10, BOX_Y + BOX_H], fill=accent)
        img.paste(cutout, ((PHOTO_W - nw) // 2, 0), cutout)

    TX = PHOTO_W + 30
    TW = XW - TX - MARGIN
    draw2 = ImageDraw.Draw(img)

    for sz in range(26, 12, -1):
        fq    = f(sz, bold=True)
        lines = wrap(quote, fq, TW, draw2)
        lh    = int(sz * 1.4)
        if len(lines) * lh <= int(XH * 0.45):
            break
    ty = int(XH * 0.18)
    for line in lines:
        draw2.text((TX, ty), line, font=fq, fill=DARK)
        ty += lh

    ty += 20
    draw2.rectangle([TX, ty, TX + 40, ty + 3], fill=accent)
    ty += 18

    draw2.text((TX, ty), name, font=f(28, bold=True), fill=DARK)
    ty += 38
    for line in cred.replace("/", "\n").split("\n"):
        draw2.text((TX, ty), line.strip().upper(), font=f(16), fill=GRAY)
        ty += 22

    draw2.text((XW // 2, XH - 28), event_name.upper(),
               font=f(18, bold=True), fill=accent, anchor="mm")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path, "PNG", quality=95)
    print(f"Saved: {output_path}")


# ── CLI ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Speaker Card Generator")
    p.add_argument("--photo",         default="",         help="인물 사진 경로 (없으면 빈 자리)")
    p.add_argument("--quote",         required=True,      help="인용구 텍스트")
    p.add_argument("--name",          required=True,      help="연자 이름")
    p.add_argument("--cred",          required=True,      help="직함/소속 (/ 로 줄바꿈)")
    p.add_argument("--output",        required=True,      help="출력 파일 경로 (.png)")
    p.add_argument("--event-name",    default="MY EVENT", help="행사명 (하단 표시)")
    p.add_argument("--accent-color",  default=None,       help="포인트 색상 (#hex 또는 purple/teal/navy/rose/slate)")
    p.add_argument("--texture",       default=None,       help="배경 텍스처 이미지 경로")
    p.add_argument("--scale",         type=float, default=1.0,  help="사진 크기 비율 (기본 1.0)")
    p.add_argument("--photo-y",       type=int,   default=0,    help="사진 Y 오프셋 (음수=위로)")
    p.add_argument("--x",             action="store_true",      help="X(Twitter) 1200x675 버전도 생성")
    a = p.parse_args()

    accent = BOX_COLORS.get(a.accent_color, a.accent_color)

    generate(
        a.photo, a.quote.replace("\\n", "\n"),
        a.name, a.cred.replace("\\n", "\n"),
        a.output,
        event_name=a.event_name,
        accent_color=accent,
        texture_path=a.texture,
        photo_scale=a.scale,
        photo_y_offset=a.photo_y,
    )

    if a.x:
        base, ext = os.path.splitext(a.output)
        generate_x(
            a.photo, a.quote.replace("\\n", "\n"),
            a.name, a.cred.replace("\\n", "\n"),
            base + "_x" + ext,
            event_name=a.event_name,
            accent_color=accent,
            texture_path=a.texture,
        )
