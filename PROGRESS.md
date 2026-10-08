# LÉON: Three Triggers — 진행 상황

> 영화 *Léon: The Professional* (1994) 기반 인터랙티브 픽션 기말과제
> Twine + SugarCube 2.37.3 / Tweego CLI 빌드

마지막 업데이트: 2026-06-05

---

## 📊 한눈에 보기

| 항목 | 수치 |
|---|---|
| 패시지 | **58개** (story 5 + leon 42 + mathilda 7 + stansfield 3 + debug 1) |
| 이미지 | **사용 ~80장** (전 패시지 전용, 메인 4컷 gpt-image-2 / 파일 98개 = 백업·변형 포함) |
| 빌드 결과 HTML | ~710KB |
| 엔딩 | **5개** (희생 / 조용 / 복수 / 빚 / 닫힌 문[배드]) |
| 전체 진행률 | **~100%** (ACT 1~3 + 5엔딩 + 에필로그 완성, 제출 패키징 완료) |

> 상세 시스템 설계는 `SYSTEM.md`, 공개용 소개는 `README.md` 참고.

---

## 🛠 빌드 환경

```
LEON/
├── tweego.exe                          # CLI 컴파일러
├── storyformats/sugarcube-2/format.js  # 스토리 포맷 (SugarCube 2.37.3)
├── build.bat                           # 더블클릭으로 빌드
├── LEON_Three_Triggers.html            # 빌드 결과물 (~710KB)
├── README.md                           # 공개용 소개 (개요/실행/Twee/이미지/AI)
├── PROGRESS.md                         # (이 문서) 진행 기록
├── SYSTEM.md                           # 시스템 설계 명세 (변수/게이트/엔딩)
├── src/
│   ├── story.twee                      # 시스템 패시지 (StoryInit, Start, PassageHeader)
│   ├── script.js                       # 매크로 + HUD + 라이트박스 + 디버그 토글 + 사운드
│   ├── style.css                       # 시네마틱 스타일 (레터박스/그레인/게이트/소품/수칙)
│   └── passages/
│       ├── leon.twee                   # 레옹 챕터 (2인칭) — 42 패시지
│       ├── mathilda.twee               # 마틸다 챕터 (1인칭) — 7 패시지
│       ├── stansfield.twee             # 스탠스필드 챕터 (3인칭) — 3 패시지
│       └── debug.twee                  # 디버그 메뉴 (전 챕터/엔딩 점프 + 스탯 설정)
├── images/                             # PNG 98개 (사용 ~80, 1536×1024) · *_img1=백업, *_img2=대안
└── tools/                              # 이미지 생성 스크립트 34개 + image-gen.html (브라우저 GUI)
                                        #   장면·세트별 배치: generate_act2 / act3 / tonyscene /
                                        #   reckoning / sacrifice2 / props / stansfield_* / img2_test ...
```

**빌드 방법**: `build.bat` 더블클릭 또는 터미널에서:
```bash
tweego --format=sugarcube-2 -o LEON_Three_Triggers.html src/
```

---

## 📜 스토리 진행 상황

### ✅ ACT 1 — LÉON 시점 (10 패시지, 거의 완성)

```
Start (프롤로그)
  ↓
Leon_01_Hit (호텔 14층 청부살인) ──→ Leon_01_Hit_End (새벽 귀가)
  ↓
Leon_02_Home (아파트, 화분, 우유)
  ↓
Leon_03_Stairs (복도의 소녀) ─┬─→ Leon_03_Close (문 닫음 — 규율↑)
                              └─→ Leon_03_Watch (지켜봄 — 애착↑)
  ↓
Leon_04_Door (★ 중앙 분기점 ★)
  총성 → 비명 → "제발요. 살려주세요"
  ├─→ Leon_05_Open  (문 연다 — END ACT 1)
  ├─→ Leon_05_Closed (문 닫는다)
  └─→ Mathilda_01_Hallway (그녀 시점으로)
```

### ✅ Mathilda 인터루드 (5 패시지)

```
Mathilda_01_Hallway (가족 살해 직후) ─┬─→ KnockDoor (202호 문 두드림)
                                     ├─→ Hide (숨음 — 스탠스필드 얼굴 단서)
                                     └─→ Run (도망)
                                          ↓
                                     Mathilda_01_End
                                     (openedDoor / closedDoor에 따라 분기)
```

