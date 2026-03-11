import ast
import operator as op
import re

import numpy as np

DEFAULT_DOMAIN = (-5.0, 5.0)
DEFAULT_STEPS = 60
DEFAULT_COLOR = "#16a34a"

_ALLOWED_BINOPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
}

_ALLOWED_UNARYOPS = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}

_ALLOWED_FUNCS = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "asin": np.arcsin,
    "acos": np.arccos,
    "atan": np.arctan,
    "exp": np.exp,
    "log": np.log,
    "ln": np.log,
    "sqrt": np.sqrt,
    "abs": np.abs,
    "floor": np.floor,
    "ceil": np.ceil,
}

_ALLOWED_CONSTS = {
    "pi": np.pi,
    "e": np.e,
}

_LEADING_KEYWORDS = re.compile(r"^(plot|trace|dessine|dessiner|draw|make|show)\b", re.IGNORECASE)
_FUNC_SIGNATURE = re.compile(r"f\s*\(\s*([a-zA-Z,\s]+)\s*\)\s*=", re.IGNORECASE)

_RANGE_BODY = r"(?P<a>[-+]?\d*\.?\d+)\s*(?:,|;|\.\.|to|a)\s*(?P<b>[-+]?\d*\.?\d+)"
_AXIS_RANGE = re.compile(
    rf"\b(?P<axis>x|y)\b\s*(?:in|=|:|sur|dans)?\s*[\[\(]?\s*{_RANGE_BODY}\s*[\]\)]?",
    re.IGNORECASE,
)
_DOMAIN_RANGE = re.compile(
    rf"\b(?:domain|domaine|range|sur|in)\b\s*[:=]?\s*[\[\(]?\s*{_RANGE_BODY}\s*[\]\)]?",
    re.IGNORECASE,
)
_TOKEN_RE = re.compile(r"\s*(\d*\.\d+|\d+|[a-zA-Z_]\w*|\*\*|[+\-*/()%])")


def normalize_text(text):
    if text is None:
        return ""
    return str(text)


def normalize_expression(expr):
    return re.sub(r"(\d),(\d)", r"\1.\2", expr)


def _is_number_token(token):
    return re.fullmatch(r"\d*\.\d+|\d+", token) is not None


def _is_identifier_token(token):
    return re.fullmatch(r"[a-zA-Z_]\w*", token) is not None


def _is_operand_end(token):
    return _is_number_token(token) or _is_identifier_token(token) or token == ")"


def _is_operand_start(token):
    return _is_number_token(token) or _is_identifier_token(token) or token == "("


def _is_function_call(cur_token, next_token):
    return _is_identifier_token(cur_token) and cur_token in _ALLOWED_FUNCS and next_token == "("


def apply_implicit_multiplication(expr):
    tokens = _TOKEN_RE.findall(expr)
    if not tokens:
        return expr

    out = []
    last_index = len(tokens) - 1
    for idx, token in enumerate(tokens):
        out.append(token)
        if idx == last_index:
            continue
        next_token = tokens[idx + 1]
        if _is_operand_end(token) and _is_operand_start(next_token):
            if _is_function_call(token, next_token):
                continue
            out.append("*")
    return "".join(out)


def parse_signature(text):
    if not text:
        return None
    match = _FUNC_SIGNATURE.search(text)
    if not match:
        return None
    var_part = match.group(1)
    raw_vars = [v.strip().lower() for v in re.split(r"[\s,]+", var_part) if v.strip()]
    if not raw_vars:
        return None
    vars_unique = []
    for var in raw_vars:
        if var not in vars_unique:
            vars_unique.append(var)
    return vars_unique


def _parse_range(a_str, b_str):
    a = float(a_str)
    b = float(b_str)
    if a > b:
        a, b = b, a
    return a, b


def parse_domains(text):
    text = normalize_text(text).lower()
    domain_x = None
    domain_y = None

    for match in _AXIS_RANGE.finditer(text):
        axis = match.group("axis").lower()
        a, b = _parse_range(match.group("a"), match.group("b"))
        if axis == "x":
            domain_x = (a, b)
        else:
            domain_y = (a, b)

    if domain_x is None or domain_y is None:
        for match in _DOMAIN_RANGE.finditer(text):
            a, b = _parse_range(match.group("a"), match.group("b"))
            if domain_x is None:
                domain_x = (a, b)
            if domain_y is None:
                domain_y = (a, b)

    return domain_x, domain_y


def strip_domains(text):
    if not text:
        return text
    cleaned = _AXIS_RANGE.sub("", text)
    cleaned = _DOMAIN_RANGE.sub("", cleaned)
    return cleaned


def replace_variables(expr, mapping):
    updated = expr
    for src, dst in mapping.items():
        updated = re.sub(rf"\b{re.escape(src)}\b", dst, updated)
    return updated


def extract_expression(text):
    if text is None:
        raise ValueError("Aucune expression fournie.")
    expr = str(text).strip()
    if not expr:
        raise ValueError("Aucune expression fournie.")
    if "=" in expr:
        expr = expr.rsplit("=", 1)[-1]
    else:
        expr = _LEADING_KEYWORDS.sub("", expr)
        expr = re.sub(r"^f\s*\(.*?\)\s*", "", expr, flags=re.IGNORECASE)
    expr = expr.strip()
    if not expr:
        raise ValueError("Expression introuvable. Exemple: f(x)=sin(x)")
    expr = expr.replace("^", "**")
    expr = normalize_expression(expr)
    expr = apply_implicit_multiplication(expr)
    return expr


