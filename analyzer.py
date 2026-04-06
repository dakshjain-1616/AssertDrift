"""AST-based assertion analyzer for test files."""

import ast
from pathlib import Path
from typing import List, Dict


class AssertionScorer:
    """Scores assertions based on strength rubric."""

    ZERO = 0   # tautologies like assert True
    LOW = 1    # existence checks like assert x is not None
    MEDIUM = 2 # type checks like isinstance(x, str)
    HIGH = 3   # exact value checks like assert x == "literal"

    def score_assert_stmt(self, node: ast.Assert) -> int:
        """Score an `assert <expr>` statement node."""
        test = node.test

        # ZERO: bare tautology constants (assert True, assert 1)
        if isinstance(test, ast.Constant):
            if test.value is True or test.value == 1:
                return self.ZERO

        # LOW: existence check — x is not None / x is None
        if isinstance(test, ast.Compare):
            if len(test.ops) == 1 and isinstance(test.ops[0], (ast.IsNot, ast.Is)):
                if isinstance(test.comparators[0], ast.Constant) and test.comparators[0].value is None:
                    return self.LOW

        # MEDIUM: isinstance() type check inside assert
        if isinstance(test, ast.Call):
            func = test.func
            if isinstance(func, ast.Name) and func.id == 'isinstance':
                return self.MEDIUM

        # HIGH: exact equality with a literal  (assert x == "val", assert x == 42)
        if isinstance(test, ast.Compare):
            if len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq):
                # Either side being a constant counts
                left_const = isinstance(test.left, ast.Constant)
                right_const = any(isinstance(c, ast.Constant) for c in test.comparators)
                if left_const or right_const:
                    return self.HIGH

        # HIGH: boolean AND of multiple checks (assert a == 1 and b == 2)
        if isinstance(test, ast.BoolOp) and isinstance(test.op, ast.And):
            scores = []
            for value in test.values:
                dummy = ast.Assert(test=value, msg=None)
                scores.append(self.score_assert_stmt(dummy))
            return max(scores) if scores else self.LOW

        return self.LOW

    def score_call_assertion(self, call: ast.Call) -> int:
        """Score a unittest-style self.assertX() call expression."""
        if not isinstance(call.func, ast.Attribute):
            return self.LOW
        method = call.func.attr

        # ZERO: assertTrue(True) / assertFalse(False)
        if method in ('assertTrue', 'assertFalse'):
            if call.args and isinstance(call.args[0], ast.Constant):
                if call.args[0].value in (True, False, 1, 0):
                    return self.ZERO
            return self.LOW

        # LOW: existence-only checks
        if method in ('assertIsNotNone', 'assertIsNone', 'assertIn', 'assertNotIn'):
            return self.LOW

        # MEDIUM: type / membership
        if method in ('assertIsInstance', 'assertNotIsInstance'):
            return self.MEDIUM

        # HIGH: exact value comparisons
        if method in ('assertEqual', 'assertEquals', 'assertNotEqual',
                      'assertAlmostEqual', 'assertGreater', 'assertLess',
                      'assertGreaterEqual', 'assertLessEqual'):
            return self.HIGH

        return self.LOW


class TestFileAnalyzer:
    """Analyzes test files and scores assertion strength."""

    def __init__(self):
        self.scorer = AssertionScorer()

    def extract_test_functions(self, filepath: str) -> List[Dict]:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                source = f.read()
            tree = ast.parse(source)
        except SyntaxError:
            return []

        # Collect top-level and class-method test functions, preserving line order
        test_functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('test_'):
                    continue
                assertions = []
                # Walk only direct body — avoid double-counting nested functions
                for child in ast.walk(node):
                    # Skip assertions inside nested functions
                    if child is not node and isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    # ast.Assert statements
                    if isinstance(child, ast.Assert):
                        score = self.scorer.score_assert_stmt(child)
                        assertions.append({'score': score, 'lineno': child.lineno})
                    # Standalone unittest self.assertX() calls
                    elif isinstance(child, ast.Expr) and isinstance(child.value, ast.Call):
                        call = child.value
                        if isinstance(call.func, ast.Attribute):
                            attr = call.func.attr
                            if attr.startswith('assert') or attr.startswith('Assert'):
                                score = self.scorer.score_call_assertion(call)
                                assertions.append({'score': score, 'lineno': child.lineno})

                test_functions.append({
                    'name': node.name,
                    'lineno': node.lineno,
                    'assertions': assertions,
                    'assertion_count': len(assertions),
                })

        # Sort by source line so output matches file order
        test_functions.sort(key=lambda f: f['lineno'])
        return test_functions

    def analyze_file(self, filepath: str) -> Dict:
        test_functions = self.extract_test_functions(filepath)
        all_scores = [a['score'] for t in test_functions for a in t['assertions']]
        avg = sum(all_scores) / len(all_scores) if all_scores else 0.0
        strength = ('HIGH' if avg >= 2.5 else
                    'MEDIUM' if avg >= 1.5 else
                    'LOW' if avg >= 0.5 else 'ZERO')
        return {
            'file': filepath,
            'test_functions': test_functions,
            'total_assertions': len(all_scores),
            'avg_score': avg,
            'strength': strength,
            'flagged': avg < 1.5,
        }

    def analyze_directory(self, directory: str) -> List[Dict]:
        """Recursively find all test_*.py files under directory."""
        dir_path = Path(directory)
        if not dir_path.exists():
            return []
        # rglob finds test files in all subdirectories
        test_files = sorted(dir_path.rglob('test_*.py'))
        return [self.analyze_file(str(f)) for f in test_files]


def analyze_tests(directory: str) -> List[Dict]:
    return TestFileAnalyzer().analyze_directory(directory)
