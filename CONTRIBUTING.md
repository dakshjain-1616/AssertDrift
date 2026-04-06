# Contributing to assertdrift

Thanks for your interest! Here's how to get started.

## Setup

```bash
git clone https://github.com/neo-ai/assertdrift
cd assertdrift
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Running Tests

```bash
# Run the self-test suite
python main.py tests/

# Run with pytest (if installed)
pytest tests/ -v
```

## Adding a New Assertion Pattern

1. Open `analyzer.py`
2. Add the pattern to `score_assert_stmt()` (for `assert` statements) or `score_call_assertion()` (for `self.assertX()` calls)
3. Add a corresponding test case in `tests/test_assertdrift.py`
4. Run `python main.py tests/` to verify scoring

## Scoring Rubric

New patterns must fit one of the four levels:

| Level | Score | Criteria |
|-------|-------|----------|
| ZERO | 0 | Always passes — tautology |
| LOW | 1 | Existence / truthy check only |
| MEDIUM | 2 | Type or membership check |
| HIGH | 3 | Exact value / state check |

## Pull Request Guidelines

- Keep PRs focused — one change per PR
- Include a test case for any new pattern
- Run `python main.py tests/` and confirm all 4 self-tests still pass
- Update the scoring rubric table in `README.md` if adding new patterns

## Reporting Bugs

Open an issue with:
- Python version (`python --version`)
- The assertion pattern that was scored incorrectly
- Expected score vs actual score