### ✅ ACT 2 — LÉON 시점 (도입부 + 본편 완성, 2026-05-31)

```
Leon_06_Training (베레타 분해) ─┬─→ Leon_07_Lesson (가르친다)
                                └─→ Leon_07_Refuse (거절한다)
  ↓
Leon_08_Morning → Leon_09_Tony (토니의 식당)
  ↓
Leon_10_TonyDeal (토니 경고+돈 보관) [경계심+1]
  ├─(규율)→ Leon_11_Plan (setter +2)
  └─(애착)→ Leon_10_Money [flag moneyForMathilda, 단서]
  ↓
Leon_11_Plan (마틸다가 스탠스필드 위치 파악) [기술+1]
  ├─ Leon_11_Restrain (말린다) [분노-, 신뢰+]
  ├─ ❖신뢰2 Leon_11_Together [flag firstOp]
  └─ ❖애착5 Leon_11_Confess [단서: 레옹의 과거]
  ↓
Leon_12_Recon (건물 정찰) [경계심+1]
  ├─ Leon_12_Solo (혼자) [애착+2]
  └─ ❖기술2 Leon_12_Lookout [flag mathildaArmed, item 무전기]
  ↓
Leon_13_Infiltration (잠입, timed 긴장 + 스탠스필드 등장)
  ├─ ❖경계심2 Leon_13_Trap [flag sensedTrap, 단서]
  └─ Leon_13_Push (계속) [총격전]
  ↓
Leon_14_ActEnd (귀가→마틸다 사라짐) [flag mathildaGone] → ACT 3 예고
```

> 게이트/플래그/소지품/단서 시스템 전부 ACT 2에서 실사용. 브라우저 검증 완료(게이트 해금/잠김, setter 링크, 플래그 누적, 콘솔 에러 0).
> 누적 플래그: moneyForMathilda, firstOp, mathildaArmed, sensedTrap, mathildaGone (+ ACT1의 openedDoor/closedDoor)

### ✅ ACT 3 + 스탠스필드 시점 + 5엔딩 (완성, 2026-06-01)

> `mathildaGone` → 추격(Leon_15) → 구출(Leon_16, 몸 던지기/손목 사격) → 스탠스필드 시점(Stansfield_01~03, 알약·베토벤·토니 가족 협박) → 포위전 3단(Leon_17/17b/17c) → 마지막 선택(Leon_18) → **5엔딩**(희생→에필로그 화분 / 조용 / 복수 / 빚 / 닫힌 문).
> 상세 흐름·변경 내역은 이 문서 맨 아래 **작업 로그(2026-06-01)** 참고.

---

## 🎨 이미지 자산 (사용 ~80장 / 파일 98개)

전부 생성형 AI 제작(영화 스틸·배우 비복제). 초기 ~35장에서 ACT2·ACT3·소품까지 확장했고, 메인 4컷은 gpt-image-2로 교체.

### 카테고리별 (대표 파일)
| 카테고리 | 예시 |
|---|---|
| 타이틀/establishing | `title_v3`(image-2), `nyc_dawn`, `nyc_little_italy`, `recon_building` |
| 레옹 (2인칭) | `leon_portrait`(image-2), `leon_apartment`, `leon_stairs`, `leon_door_choice`, `leon_open_ending`, `leon_pursuit`, `leon_confession`, `leon_reading`(글 가르치기) |
| 마틸다 (1인칭) | `mathilda_portrait`(image-2), `mathilda_hallway`, `mathilda_knock`, `mathilda_in_apartment`, `mathilda_resolve`, `mathilda_training`, `mathilda_mourning`, `school_office`, `school_planting`, `vent_escape` |
| 스탠스필드 (3인칭) | `stansfield_face`(image-2), `stansfield_desk`, `stansfield_tony`, `stansfield_wounded`, `stansfield_looms`, `stansfield_fear`, `clipping_stansfield` |
| 토니 씬 | `tony_table`, `tony_envelope`, `tony_restaurant_night`, `tony_hands_newspaper`, `tony_defeated`, `prop_family_photo` |
| 잠입/액션/엔딩 | `building_lobby`, `lobby_v1/v4`, `lobby_aftermath`, `office_night`, `shattered_glass`, `siege_corridor`, `sniper_lesson`, `scope_face`, `end_light`, `end_milk_plant`, `end_revenge`, `end_reckoning`, `grenade_pin`, `fallen_plant` |
| 소품/단서 (쇼케이스) | `clue_pistol`, `clue_plant`, `clue_milk`, `clue_milk_glass`, `beretta_parts`, `casings_marble`, `prop_milk`, `prop_doll` |