def _eval_node(node, x, y):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, x, y)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Valeur non supportee.")
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_BINOPS:
            raise ValueError("Operateur non supporte.")
        left = _eval_node(node.left, x, y)
        right = _eval_node(node.right, x, y)
        return _ALLOWED_BINOPS[op_type](left, right)
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_UNARYOPS:
            raise ValueError("Operateur unaire non supporte.")
        operand = _eval_node(node.operand, x, y)
        return _ALLOWED_UNARYOPS[op_type](operand)
    if isinstance(node, ast.Name):
        if node.id == "x":
            return x
        if node.id == "y":
            return y
        if node.id in _ALLOWED_CONSTS:
            return _ALLOWED_CONSTS[node.id]
        raise ValueError(f"Nom non supporte: {node.id}")
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Fonction non supportee.")
        func_name = node.func.id
        func = _ALLOWED_FUNCS.get(func_name)
        if func is None:
            raise ValueError(f"Fonction non supportee: {func_name}")
        args = [_eval_node(arg, x, y) for arg in node.args]
        if func_name == "log" and len(args) == 2:
            return np.log(args[0]) / np.log(args[1])
        if len(args) != 1:
            raise ValueError("Nombre d'arguments invalide.")
        return func(args[0])
    raise ValueError("Expression invalide.")


def safe_eval(expr, x, y):
    try:
        tree = ast.parse(expr, mode="eval")
    except Exception as exc:
        raise ValueError("Expression invalide.") from exc
    return _eval_node(tree, x, y)


def get_names(expr):
    try:
        tree = ast.parse(expr, mode="eval")
    except Exception:
        return set()
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
    return names


def plot_function(text, domain=None, steps=None):
    raw_text = normalize_text(text)
    signature_vars = parse_signature(raw_text)
    domain_x, domain_y = parse_domains(raw_text)

    cleaned = strip_domains(raw_text)
    expr = extract_expression(cleaned)

    if signature_vars:
        if len(signature_vars) >= 2:
            mapping = {signature_vars[0]: "x", signature_vars[1]: "y"}
            expr = replace_variables(expr, mapping)
            signature_vars = ["x", "y"]
        else:
            mapping = {signature_vars[0]: "x"}
            expr = replace_variables(expr, mapping)
            signature_vars = ["x"]

    names = get_names(expr)
    if signature_vars:
        is_2d = "y" in signature_vars
    else:
        is_2d = "y" in names

    if not is_2d and "y" in names:
        raise ValueError("L'expression utilise y. Utilisez f(x,y)=... pour la 3D.")

    if is_2d:
        domain_x = domain_x or domain or DEFAULT_DOMAIN
        domain_y = domain_y or domain_x or DEFAULT_DOMAIN
        lo_x, hi_x = domain_x
        lo_y, hi_y = domain_y
        n = steps if steps is not None else DEFAULT_STEPS

        xs = np.linspace(lo_x, hi_x, n)
        ys = np.linspace(lo_y, hi_y, n)
        X, Y = np.meshgrid(xs, ys)

        Z = safe_eval(expr, X, Y)
        if np.iscomplexobj(Z):
            raise ValueError("La fonction doit etre reelle.")
        Z = np.asarray(Z, dtype=float)
        Z = np.where(np.isfinite(Z), Z, np.nan)

        axes = {
            "x": X.tolist(),
            "y": Y.tolist(),
            "z": Z.tolist(),
        }

        formulas = {"f(x,y)": f"f(x,y) = {expr}"}

        calculations = {}
        if np.isfinite(Z).any():
            calculations = {
                "z_min": float(np.nanmin(Z)),
                "z_max": float(np.nanmax(Z)),
            }

        return {
            "axes": axes,
            "formulas": formulas,
            "calculations": calculations,
            "render": "surface",
            "expr": expr,
            "dimension": 2,
            "signature": "f(x,y)",
            "domain": {"x": domain_x, "y": domain_y},
        }

    domain_x = domain_x or domain_y or domain or DEFAULT_DOMAIN
    lo, hi = domain_x
    n = steps if steps is not None else DEFAULT_STEPS

    xs = np.linspace(lo, hi, n)
    ys = safe_eval(expr, xs, np.zeros_like(xs))
    ys = np.asarray(ys, dtype=float)
    ys = np.where(np.isfinite(ys), ys, np.nan)

    axes = {
        "x": xs.tolist(),
        "y": ys.tolist(),
    }

    formulas = {"f(x)": f"f(x) = {expr}"}

    calculations = {}
    if np.isfinite(ys).any():
        calculations = {
            "y_min": float(np.nanmin(ys)),
            "y_max": float(np.nanmax(ys)),
        }

    return {
        "axes": axes,
        "formulas": formulas,
        "calculations": calculations,
        "render": "line2d",
        "expr": expr,
        "dimension": 1,
        "signature": "f(x)",
        "domain": {"x": domain_x, "y": None},
    }
