#!/usr/bin/env python3
"""Deterministic evidence-rubric scorer for hplan.

The scorer intentionally uses transparent keyword and structure checks. It is a
gate signal, not a replacement for PM judgment or customer discovery.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


RUBRIC: dict[str, int] = {
    "icp_specificity": 20,
    "recent_painful_event": 15,
    "current_workaround": 15,
    "repetition": 10,
    "economic_pain": 15,
    "switching_trigger": 10,
    "mvp_narrowness": 10,
    "acquisition_path": 5,
}

AXIS_LABELS: dict[str, str] = {
    "icp_specificity": "ICP specificity",
    "recent_painful_event": "Recent painful event",
    "current_workaround": "Current workaround",
    "repetition": "Repetition / frequency",
    "economic_pain": "Economic pain",
    "switching_trigger": "Switching trigger",
    "mvp_narrowness": "MVP narrowness",
    "acquisition_path": "Acquisition path to first 5 users",
}

ECONOMIC_PATTERNS = [
    r"\$\s?\d",
    r"\b\d+[kKmM]\b",
    r"\b(revenue|cost|budget|deal|cash|margin|profit|price|paid|pay|invoice)\b",
    r"\b(churn|renewal|risk|compliance|fine|penalty|loss|lost|lawsuit)\b",
    r"\b(conversion|sales|pipeline|expansion|collection|roi)\b",
    r"(매출|비용|예산|리스크|위험|벌금|손실|이탈|전환|계약|결제|청구)",
]


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple, set)):
        return "\n".join(_as_text(item) for item in value if _as_text(item))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value).strip()


def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9가-힣$]+", text.lower())


def _contains(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def _count_items(value: Any) -> int:
    if isinstance(value, (list, tuple, set)):
        return len([item for item in value if _as_text(item)])
    text = _as_text(value)
    if not text:
        return 0
    parts = re.split(r"[,;\n]+", text)
    return len([part for part in parts if part.strip()])


def _interview_lines(value: Any) -> list[str]:
    if isinstance(value, (list, tuple, set)):
        return [line.strip() for line in (_as_text(item) for item in value) if line.strip()]
    return [line.strip() for line in _as_text(value).splitlines() if line.strip()]


def _economic_pain_present(text: str) -> bool:
    return _contains(text, ECONOMIC_PATTERNS)


def _score_icp(target: str) -> tuple[int, list[str]]:
    signals: list[str] = []
    text = target.lower()
    words = _tokens(target)
    generic = {"everyone", "anyone", "users", "people", "general", "consumer"}
    score = 0

    if len(words) >= 5 and not any(word in generic for word in words):
        score += 6
        signals.append("specific target description")
    if _contains(text, [r"\b(who|that|which)\b", r"(처리|관리|검토|운영|사용|하는)"]):
        score += 4
        signals.append("behavioral qualifier")
    if _contains(
        text,
        [
            r"\b(review|handle|manage|operate|process|ship|run|use|triage|respond)\b",
            r"(검토|처리|관리|운영|대응)",
        ],
    ):
        score += 4
        signals.append("observable behavior")
    if _contains(
        text,
        [
            r"\b(leads|operators|managers|admins|engineers|founders|reps|teams|pm|finance|security|sales)\b",
            r"(담당자|운영자|관리자|팀|리드|PM|재무|보안|영업)",
        ],
    ):
        score += 4
        signals.append("role or team named")
    if _contains(text, [r"\b(weekly|daily|monthly|every|during|when)\b", r"(매주|매일|매월|반복|때마다)"]):
        score += 2
        signals.append("usage context or cadence")

    return min(score, RUBRIC["icp_specificity"]), signals


def _score_recent_event(combined: str) -> tuple[int, list[str]]:
    signals: list[str] = []
    score = 0
    if _contains(combined, [r"\b(yesterday|today|last\s+(week|month)|this\s+week|recently)\b", r"(어제|오늘|지난주|지난달|최근)"]):
        score += 8
        signals.append("recent timing")
    if _contains(combined, [r"\b(stalled|delayed|lost|missed|failed|blocked|escalated|broke|late)\b", r"(지연|실패|손실|막힘|늦|놓쳤)"]):
        score += 4
        signals.append("painful event verb")
    if _contains(combined, [r"\b\d+\b", r"\b(one|two|three|four|five)\b", r"\b(deal|customer|ticket|invoice|request)s?\b", r"(건|명|계약|고객|청구서)"]):
        score += 3
        signals.append("concrete event detail")
    return min(score, RUBRIC["recent_painful_event"]), signals


def _score_workaround(alternatives: Any, combined: str) -> tuple[int, list[str]]:
    signals: list[str] = []
    score = 0
    item_count = _count_items(alternatives)
    alternatives_text = _as_text(alternatives).lower()

    if item_count >= 1:
        score += 4
        signals.append("alternative named")
    if item_count >= 2:
        score += 3
        signals.append("multiple alternatives")
    if _contains(
        alternatives_text,
        [
            r"\b(spreadsheet|slack|email|template|consultant|manual|outsourc|tracker|current|tool|workaround)\b",
            r"(스프레드시트|엑셀|슬랙|이메일|수동|외주|컨설턴트|대체)",
        ],
    ):
        score += 4
        signals.append("workaround mechanism")
    if _contains(combined, [r"\b(use|uses|today|pay|spend|paid|currently|already)\b", r"(현재|이미|사용|지불|쓴다)"]):
        score += 4
        signals.append("current effort or spend")
    return min(score, RUBRIC["current_workaround"]), signals


def _score_repetition(combined: str, line_count: int) -> tuple[int, list[str]]:
    signals: list[str] = []
    score = 0
    if _contains(combined, [r"\b(weekly|daily|monthly|every|per\s+(week|month|day)|recurring|repeat)\b", r"(매주|매일|매월|반복|정기)"]):
        score += 6
        signals.append("cadence")
    if _contains(combined, [r"\b(multiple|many|several|three|five|\d+)\b", r"(여러|반복|다수|\d+)"]):
        score += 2
        signals.append("volume or repetition detail")
    if line_count >= 2:
        score += 2
        signals.append("multiple interview lines")
    return min(score, RUBRIC["repetition"]), signals


def _score_economic_pain(combined: str, interviews: list[str]) -> tuple[int, list[str]]:
    signals: list[str] = []
    score = 0
    if _economic_pain_present(combined):
        score += 6
        signals.append("economic keyword")
    if _contains(combined, [r"\$\s?\d", r"\b\d+[kKmM]\b", r"\b(pay|paid|cost|budget|price)\b", r"(지불|비용|예산|가격)"]):
        score += 5
        signals.append("money amount or spend")
    if _contains(combined, [r"\b(risk|churn|renewal|compliance|loss|lost|penalty|delay|cash|collection)\b", r"(위험|리스크|이탈|손실|벌금|지연)"]):
        score += 2
        signals.append("business risk")
    if interviews and _economic_pain_present("\n".join(interviews)):
        score += 2
        signals.append("economic pain in interview notes")
    return min(score, RUBRIC["economic_pain"]), signals


def _score_switching(combined: str) -> tuple[int, list[str]]:
    signals: list[str] = []
    score = 0
    if _contains(combined, [r"\b(switch|stop using|replace|leave|move from|migrate)\b", r"(전환|교체|그만|바꾸)"]):
        score += 7
        signals.append("switching language")
    if _contains(combined, [r"\b(if|when|would|reduced|reliable|without|trigger)\b", r"(만약|조건|하면|때|신뢰|줄이면)"]):
        score += 3
        signals.append("trigger condition")
    return min(score, RUBRIC["switching_trigger"]), signals


def _score_mvp(features: Any) -> tuple[int, list[str]]:
    count = _count_items(features)
    if count == 0:
        return 0, []
    if count <= 3:
        return 10, [f"{count} feature candidates"]
    if count == 4:
        return 5, ["4 feature candidates"]
    return 2, [f"{count} feature candidates"]


def _score_acquisition(combined: str) -> tuple[int, list[str]]:
    signals: list[str] = []
    score = 0
    if _contains(combined, [r"\b(first\s*)?5\b", r"\bfive\b", r"(5명|다섯)"]):
        score += 3
        signals.append("first five users referenced")
    if _contains(combined, [r"\b(introduce|intro|refer|peer group|network|name|customer|lead)s?\b", r"(소개|추천|네트워크|고객|리드)"]):
        score += 2
        signals.append("reachable acquisition path")
    return min(score, RUBRIC["acquisition_path"]), signals


def generate_report(payload: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "idea": _as_text(payload.get("idea")),
        "target": _as_text(payload.get("target")),
        "hypothesis": _as_text(payload.get("hypothesis")),
        "alternatives": _as_text(payload.get("alternatives")),
        "features": _as_text(payload.get("features")),
        "interview_notes": _as_text(payload.get("interview_notes")),
    }
    interviews = _interview_lines(payload.get("interview_notes"))
    combined = "\n".join(value for value in fields.values() if value)

    scored = {
        "icp_specificity": _score_icp(fields["target"]),
        "recent_painful_event": _score_recent_event(combined),
        "current_workaround": _score_workaround(payload.get("alternatives"), combined),
        "repetition": _score_repetition(combined, len(interviews)),
        "economic_pain": _score_economic_pain(combined, interviews),
        "switching_trigger": _score_switching(combined),
        "mvp_narrowness": _score_mvp(payload.get("features")),
        "acquisition_path": _score_acquisition(combined),
    }

    axes = {
        axis: {
            "label": AXIS_LABELS[axis],
            "score": score,
            "max": RUBRIC[axis],
            "signals": signals,
        }
        for axis, (score, signals) in scored.items()
    }
    score = sum(axis["score"] for axis in axes.values())
    missing = [axis for axis, data in axes.items() if data["score"] < data["max"] * 0.55]

    build_conditions = {
        "score_at_least_75": score >= 75,
        "interview_lines": len(interviews),
        "interview_lines_at_least_2": len(interviews) >= 2,
        "economic_pain": _economic_pain_present(combined),
    }

    if all(
        [
            build_conditions["score_at_least_75"],
            build_conditions["interview_lines_at_least_2"],
            build_conditions["economic_pain"],
        ]
    ):
        decision = "build"
    elif score >= 55:
        decision = "interview"
    elif score >= 35:
        decision = "pivot"
    else:
        decision = "hold"

    return {
        "score": score,
        "decision": decision,
        "missing": missing,
        "axes": axes,
        "rubric": RUBRIC,
        "build_conditions": build_conditions,
        "input": fields,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Evidence Rubric Report",
        "",
        f"Score: `{report['score']}/100`",
        f"Decision: `{report['decision']}`",
        "",
        "## Breakdown",
        "",
        "| Axis | Score | Max | Signals |",
        "|---|---:|---:|---|",
    ]
    for axis, data in report["axes"].items():
        signals = ", ".join(data["signals"]) if data["signals"] else "missing"
        lines.append(f"| {data['label']} (`{axis}`) | {data['score']} | {data['max']} | {signals} |")

    missing = ", ".join(f"`{axis}`" for axis in report["missing"]) or "none"
    conditions = report["build_conditions"]
    lines.extend(
        [
            "",
            "## Missing",
            "",
            missing,
            "",
            "## Build Conditions",
            "",
            f"- Score >= 75: `{conditions['score_at_least_75']}`",
            f"- Interview lines >= 2: `{conditions['interview_lines_at_least_2']}` ({conditions['interview_lines']})",
            f"- Economic pain keyword present: `{conditions['economic_pain']}`",
            "",
        ]
    )
    return "\n".join(lines)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("input JSON must be an object")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Score hplan evidence rubric input.")
    parser.add_argument("input", type=Path, help="Path to JSON input")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    args = parser.parse_args()

    report = generate_report(_load_json(args.input))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report))


if __name__ == "__main__":
    main()
