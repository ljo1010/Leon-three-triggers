# LÉON: Three Triggers

Twine + SugarCube 2.37.3 인터랙티브 픽션 기말과제.
영화 레옹 기반, 다중 시점 (레옹/마틸다/스탠스필드).

## 빌드
`build.bat` 실행 → `LEON_Three_Triggers.html` 생성

## 구조
- `src/story.twee` — 메인 스토리, StoryInit, 시스템 패시지
- `src/passages/leon.twee` — 레옹 챕터
- `src/passages/mathilda.twee` — 마틸다 챕터
- `src/style.css` — 시네마틱 스타일
- `src/script.js` — 매크로 + HUD + 사운드

## 주의사항
- SugarCube 내장 `<<type>>`, `<<timed>>`, `<<next>>` 사용 (Harlowe 문법 X)
- `Config.debug = true` 절대 금지 (화면 깨짐)
- 패시지 추가 시 `Debug_Jump`에도 점프 링크 추가