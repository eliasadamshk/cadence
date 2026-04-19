"""Eval CLI runner.

Usage:
    python -m evals.runner fast                           # all scenarios, fast mode
    python -m evals.runner fast simple_updates blockers    # specific scenarios
    python -m evals.runner e2e                             # all scenarios, full E2E
    python -m evals.runner e2e mixed                       # specific scenario, E2E

Options:
    --model MODEL       Override OpenRouter model (can repeat for comparison)
    --runs N            Run each scenario N times, report best (default: 1)
"""
from __future__ import annotations

import asyncio
import importlib
import sys

from evals.scenarios import Scenario
from evals.scoring import ScenarioScore, print_report

ALL_SCENARIO_NAMES = [
    "simple_updates",
    "blockers",
    "new_tickets",
    "reassignment",
    "no_actions",
    "mixed",
]


def load_scenarios(names: list[str]) -> list[Scenario]:
    scenarios = []
    for name in names:
        mod = importlib.import_module(f"evals.scenarios.{name}")
        scenarios.append(mod.scenario)
    return scenarios


async def run_fast(
    scenarios: list[Scenario],
    model: str | None = None,
    runs: int = 1,
) -> list[ScenarioScore]:
    from evals.eval_actions import eval_scenario

    scores = []
    for s in scenarios:
        label = f"Running fast eval: {s.name}"
        if runs > 1:
            label += f" (best of {runs})"
        print(f"{label}...")
        best: ScenarioScore | None = None
        for _ in range(runs):
            try:
                score = await eval_scenario(s, model_override=model)
            except Exception as e:
                print(f"  ERROR: {e}")
                continue
            if best is None or score.f1 > best.f1:
                best = score
        if best is None:
            best = ScenarioScore(
                name=s.name, matches=[], false_positives=[],
                precision=0, recall=0, f1=0,
            )
        scores.append(best)  # type: ignore[arg-type]
    return scores


async def run_e2e(scenarios: list[Scenario], runs: int = 1) -> list[ScenarioScore]:
    from evals.eval_e2e import eval_scenario

    scores = []
    for s in scenarios:
        label = f"Running E2E eval: {s.name} (~50s per run)"
        if runs > 1:
            label += f" x{runs} runs, best-of"
        print(f"{label}...")
        best: ScenarioScore | None = None
        for r in range(runs):
            if runs > 1:
                print(f"  run {r + 1}/{runs}...", end=" ", flush=True)
            try:
                score = await eval_scenario(s)
            except Exception as e:
                print(f"ERROR: {e}")
                continue
            if runs > 1:
                print(f"F1={score.f1:.0%}")
            if best is None or score.f1 > best.f1:
                best = score
            if best.f1 >= 1.0:
                break  # perfect score, no need for more runs
        if best is None:
            best = ScenarioScore(
                name=s.name, matches=[], false_positives=[],
                precision=0, recall=0, f1=0,
            )
        scores.append(best)
    return scores


def parse_args(argv: list[str]):
    mode = argv[1] if len(argv) > 1 else None
    if mode not in ("fast", "e2e"):
        print(__doc__)
        sys.exit(1)

    models: list[str] = []
    names: list[str] = []
    runs = 1
    i = 2
    while i < len(argv):
        if argv[i] == "--model" and i + 1 < len(argv):
            models.append(argv[i + 1])
            i += 2
        elif argv[i] == "--runs" and i + 1 < len(argv):
            runs = int(argv[i + 1])
            i += 2
        else:
            names.append(argv[i])
            i += 1

    if not names:
        names = ALL_SCENARIO_NAMES
    if not models:
        models = [None]  # type: ignore[list-item]

    return mode, names, models, runs


async def main():
    mode, names, models, runs = parse_args(sys.argv)
    scenarios = load_scenarios(names)

    for model in models:
        if model:
            print(f"\n{'=' * 70}")
            print(f"MODEL: {model}")
            print(f"{'=' * 70}")

        if mode == "fast":
            scores = await run_fast(scenarios, model=model, runs=runs)
        else:
            scores = await run_e2e(scenarios, runs=runs)

        print_report(scores)


if __name__ == "__main__":
    asyncio.run(main())
