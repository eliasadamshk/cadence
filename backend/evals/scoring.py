from __future__ import annotations

from dataclasses import dataclass

from app.models.actions import ExtractedAction
from evals.scenarios import ExpectedAction


@dataclass
class MatchResult:
    expected: ExpectedAction
    matched: ExtractedAction | None
    score: float  # 0.0 to 1.0


@dataclass
class ScenarioScore:
    name: str
    matches: list[MatchResult]
    false_positives: list[ExtractedAction]
    precision: float
    recall: float
    f1: float


def score_actions(
    name: str,
    expected: list[ExpectedAction],
    actual: list[ExtractedAction],
) -> ScenarioScore:
    used_actual: set[int] = set()
    matches: list[MatchResult] = []

    for exp in expected:
        best_idx = -1
        best_score = 0.0

        for i, act in enumerate(actual):
            if i in used_actual:
                continue
            s = _match_score(exp, act)
            if s > best_score:
                best_score = s
                best_idx = i

        if best_idx >= 0 and best_score >= 0.5:
            used_actual.add(best_idx)
            matches.append(MatchResult(expected=exp, matched=actual[best_idx], score=best_score))
        else:
            matches.append(MatchResult(expected=exp, matched=None, score=0.0))

    false_positives = [act for i, act in enumerate(actual) if i not in used_actual]

    true_pos = sum(1 for m in matches if m.matched)
    precision = true_pos / (true_pos + len(false_positives)) if (true_pos + len(false_positives)) > 0 else 1.0
    recall = true_pos / len(expected) if expected else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return ScenarioScore(
        name=name,
        matches=matches,
        false_positives=false_positives,
        precision=precision,
        recall=recall,
        f1=f1,
    )


def _match_score(exp: ExpectedAction, act: ExtractedAction) -> float:
    if exp.kind != act.kind:
        return 0.0

    score = 0.5  # kind matched

    if exp.card_id:
        score += 0.3 if act.card_id == exp.card_id else 0.0

    if exp.title_contains:
        score += 0.3 if act.title and exp.title_contains.lower() in act.title.lower() else 0.0

    if exp.to_status:
        score += 0.1 if act.to_status == exp.to_status else 0.0

    if exp.assignee:
        score += 0.1 if act.assignee and exp.assignee.lower() in act.assignee.lower() else 0.0

    return min(score, 1.0)


def print_report(scores: list[ScenarioScore]):
    print("\n" + "=" * 70)
    print("EVAL REPORT")
    print("=" * 70)

    for s in scores:
        status = "PASS" if s.f1 >= 0.8 else "WARN" if s.f1 >= 0.5 else "FAIL"
        print(f"\n[{status}] {s.name}")
        print(f"  Precision: {s.precision:.0%}  Recall: {s.recall:.0%}  F1: {s.f1:.0%}")

        for m in s.matches:
            if m.matched:
                print(f"  + {m.expected.kind} {m.expected.card_id or m.expected.title_contains or ''} (score: {m.score:.2f})")
            else:
                print(f"  - MISSED: {m.expected.kind} {m.expected.card_id or m.expected.title_contains or ''}")

        for fp in s.false_positives:
            print(f"  ! FALSE POS: {fp.kind} {fp.card_id or fp.title or ''}: {fp.summary}")

    total_f1 = sum(s.f1 for s in scores) / len(scores) if scores else 0
    print(f"\n{'=' * 70}")
    print(f"AGGREGATE F1: {total_f1:.0%}  ({len(scores)} scenarios)")
    print("=" * 70)
