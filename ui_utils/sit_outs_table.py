import tkinter as tk


class SitOutsTable(tk.Frame):
    """Table where each row is a student + checkboxes for the days they sit out."""
    DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._rows: list[tuple[tk.Entry, list[tk.BooleanVar], tk.Frame]] = []

        header = tk.Frame(self)
        header.pack(fill='x')
        tk.Label(header, text='Student Name', width=20, anchor='w',
                 font=('Helvetica', 10, 'bold')).grid(row=0, column=0, padx=4)
        for i, day in enumerate(self.DAYS):
            tk.Label(header, text=day, width=5,
                     font=('Helvetica', 10, 'bold')).grid(row=0, column=i + 1)

        self.rows_frame = tk.Frame(self)
        self.rows_frame.pack(fill='x')

        tk.Button(self, text='+ Add Student', command=self.add_row).pack(anchor='w', pady=(4, 0))

    def add_row(self, student: str = '', absent_days: list[str] | None = None):
        frame = tk.Frame(self.rows_frame)
        frame.pack(fill='x', pady=1)

        name_entry = tk.Entry(frame, width=20)
        name_entry.grid(row=0, column=0, padx=4)
        if student:
            name_entry.insert(0, student)

        day_vars: list[tk.BooleanVar] = []
        for i, day in enumerate(self.DAYS):
            var = tk.BooleanVar(value=absent_days is not None and day in absent_days)
            tk.Checkbutton(frame, variable=var).grid(row=0, column=i + 1)
            day_vars.append(var)

        tk.Button(frame, text='✕', width=3,
                  command=lambda f=frame: self._remove_row(f)).grid(
                  row=0, column=len(self.DAYS) + 1, padx=4)

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
