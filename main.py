"""AssertDrift CLI - Analyze test assertion strength."""

import sys
from pathlib import Path

# Ensure the tool's own directory is on sys.path so imports work
# regardless of where the user runs the script from
sys.path.insert(0, str(Path(__file__).parent))

import typer
from analyzer import analyze_tests
from reporter import print_results
from suggester import generate_suggestions_for_results

app = typer.Typer(help="AssertDrift — Detect tests that pass but prove nothing.")


@app.command()
def analyze(
    tests_dir: str = typer.Argument(..., help="Directory containing test_*.py files (searched recursively)"),
    suggest: bool = typer.Option(False, "--suggest", "-s", help="Generate AI-powered improvement suggestions via OpenRouter"),
):
    """Scan test files and score every assertion by strength (ZERO → LOW → MEDIUM → HIGH)."""
    tests_path = Path(tests_dir)

    if not tests_path.exists():
        typer.echo(f"Error: '{tests_dir}' does not exist.", err=True)
        raise typer.Exit(code=1)

    if not tests_path.is_dir():
        typer.echo(f"Error: '{tests_dir}' is not a directory.", err=True)
        raise typer.Exit(code=1)

    results = analyze_tests(str(tests_path))

    if not results:
        typer.echo(f"No test_*.py files found under '{tests_dir}'.")
        raise typer.Exit(code=0)

    suggestions = None
    if suggest:
        typer.echo("Generating AI suggestions via OpenRouter…")
        try:
            suggestions = generate_suggestions_for_results(results)
        except ValueError as e:
            typer.echo(f"Warning: {e}", err=True)
            typer.echo("Continuing without suggestions.", err=True)
            suggest = False

    print_results(results, show_suggestions=suggest, suggestions=suggestions)


if __name__ == "__main__":
    app()
