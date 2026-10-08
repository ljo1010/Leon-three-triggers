# LÉON: Three Triggers — 시스템 설계

> ACT 2 진입 전 확정한 게임 시스템 명세. 단일 기준점(SSOT).
> 핵심 철학: **스탯 = 소프트 게이트 / 엔딩 = 플래그 기반** (베데스다식 선택지 다양화)

마지막 업데이트: 2026-05-31

---

## 1. 변수 명세

`StoryInit`에 정의 (src/story.twee). 모든 스탯은 정수.

| 변수 | 라벨 | 시작값 | 의미 | ↑ 시 해금되는 선택지 결 |
|---|---|---|---|---|
| `$leon.attachment` | 애착 | 0 | 마틸다에 대한 정 | 보호·감정·희생 |
| `$leon.discipline` | 규율 | 10 | 프로 정신 | 냉정·거절·전술 |
| `$leon.suspicion` | 경계심 | 0 | 위협 감지력 | 함정 간파·선제 대응 |
| `$mathilda.trust` | 신뢰 | 0 | 레옹을 믿는 정도 | 협력·고백 |
| `$mathilda.rage` | 분노 | 0 | 복수심 | 무모·폭력 |
| `$mathilda.skill` | 기술 | 0 | 훈련 성취도 | 작전 참여·사격 |
| `$stansfield.high` | 약물 | 5 | 도취 상태 | (스탠스필드 시점) |
| `$stansfield.cruelty` | 잔혹도 | 0 | 잔혹함 | (스탠스필드 시점) |
| `$clues` | — | `[]` | 발견 단서 배열 | — |
| `$inventory` | — | `[]` | 소지품 배열 | 아이템 게이트 |
| `$endingFlags` | — | `{}` | 엔딩 결정 플래그 | — |

**축(axis) 관계** — 같은 시점 안에서 대립하는 한 쌍씩:
- 레옹: `attachment ↔ discipline` (정 vs 프로), `suspicion`은 독립축
- 마틸다: `trust ↔ rage` (믿음 vs 복수), `skill`은 누적축

> ⚠️ 한 선택지가 한쪽을 올리면 보통 반대쪽을 내린다 (zero-sum 느낌). ACT 1이 이 패턴.
> skill·suspicion은 깎이지 않고 쌓이기만 하는 누적축 → 후반 게이트 재료.

---

## 2. 헬퍼 매크로 (src/script.js)

### `<<gate "경로" 임계값 "패시지">>라벨<</gate>>`
임계값 게이트 선택지. 스탯 ≥ 임계값이면 골드 태그 달린 특별 링크 해금,
미만이면 회색으로 잠긴 채 요구치를 보여줌(플레이어가 빌드 방향을 알 수 있게).
```
<<gate "leon.suspicion" 6 "Leon_10_Trap">>입구가 너무 조용하다 — 뒤로 돈다<</gate>>
<<gate "mathilda.skill" 3 "Leon_11_Solo">>마틸다에게 저격을 맡긴다<</gate>>
```
- 경로는 `"obj.key"` 형식. 라벨 한글 OK.
- 잠긴 선택지를 **숨기고 싶으면** `<<gate>>` 대신 평범한 `<<if>>` + `[[..]]` 사용.

### `<<pick "패시지" "라벨" "효과텍스트" ["셋터"]>>`
효과 미리보기 선택지. 클릭 전에 라벨 우측에 효과 태그(`.fx-tag`)를 보여준다.
```
<<pick "Leon_11_Restrain" "그녀를 말린다" "분노 −1 · 신뢰 +1 · 규율 +1">>
<<pick "Leon_11_Plan" '(규율) "정리할 거다."' "규율 +2" "$leon.discipline += 2">>
```
- 효과 태그 = **도착 패시지의 진입 `<<set>>` + (있으면) 4번째 인자 셋터**. 수동 동기화 — 도착 패시지의 set을 바꾸면 태그도 같이 고칠 것.
- 라벨에 `"`가 있으면 작은따옴표로 감싸기: `'(규율) "..."'`
- 셋터(4번째 인자)를 주면 클릭 시 실행 → 셋터 링크 `[[..][..]]` 대체.
- ⚠️ **이름이 `choice`면 안 됨** — SugarCube 내장 `<<choice>>`(deprecated)와 충돌해 덮어쓰기 실패. 그래서 `pick`.