### 생성 모델 / 메모
- **gpt-image-1** — 대부분(~94장), 1536×1024 / quality high. 미성년자·무기·유혈은 손·실루엣·POV·정물로 우회.
- **gpt-image-2** — 메인 4컷(타이틀·레옹·마틸다·스탠스필드) 교체. 화질↑·디테일↑이나 컷당 ~125초(약 2.5배 느림). image-1 원본은 `*_img1.png`로 백업.
- 미사용/백업/대안/구버전 18개(`*_img1`, `*_img2`, `lobby_v2/3`, `title`/`title_v1/2`, `leon_eye_memory` 등)는 제출 zip에서 제외.

### 🚨 학습 포인트 (다음 이미지 생성 시 참고)

**프롬프트 작성 룰**:
- 미성년자 직접 묘사 금지 (12살, 어린아이 등 표현 X)
- 미성년자 + 위협/멍/무기 조합 절대 금지
- 흡연 묘사 금지 (커피로 대체)
- "alley" + "4am" + "dark coat" 같은 포식자 신호 조합 회피
- 톤은 누아르 유지하되 BASE에서 "neo-noir thriller" → "character drama"로 부드럽게

**통과율 높이는 패턴**:
- 부재로 암시 (떨어진 물건, 빈 공간, 깜빡이는 등)
- 부분 노출 (손, 발, 그림자, 뒷모습)
- POV 시점 (등장인물 자체는 안 보임)
- 오브젝트 매크로 (단서/소품 클로즈업)
- 인물 묘사 시 "young adult", "early twenties" 명시

---

## ⚙️ 시스템 / 기능

### 변수 (StoryInit)
```javascript
$perspective       // "leon" | "mathilda" | "stansfield"
$mathilda          // {trust, rage, skill}
$leon              // {attachment, discipline, suspicion}
$stansfield        // {high, cruelty}
$clues             // [] (단서 배열)
$inventory         // []
$endingFlags       // {openedDoor, closedDoor, ...}
```

### 매크로 (script.js)
- `<<gate "leon.discipline" 5 "패시지">>라벨<</gate>>` — **임계값 선택지** (베데스다식, 2026-05-31 추가). 스탯 ≥ 임계값이면 특별 링크 해금, 미만이면 잠긴 채 요구치 표시. 상세는 `SYSTEM.md`
- `<<item "이름">>` — 소지품 추가 + 토스트 (체크: `$inventory.includes()`)
- `<<flag "이름">>` — 엔딩 플래그 설정 (엔딩 분기는 이것만 읽음)
- `<<pick "패시지" "라벨" "효과" ["셋터"]>>` — **효과 미리보기 선택지**. 라벨 옆에 얻을 스탯 변화를 태그로 표시 (예: `분노 −1 · 신뢰 +1`). `<<gate>>`도 4번째 인자로 효과 태그 지원
- *(JS/CSS 기능)* 이미지 클릭 확대(**라이트박스**), 소품 쇼케이스(`.prop` + 캡션), 수칙 강조(`.rule`), 배드엔딩 태그, 시점 자동 판별, 페이지 이동 시 스크롤 상단 복귀
- `<<gunshot>>` — 화면 흔들림 + 플래시 + 사운드
- `<<shake>>` — 흔들림만
- `<<flash>>` — 번쩍만
- `<<clue "단서명">>` — 단서 추가 + 토스트 표시
- `<<sfx "이름">>` — 효과음 재생
- `<<bgm "이름">>` — BGM 재생 (페이드인/아웃)
- `<<type Xms>>...<</type>>` — 타입라이터 효과 (SugarCube 내장)
- `<<timed>><<next>>` — 타이밍 시퀀스 (SugarCube 내장)

