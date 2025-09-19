import tkinter as tk
from tkinter import ttk
import math

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.resizable(False, False)
        self.configure(padx=8, pady=8)

        self.expr = ""
        self.is_scientific = False
        self.last_ans = ""
        self._create_widgets()

    def _create_widgets(self):
        # Display
        self.display_var = tk.StringVar(value="0")
        display = ttk.Entry(self, textvariable=self.display_var, justify="right", font=("Segoe UI", 18))
        display.grid(row=0, column=0, columnspan=5, sticky="ew", ipady=10)
        display.state(["readonly"])

        # Page toggle
        self.mode_btn = ttk.Button(self, text="Scientific ▶", command=self._toggle_mode)
        self.mode_btn.grid(row=1, column=0, columnspan=5, sticky="ew", pady=(6,0))

        # Basic frame
        self.basic_frame = ttk.Frame(self)
        self.basic_frame.grid(row=2, column=0, columnspan=5, pady=(8,0))

        basic_buttons = [
            ["C", "⌫", "(", ")", "/"],
            ["7", "8", "9", "*", "%"],
            ["4", "5", "6", "-", "^"],
            ["1", "2", "3", "+", "pow"],
            ["0", ".", "=", "ANS", "OFF"]
        ]

        for r, row in enumerate(basic_buttons):
            for c, label in enumerate(row):
                action = lambda ch=label: self.on_button(ch)
                btn = ttk.Button(self.basic_frame, text=label, command=action)
                btn.grid(row=r, column=c, ipadx=10, ipady=10, padx=4, pady=4, sticky="nsew")

        for i in range(5):
            self.basic_frame.columnconfigure(i, weight=1)

        # Scientific frame (hidden initially)
        self.science_frame = ttk.Frame(self)
        sci_buttons = [
            ["sqrt", "root", "factorial", "abs", "pi"],
            ["sin", "cos", "tan", "asin", "acos"],
            ["atan", "log", "ln", "e", "deg"],
            ["rad", "pow", "^", "ANS", "BACK"]
        ]

        for r, row in enumerate(sci_buttons):
            for c, label in enumerate(row):
                action = lambda ch=label: self.on_button(ch)
                btn = ttk.Button(self.science_frame, text=label, command=action)
                btn.grid(row=r, column=c, ipadx=8, ipady=10, padx=4, pady=4, sticky="nsew")

        for i in range(5):
            self.science_frame.columnconfigure(i, weight=1)

        # Bind keys
        self.bind_all("<Key>", self.on_key)

    def _toggle_mode(self):
        self.is_scientific = not self.is_scientific
        if self.is_scientific:
            self.basic_frame.grid_remove()
            self.science_frame.grid(row=2, column=0, columnspan=5, pady=(8,0))
            self.mode_btn.config(text="Basic ◀")
        else:
            self.science_frame.grid_remove()
            self.basic_frame.grid(row=2, column=0, columnspan=5, pady=(8,0))
            self.mode_btn.config(text="Scientific ▶")

    def on_button(self, char):
        if char == "C":
            self.expr = ""
            self.display_var.set("0")
            return
        if char == "⌫":
            self.expr = self.expr[:-1]
            self.display_var.set(self.expr or "0")
            return
        if char == "OFF":
            self.quit()
            return
        if char == "=":
            self._evaluate()
            return
        if char == "ANS":
            self.expr += self.last_ans
            self.display_var.set(self.expr)
            return
        if char == "BACK":
            if self.is_scientific:
                self._toggle_mode()
            return
        if char == "deg":
            self.expr += "deg("
            self.display_var.set(self.expr)
            return
        if char == "rad":
            self.expr += "rad("
            self.display_var.set(self.expr)
            return

        # insert functions and tokens
        if char in ("sqrt", "ln", "abs"):
            self.expr += f"{char}("
        elif char == "root":
            self.expr += "root("
        elif char == "pow":
            self.expr += "pow("
        elif char == "factorial":
            self.expr += "!"
        elif char == "^":
            self.expr += "^"
        elif char in ("pi", "e"):
            self.expr += char
        else:
            if char.isalpha() and char not in ("pi","e"):
                if char in ("sin","cos","tan","asin","acos","atan","log"):
                    self.expr += f"{char}("
                else:
                    self.expr += char
            else:
                self.expr += char

        self.display_var.set(self.expr or "0")

    def on_key(self, event):
        key = event.keysym
        char = event.char
        if key in ("Return", "KP_Enter"):
            self._evaluate()
        elif key == "BackSpace":
            self.on_button("⌫")
        elif key == "Escape":
            self.on_button("C")
        else:
            allowed = "0123456789+-*/().,^%!,"  # allow percent and comma
            if char and (char in allowed):
                self.on_button(char)
            else:
                if char.isalpha():
                    self.expr += char
                    self.display_var.set(self.expr or "0")

    def _evaluate(self):
        if not self.expr:
            return
        expr = self.expr.replace("×", "*").replace("÷", "/")

        # support numeric-prefix nth-root like 3root(27) -> root(3,27)
        expr = self._replace_numeric_prefix_root(expr)

        # transform ^ -> pow()
        expr = self._replace_caret_with_pow(expr)
        # transform factorial n! -> factorial(n)
        expr = self._replace_factorials(expr)

        try:
            result = eval(expr, {"__builtins__": None}, self._safe_funcs())
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 12)
            self.last_ans = str(result)
            self.expr = str(result)
            self.display_var.set(self.expr)
        except Exception:
            self.display_var.set("Error")
            self.expr = ""

    def _replace_numeric_prefix_root(self, s):
        # Finds patterns like "<number>root(<expr>)" and converts to "root(<number>,<expr>)".
        out = []
        i = 0
        L = len(s)
        while i < L:
            if s.startswith("root", i):
                out.append("root")
                i += 4
                continue

            idx = s.find("root", i)
            if idx == -1:
                out.append(s[i:])
                break

            # capture numeric prefix immediately before idx
            j = idx - 1
            if j < 0:
                out.append(s[i:idx])
                out.append("root")
                i = idx + 4
                continue

            num_chars = "+-0123456789.eE"
            k = j
            found_digit = False
            while k >= i and s[k] in num_chars:
                if s[k].isdigit():
                    found_digit = True
                k -= 1
            num_start = k + 1
            if not found_digit:
                out.append(s[i:idx])
                out.append("root")
                i = idx + 4
                continue

            number_token = s[num_start:idx]
            # require immediate adjacency (no whitespace)
            if s[num_start:idx].strip() != number_token:
                out.append(s[i:idx])
                out.append("root")
                i = idx + 4
                continue

            after = idx + 4
            if after >= L or s[after] != '(':
                out.append(s[i:after])
                i = after
                continue

            # find matching closing parenthesis
            depth = 0
            j = after
            while j < L:
                if s[j] == '(':
                    depth += 1
                elif s[j] == ')':
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if j >= L or s[j] != ')':
                out.append(s[i:after])
                i = after
                continue

            arg = s[after+1:j]
            out.append(s[i:num_start])
            out.append(f"root({number_token},{arg})")
            i = j + 1

        return "".join(out)

    def _replace_caret_with_pow(self, s):
        out = ""
        i = 0
        L = len(s)
        while i < L:
            if s[i] == '^':
                if not out:
                    out += '^'
                    i += 1
                    continue
                # left token
                if out[-1] == ')':
                    k = len(out) - 1
                    depth = 0
                    while k >= 0:
                        if out[k] == ')':
                            depth += 1
                        elif out[k] == '(':
                            depth -= 1
                            if depth == 0:
                                break
                        k -= 1
                    left = out[k:]
                    out = out[:k]
                else:
                    k = len(out) - 1
                    while k >= 0 and (out[k].isalnum() or out[k] in "._"):
                        k -= 1
                    left = out[k+1:]
                    out = out[:k+1]
                # right token
                k = i + 1
                if k < L and s[k] == '(':
                    depth = 0
                    start = k
                    while k < L:
                        if s[k] == '(':
                            depth += 1
                        elif s[k] == ')':
                            depth -= 1
                            if depth == 0:
                                k += 1
                                break
                        k += 1
                    right = s[start:k]
                else:
                    start = k
                    while k < L and (s[k].isalnum() or s[k] in "._"):
                        k += 1
                    right = s[start:k]
                out += f"pow({left},{right})"
                i = k
            else:
                out += s[i]
                i += 1
        return out

    def _replace_factorials(self, s):
        out = ""
        i = 0
        L = len(s)
        while i < L:
            if s[i] == '!':
                if not out:
                    out += '!'
                    i += 1
                    continue
                if out[-1] == ')':
                    k = len(out) - 1
                    depth = 0
                    while k >= 0:
                        if out[k] == ')':
                            depth += 1
                        elif out[k] == '(':
                            depth -= 1
                            if depth == 0:
                                break
                        k -= 1
                    left = out[k:]
                    out = out[:k]
                else:
                    k = len(out) - 1
                    while k >= 0 and (out[k].isalnum() or out[k] in "._"):
                        k -= 1
                    left = out[k+1:]
                    out = out[:k+1]
                out += f"factorial({left})"
                i += 1
            else:
                out += s[i]
                i += 1
        return out

    def _safe_funcs(self):
        def root(n, x):
            n_val = float(n)
            x_val = float(x)
            if n_val == 0:
                raise ValueError("root: n cannot be 0")
            if x_val < 0 and int(n_val) % 2 == 1:
                return - (abs(x_val) ** (1.0 / n_val))
            return x_val ** (1.0 / n_val)

        def ln(x):
            return math.log(x)

        def log(x, base=10):
            return math.log(x, base)

        def factorial(n):
            if isinstance(n, float) and n.is_integer():
                n = int(n)
            if not (isinstance(n, int) and n >= 0):
                raise ValueError("factorial only defined for non-negative integers")
            return math.factorial(n)

        def deg(x):
            return math.radians(x)

        def rad(x):
            return math.radians(x)

        safe = {
            "sqrt": math.sqrt,
            "pow": pow,
            "root": root,
            "abs": abs,
            "round": round,
            "log": log,
            "ln": ln,
            "pi": math.pi,
            "e": math.e,
            "factorial": factorial,
            # trig
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            # degree/radian helpers
            "deg": deg,
            "rad": rad,
        }
        return safe

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