### `<<gate>>`의 효과 태그 (4번째 인자)
`<<gate "경로" 임계값 "패시지" "효과텍스트">>라벨<</gate>>` — 해금/잠김 모두 효과 태그 표시.
잠긴 상태에서도 "무엇을 얻는지"가 보여 빌드 유도가 명확.

### `<<item "이름">>`
소지품 추가 + 토스트. 중복 추가 방지. 체크는 `$inventory.includes("이름")`.
```
<<item "베레타 92FS">>
<<if $inventory.includes("우유")>> ... <</if>>
```

### `<<flag "이름">>` 또는 `<<flag "이름" 값>>`
엔딩 플래그를 한곳에서 설정. 엔딩 분기는 오직 이걸로만 읽는다.
```
<<flag "killedTony">>          /* endingFlags.killedTony = true */
<<flag "route" "revenge">>     /* endingFlags.route = "revenge" */
```

### 기존 매크로 (유지)
`<<gunshot>>` `<<shake>>` `<<flash>>` `<<clue "이름">>` `<<sfx "이름">>` `<<bgm "이름">>`

---

## 3. 엔딩 설계 (플래그 기반)

**원칙**: 스탯은 엔딩을 직접 결정하지 않는다. 스탯은 *특별 선택지를 여는 열쇠*일 뿐.
플레이어가 그 선택을 실제로 하면 `<<flag>>`가 찍히고, **엔딩은 플래그 조합으로만** 갈린다.
→ 같은 엔딩이라도 스탯 빌드에 따라 가는 길(중간 선택지)이 달라짐 = 베데스다식 다양성.

### 핵심 플래그
| 플래그 | 찍히는 시점 | 상태 |
|---|---|---|
| `openedDoor` | Leon_05_Open | ✅ 구현 |
| `closedDoor` | Leon_05_Closed | ✅ 구현 — **배드엔딩 플래그** (아래 참고) |
| `moneyForMathilda` | Leon_10_Money | ✅ 구현 — 토니에게 그녀 몫 돈 부탁 |
| `firstOp` | Leon_11_Together | ✅ 구현 — 함께 가기로 약속 |
| `mathildaArmed` | Leon_12_Lookout | ✅ 구현 — 마틸다에게 무전기+총 |
| `sensedTrap` | Leon_13_Trap | ✅ 구현 — 함정을 간파 |
| `mathildaGone` | Leon_14_ActEnd | ✅ 구현 — 그녀가 홀로 떠남 (ACT 3 트리거) |
| `killedTony` | (ACT 3 예정) | 토니와 결별/제거 |
| `route` | (ACT 3 예정) | "quiet" / "revenge" / "sacrifice" 등 |

### 닫힌 문 = 배드엔딩 (회피 경로)
`closedDoor`는 진행 플래그가 아니라 **배드엔딩**이다. 두 곳 모두 동일 처리:
- `Leon_05_Closed` / `Mathilda_01_End`(closedDoor 분기) → `✖ BAD ENDING — 닫힌 문` 표시
- `[[다시 선택한다|Leon_04_Door][...상태 복원...]]`로 do-over (closedDoor=false, 닫힌문 스탯 변경 되돌림)
- ⚠️ 닫힌 문 경로는 **ACT 2(Leon_06_Training)로 진행하지 않는다** — 마틸다가 떠난 상태라 훈련 장면과 모순되기 때문.

### 엔딩 트리 (ACT 3에서 구현 완료)
Leon_18_LastChoice에서 선택지로 갈리고, 각 엔딩 패시지가 `<<flag "route" ...>>`를 찍는다.
- **두 방아쇠 (희생)** `Leon_END_Sacrifice` → `route="sacrifice"`. **항상 선택 가능**(원작 정전 라인). 레옹이 수류탄으로 스탠스필드와 함께 산화 → 에필로그 `Mathilda_END_School`(화분을 땅에 심음).
- **우유와 화분 (조용)** `Leon_END_Quiet` → `route="quiet"`. 게이트 **애착 ≥ 7**. 둘 다 생존하는 what-if.
- **그림자 (복수)** `Leon_END_Revenge` → `route="revenge"`. **`mathildaArmed` 플래그 必 + 게이트 분노 ≥ 4**. 마틸다가 직접 방아쇠 → 또 하나의 청소부.
- **닫힌 문 (배드엔딩)** `closedDoor` — ACT1에서 종료, ACT3 도달 안 함.