### HUD (자동 갱신, 패시지 태그로 시점 판별)
- 좌상단: 시점 (▸ LÉON / MATHILDA / STANSFIELD)
- 중앙: 레옹·마틸다 **6스탯 모두 표시** — 애착/규율/경계심 · 신뢰/분노/기술 (현재 시점은 밝게 강조). 스탠스필드 시점은 약물/잔혹도
- 우상단: 단서 카운터 (클릭 시 목록 alert)

### UI 레이아웃
- 상단 가로 띠: HUD / 상단·하단: 시네마틱 레터박스
- 좌측 하단: 🔊 사운드 토글 · 우측 하단: 🛠 Debug 메뉴(`showDebug` ON일 때만)
- 본문: 화면 정중앙 fixed, **max-width `--content-width`(960px)**
- **이미지 클릭 → 라이트박스 확대**(ESC/클릭 닫기), 소품은 캡션 달린 쇼케이스(`.prop`), 수칙은 골드 callout(`.rule`)

### 페이싱

**서스펜스 timing(`<<timed>>`) 유지** (★):
- `Leon_01_Hit` — 15초 카운트 + 7발 총성
- `Leon_04_Door` — **중앙 분기점 20초 시퀀스** (총성→비명→침묵→노크→"제발요"→문고리)
- `Mathilda_01_Hallway` — 벽 너머 총성 / `Mathilda_01_Hide` — 스탠스필드 콧노래
- **ACT3** — `Leon_13_Infiltration`(15초 잠입), 포위전 3단(전기차단→어둠 교전→환풍구), `Leon_END_Sacrifice2`(죽음 **27초 점층** 시퀀스), 에필로그 화분 심기
- ⚠️ 디버그 시 `setup.fastMode = true`로 모든 timing 즉시화(검수용) → 제출 시 `false`

**타입라이터만 (timing 없이)**:
- "······" 망설임 점 (Leon_03_Stairs)
- "······저 사람들이 우리 가족을 죽였어요." (Leon_05_Open)
- "이걸 가르쳐 줄 수 있어요?" (Leon_06_Training)
- "레옹. 너 — 누구 데리고 온 거 아니지?" (Leon_09_Tony)
- "똑. 똑. 똑." + "...제발요. 살려주세요." (Mathilda_01_KnockDoor)

**전부 정적 표시**: 나머지 모든 패시지

### 사운드 (준비됨, 파일 없음)

매크로는 다 작동하지만 mp3 파일이 아직 없음. 추가 시 `audio/` 폴더 만들고:
```
audio/bgm_leon.mp3
audio/bgm_mathilda.mp3
audio/bgm_stansfield.mp3
audio/bgm_tense.mp3
audio/sfx_gunshot.mp3
audio/sfx_door_knock.mp3
audio/sfx_milk_pour.mp3
audio/sfx_flash.mp3
audio/sfx_heartbeat.mp3
```

---

## 🎯 진행률

```
세팅          ████████████████████ 100%
시스템        ████████████████████ 100%
이미지 자산   ████████████████████ 100% (전 패시지 전용, 메인 image-2 교체)
페이싱        ████████████████████ 100%
UI 정리       ████████████████████ 100%
ACT 1         ████████████████████ 100%
ACT 2         ████████████████████ 100% (본편+저격 교습+글 가르치기 등)
ACT 3         ████████████████████ 100% (추격→구출→포위전→희생, 확장 완료)
엔딩          ████████████████████ 100% (5엔딩 + 에필로그)
스탠스필드    ████████████████████ 100% (시점 3챕터: 알약/토니 심문 2단)
사운드        ░░░░░░░░░░░░░░░░░░░░   0% (매크로만 준비, mp3 없음)
─────────────────────────────────────
전체          ████████████████████  ~100%
```

---

## 🚦 다음 작업 후보

### 우선순위 높음
1. **ACT 2 본편 작성** — Leon_09_Tony 이후 갈등 폭발, 마틸다 첫 작전, 호텔 잠입
2. **엔딩 트리 설계** — 변수 조합으로 4~5개 엔딩 분기 설계
   - 엔딩 1: 우유와 화분 (조용한 결말, mathilda.trust↑ + leon.attachment↑ + openedDoor)
   - 엔딩 2: ?
   - 엔딩 3: 그림자 (복수 결말, mathilda.rage↑ + leon.attachment↓)

