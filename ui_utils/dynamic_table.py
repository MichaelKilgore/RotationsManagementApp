import tkinter as tk

""" This is a generic table which can be instantiated with n columns
    and allows the user to insert and remove rows from the table.
"""
class DynamicTable(tk.Frame):
    """A table of rows where each row has N entry fields and a remove button."""

    def __init__(self, parent, col_headers: list[str], **kwargs):
        super().__init__(parent, **kwargs)
        self.col_headers = col_headers
        self.rows: list[list[tk.Entry]] = []

        header_frame = tk.Frame(self)
        header_frame.pack(fill='x')
        for i, h in enumerate(col_headers):
            tk.Label(header_frame, text=h, font=('Helvetica', 10, 'bold'), width=20, anchor='w').grid(row=0, column=i, padx=4)
        tk.Label(header_frame, text='', width=6).grid(row=0, column=len(col_headers))  # spacer for remove btn

        self.rows_frame = tk.Frame(self)
        self.rows_frame.pack(fill='x')

        add_btn = tk.Button(self, text='+ Add Row', command=self.add_row)
        add_btn.pack(anchor='w', pady=(4, 0))

        self.add_row()  # start with one blank row

    def add_row(self, values: list[str] | None = None):
        row_frame = tk.Frame(self.rows_frame)
        row_frame.pack(fill='x', pady=1)

        entries = []
        for i, _ in enumerate(self.col_headers):
            e = tk.Entry(row_frame, width=20)
            e.grid(row=0, column=i, padx=4)
            if values and i < len(values):
                e.insert(0, values[i])
            entries.append(e)

        remove_btn = tk.Button(row_frame, text='✕', width=3,
                               command=lambda f=row_frame, r=entries: self._remove_row(f, r))
        remove_btn.grid(row=0, column=len(self.col_headers), padx=4)

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