> 엔딩 선택지는 스탯 게이트로 *열리고*, 실제 엔딩은 그 선택으로 찍히는 `route` 플래그로 결정.
> `killedTony`는 미사용(ACT3에서 토니 배신 분기를 넣지 않음). 필요 시 확장.

---

## 4. 디버그 (src/passages/debug.twee)
- 현재 상태에 소지품·엔딩 플래그 표시
- 스탯 강제 설정: 신뢰/분노/스킬/애착/규율/**경계심**
- 엔딩 조건 프리셋, 전체 리셋
- **새 패시지 추가 시 점프 링크 + (게이트/플래그 쓰면) 프리셋 갱신**

---

## 5. ACT 2 게이트 & 스탯 소스 (브라우저 검증 완료)

### 스탯 소스 (어디서 ± 되는가)
| 스탯 | 소스 (누적) |
|---|---|
| `mathilda.trust` | KnockDoor +2 · **Leon_06_Training +1** · **Leon_07_Lesson +1** · Restrain +1 · Together +1 · Confess +1 · Run −1 |
| `mathilda.skill` | Leon_07_Lesson +1 · Leon_11_Plan +1(무조건) · Leon_12_Lookout +1 |
| `mathilda.rage` | Hide +1 · Run +2 · Leon_13_Push +1 · (Restrain −1) |
| `leon.suspicion` | Leon_10_TonyDeal +1(무조건) · Leon_12_Recon +1(무조건) · Leon_13_Trap +1 |
| `leon.attachment` | Watch +1 · Open +3 · Lesson +2 · Money +2 · Solo +2 · Confess +1 · (Close/Refuse 등 −) |

> trust 소스를 본편에 분산(Training+1, Lesson+1)한 이유: 신뢰 게이트가 인터루드 KnockDoor에만
> 의존하면 "문 열고 ACT2 직행" 경로에서 영영 잠긴다. 분산 후 **가르치거나(Lesson) 노크하면** 도달.

### 게이트 도달성 (경로별 검증)
| 게이트 | 위치 | 임계 | 도달 조건 | 검증 |
|---|---|---|---|---|
| 신뢰 | Leon_11_Plan | 2 | 가르침 **또는** 노크 | 직행+가르침=2 해금 / 냉정+거절=1 잠김 / 노크=2~3 해금 |
| 애착 | Leon_11_Plan | 5 | 애착 빌드 | open+lesson(+money)=5~7 해금 / 냉정=잠김 |
| 기술 | Leon_12_Recon | 2 | 가르친 경우만 | 가르침=2 해금 / 거절=1 잠김 |
| 경계심 | Leon_13_Infiltration | 2 | **모든 경로** | Tony+Recon 무조건 → 2 (단, `<<timed 15s>>` 안이라 시퀀스 후 등장) |

> 설계 의도: 냉정/거절 경로는 일부 게이트가 잠긴 채 "요구치"만 보임 = 베데스다식 위계. 의도된 것.

---

## 6. ACT 2 작성 체크리스트 (이 시스템으로)
1. 갈등마다 축을 건드린다 — 선택지가 attachment/discipline 또는 trust/rage를 ±.
2. 누적축(skill·suspicion)을 쌓을 기회를 ACT 2 전반에 분산 → 후반 게이트가 의미 생기게.
3. 분기점에선 `<<gate>>`로 특별 선택지 1~2개 + 누구나 가능한 기본 선택지.
4. 돌이킬 수 없는 핵심 선택엔 `<<flag>>` 찍기.
5. 소지품(베레타·우유·화분)이 후속 패시지에서 쓰이면 `<<item>>`으로 등록.