### 우선순위 중간
3. **스탠스필드 시점 챕터** — ACT 1 같은 사건을 그의 관점에서 (DEA, 약물, 음악)
4. **ACT 3 작성** — 추격과 대결
5. **사운드 에셋** — 무료 라이브러리(Freesound.org, pixabay) 에서 mp3 5~10개 가져와 audio/에 배치

### 우선순위 낮음 (폴리시)
6. 추가 이미지 (필요 시 `tools/image-gen.html` 사용)
7. 디버그 메뉴 챕터 점프 링크 추가 (새 패시지마다)
8. 모바일 레이아웃 더 정밀하게

---

## 🔧 도구 사용법

### 이미지 추가 생성
브라우저 GUI: `tools/image-gen.html` 더블클릭
- 시점 프리셋 (LÉON / MATHILDA / STANSFIELD)
- 씬 타입 (환경 / 인물 / 단서 / 액션 / 시네마틱)
- 톤앤매너 자동 주입
- 히스토리 보관

또는 Python 스크립트로 배치:
```bash
export OPENAI_API_KEY="sk-..."
python tools/generate_one.py  # 파일 안의 IMAGES 배열만 편집
```

### 새 패시지 추가 시 체크리스트
1. `src/passages/{leon,mathilda,stansfield}.twee` 적절한 곳에 `::패시지명 [태그]` 추가
2. `src/passages/debug.twee`에 점프 링크 추가 (CLAUDE.md 룰)
3. 이미지 필요하면 `images/`에 추가 (1536×1024 권장)
4. `build.bat` 더블클릭

### 게임 실행
- `LEON_Three_Triggers.html` 더블클릭 → 브라우저
- 변경 후 캐시 비우려면 **Ctrl+Shift+R**

---

## 📝 알려진 이슈

- [ ] `Leon_06_Training`과 `Leon_07_Lesson` 모두 같은 `training_silhouette.png` 사용 중 (Lesson은 `mathilda_training.png`로 교체됨, Training은 두 장 연속 — 의도적)
- [ ] 사운드 mp3 파일 없음 — 매크로 호출 시 콘솔에 "BGM error" 뜨지만 게임은 정상 작동
- [ ] `leon_eye_memory.png` 미사용 상태 (마틸다 눈으로 교체됨)
- [ ] 디버그 메뉴 ACT 2 패시지 일부 점프 링크 누락
- [ ] 빌드 시 한국어 패시지명 일부 인코딩 문제 가능성 (현재까지는 OK)

---

## 🔐 보안 메모

- API 키 두 개 채팅에 노출됨 → **모두 폐기 처리 권장**:
  - `sk-proj-rfAG22...` (1차)
  - `sk-proj-dQRTk7...` (2차, 모든 이미지 생성에 사용)
- https://platform.openai.com/api-keys 에서 확인/회전
- 향후 키는 환경변수로만 (`.env` 파일도 git에 안 올라가게)

---

## 📌 작업 로그 — 2026-06-01 세션

### 스토리 (ACT2 완성 → ACT3 + 5엔딩)
- **시스템 정비**: 죽은 변수 부활(경계심/기술/소지품/스탠스필드), `<<gate>>`(임계값 선택지)·`<<flag>>`·`<<item>>`·`<<pick>>`(효과 미리보기 선택지) 매크로 도입
- **ACT 2 본편**: 토니 경고/돈 → 마틸다 복수 결심 → 옥상 저격 교습(Leon_11b) → 건물 정찰 → 잠입(함정) → 그녀가 홀로 떠남
- **ACT 3 전체**: 추격 → 구출(몸 던지기 / **손목 사격 분기**) → 스탠스필드 시점(알약·베토벤) → **토니 심문 2단(가족 협박)** → 포위전 3단(전기차단·어둠 교전·환풍구 작별) → 마지막 선택
- **엔딩 5개**: 희생(두 방아쇠, 2단 죽음 시퀀스+에필로그 화분 심기) / 조용(우유와 화분) / 그림자(복수) / **빚(손목 사격 전용)** / 닫힌 문(배드)
- **영화 충실성**: 레옹 과거 19살로 수정, 남동생 복수 동력 부각, 스탠스필드 코카인 동기, 글 가르치기("LEON"), "사는 맛" 대사, 센트럴파크 연습

