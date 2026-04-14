import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import io
import json
from pathlib import Path

STATE_FILE = Path.home() / '.rotations_management_app.json'

from SimulateRounds import run_simulation
from RoundsPresentation import RoundsPresentation
from CreateGoogleSlides import create_google_slides


# ── helpers ──────────────────────────────────────────────────────────────────

def parse_name_list(text: str) -> list[str]:
    """Split a newline- or comma-separated string into a clean list of names."""
    names = []
    for token in text.replace('\n', ',').split(','):
        t = token.strip()
        if t:
            names.append(t)
    return names


# ── dynamic row tables ────────────────────────────────────────────────────────

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


# ── sit-outs table ───────────────────────────────────────────────────────────

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


# ── main app ──────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Rotations Management App')
        self.geometry('820x900')
        self.resizable(True, True)

        self._rounds_result = None  # stored after run_simulation

        self._build_ui()
        self._populate_defaults()
        self._load_state()
        self.protocol('WM_DELETE_WINDOW', self._on_close)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Scrollable canvas so everything fits
        canvas = tk.Canvas(self, borderwidth=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        self.main_frame = tk.Frame(canvas, padx=16, pady=16)
        self.main_frame.bind('<Configure>',
                             lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas_window = canvas.create_window((0, 0), window=self.main_frame, anchor='nw')
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, width=e.width))

        # Mouse-wheel scrolling
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units'))

        # ── Configuration ─────────────────────────────────────────────────────
        cfg_frame = self._section_frame('Configuration')
        top_row = tk.Frame(cfg_frame)
        top_row.pack(fill='x', pady=(0, 4))

        tk.Label(top_row, text='Template Slide ID:', anchor='w').grid(row=0, column=0, sticky='w', padx=(0, 8))
        self.template_id_var = tk.StringVar()
        tk.Entry(top_row, textvariable=self.template_id_var, width=50).grid(row=0, column=1, sticky='w')

        tk.Label(top_row, text='Number of Rounds:', anchor='w').grid(row=1, column=0, sticky='w', padx=(0, 8), pady=(6, 0))
        self.num_rounds_var = tk.StringVar(value='12')
        tk.Entry(top_row, textvariable=self.num_rounds_var, width=6).grid(row=1, column=1, sticky='w', pady=(6, 0))

        tk.Label(top_row, text='Days per Week:', anchor='w').grid(row=2, column=0, sticky='w', padx=(0, 8), pady=(6, 0))
        self.days_per_week_var = tk.StringVar(value='4')
        tk.Entry(top_row, textvariable=self.days_per_week_var, width=6).grid(row=2, column=1, sticky='w', pady=(6, 0))

        # ── Students ──────────────────────────────────────────────────────────
        students_frame = self._section_frame('Students  (one per line, or comma-separated)')
        self.students_text = scrolledtext.ScrolledText(students_frame, height=5, wrap='word')
        self.students_text.pack(fill='x')

        # ── Groups ────────────────────────────────────────────────────────────
        groups_frame = self._section_frame('Groups  (name + max size)')
        self.groups_table = DynamicTable(groups_frame, ['Group Name', 'Max Size'])
        self.groups_table.pack(fill='x')

        # ── Invalid Pairs ─────────────────────────────────────────────────────
        pairs_frame = self._section_frame('Invalid Student Pairs  (students who cannot share a group)')
        self.pairs_table = DynamicTable(pairs_frame, ['Student A', 'Student B'])
        self.pairs_table.pack(fill='x')

        # ── Round Sit-outs ────────────────────────────────────────────────────
        sitouts_frame = self._section_frame('Student Sit-outs  (check each day the student is absent)')
        self.sitouts_table = SitOutsTable(sitouts_frame)
        self.sitouts_table.pack(fill='x')

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = tk.Frame(self.main_frame)
        btn_frame.pack(pady=12, anchor='w')

        self.run_btn = tk.Button(btn_frame, text='Run Simulation', width=18,
                                 bg='#4a90d9', fg='black', font=('Helvetica', 11, 'bold'),
                                 command=self._on_run_simulation)
        self.run_btn.pack(side='left', padx=(0, 10))

        self.slides_btn = tk.Button(btn_frame, text='Create Google Slides', width=22,
                                    bg='#34a853', fg='black', font=('Helvetica', 11, 'bold'),
                                    state='disabled', command=self._on_create_slides)
        self.slides_btn.pack(side='left')

        # ── Output log ────────────────────────────────────────────────────────
        output_frame = self._section_frame('Output')
        self.log_text = scrolledtext.ScrolledText(output_frame, height=10, wrap='word',
                                                  state='disabled', bg='#1e1e1e', fg='#d4d4d4',
                                                  font=('Courier', 10))
        self.log_text.pack(fill='x')

    def _section_frame(self, title: str) -> tk.Frame:
        lf = tk.LabelFrame(self.main_frame, text=title, font=('Helvetica', 10, 'bold'),
                           padx=10, pady=8, bd=2, relief='groove')
        lf.pack(fill='x', pady=(8, 0))
        return lf

    # ── Default values ────────────────────────────────────────────────────────

    def _populate_defaults(self):
        self.template_id_var.set('1oQ8zrRGx5s-LbDCpxb8FOg0e62y_bsJ_OOQo1np555Y')

        students = ['marcy', 'perry', 'hamlet', 'saint nick', 'thadeus', 'maxwell',
                    'zeus', 'james', 'victor', 'kobe', 'danny', 'laquintes', 'max',
                    'sam', 'achilles', 'lincoln log', 'hermes', 'poseidon']
        self.students_text.insert('1.0', '\n'.join(students))

        # Remove the default blank row and add real groups
        for row_entries in list(self.groups_table.rows):
            for e in row_entries:
                e.master.destroy()
            self.groups_table.rows.clear()
        for name, size in [('Play Station', 4), ('Word Work', 10), ('Dramatic Play', 2), ('Writing Center', 10)]:
            self.groups_table.add_row([name, str(size)])

        # Invalid pairs
        for row_entries in list(self.pairs_table.rows):
            for e in row_entries:
                e.master.destroy()
            self.pairs_table.rows.clear()
        for a, b in [('kobe', 'marcy'), ('max', 'hermes'), ('maxwell', 'james'),
                     ('james', 'poseidon'), ('perry', 'danny')]:
            self.pairs_table.add_row([a, b])

        # Example sit-outs: add students who are always absent on specific days
        for student, days in [('thadeus', ['Tue', 'Wed']), ('laquintes', ['Tue', 'Wed'])]:
            self.sitouts_table.add_row(student, days)

    # ── State persistence ─────────────────────────────────────────────────────

    def _save_state(self):
        state = {
            'template_id': self.template_id_var.get(),
            'num_rounds': self.num_rounds_var.get(),
            'days_per_week': self.days_per_week_var.get(),
            'students': self.students_text.get('1.0', 'end').rstrip('\n'),
            'groups': self.groups_table.get_values(),
            'invalid_pairs': self.pairs_table.get_values(),
            'sit_outs': [
                {
                    'student': name_entry.get().strip(),
                    'days': [SitOutsTable.DAYS[i] for i, v in enumerate(day_vars) if v.get()]
                }
                for name_entry, day_vars, _ in self.sitouts_table._rows
                if name_entry.get().strip()
            ],
        }
        STATE_FILE.write_text(json.dumps(state, indent=2))

    def _load_state(self):
        if not STATE_FILE.exists():
            return
        try:
            state = json.loads(STATE_FILE.read_text())
        except Exception:
            return  # corrupt or unreadable file — silently keep defaults

        self.template_id_var.set(state.get('template_id', ''))
        self.num_rounds_var.set(state.get('num_rounds', '12'))
        self.days_per_week_var.set(state.get('days_per_week', '4'))

        self.students_text.delete('1.0', 'end')
        self.students_text.insert('1.0', state.get('students', ''))

        for row_entries in list(self.groups_table.rows):
            row_entries[0].master.destroy()
        self.groups_table.rows.clear()
        for row in state.get('groups', []):
            self.groups_table.add_row(row)

        for row_entries in list(self.pairs_table.rows):
            row_entries[0].master.destroy()
        self.pairs_table.rows.clear()
        for row in state.get('invalid_pairs', []):
            self.pairs_table.add_row(row)

        for _, _, frame in list(self.sitouts_table._rows):
            frame.destroy()
        self.sitouts_table._rows.clear()
        for entry in state.get('sit_outs', []):
            self.sitouts_table.add_row(entry.get('student', ''), entry.get('days', []))

    def _on_close(self):
        self._save_state()
        self.destroy()

    # ── Parsing ───────────────────────────────────────────────────────────────

    def _parse_inputs(self):
        students = parse_name_list(self.students_text.get('1.0', 'end'))

        groups_raw = self.groups_table.get_values()
        groups_to_sizes = []
        for row in groups_raw:
            if len(row) < 2:
                continue
            try:
                groups_to_sizes.append((row[0], int(row[1])))
            except ValueError:
                raise ValueError(f'Group size for "{row[0]}" must be a number.')

        pairs_raw = self.pairs_table.get_values()
        invalid_pairs = [(r[0], r[1]) for r in pairs_raw if len(r) >= 2]

        try:
            num_rounds = int(self.num_rounds_var.get().strip())
        except ValueError:
            raise ValueError('Number of rounds must be an integer.')

        try:
            days_per_week = int(self.days_per_week_var.get().strip())
            if not 1 <= days_per_week <= 5:
                raise ValueError()
        except ValueError:
            raise ValueError('Days per week must be a number between 1 and 5.')

        round_sit_outs = self.sitouts_table.get_sit_outs(num_rounds, days_per_week)

        template_id = self.template_id_var.get().strip()
        if not template_id:
            raise ValueError('Template Slide ID cannot be empty.')

        return students, groups_to_sizes, invalid_pairs, round_sit_outs, num_rounds, template_id

    # ── Logging ───────────────────────────────────────────────────────────────

    def _log(self, text: str):
        self.log_text.configure(state='normal')
        self.log_text.insert('end', text + '\n')
        self.log_text.see('end')
        self.log_text.configure(state='disabled')

    def _clear_log(self):
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.configure(state='disabled')

    # ── Actions ───────────────────────────────────────────────────────────────

    def _on_run_simulation(self):
        try:
            students, groups_to_sizes, invalid_pairs, round_sit_outs, num_rounds, template_id = self._parse_inputs()
        except ValueError as e:
            messagebox.showerror('Input Error', str(e))
            return

        self._rounds_result = None
        self.slides_btn.configure(state='disabled')
        self.run_btn.configure(state='disabled', text='Running…')
        self._clear_log()
        self._log('Starting simulation…\n')

        def worker():
            # Capture stdout from run_simulation
            buf = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = buf
            try:
                result = run_simulation(
                    students, groups_to_sizes, invalid_pairs,
                    num_rounds=num_rounds,
                    round_sit_outs=round_sit_outs,
                    debug_mode=False
                )
                sys.stdout = old_stdout
                output = buf.getvalue()
                self.after(0, lambda: self._log(output))
                self.after(0, lambda: self._log('\nSimulation complete!'))
                self._rounds_result = result
                self.after(0, lambda: self.slides_btn.configure(state='normal'))
            except Exception as e:
                sys.stdout = old_stdout
                self.after(0, lambda: self._log(f'Error: {e}'))
                self.after(0, lambda: messagebox.showerror('Simulation Error', str(e)))
            finally:
                self.after(0, lambda: self.run_btn.configure(state='normal', text='Run Simulation'))

        threading.Thread(target=worker, daemon=True).start()

    def _on_create_slides(self):
        if self._rounds_result is None:
            messagebox.showwarning('No Results', 'Run the simulation first.')
            return

        try:
            _, _, _, _, _, template_id = self._parse_inputs()
        except ValueError as e:
            messagebox.showerror('Input Error', str(e))
            return

        self.slides_btn.configure(state='disabled', text='Creating…')
        self._log('\nBuilding replacements and creating Google Slides…')

        def worker():
            try:
                replacements = RoundsPresentation().build_replacements(self._rounds_result)
                # Capture the printed URL
                buf = io.StringIO()
                old_stdout = sys.stdout
                sys.stdout = buf
                create_google_slides(template_id, replacements)
                sys.stdout = old_stdout
                output = buf.getvalue().strip()
                self.after(0, lambda: self._log(output))
                self.after(0, lambda: self._log('Done!'))
            except Exception as e:
                self.after(0, lambda: self._log(f'Error: {e}'))
                self.after(0, lambda: messagebox.showerror('Slides Error', str(e)))
            finally:
                self.after(0, lambda: self.slides_btn.configure(state='normal', text='Create Google Slides'))

        threading.Thread(target=worker, daemon=True).start()


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app = App()
    app.mainloop()
