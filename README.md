---
title: Speaker Card Generator
description: 이벤트/행사 연자 소개 SNS 카드 이미지 자동 생성기
---

# Speaker Card Generator

행사/이벤트 연자 소개 카드 이미지를 자동으로 생성합니다.

- 인물 사진 배경 자동 제거 (rembg)
- 1080x1080 Instagram / 1200x675 X(Twitter) 동시 생성
- 포인트 색상, 행사명 자유롭게 변경 가능

## 예시 결과물

| Instagram (1080x1080) | X/Twitter (1200x675) |
|----------------------|----------------------|
| ![sample](sample.png) | ![sample_x](sample_x.png) |

## 설치

```bash
pip install Pillow rembg numpy
```

## 사용법

```bash
python3 generate_speaker_card.py \
  --photo ./photo.jpg \
  --quote "여기에 연자 인용구를 입력하세요" \
  --name "홍길동" \
  --cred "PhD / 소속 기관" \
  --event-name "MY CONFERENCE 2026" \
  --output ./output/speaker.png
```

### 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--photo` | 인물 사진 경로 (없으면 빈 자리) | 없음 |
| `--quote` | 인용구 텍스트 | 필수 |
| `--name` | 연자 이름 | 필수 |
| `--cred` | 직함/소속 (/ 로 줄바꿈) | 필수 |
| `--output` | 출력 파일 경로 | 필수 |
| `--event-name` | 하단 행사명 | "MY EVENT" |
| `--accent-color` | 포인트 색상 (#hex 또는 이름) | purple |
| `--texture` | 배경 텍스처 이미지 경로 | 단색 배경 |
| `--scale` | 사진 크기 비율 | 1.0 |
| `--photo-y` | 사진 Y 오프셋 (음수=위로) | 0 |
| `--x` | X(Twitter) 버전도 함께 생성 | false |

### 색상 이름

`--accent-color` 에 이름으로 지정 가능:

| 이름 | 색상 |
|------|------|
| purple | #7B5EA7 |
| teal | #2A9D8F |
| navy | #264653 |
| rose | #C1666B |
| slate | #457B9D |
| green | #2D6A4F |
| orange | #E76F51 |

### 배경 텍스처

종이질감 이미지가 있으면 더 자연스러운 배경을 만들 수 있습니다.
없으면 단색(#EFEFEC)으로 대체됩니다.

```bash
# 종이질감 배경 적용
python3 generate_speaker_card.py ... --texture ./paper_texture.jpg
```

## 여러 연자 일괄 생성

```bash
python3 batch_generate.py --config speakers.json
```

`speakers.json` 예시:
```json
[
  {
    "photo": "./photos/speaker1.jpg",
    "quote": "AI는 도구입니다. 어떻게 쓰냐가 중요하죠.",
    "name": "홍길동",
    "cred": "PhD / 서울대학교",
    "color": "teal"
  },
  {
    "photo": "./photos/speaker2.jpg",
    "quote": "데이터가 말하게 하라.",
    "name": "김영희",
    "cred": "MD / 연세의료원",
    "color": "navy"
  }
]
```
