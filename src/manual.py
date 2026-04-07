
from __future__ import annotations

import ast
import builtins
import io
import math
from contextlib import redirect_stdout
from typing import Any


class Manual:
    def __init__(self, name):
        self.name = name
        
    @property
    def variables(self):
        return {}

    def display(self):
        print(f"Manual for {self.name}")

    def expert_tool_instructions(self) -> str:
        return "Available Expert tools: python_interpreter(code)."

    def content(self) -> str:
        return ""

    def execute_expert_tool(self, name: str, arguments: dict[str, Any]) -> str:
        return f"Unknown or disallowed expert tool: {name}"

    def execute_python_interpreter(self, arguments: dict[str, Any]) -> str:
        code = arguments.get("code")
        if not isinstance(code, str) or not code.strip():
            return "python_interpreter error: missing non-empty 'code'"
        return self._python_tool(code)

    @staticmethod
    def _python_tool(code: str) -> str:
        """Execute expert Python snippets with a small safe builtins surface.

        If there is no stdout output and the final statement is an expression,
        return that expression value (REPL-like behavior).
        """
        allowed_modules = {"math", "statistics"}

        def safe_import(
            name: str,
            globals_dict: dict[str, Any] | None = None,
            locals_dict: dict[str, Any] | None = None,
            fromlist: tuple[str, ...] | list[str] = (),
            level: int = 0,
        ) -> Any:
            # Disallow relative imports and only permit allowlisted top-level modules.
            if level != 0:
                raise ImportError("relative imports are not allowed")
            top_level = name.split(".", 1)[0]
            if top_level not in allowed_modules:
                allowed = ", ".join(sorted(allowed_modules))
                raise ImportError(
                    f"import of '{top_level}' is not allowed; allowed modules: {allowed}"
                )
            return builtins.__import__(name, globals_dict, locals_dict, fromlist, level)

        safe_builtins = {
            "__import__": safe_import,
            "abs": abs,
            "arccos": math.acos,
            "arcsin": math.asin,
            "arctan": math.atan,
            "arctan2": math.atan2,
            "ceil": math.ceil,
            "cos": math.cos,
            "degrees": math.degrees,
            "exp": math.exp,
            "floor": math.floor,
            "isfinite": math.isfinite,
            "len": len,
            "log": math.log,
            "log10": math.log10,
            "max": max,
            "min": min,
            "pow": pow,
            "print": print,
            "radians": math.radians,
            "range": range,
            "round": round,
            "sin": math.sin,
            "sqrt": math.sqrt,
            "sorted": sorted,
            "sum": sum,
            "tan": math.tan,
        }
        namespace: dict[str, Any] = {"__builtins__": safe_builtins, "math": math}
        stream = io.StringIO()
        last_value: Any = None
        has_last_expression = False

        try:
            parsed = ast.parse(code, mode="exec")
        except Exception as exc:  # noqa: BLE001
            return f"ERROR: python_interpreter: {exc}"

        for node in ast.walk(parsed):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_level = alias.name.split(".", 1)[0]
                    if top_level not in allowed_modules:
                        allowed = ", ".join(sorted(allowed_modules))
                        return (
                            "ERROR: python_interpreter: "
                            f"import of '{top_level}' is not allowed; allowed modules: {allowed}"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.level != 0 or not node.module:
                    return "ERROR: python_interpreter: relative imports are not allowed"
                top_level = node.module.split(".", 1)[0]
                if top_level not in allowed_modules:
                    allowed = ", ".join(sorted(allowed_modules))
                    return (
                        "ERROR: python_interpreter: "
                        f"import of '{top_level}' is not allowed; allowed modules: {allowed}"
                    )

        body = list(parsed.body)
        last_expr = body[-1] if body and isinstance(body[-1], ast.Expr) else None

        exec_tree = ast.Module(body=body[:-1] if last_expr else body, type_ignores=[])
        ast.fix_missing_locations(exec_tree)

        eval_code = None
        try:
            if last_expr is not None:
                eval_tree = ast.Expression(body=last_expr.value)
                ast.fix_missing_locations(eval_tree)
                eval_code = compile(eval_tree, "<python_interpreter>", "eval")
                has_last_expression = True

            exec_code = compile(exec_tree, "<python_interpreter>", "exec")
        except Exception as exc:  # noqa: BLE001
            return f"ERROR: python_interpreter: {exc}"

        try:
            with redirect_stdout(stream):
                exec(exec_code, namespace, namespace)
                if eval_code is not None:
                    last_value = eval(eval_code, namespace, namespace)
        except Exception as exc:  # noqa: BLE001
            return f"ERROR: python_interpreter: {exc}"

        output = stream.getvalue().strip()
        if output:
            return output
        if has_last_expression:
            return repr(last_value)
        return "python_interpreter: code executed with no stdout output, use print() to display results."
        
    
if __name__ == "__main__":
    a = Manual._python_tool("ciphered_text = '[8vΑΕ'\ncannon_color = 'blue'\nvelocity = 30.18\n\n# Decode the ciphered text\ncipher_mappings = {\"blue\": {\"0\": \"%\", \"1\": \"😿\", \"2\": \"Α\", \"3\": \"😤\", \"4\": \"😂\", \"5\": \"[\", \"6\": \"8\", \"7\": \"A\", \"8\": \"Ε\", \"9\": \"1\", \".\": \"v\"}}\ndecoded_text = ''.join(cipher_mappings[cannon_color][char] if char in cipher_mappings[cannon_color] else char for char in ciphered_text)\nprint(decoded_text)")
    
    
    print(a)