### 텍스트/연출
- **시점 통일**: 레옹 = 2인칭("당신"), 마틸다 = 1인칭("나"), 스탠스필드 = 3인칭
- "12년" 과다 반복 정리(레옹 경력 ~20년, 마틸다 12살만 유지)
- 엔딩 "처음으로" → 완전 재시작(`Engine.restart()`)으로 변수 초기화 버그 수정
- 비약 전환부 다리 문단 추가(연습→정찰 등)

### UI / CSS (script.js, style.css)
- **본문 폭/폰트 확대**(`--content-width`), 시점별 HUD에 6스탯 모두 표시(현재 시점 강조)
- **시점 자동 판별**(패시지 태그 기반), **페이지 이동 시 스크롤 상단 복귀** 수정
- **라이트박스**(이미지 클릭 확대), **소품 쇼케이스**(`.prop` 캡션), **수칙 강조**(`.rule`), **배드엔딩 태그**
- **디버그 토글**: `setup.showDebug`(🛠 메뉴) + `setup.fastMode`(`<<timed>>` 딜레이 제거)

### 이미지 (gpt-image-1 → 메인 gpt-image-2)
- ACT2/ACT3 전 패시지 전용 컷 + 소품/디테일 대량 생성(스탠스필드 통일, 토니 씬, 죽음 시퀀스 등)
- **메인 4컷(타이틀·레옹·마틸다·스탠스필드) gpt-image-2로 교체** (image-1 백업 `*_img1.png` 보존)
- 정책 회피 프레이밍 유지(미성년자/무기/유혈 → 손·실루엣·POV·정물)

### 제출 패키징
- `README.md` 작성 + Notion README 페이지 작성(개요/실행/Twee/이미지/AI 활용/디버그)
- 로그·미사용 이미지 제외 정리 후 `LEON_Three_Triggers_제출.zip` 생성(약 186MB, 이미지 多)

### 남은 일 / 메모
- 사운드 mp3 미배치(매크로만 준비)
- zip 용량 큼 → 필요 시 이미지 JPG 변환으로 ~30MB대 축소 가능
- ⚠️ OpenAI API 키 채팅 노출 — 폐기(rotate) 권장

---

## 📌 작업 로그 — 2026-06-05 세션 (이미지 리파인 + 프롤로그/시점 + 사운드 + UI 버그)

### 🐛 핵심 버그 수정
- **`<<bgm>>` 매크로가 그동안 한 번도 작동 안 했음** — `track.…fadeTo(0.5,2)` 호출했는데 SugarCube 2.37엔 `fadeTo`가 없음(→ 매번 예외, catch로 "BGM error"만 찍고 무음). `track.loop(true); track.fade(2, 0.5, 0);`로 교체. 브라우저 실측으로 0→0.5 페이드인 확인. **게임 전체 BGM 부활.**
- **HUD와 본문 제목(ACT 배지) 겹침** — `#story`의 `transform: translateY(-50%)` 센터링이 max-height 적용 전 콘텐츠 높이로 계산돼 박스를 과하게 끌어올림. flex(`justify-content: safe center`) + `top:8.5em/bottom:5.5em` 앵커로 교체. 실측 검증(긴 본문 18px 여백, 짧은 본문 중앙 유지).

### 🎵 사운드
- 엔딩 곡 연결: `audio/bgm_ending.mp3`(Sting – Shape of My Heart, 사용자 보유 파일) → `Mathilda_END_Plant`(화분 심기 에필로그)에서 `<<bgm "ending">>`. `bgm_ending` 트랙 등록 + `bgm_all` 리스트 추가.
- ⚠️ 저작권 음원이라 배포 시 로열티프리 대체 권장. 자동재생은 첫 클릭(제스처) 후 해제됨.

