# hplan_codex

> **WHETHER before HOW** — 만들어야 하는가를 먼저 묻고, 어떻게 만들지를 묻습니다.

Codex CLI용 PM Build Gate. AI 에이전트 코딩에 구조화된 의사결정 프레임워크.

[![local%20folders](https://img.shields.io/badge/local%20folders-28-blue)](skills/)
[![plugins](https://img.shields.io/badge/plugins-5-green)](skills/)
[![Codex CLI baseline](https://img.shields.io/badge/Codex%20CLI%20baseline-0.130.0-black)](https://developers.openai.com/codex)
[![license](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## 문제

AI 코딩 에이전트는 빠릅니다. 너무 빠릅니다.
무엇을 시키든 만들어냅니다 — 잘못된 제품을, 빠른 속도로.

hplan_codex는 HOW 앞에 **WHETHER 게이트**를 추가합니다:
- 이게 해결해야 할 맞는 문제인가?
- 실제 고통의 증거가 있는가?
- 이 규모에서 운영 비용이 감당 가능한가?

## Core 계약과 Local Folder

hplan-core 계약은 Codex 기준 **canonical capability 34개**를 정의합니다. 이 중 **25개는 native**, **9개는 adapter-required**입니다. `adapter-required` capability는 활성 상태가 아니므로, 별도 adapter가 승인되기 전에는 문서화된 draft 또는 local fallback을 사용합니다.

이 저장소에는 **local skill folder 28개**도 있습니다. 이는 28개 기능이라는 뜻이 아니라 설치 레이아웃 수이며, compatibility alias folder인 `roadmap`, `router`, `stakeholder-update` 3개를 포함합니다.

---

## 사전 준비: Codex CLI 설치

hplan_codex는 OpenAI Codex CLI 안에서 동작합니다. **먼저 Codex CLI를 설치하세요:**

```bash
npm install -g @openai/codex
```

공식 문서 및 다른 설치 방법: https://developers.openai.com/codex

---

## hplan_codex 설치

**권장 — Codex 세션 안에서 스킬 설치:**

```
$skill-installer https://github.com/kimsanguine/hplan_codex
```

28개 local folder를 Codex CLI 스킬 디렉토리에 설치합니다. 여기에는 compatibility alias 3개가 포함됩니다. 현재 작업 중인 프로젝트에 `harness/` 파일이나 보조 스크립트를 복사하지는 않습니다.

**프로젝트 설정 — latest-main bootstrap (tag-pinned/reproducible 아님):**

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan_codex/main/scripts/setup.sh)
```

`scripts/setup.sh`는 `harness/` 템플릿, `AGENTS.md`, `config.toml.example`,
`scripts/track-probe.sh` 같은 보조 스크립트를 프로젝트로 복사합니다.
Codex 스킬 설치는 하지 않으므로 `$skill-installer`와 함께 사용합니다.

`main`에 push하기 전 로컬 변경으로 설치를 검증하려면:

```bash
HPLAN_CODEX_SOURCE_DIR=/path/to/hplan_codex bash scripts/setup.sh --dir=/path/to/test-project
```

**수동 대안 — 검증된 local-source setup** (clone + 스킬 + 완전한 프로젝트 bootstrap):

```bash
git clone https://github.com/kimsanguine/hplan_codex.git
# doctor가 검증하는 Codex CLI scope에 스킬을 복사합니다.
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R hplan_codex/skills/* "${CODEX_HOME:-$HOME/.codex}/skills/"
# 이 명령은 harness, doctor, snapshot, repair backup도 현재 프로젝트에 설치합니다.
HPLAN_CODEX_SOURCE_DIR="$(pwd)/hplan_codex" bash hplan_codex/scripts/setup.sh --dir=.
# 선택: config 예시를 보관한 뒤, 기존 전역 설정에 필요한 값만 수동 병합합니다.
mkdir -p "${CODEX_HOME:-$HOME/.codex}"
cp -n hplan_codex/config.toml.example "${CODEX_HOME:-$HOME/.codex}/config.toml.example"
```

---

## 첫 10분 성공 경로

첫 성공에는 별도 설치 두 가지가 필요합니다. `$skill-installer`는 `$CODEX_HOME/skills`에 스킬을 설치하고, `scripts/setup.sh`는 프로젝트 로컬의 harness, doctor, core snapshot만 복사합니다. 프로젝트 폴더에서 다음 순서를 확인합니다:

1. Codex 세션에서 `$skill-installer https://github.com/kimsanguine/hplan_codex`를 실행하고, 완료 후 새 turn을 시작합니다.
2. 프로젝트 디렉토리에서 아래 latest-main bootstrap을 실행합니다. `$skill-installer` 실행 후 동작하지만 tag-pinned/reproducible한 설치는 아닙니다.

   ```bash
   bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan_codex/main/scripts/setup.sh) --dir=.
   ```
3. 읽기 전용 설치 확인을 실행합니다: `python3 scripts/hplan_doctor.py`. 이 명령은 활성 `$CODEX_HOME`의 첫 성공 스킬 3개와 프로젝트 snapshot을 함께 확인합니다.
4. Codex CLI에서 프로젝트를 열고 `$brainstorm "아이디어"`를 실행합니다.
5. 첫 WHETHER 판단(`GO`, `INVESTIGATE`, `HOLD`)을 기록합니다.
6. 아이디어를 계속 볼 가치가 있으면 `harness/pain.md`에 AI 생성 seed가 아닌 실제 증거를 추가합니다.
7. `$evidence-rubric`을 실행하고 점수와 부족한 증거를 남깁니다.

첫 성공 기준: 10분 안에 build/no-build 판단과 다음 증거 액션이 문서화됩니다.

### 처음에는 이 세 스킬을 권장합니다

1. `$brainstorm` — WHETHER 게이트부터 시작하므로 기능 목록이 아니라 구체적인 build/no-build 방향을 먼저 만듭니다.
2. `$socratic-question` — 그 방향에 숨어 있는 가정을 명시하고 구현 전에 가장 위험한 불확실성을 드러냅니다.
3. `$evidence-rubric` — 증거를 점수화하고 부족한 항목을 알려 줍니다. AI 생성 seed는 `GO`의 실제 증거로 계산하지 않습니다.

### 읽기 전용 `hplan doctor` 대응 명령

`scripts/setup.sh`로 준비한 프로젝트에서 `python3 scripts/hplan_doctor.py`를 실행하세요.
이 명령은 파일을 쓰지 않으며 Python, 확인 가능한 Codex CLI 버전, `$CODEX_HOME/skills`의 첫 성공 스킬 3개, `runtime/hplan-core/`의 총 4개 snapshot artifact를 확인합니다.

- `정상` — `$brainstorm "아이디어"`로 시작합니다.
- `자동 복구 가능` — 첫 성공 스킬이 없으면 Codex에서 `$skill-installer https://github.com/kimsanguine/hplan_codex`를 실행합니다. snapshot만 누락되었으면 `python3 scripts/repair_hplan_core_snapshot.py --root .`를 실행합니다. 그 뒤 doctor를 다시 실행합니다. 이 명시적 로컬 복구는 runtime snapshot artifact 4개만 되돌리며, doctor 자체는 절대 쓰지 않습니다.
- `강사 호출` — mismatch 출력을 보존하고 패키지 관리자에게 matching core snapshot을 요청합니다. doctor는 임의로 덮어쓰지 않습니다.

프로젝트 snapshot은 `runtime/hplan-core/`의 총 4개 artifact입니다: `hplan-core.lock`, `hplan-capability-matrix.json`, `HPLAN_CAPABILITY_MATRIX.md`, `hplan-core-adapter.json`. 복구 원본은 프로젝트 로컬 `.hplan-core-snapshot/` backup이며, 체크인된 `hplan-core-fixture/`는 CI parity 전용 데이터이므로 복구 원본이 아닙니다.

**전체 워크플로우:**

```
$brainstorm → $socratic-question → $opp-tree → $prd → $conductor
```

공개 저장소 정책: 프로젝트 `docs/`와 `.archive/`는 제외합니다. 공개 runtime 데이터는 `runtime/hplan-core/`로 한정하고, 긴 가이드와 과거 자료는 private로 유지합니다.

---

## 5개 플러그인 라이프사이클

| 플러그인 | 핵심 질문 | 주요 스킬 |
|---|---|---|
| **hplan** | 만들어야 하는가? | brainstorm, evidence-rubric |
| **discover** | 진짜 문제가 무엇인가? | socratic-question, opp-tree |
| **architect** | 어떻게 설계하는가? | orchestration, memory-arch |
| **deliver** | 어떻게 만들고 출시하는가? | prd, conductor, sprint |
| **operate** | 어떻게 지속하는가? | pm-engine, metrics-design |

---

## 보안 & 샌드박스

hplan_codex는 Codex CLI 샌드박스 안에서 실행됩니다. 아래 샌드박스 동작은 **Codex CLI 0.130.0 baseline**에서 검증된 내용이며, 새 CLI에서는 현재 문서를 확인해야 합니다:

| 모드 | 권한 |
|---|---|
| `read-only` | 프로젝트 파일 읽기 전용 — 쓰기·네트워크 불가 |
| `workspace-write` | 프로젝트 파일 읽기 + 쓰기 + 워크스페이스 내 명령 실행 (기본값) |
| `danger-full-access` | 전체 읽기/쓰기 + 네트워크 — 태스크를 신뢰할 때만 사용 |

샌드박스 모드는 Codex CLI 세션 또는 설정에서 지정합니다. hplan_codex의 빌드 단계 스킬은 `workspace-write`를 전제로 합니다.

> 검증된 Codex CLI 0.130.0 baseline에서는 파일 기반 hook을 사용할 수 없었습니다. `scripts/track-probe.sh`는 `bash scripts/track-probe.sh`로 직접 실행하거나 Codex automation에 연결할 수 있는 수동 스프린트 추적 프로브로 제공됩니다.

## 현재 상태 & 검증

현재 실행 가능:
- `$skill-installer`를 통한 스킬 설치
- `bash scripts/setup.sh`를 통한 harness/script 부트스트랩
- `bash scripts/track-probe.sh` 수동 프로브 실행
- `python3 scripts/hplan_doctor.py` 읽기 전용 설치 및 core snapshot 점검
- `python3 scripts/repair_hplan_core_snapshot.py --root .` 명시적 로컬 snapshot 복구
- `python3 scripts/validate_agents.py` 정적 스킬/문서 검증

예정 또는 adapter 의존 기능은
[skills/ROUTING_REGISTRY.md](skills/ROUTING_REGISTRY.md)에서 관리합니다.

공개 canonical 참조: [스킬 상태 registry](skills/ROUTING_REGISTRY.md)와 `runtime/hplan-core/` core snapshot입니다.

검증 명령:

```bash
python3 scripts/validate_agents.py
python3 scripts/hplan_doctor.py
python3 scripts/cogs_sentinel.py --json
# CI는 private core commit에 고정된 체크인 `hplan-core-fixture`를 사용합니다.
# 이는 parity fixture이며 public core 배포물이 아닙니다. 유지보수 시 승인된
# local core checkout과 비교할 때만 HPLAN_CORE_DIR를 지정합니다.
python3 -m unittest discover -s tests
bash -n scripts/setup.sh scripts/track-probe.sh
bash scripts/setup.sh --help
HPLAN_CODEX_SOURCE_DIR="$PWD" bash scripts/setup.sh --dir="$(mktemp -d)"
mkdir -p .track
printf '%s\n' track-smoke > .track/current_task
printf '%s\n' '{"tool_name":"write_file","tool_input":{"file_path":"noop","content":"a\nb\n"}}' | bash scripts/track-probe.sh
test -s .track/actual_log.jsonl
```

---

## 스킬 호출

```
$socratic-question [아이디어]    ← 가정 심문
$opp-tree [도메인]               ← 기회 발굴
$brainstorm [아이디어]           ← WHETHER 3문 체크
$prd [제품]                      ← 15섹션 PRD 작성
$cost-sim [기능]                 ← 비용 시뮬레이션
```

---

## 핵심 원칙

**P1 — 결정론 우선**: LLM은 분류·초안·자연어 생성에만. if문으로 쓰지 않는다.
**P2 — Fail Loud**: 불확실성을 숨기지 않는다. 검증 없는 "완료" 보고 금지.
**P3 — 외과적 변경**: 필요한 것만 건드린다.
**P4 — 목표 주도**: 검증 행위가 인용된 "완료"만 인정한다.
