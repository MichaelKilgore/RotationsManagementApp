import tkinter as tk
from ui_utils.theme import COLORS, FONTS, bind_text_hover


class SitOutsTable(tk.Frame):
    """Table where each row is a student + checkboxes for the days they sit out."""
    DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

    def __init__(self, parent, **kwargs):
        kwargs.setdefault('bg', COLORS['card'])
        super().__init__(parent, **kwargs)
        self._rows: list[tuple[tk.Entry, list[tk.BooleanVar], tk.Frame]] = []

        header = tk.Frame(self, bg=COLORS['header_bg'])
        header.pack(fill='x')
        tk.Label(header, text='Student Name', width=22, anchor='w',
                 font=FONTS['h2'], bg=COLORS['header_bg'],
                 fg=COLORS['text']).grid(row=0, column=0, padx=(8, 4), pady=5)
        for i, day in enumerate(self.DAYS):
            tk.Label(header, text=day, width=5,
                     font=FONTS['h2'], bg=COLORS['header_bg'],
                     fg=COLORS['text']).grid(row=0, column=i + 1, pady=5)
        tk.Label(header, text='', width=4,
                 bg=COLORS['header_bg']).grid(row=0, column=len(self.DAYS) + 1)

        self.rows_frame = tk.Frame(self, bg=COLORS['card'])
        self.rows_frame.pack(fill='x')

        add_btn = tk.Button(self, text='+ Add Student',
                            bg=COLORS['card'], fg=COLORS['primary'],
                            font=FONTS['body'], relief='flat', bd=0,
                            padx=8, pady=5, cursor='hand2',
                            command=self.add_row)
        add_btn.pack(anchor='w', padx=4, pady=(2, 4))
        bind_text_hover(add_btn, COLORS['card'], COLORS['header_bg'])

    def add_row(self, student: str = '', absent_days: list[str] | None = None):
        row_idx = len(self._rows)
        row_bg = COLORS['row_even'] if row_idx % 2 == 0 else COLORS['row_odd']

        frame = tk.Frame(self.rows_frame, bg=row_bg)
        frame.pack(fill='x')

        name_entry = tk.Entry(frame, width=22,
                              bg=COLORS['entry_bg'], fg=COLORS['text'],
                              relief='flat',
                              highlightthickness=1,
                              highlightbackground=COLORS['entry_border'],
                              highlightcolor=COLORS['primary'],
                              font=FONTS['body'],
                              insertbackground=COLORS['primary'])
        name_entry.grid(row=0, column=0, padx=(8, 4), pady=4)
        if student:
            name_entry.insert(0, student)

        day_vars: list[tk.BooleanVar] = []
        for i, day in enumerate(self.DAYS):
            var = tk.BooleanVar(value=absent_days is not None and day in absent_days)
            tk.Checkbutton(frame, variable=var,
                           bg=row_bg, activebackground=row_bg,
                           selectcolor=COLORS['entry_bg']).grid(row=0, column=i + 1, pady=4)
            day_vars.append(var)

        remove_btn = tk.Button(frame, text='x', width=3,
                               bg=row_bg, fg=COLORS['text_muted'],
                               relief='flat', bd=0,
                               font=FONTS['small'], cursor='hand2',
                               command=lambda f=frame: self._remove_row(f))
        remove_btn.grid(row=0, column=len(self.DAYS) + 1, padx=(4, 8))
        remove_btn.bind('<Enter>',
                        lambda e, btn=remove_btn: btn.configure(bg=COLORS['danger'], fg='white'))
        remove_btn.bind('<Leave>',
                        lambda e, btn=remove_btn, bg=row_bg: btn.configure(bg=bg, fg=COLORS['text_muted']))

        self._rows.append((name_entry, day_vars, frame))

    def _remove_row(self, frame: tk.Frame):
        self._rows = [(n, d, f) for n, d, f in self._rows if f is not frame]
        frame.destroy()

    def get_sit_outs(self, num_rounds: int, days_per_week: int) -> list[list[str]]:
        """Compute round_sit_outs by mapping each round to its day-of-week."""
        active_days = self.DAYS[:days_per_week]
        schedule: list[tuple[str, set[str]]] = []
        for name_entry, day_vars, _ in self._rows:
            name = name_entry.get().strip()
            if name:
                absent = {self.DAYS[i] for i, v in enumerate(day_vars)
                          if v.get() and i < days_per_week}
                if absent:
                    schedule.append((name, absent))

        return [
            [name for name, absent in schedule if active_days[r % days_per_week] in absent]
            for r in range(num_rounds)
        ]
