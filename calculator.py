"""
Simple GUI Calculator (Tkinter)
Matches the Daily UI #004 style layout: C / +/- / % / ÷ row,
light-dark segmented toggle, previous-expression line, accent #F57927.
Run with: python calculator.py
"""

import tkinter as tk

ACCENT = "#F57927"

LIGHT = {"bg": "#EFEFF2", "card": "#FFFFFF", "text": "#17171A", "sub": "#8A8A93", "key": "#F0F0F2"}
DARK = {"bg": "#0E0E10", "card": "#17171A", "text": "#FFFFFF", "sub": "#8A8A93", "key": "#2E2E32"}


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.geometry("340x560")
        self.resizable(False, False)

        self.dark_mode = False
        self.current = "0"
        self.stored = None
        self.pending_op = None
        self.just_evaluated = False

        self.result_var = tk.StringVar(value="0")
        self.prev_var = tk.StringVar(value=" ")

        self._build_ui()
        self._apply_theme()
        self.bind("<Key>", self._on_key)

    def _build_ui(self):
        self.toggle_row = tk.Frame(self)
        self.toggle_row.pack(pady=(18, 20))

        self.light_btn = tk.Button(self.toggle_row, text="☀", width=3, relief="flat",
                                    command=lambda: self.set_theme(False))
        self.light_btn.pack(side="left")
        self.dark_btn = tk.Button(self.toggle_row, text="🌙", width=3, relief="flat",
                                   command=lambda: self.set_theme(True))
        self.dark_btn.pack(side="left")

        self.result_block = tk.Frame(self)
        self.result_block.pack(fill="x", padx=20)

        self.prev_label = tk.Label(self.result_block, textvariable=self.prev_var, font=("Segoe UI", 11), anchor="e")
        self.prev_label.pack(fill="x")
        self.result_label = tk.Label(self.result_block, textvariable=self.result_var,
                                      font=("Segoe UI", 30, "bold"), anchor="e")
        self.result_label.pack(fill="x", pady=(2, 16))

        self.card = tk.Frame(self)
        self.card.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.tool_row = tk.Frame(self.card)
        self.tool_row.pack(fill="x", pady=(10, 10), padx=6)
        self.icons_label = tk.Label(self.tool_row, text="🕘  💾  ⚙", font=("Segoe UI", 11))
        self.icons_label.pack(side="left")
        self.close_btn = tk.Label(self.tool_row, text="✕", font=("Segoe UI", 11), cursor="hand2")
        self.close_btn.pack(side="right")
        self.close_btn.bind("<Button-1>", lambda e: self.clear())

        self.keypad = tk.Frame(self.card)
        self.keypad.pack(fill="both", expand=True, padx=6, pady=(0, 10))

        rows = [
            [("C", "clear"), ("+/-", "sign"), ("%", "percent"), ("/", "op")],
            [("7", "digit"), ("8", "digit"), ("9", "digit"), ("*", "op")],
            [("4", "digit"), ("5", "digit"), ("6", "digit"), ("-", "op")],
            [("1", "digit"), ("2", "digit"), ("3", "digit"), ("+", "op")],
            [("0", "wide"), (".", "digit"), ("=", "equals")],
        ]

        self.buttons = []
        for r, row in enumerate(rows):
            self.keypad.grid_rowconfigure(r, weight=1)
            col = 0
            for label, kind in row:
                self.keypad.grid_columnconfigure(col, weight=1)
                colspan = 2 if kind == "wide" else 1
                is_op = kind in ("op", "equals")
                btn = tk.Button(
                    self.keypad, text=label, font=("Segoe UI", 16, "bold"), relief="flat",
                    command=lambda l=label, k=kind: self.on_press(l, k),
                    bg=ACCENT if is_op else None, fg="white" if is_op else (
                        "#E2483B" if kind == "clear" else None),
                )
                btn.grid(row=r, column=col, columnspan=colspan, sticky="nsew", padx=5, pady=5)
                self.buttons.append((btn, kind))
                col += colspan

    def _apply_theme(self):
        t = DARK if self.dark_mode else LIGHT
        self.configure(bg=t["bg"])
        self.toggle_row.configure(bg=t["bg"])
        self.result_block.configure(bg=t["bg"])
        self.prev_label.configure(bg=t["bg"], fg=t["sub"])
        self.result_label.configure(bg=t["bg"], fg=t["text"])
        self.card.configure(bg=t["card"])
        self.tool_row.configure(bg=t["card"])
        self.icons_label.configure(bg=t["card"], fg=t["sub"])
        self.close_btn.configure(bg=t["card"], fg=t["sub"])
        self.keypad.configure(bg=t["card"])
        self.light_btn.configure(bg=t["card"] if not self.dark_mode else t["key"],
                                  fg=t["text"], activebackground=t["card"])
        self.dark_btn.configure(bg=t["card"] if self.dark_mode else t["key"],
                                 fg=t["text"], activebackground=t["card"])

        for btn, kind in self.buttons:
            if kind not in ("op", "equals"):
                fg = "#E2483B" if kind == "clear" else t["text"]
                btn.configure(bg=t["key"], fg=fg, activebackground=t["key"])

    def set_theme(self, dark):
        self.dark_mode = dark
        self._apply_theme()

    def on_press(self, label, kind):
        if kind == "digit":
            if self.just_evaluated:
                self.current = "0"
                self.just_evaluated = False
            if label == "." and "." in self.current:
                return
            self.current = label if self.current == "0" and label != "." else self.current + label
        elif kind == "clear":
            self.clear()
        elif kind == "sign":
            self.current = str(float(self.current) * -1)
        elif kind == "percent":
            self.current = str(float(self.current) / 100)
        elif kind == "op":
            self.set_operator(label)
        elif kind == "equals":
            self.compute()
        self._render()

    def clear(self):
        self.current = "0"
        self.stored = None
        self.pending_op = None
        self.just_evaluated = False
        self.prev_var.set(" ")
        self._render()

    def set_operator(self, op):
        if self.pending_op and self.stored is not None and not self.just_evaluated:
            self.compute()
        self.stored = float(self.current)
        self.pending_op = op
        self.just_evaluated = True
        self.prev_var.set(f"{self.stored:,.0f} {op}")

    def compute(self):
        if self.pending_op is None or self.stored is None:
            return
        b = float(self.current)
        ops = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
               "*": lambda a, b: a * b, "/": lambda a, b: a / b if b else float("nan")}
        result = ops[self.pending_op](self.stored, b)
        self.prev_var.set(f"{self.stored:,.0f} {self.pending_op} {b:,.0f}")
        self.current = "Error" if result != result else str(round(result, 10))
        self.stored = None
        self.pending_op = None
        self.just_evaluated = True

    def _render(self):
        self.result_var.set(self.current)

    def _on_key(self, event):
        if event.char in "0123456789.":
            self.on_press(event.char, "digit")
        elif event.char in "+-*/":
            self.on_press(event.char, "op")
        elif event.keysym == "Return":
            self.on_press("=", "equals")
        elif event.keysym == "BackSpace":
            self.current = self.current[:-1] or "0"
            self._render()


if __name__ == "__main__":
    Calculator().mainloop()
