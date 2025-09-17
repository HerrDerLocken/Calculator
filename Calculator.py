import tkinter as tk
from tkinter import ttk
import math

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.resizable(False, False)
        self.configure(padx=8, pady=8)

        self.expr = ""  # current expression string
        self._create_widgets()

    def _create_widgets(self):
        # Display frame
        display_frame = ttk.Frame(self)
        display_frame.grid(row=0, column=0, sticky="nsew")

        self.display_var = tk.StringVar(value="0")
        display = ttk.Entry(display_frame, textvariable=self.display_var, justify="right", font=("Segoe UI", 18))
        display.grid(row=0, column=0, sticky="ew", ipady=10)
        display.state(["readonly"])

        # Buttons frame
        btns = [
            ["C", "⌫", "(", ")"],
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            ["0", ".", "=", "+"],
        ]

        buttons_frame = ttk.Frame(self)
        buttons_frame.grid(row=1, column=0, pady=(8,0))

        for r, row in enumerate(btns):
            for c, label in enumerate(row):
                action = lambda char=label: self.on_button(char)
                btn = ttk.Button(buttons_frame, text=label, command=action)
                btn.grid(row=r, column=c, ipadx=12, ipady=12, padx=4, pady=4, sticky="nsew")

        # make columns expand evenly
        for i in range(4):
            buttons_frame.columnconfigure(i, weight=1)

        # keyboard bindings
        self.bind_all("<Key>", self.on_key)

    def on_button(self, char):
        if char == "C":
            self.expr = ""
            self.display_var.set("0")
            return
        if char == "⌫":
            self.expr = self.expr[:-1]
            self.display_var.set(self.expr or "0")
            return
        if char == "=":
            self._evaluate()
            return

        # append other chars
        self.expr += char
        self.display_var.set(self.expr)

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
            # accept digits, operators, parentheses, decimal point
            allowed = "0123456789+-*/()."
            if char in allowed:
                self.on_button(char)

    def _evaluate(self):
        if not self.expr:
            return
        # Replace × and ÷ if present (not used here but safe)
        safe_expr = self.expr.replace("×", "*").replace("÷", "/")
        try:
            # Evaluate in a restricted environment
            result = eval(safe_expr, {"__builtins__": None}, self._safe_funcs())
            # Format result: remove trailing .0 for integers
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    # limit float precision to 12 significant digits
                    result = round(result, 12)
            self.expr = str(result)
            self.display_var.set(self.expr)
        except Exception:
            self.display_var.set("Error")
            self.expr = ""

    def _safe_funcs(self):
        # expose math functions/constants if you want (optional)
        safe = {
            "sqrt": math.sqrt,
            "pow": pow,
            "abs": abs,
            "round": round,
            "pi": math.pi,
            "e": math.e
        }
        return safe

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
