import tkinter as tk
from ui_utils.theme import COLORS, FONTS, bind_text_hover

""" This is a generic table which can be instantiated with n columns
    and allows the user to insert and remove rows from the table.
"""
class DynamicTable(tk.Frame):
    """A table of rows where each row has N entry fields and a remove button."""

    def __init__(self, parent, col_headers: list[str], **kwargs):
        kwargs.setdefault('bg', COLORS['card'])
        super().__init__(parent, **kwargs)
        self.col_headers = col_headers
        self.rows: list[list[tk.Entry]] = []

        # Column headers
        header_frame = tk.Frame(self, bg=COLORS['header_bg'])
        header_frame.pack(fill='x')
        for i, h in enumerate(col_headers):
            tk.Label(header_frame, text=h, font=FONTS['h2'],
                     bg=COLORS['header_bg'], fg=COLORS['text'],
                     width=20, anchor='w').grid(row=0, column=i, padx=(8, 4), pady=5)
        tk.Label(header_frame, text='', width=4,
                 bg=COLORS['header_bg']).grid(row=0, column=len(col_headers))

        self.rows_frame = tk.Frame(self, bg=COLORS['card'])
        self.rows_frame.pack(fill='x')

        add_btn = tk.Button(self, text='+ Add Row',
                            bg=COLORS['card'], fg=COLORS['primary'],
                            font=FONTS['body'], relief='flat', bd=0,
                            padx=8, pady=5, cursor='hand2',
                            command=self.add_row)
        add_btn.pack(anchor='w', padx=4, pady=(2, 4))
        bind_text_hover(add_btn, COLORS['card'], COLORS['header_bg'])

        self.add_row()  # start with one blank row

    def add_row(self, values: list[str] | None = None):
        row_idx = len(self.rows)
        row_bg = COLORS['row_even'] if row_idx % 2 == 0 else COLORS['row_odd']

        row_frame = tk.Frame(self.rows_frame, bg=row_bg)
        row_frame.pack(fill='x')

        entries = []
        for i in range(len(self.col_headers)):
            e = tk.Entry(row_frame, width=22,
                         bg=COLORS['entry_bg'], fg=COLORS['text'],
                         relief='flat',
                         highlightthickness=1,
                         highlightbackground=COLORS['entry_border'],
                         highlightcolor=COLORS['primary'],
                         font=FONTS['body'],
                         insertbackground=COLORS['primary'])
            e.grid(row=0, column=i, padx=(8, 4), pady=4)
            if values and i < len(values):
                e.insert(0, values[i])
            entries.append(e)

        remove_btn = tk.Button(row_frame, text='x', width=3,
                               bg=row_bg, fg=COLORS['text_muted'],
                               relief='flat', bd=0,
                               font=FONTS['small'], cursor='hand2',
                               command=lambda f=row_frame, r=entries: self._remove_row(f, r))
        remove_btn.grid(row=0, column=len(self.col_headers), padx=(4, 8))
        remove_btn.bind('<Enter>',
                        lambda e, btn=remove_btn: btn.configure(bg=COLORS['danger'], fg='white'))
        remove_btn.bind('<Leave>',
                        lambda e, btn=remove_btn, bg=row_bg: btn.configure(bg=bg, fg=COLORS['text_muted']))

        self.rows.append(entries)

    def _remove_row(self, frame: tk.Frame, entries: list[tk.Entry]):
        if entries in self.rows:
            self.rows.remove(entries)
        frame.destroy()

    def get_values(self) -> list[list[str]]:
        result = []
        for row_entries in self.rows:
            vals = [e.get().strip() for e in row_entries]
            if any(vals):
                result.append(vals)
        return result
