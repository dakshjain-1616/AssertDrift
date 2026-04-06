<div align="center">

# assertdrift
### Detect Tests That Pass But Prove Nothing

[![Built with NEO](https://img.shields.io/badge/Built%20with-NEO%20AI%20Agent-6741d9?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0tMiAxNWwtNS01IDEuNDEtMS40MUwxMCAxNC4xN2w3LjU5LTcuNTlMMTkgOGwtOSA5eiIvPjwvc3ZnPg==&logoColor=white)](https://heyneo.so)
[![Autonomous AI](https://img.shields.io/badge/Autonomous-AI%20Generated-ff6b6b?style=for-the-badge)](https://heyneo.so)
[![VS Code Extension](https://img.shields.io/badge/VS%20Code-NEO%20Extension-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)](https://marketplace.visualstudio.com/items?itemName=NeoResearchInc.heyneo)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![OpenRouter](https://img.shields.io/badge/AI%20Model-qwen%2Fqwen3.6--plus%3Afree-00b4d8?style=for-the-badge)](https://openrouter.ai)

</div>

---

> 🤖 **This project was created entirely autonomously by [NEO](https://heyneo.so) — Your Autonomous AI Agent.**
> NEO planned, wrote, tested, and verified every file in this repository without human intervention.
> Try NEO yourself → [heyneo.so](https://heyneo.so) · [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=NeoResearchInc.heyneo)

---

## The Problem

You have 500 tests. They all pass. You ship. Production breaks.

This happens because **passing tests ≠ good tests**. Most test suites are full of assertions that look like they're verifying something but aren't — existence checks that always return an object, tautologies that literally always pass, type checks that don't verify actual values. These give you a **false green**: CI passes, coverage looks great, and the code is still broken.

**assertdrift finds these tests automatically**, scores them by how much they actually prove, and tells you exactly which ones to fix.

---

## Why assertdrift?

| Tool | What it tells you |
|------|------------------|
| pytest | ✅ / ❌ — did it crash? |
| coverage.py | Which lines were executed |
| assertdrift | **Whether the assertions actually verify anything** |

Coverage tools measure *execution*. assertdrift measures *proof strength*. They solve different problems — you need both.

---

## Scoring Rubric

| Score | Label | Meaning | Examples |
|-------|-------|---------|---------|
| **0** | 🔴 ZERO | Tautology — mathematically always passes | `assert True`, `assertTrue(True)`, `assert 1` |
| **1** | 🟠 LOW | Checks existence or truthiness only | `assert x is not None`, `assertIsNotNone(x)`, `assertTrue(x)` |
| **2** | 🟡 MEDIUM | Checks type or membership | `assertIsInstance(x, str)`, `assertIn(k, d)` |
| **3** | 🟢 HIGH | Checks an exact value or precise state | `assertEqual(x, 42)`, `assert x == "exact"`, `assert resp.status == 200` |

> **Flagged** = test function with average score below **1.5**. These are the ones giving you false confidence.

---

## Architecture

> Open `architecture.excalidraw` in [Excalidraw](https://excalidraw.com) for the full interactive diagram.

---

## Infographic

<div align="center">
  <img src="infographic.svg" alt="assertdrift scoring rubric and pipeline" width="100%"/>
</div>

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/neo-ai/assertdrift
cd assertdrift
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Scan your test suite — no API key needed
python main.py /path/to/your/tests/

# Run on assertdrift's own tests (built-in demo)
python main.py tests/

# Get AI-powered rewrite suggestions for weak tests
cp .env.example .env            # add your OPENROUTER_API_KEY
export $(cat .env | xargs)
python main.py tests/ --suggest
```

---

## Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

```dotenv
# Required only for --suggest mode (AI rewrite suggestions)
# Free key at: https://openrouter.ai/keys
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

> **Basic scanning** works with **zero config, no API key**. Only `--suggest` requires one.

---

## Commands

| Command | What it does |
|---------|-------------|
| `python main.py tests/` | Scan `tests/` and all subdirectories |
| `python main.py .` | Scan entire project for `test_*.py` files |
| `python main.py tests/ --suggest` | Scan + AI rewrites for all flagged tests |
| `python main.py tests/ -s` | Short form of `--suggest` |
| `python main.py --help` | Show CLI help |

---

## Supported Assertion Patterns

| Pattern | Scored as |
|---------|-----------|
| `assert True` / `assert 1` | 🔴 ZERO |
| `assert x is not None` / `assert x is None` | 🟠 LOW |
| `assertTrue(x)` / `assertFalse(x)` | 🟠 LOW |
| `assertIsNotNone(x)` / `assertIsNone(x)` | 🟠 LOW |
| `assertIn(x, collection)` / `assertNotIn` | 🟠 LOW |
| `assertIsInstance(x, T)` / `assertNotIsInstance` | 🟡 MEDIUM |
| `assert x == "literal"` / `assert x == 42` | 🟢 HIGH |
| `assertEqual(x, value)` / `assertNotEqual` | 🟢 HIGH |
| `assertGreater` / `assertLess` / `assertAlmostEqual` | 🟢 HIGH |
| `assert a == 1 and b == 2` | 🟢 HIGH (compound) |

Works with standalone `def test_*()` functions, `unittest.TestCase` class methods, `async def test_*()` async tests, and nested test directories.

---

## File Structure

```
assertdrift/
├── main.py                  # CLI entry point (typer)
├── analyzer.py              # AST walker + assertion scorer
├── reporter.py              # Rich terminal table output
├── suggester.py             # OpenRouter / qwen3.6-plus integration
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── LICENSE
├── CONTRIBUTING.md
├── architecture.excalidraw
├── infographic.svg
└── tests/
    └── test_assertdrift.py
```

---

## Built with NEO

<div align="center">

[![NEO Autonomous AI Agent](https://img.shields.io/badge/🤖%20NEO-Autonomous%20AI%20Agent-6741d9?style=for-the-badge)](https://heyneo.so)

**This entire project — every file, every line of code, every test — was created autonomously by [NEO](https://heyneo.so).**

NEO is an autonomous AI agent that plans, codes, tests, and ships software on your behalf.

[**Try NEO → heyneo.so**](https://heyneo.so) · [**VS Code Extension**](https://marketplace.visualstudio.com/items?itemName=NeoResearchInc.heyneo)

</div>

---

## License

MIT
