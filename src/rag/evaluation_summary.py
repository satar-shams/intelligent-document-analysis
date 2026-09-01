import json
from pathlib import Path


RESULTS_PATH = Path(
    "data/evaluation/manually_evaluated_results.jsonl"
)


def read_results(path: Path) -> list[dict]:
    results = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                results.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {exc}"
                ) from exc

    return results


def percentage(value: int, total: int) -> float:
    if total == 0:
        return 0.0

    return value / total * 100


def summarize_results(results: list[dict]) -> dict:
    total = len(results)

    answerable = sum(
        result["evaluation"]["answerable_from_context"]
        for result in results
    )

    correct = sum(
        result["evaluation"]["correct"]
        for result in results
    )

    grounded = sum(
        result["evaluation"]["grounded"]
        for result in results
    )

    return {
        "total": total,
        "answerable": answerable,
        "not_answerable": total - answerable,
        "correct": correct,
        "incorrect": total - correct,
        "grounded": grounded,
        "not_grounded": total - grounded,
    }


def main() -> None:
    results = read_results(RESULTS_PATH)
    summary = summarize_results(results)

    total = summary["total"]

    print("=" * 80)
    print("RAG EVALUATION SUMMARY")
    print("=" * 80)

    print(
        f"Total cases             : {total}"
    )

    print(
        f"Answerable from context : "
        f"{summary['answerable']} "
        f"({percentage(summary['answerable'], total):.1f}%)"
    )

    print(
        f"Not answerable          : "
        f"{summary['not_answerable']} "
        f"({percentage(summary['not_answerable'], total):.1f}%)"
    )

    print(
        f"Correct answers         : "
        f"{summary['correct']} "
        f"({percentage(summary['correct'], total):.1f}%)"
    )

    print(
        f"Incorrect answers       : "
        f"{summary['incorrect']} "
        f"({percentage(summary['incorrect'], total):.1f}%)"
    )

    print(
        f"Grounded answers        : "
        f"{summary['grounded']} "
        f"({percentage(summary['grounded'], total):.1f}%)"
    )

    print(
        f"Not grounded            : "
        f"{summary['not_grounded']} "
        f"({percentage(summary['not_grounded'], total):.1f}%)"
    )


if __name__ == "__main__":
    main()