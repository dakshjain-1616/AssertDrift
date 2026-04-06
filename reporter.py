"""Rich-based reporter for assertion analysis results."""

from rich.table import Table
from rich.console import Console
from typing import List, Dict, Optional


def _per_func_avg(test_func: Dict) -> float:
    assertions = test_func['assertions']
    if not assertions:
        return 0.0
    return sum(a['score'] for a in assertions) / len(assertions)


def _strength_label(avg: float) -> str:
    if avg >= 2.5:
        return 'HIGH'
    if avg >= 1.5:
        return 'MEDIUM'
    if avg >= 0.5:
        return 'LOW'
    return 'ZERO'


def render_report(results: List[Dict], show_suggestions: bool = False,
                  suggestions: Optional[List[str]] = None) -> None:
    console = Console()

    table = Table(
        title="AssertDrift Analysis Report",
        header_style="bold magenta",
        border_style="blue",
    )
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Test Name", style="cyan")
    table.add_column("Assertions", justify="right")
    table.add_column("Avg Score", justify="right")
    table.add_column("Strength", justify="center")
    table.add_column("Flagged", justify="center")
    if show_suggestions:
        table.add_column("Suggested Improvement", style="italic yellow")

    row_idx = 0
    for result in results:
        file_name = result['file']
        for test_func in result['test_functions']:
            avg_score = _per_func_avg(test_func)
            strength = _strength_label(avg_score)
            flagged = avg_score < 1.5
            color = ('green' if strength == 'HIGH' else
                     'yellow' if strength == 'MEDIUM' else
                     'red' if strength == 'LOW' else
                     'bright_red')

            row = [
                file_name,
                test_func['name'],
                str(test_func['assertion_count']),
                f"{avg_score:.2f}",
                strength,
                "⚠️" if flagged else "✓",
            ]

            if show_suggestions:
                hint = ""
                if suggestions and row_idx < len(suggestions):
                    hint = suggestions[row_idx] or ""
                    if len(hint) > 80:
                        hint = hint[:77] + "..."
                row.append(hint)

            table.add_row(*row, style=color)
            row_idx += 1

    console.print(table)

    total_tests = sum(len(r['test_functions']) for r in results)
    total_assertions = sum(r['total_assertions'] for r in results)
    flagged_count = sum(
        1 for r in results
        for t in r['test_functions']
        if _per_func_avg(t) < 1.5
    )

    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  Total test files:     {len(results)}")
    console.print(f"  Total test functions: {total_tests}")
    console.print(f"  Total assertions:     {total_assertions}")
    console.print(f"  Flagged weak tests:   {flagged_count}")


def print_results(results: List[Dict], show_suggestions: bool = False,
                  suggestions: Optional[List[str]] = None) -> None:
    render_report(results, show_suggestions, suggestions)
