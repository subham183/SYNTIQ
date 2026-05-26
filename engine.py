"""
SYNTIQ - Hybrid AST Analyzer & Linguistic Humanizer Engine
Core processing pipeline: AST parsing + linguistic pre-filtering
"""

import ast
import re
import time
import random
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Any


# ─── AST ANALYSIS ENGINE ────────────────────────────────────────────────────

class ASTAnalyzer:
    """
    Traverses Python source code as an Abstract Syntax Tree.
    Computes cyclomatic complexity, detects security hazards,
    counts nested structures, and profiles function metrics.
    """

    DANGEROUS_CALLS = {'eval', 'exec', 'compile', '__import__', 'open',
                       'subprocess', 'os.system', 'pickle.loads'}
    AI_FINGERPRINTS = [
        r'\bdelve\b', r'\bfurthermore\b', r'\bin conclusion\b',
        r'\bit is worth noting\b', r'\bnotably\b', r'\bit\'s important to note\b',
        r'\bto summarize\b', r'\boverall\b', r'\bin summary\b',
        r'\bto begin with\b', r'\bfirstly\b', r'\bsecondly\b',
    ]

    def __init__(self, source: str):
        self.source = source
        self.tree = None
        self.errors = []

    def parse(self) -> bool:
        try:
            self.tree = ast.parse(self.source)
            return True
        except SyntaxError as e:
            self.errors.append(f"SyntaxError at line {e.lineno}: {e.msg}")
            return False

    def _count_nested_loops(self, node, depth=0) -> Tuple[int, int]:
        """Recursively traverse AST to count loop nesting depth."""
        max_depth = depth
        total_loops = 0
        for child in ast.walk(node):
            if child is node:
                continue
            if isinstance(child, (ast.For, ast.While)):
                total_loops += 1
                _, child_max = self._count_nested_loops(child, depth + 1)
                max_depth = max(max_depth, child_max)
        return total_loops, max_depth

    def _detect_dangerous_nodes(self) -> List[Dict]:
        hazards = []
        for node in ast.walk(self.tree):
            # eval / exec calls
            if isinstance(node, ast.Call):
                func = node.func
                name = None
                if isinstance(func, ast.Name):
                    name = func.id
                elif isinstance(func, ast.Attribute):
                    name = func.attr
                if name in {'eval', 'exec', 'compile'}:
                    hazards.append({
                        'type': 'DANGEROUS_CALL',
                        'node': name,
                        'line': getattr(node, 'lineno', '?'),
                        'severity': 'CRITICAL',
                        'detail': f"Unsafe call to `{name}()` — arbitrary code execution risk"
                    })
            # bare except
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                hazards.append({
                    'type': 'BARE_EXCEPT',
                    'node': 'except',
                    'line': getattr(node, 'lineno', '?'),
                    'severity': 'WARNING',
                    'detail': "Bare `except:` swallows all exceptions silently"
                })
            # global variable mutation
            if isinstance(node, ast.Global):
                hazards.append({
                    'type': 'GLOBAL_MUTATION',
                    'node': ', '.join(node.names),
                    'line': getattr(node, 'lineno', '?'),
                    'severity': 'INFO',
                    'detail': f"Global state mutation: {', '.join(node.names)}"
                })
        return hazards

    def _analyze_functions(self) -> List[Dict]:
        functions = []
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [a.arg for a in node.args.args]
                body_lines = (node.end_lineno - node.lineno) if hasattr(node, 'end_lineno') else 0
                has_docstring = (
                    node.body and
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)
                )
                functions.append({
                    'name': node.name,
                    'args': args,
                    'line': node.lineno,
                    'body_lines': body_lines,
                    'has_docstring': has_docstring,
                    'is_async': isinstance(node, ast.AsyncFunctionDef),
                })
        return functions

    def _compute_complexity(self) -> int:
        """McCabe cyclomatic complexity approximation."""
        complexity = 1
        branch_nodes = (ast.If, ast.For, ast.While, ast.ExceptHandler,
                        ast.With, ast.Assert, ast.comprehension)
        for node in ast.walk(self.tree):
            if isinstance(node, branch_nodes):
                complexity += 1
            if isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity

    def analyze(self) -> Dict:
        if not self.parse():
            return {'success': False, 'errors': self.errors}

        total_loops, max_nest = self._count_nested_loops(self.tree)
        hazards = self._detect_dangerous_nodes()
        functions = self._analyze_functions()
        complexity = self._compute_complexity()

        lines = self.source.splitlines()
        loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        comment_lines = len([l for l in lines if l.strip().startswith('#')])
        imports = [n for n in ast.walk(self.tree) if isinstance(n, (ast.Import, ast.ImportFrom))]

        risk_score = min(100, complexity * 3 + max_nest * 8 +
                         sum(5 if h['severity'] == 'CRITICAL' else 2 for h in hazards))

        grade = 'A' if risk_score < 20 else 'B' if risk_score < 40 else \
                'C' if risk_score < 60 else 'D' if risk_score < 80 else 'F'

        return {
            'success': True,
            'errors': [],
            'metrics': {
                'loc': loc,
                'comment_lines': comment_lines,
                'total_lines': len(lines),
                'complexity': complexity,
                'complexity_grade': grade,
                'risk_score': risk_score,
                'nested_loops': total_loops,
                'max_nesting_depth': max_nest,
                'import_count': len(imports),
                'function_count': len(functions),
            },
            'hazards': hazards,
            'functions': functions,
            'grade': grade,
        }


