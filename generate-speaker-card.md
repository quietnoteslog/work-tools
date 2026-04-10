---
title: 연자 소개 카드 자동 생성
description: 연자 정보 파일과 사진 폴더를 기반으로 SNS 카드 이미지를 일괄 생성한다
requires: generate_speaker_card.py (같은 폴더)
---

# 연자 소개 카드 자동 생성 스킬

## 트리거

"연자 카드 만들어줘", "speaker card 생성", "연자 이미지 만들어줘" 등

## 실행 순서

### Step 1. 파일 확인

아래 파일/폴더가 있는지 확인한다:
- `generate_speaker_card.py` (스크립트)
- `photos/` 폴더 (연자 사진)
- 연자 정보 파일 (엑셀/CSV/텍스트 중 하나)

없으면 사용자에게 위치를 물어본다.

### Step 2. 연자 정보 읽기

연자 정보 파일을 읽어서 아래 항목을 추출한다:
- 이름 (name)
- 직함/소속 (cred) — `/`로 구분
- 인용구 (quote)
- 사진 파일명 또는 매칭 가능한 키워드

### Step 3. 사진 매칭

`photos/` 폴더의 파일 목록을 읽고,
연자 이름 또는 번호로 사진 파일과 매칭한다.

매칭 안 되는 연자가 있으면 사용자에게 알리고 계속 진행한다.

### Step 4. 카드 생성

각 연자마다 아래 명령어를 실행한다:

```bash
python3 generate_speaker_card.py \
  --photo [사진경로] \
  --quote "[인용구]" \
  --name "[이름]" \
  --cred "[직함/소속]" \
  --event-name "[행사명]" \
  --output ./output/[이름].png
```

행사명이 지정되지 않은 경우 사용자에게 묻는다.
색상(`--accent-color`)은 연자 순서에 따라 자동 순환: purple → teal → navy → rose → slate

### Step 5. 완료 보고

```
[연자 카드 생성 완료]

생성: N장
저장: output/

- 홍길동.png ✓
- 김영희.png ✓
- 이철수.png ✓ (사진 없음 → 빈 자리로 생성)

수정이 필요한 카드가 있으면 말씀해주세요.
```

## 사용 팁

- 사진이 없는 연자는 빈 자리(`--photo ""`)로 생성 가능
- X(Twitter) 버전도 필요하면 "X 버전도 같이 뽑아줘" 추가
- 색상을 특정 연자에 맞게 지정하려면 "홍길동은 teal로" 등 말하면 됨

## 설치 방법

1. 이 파일을 `.claude/skills/` 폴더에 저장
2. `generate_speaker_card.py`를 작업 폴더에 준비
3. Claude Code에서 "연자 카드 만들어줘" 실행