### 🎬 스토리 / 패시지
- **프롤로그 확장**: `Leon_00_Briefing`(토니 의뢰 + 선글라스에 토니 반사) → `Leon_01_Hit`(잔당 제압 액션 2컷) → `Leon_01_Warning`(마약상 칼 협박, "토니가 보냈다…").
- **ACT2 = 마틸다 1인칭 시점** 전수 검증 완료(Leon_06~Leon_14_ActEnd 전부 `[mathilda]`, 2인칭 "당신" 0). 레옹 단독 장면은 "전해 들음/무전 너머"로 처리.
- **토니 대사 영화화**(Leon_09/10): 레옹이 말주변 없이 머뭇대다 돈을 요구 → 토니 "은행처럼 지켜준다 + 너 최근에 여자라도 생긴 거야?".
- **인터루드 = 필수 플래시백**: `Leon_05_Open`에서 양자택일 제거 → 문 열면 무조건 "한 시간 전 — 그녀가 본 것"으로 인터루드 진입. `Leon_04_Door` 미리보기 곁가지 제거(클라이맥스 2선택만).
- `Mathilda_01_Hallway` 도입에 **우유 심부름 다녀와 일당 발견** 정황 보강.
- 저격 선택지 라벨 "현장으로 나간다" → **"옥상에서 사격을 배운다"**(연습 장면에 맞게, 3곳).
- **`Stansfield_00_Aftermath` 신규**: 구출 직후 → 스탠스필드 시점 다리 패시지(빈손/부상 분기) → `Stansfield_01`. 어색한 점프 해소.
- **"우유와 화분" 엔딩 강화**: 회복 감각·"뿌리 없는 화분→흙에 뿌리내림" 콜백·페이싱 재배치.
- 액션 컷 추가: `Leon_17_Siege`(창밖 포위 + 문 돌파=천장 매복), `Leon_17b_Hold`(어둠 교전·부상·마틸다 눈, **섬광탄→수류탄**+폭발), `Leon_13_Push`(로비 총격전).
- 어색한 소품 제거: `Leon_01_Hit_End` 베레타 진열, `Leon_03_Stairs` "같은 우유".

### 🖼 이미지 (전부 gpt-image-2, 원본 `*_img1` 백업)
- **신규**: leon_glasses_tony, leon_warning_knife(선글라스 줌인 투샷), hit_action1/2, mathilda_hide_pov, mathilda_note(영어 손글씨 "I'M SORRY. THIS IS MY JOB."), mathilda_captured, lobby_gunfight, siege_street, door_breach(천장 매복), darkness_fight, leon_wounded_wall, grenade_blast.
- **교체/개선**: 스탠스필드 6컷 얼굴 통일, 토니 4컷 통일(table/defeated/envelope/hands_newspaper), scope_face(조깅인 표적=영화 정확도), leon_stairs(문틈 마틸다 POV), leon_open_ending(문 앞 마틸다), mathilda_in_apartment(입실), clue_milk(쏟아진 우유), sniper_lesson(역할 교체: 마틸다 조준/레옹 망원경), mathilda_resolve(신문 크게), mathilda_with_leon(미형↔거침 조정 후 시네마틱 유지), grenade_pin(반지→수류탄 핀).
- **삭제(미사용 정리)**: 초기 26개 + clue_pistol, prop_milk, rain_window, leon_warning.
- **노하우**: `moderation:"low"`가 gpt-image-2에서 작동 → 무기/총격/칼 컷 통과. 단 **유혈·미성년자 폭행은 하한선에 막혀 불가**(마틸다는 성인 묘사로 우회).

### ⚙️ UI
- 단서 목록: native `alert` → **시네마틱 모달**(라이트박스식 페이드/블러, 시점별 액센트, 스태거 애니메이션, ESC/바깥/닫기).

### 엔딩 (총 5개 — 사용자에게 확인)
- 우유와 화분(둘 다 생존) / 희생(마틸다만) / 그림자(복수, 둘 다·어두움) / 빚(손목사격 전용) / 닫힌 문(BAD). 마지막 선택에서 조건 충족분만 노출.

### 남은 일 / 메모
- 다른 BGM/SFX mp3 미배치(이제 매크로는 정상 → 파일만 넣으면 됨): bgm_leon/mathilda/stansfield/tense, sfx_*.
- 새로 쌓인 백업(`*_img1.png`)·tools 스크립트 정리 필요 시 일괄.
- ⚠️ 이번 세션 신규 OpenAI 키도 채팅 노출 — 작업 종료 후 회전(폐기) 권장.