# ─── LINGUISTIC HUMANIZER ENGINE ────────────────────────────────────────────

class LinguisticHumanizer:
    """
    Pre-filters AI-generated text: strips fingerprints, normalizes
    structure, analyzes burstiness, and simulates humanized output.
    """

    AI_PATTERNS = [
        (r'\bDelve\b', 'Explore'),
        (r'\bdelve\b', 'explore'),
        (r'\bFurthermore\b', 'Also'),
        (r'\bfurthermore\b', 'also'),
        (r'\bIn conclusion\b', 'To wrap up'),
        (r'\bin conclusion\b', 'to wrap up'),
        (r'\bIt is worth noting that\b', 'Note that'),
        (r'\bNotably\b', 'Interestingly'),
        (r'\bnotably\b', 'interestingly'),
        (r'\bIt\'s important to note\b', 'Keep in mind'),
        (r'\bTo summarize\b', 'In short'),
        (r'\bOverall\b', 'All things considered'),
        (r'\bFirstly\b', 'First'),
        (r'\bSecondly\b', 'Second'),
        (r'\bLastly\b', 'Finally'),
        (r'\bIn summary\b', 'Briefly'),
        (r'\bMoreover\b', 'On top of that'),
        (r'\bHowever\b', 'But'),
        (r'\bNevertheless\b', 'Still'),
        (r'\bConsequently\b', 'So'),
        (r'\bThis means that\b', 'This shows'),
        (r'\bThis demonstrates\b', 'This shows'),
        (r'\bIt can be seen that\b', ''),
        (r'\bAs a result\b', 'Because of this'),
    ]

    STRUCTURAL_HEADERS = re.compile(
        r'^(Introduction|Conclusion|Summary|Overview|Background|'
        r'Explanation|Analysis|Discussion|Key Points?|Main Points?)[:\s]*\n',
        re.MULTILINE | re.IGNORECASE
    )

    REPETITIVE_FORMATTING = re.compile(r'\n{3,}')
    MARKDOWN_BOLD = re.compile(r'\*\*(.*?)\*\*')
    MARKDOWN_HEADERS = re.compile(r'^#{1,6}\s+', re.MULTILINE)
    BULLET_NORMALIZE = re.compile(r'^[\s]*[-•*]\s+', re.MULTILINE)

    def __init__(self, text: str):
        self.original = text
        self.processed = text
        self.replacements_made = []

    def strip_ai_fingerprints(self) -> 'LinguisticHumanizer':
        for pattern, replacement in self.AI_PATTERNS:
            matches = re.findall(pattern, self.processed)
            if matches:
                self.replacements_made.extend(
                    [{'from': m, 'to': replacement, 'type': 'AI_FINGERPRINT'} for m in matches]
                )
            self.processed = re.sub(pattern, replacement, self.processed)
        return self

    def strip_structural_headers(self) -> 'LinguisticHumanizer':
        self.processed = self.STRUCTURAL_HEADERS.sub('', self.processed)
        return self

    def normalize_formatting(self) -> 'LinguisticHumanizer':
        self.processed = self.MARKDOWN_BOLD.sub(r'\1', self.processed)
        self.processed = self.MARKDOWN_HEADERS.sub('', self.processed)
        self.processed = self.REPETITIVE_FORMATTING.sub('\n\n', self.processed)
        self.processed = self.processed.strip()
        return self

    def _sentence_lengths(self) -> List[int]:
        sentences = re.split(r'(?<=[.!?])\s+', self.processed)
        return [len(s.split()) for s in sentences if s.strip()]

    def _burstiness_score(self, lengths: List[int]) -> float:
        if len(lengths) < 2:
            return 0.0
        mean = sum(lengths) / len(lengths)
        if mean == 0:
            return 0.0
        variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
        std = variance ** 0.5
        # Coefficient of variation — higher = more bursty (more human)
        return round((std / mean) * 100, 1)

    def _perplexity_score(self, text: str) -> float:
        """Approximate perplexity via vocabulary diversity."""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        if not words:
            return 0.0
        unique = set(words)
        # Type-Token Ratio scaled to 0-100
        ttr = len(unique) / len(words)
        return round(ttr * 100, 1)

    def analyze_and_transform(self) -> Dict:
        start = time.time()

        # Run pipeline
        self.strip_ai_fingerprints() \
            .strip_structural_headers() \
            .normalize_formatting()

        elapsed = round((time.time() - start) * 1000, 2)

        original_lengths = re.split(r'(?<=[.!?])\s+', self.original)
        processed_lengths_list = self._sentence_lengths()

        orig_perplexity = self._perplexity_score(self.original)
        proc_perplexity = self._perplexity_score(self.processed)
        orig_burstiness = self._burstiness_score(
            [len(s.split()) for s in original_lengths if s.strip()]
        )
        proc_burstiness = self._burstiness_score(processed_lengths_list)

        chars_removed = len(self.original) - len(self.processed)
        reduction_pct = round((chars_removed / max(len(self.original), 1)) * 100, 1)

        return {
            'original': self.original,
            'humanized': self.processed,
            'replacements': self.replacements_made,
            'metrics': {
                'original_chars': len(self.original),
                'processed_chars': len(self.processed),
                'chars_removed': chars_removed,
                'reduction_pct': reduction_pct,
                'fingerprints_removed': len(self.replacements_made),
                'orig_perplexity': orig_perplexity,
                'proc_perplexity': proc_perplexity,
                'orig_burstiness': orig_burstiness,
                'proc_burstiness': proc_burstiness,
                'processing_ms': elapsed,
            },
        }


# ─── SUBMISSION TRACKER ─────────────────────────────────────────────────────

class SubmissionTracker:
    """In-memory analytics store (simulates DB aggregations)."""
    _store: List[Dict] = []

    @classmethod
    def record(cls, code_result: Dict, text_result: Dict):
        entry = {
            'id': hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper(),
            'timestamp': datetime.now().isoformat(),
            'code_loc': code_result.get('metrics', {}).get('loc', 0),
            'complexity': code_result.get('metrics', {}).get('complexity', 0),
            'hazard_count': len(code_result.get('hazards', [])),
            'grade': code_result.get('grade', '?'),
            'chars_modified': text_result.get('metrics', {}).get('chars_removed', 0),
            'fingerprints': text_result.get('metrics', {}).get('fingerprints_removed', 0),
        }
        cls._store.append(entry)
        return entry['id']

    @classmethod
    def aggregate(cls) -> Dict:
        if not cls._store:
            return {
                'total_submissions': 0,
                'avg_complexity': 0,
                'total_chars_modified': 0,
                'total_hazards_caught': 0,
                'total_fingerprints': 0,
                'grade_dist': {},
                'recent': []
            }
        total = len(cls._store)
        avg_complexity = round(sum(e['complexity'] for e in cls._store) / total, 1)
        total_chars = sum(e['chars_modified'] for e in cls._store)
        total_hazards = sum(e['hazard_count'] for e in cls._store)
        total_fp = sum(e['fingerprints'] for e in cls._store)
        grade_dist = {}
        for e in cls._store:
            grade_dist[e['grade']] = grade_dist.get(e['grade'], 0) + 1

        return {
            'total_submissions': total,
            'avg_complexity': avg_complexity,
            'total_chars_modified': total_chars,
            'total_hazards_caught': total_hazards,
            'total_fingerprints': total_fp,
            'grade_dist': grade_dist,
            'recent': list(reversed(cls._store[-6:])),
        }
