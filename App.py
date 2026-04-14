import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import io
import json
from pathlib import Path
from ui_utils.dynamic_table import DynamicTable
from ui_utils.sit_outs_table import SitOutsTable
from ui_utils.theme import COLORS, FONTS, bind_hover, bind_text_hover

STATE_FILE = Path.home() / '.rotations_management_app.json'

from SimulateRounds import run_simulation
from RoundsPresentation import RoundsPresentation
from CreateGoogleSlides import create_google_slides



# ── main app ──────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Rotations Management App')
        self.geometry('860x920')
        self.resizable(True, True)
        self.configure(bg=COLORS['bg'])

        # Use the clam ttk theme for cleaner scrollbars and ttk widgets
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TScrollbar',
                        background=COLORS['divider'],
                        troughcolor=COLORS['bg'],
                        borderwidth=0,
                        arrowcolor=COLORS['text_muted'])

        self._rounds_result = None  # stored after run_simulation

        self._build_ui()
        self._populate_defaults()
        self._load_state()
        self.protocol('WM_DELETE_WINDOW', self._on_close)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Scrollable canvas
        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg=COLORS['bg'])
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        self.main_frame = tk.Frame(canvas, bg=COLORS['bg'], padx=24, pady=20)
        self.main_frame.bind('<Configure>',
                             lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas_window = canvas.create_window((0, 0), window=self.main_frame, anchor='nw')
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, width=e.width))

        # Mouse-wheel scrolling
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units'))

        # ── App title ─────────────────────────────────────────────────────────
        tk.Label(self.main_frame, text='Rotations Management',
                 font=FONTS['h1'], bg=COLORS['bg'], fg=COLORS['primary']).pack(anchor='w', pady=(0, 4))
        tk.Frame(self.main_frame, bg=COLORS['divider'], height=1).pack(fill='x', pady=(0, 12))

        # ── Configuration ─────────────────────────────────────────────────────
        cfg_frame = self._section_frame('Configuration')
        top_row = tk.Frame(cfg_frame, bg=COLORS['card'])
        top_row.pack(fill='x', pady=(0, 4))

        self.template_id_var = tk.StringVar()
        self.num_rounds_var = tk.StringVar(value='12')
        self.days_per_week_var = tk.StringVar(value='4')

        fields = [
            ('Template Slide ID:', self.template_id_var, 50),
            ('Number of Rounds:',  self.num_rounds_var,  6),
            ('Days per Week:',     self.days_per_week_var, 6),
        ]
        for row_idx, (label, var, width) in enumerate(fields):
            pady = (0, 0) if row_idx == 0 else (6, 0)
            tk.Label(top_row, text=label, anchor='w',
                     bg=COLORS['card'], fg=COLORS['text'],
                     font=FONTS['body']).grid(row=row_idx, column=0, sticky='w',
                                              padx=(0, 12), pady=pady)
            tk.Entry(top_row, textvariable=var, width=width,
                     bg=COLORS['entry_bg'], fg=COLORS['text'],
                     relief='flat',
                     highlightthickness=1,
                     highlightbackground=COLORS['entry_border'],
                     highlightcolor=COLORS['primary'],
                     font=FONTS['body'],
                     insertbackground=COLORS['primary']).grid(row=row_idx, column=1,
                                                              sticky='w', pady=pady)

        # ── Students ──────────────────────────────────────────────────────────
        students_frame = self._section_frame('Students')
        self.students_table = DynamicTable(students_frame, ['Student Name'])
        self.students_table.pack(fill='x')

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

        # ── Action buttons ────────────────────────────────────────────────────
        btn_frame = tk.Frame(self.main_frame, bg=COLORS['bg'])
        btn_frame.pack(pady=20, anchor='w')

        self.run_btn = tk.Button(
            btn_frame, text='Run Simulation',
            bg=COLORS['primary'], fg='white',
            font=FONTS['h2'], relief='flat', bd=0,
            padx=20, pady=10, cursor='hand2',
            command=self._on_run_simulation)
        self.run_btn.pack(side='left', padx=(0, 12))
        bind_hover(self.run_btn, COLORS['primary'], COLORS['primary_active'])

        self.slides_btn = tk.Button(
            btn_frame, text='Create Google Slides',
            bg=COLORS['success'], fg='white',
            font=FONTS['h2'], relief='flat', bd=0,
            padx=20, pady=10, cursor='hand2',
            state='disabled', command=self._on_create_slides)
        self.slides_btn.pack(side='left')
        bind_hover(self.slides_btn, COLORS['success'], COLORS['success_active'])

        # ── Output log ────────────────────────────────────────────────────────
        output_frame = self._section_frame('Output')
        self.log_text = scrolledtext.ScrolledText(
            output_frame, height=10, wrap='word',
            state='disabled',
            bg=COLORS['log_bg'], fg=COLORS['log_fg'],
            font=FONTS['mono'],
            relief='flat', bd=0,
            padx=10, pady=8,
            insertbackground='white')
        self.log_text.pack(fill='x')

    def _section_frame(self, title: str) -> tk.Frame:
        lf = tk.LabelFrame(self.main_frame, text=f'  {title}  ',
                           font=FONTS['h2'],
                           bg=COLORS['card'], fg=COLORS['primary'],
                           padx=0, pady=0,
                           bd=1, relief='groove')
        lf.pack(fill='x', pady=(0, 10))
        return lf

    # ── Default values ────────────────────────────────────────────────────────

    def _populate_defaults(self):
        self.template_id_var.set('1oQ8zrRGx5s-LbDCpxb8FOg0e62y_bsJ_OOQo1np555Y')

        students = ['marcy', 'perry', 'hamlet', 'saint nick', 'thadeus', 'maxwell',
                    'zeus', 'james', 'victor', 'kobe', 'danny', 'laquintes', 'max',
                    'sam', 'achilles', 'lincoln log', 'hermes', 'poseidon']
        for row_entries in list(self.students_table.rows):
            row_entries[0].master.destroy()
        self.students_table.rows.clear()
        for name in students:
            self.students_table.add_row([name])

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

        # Example sit-outs
        for student, days in [('thadeus', ['Tue', 'Wed']), ('laquintes', ['Tue', 'Wed'])]:
            self.sitouts_table.add_row(student, days)

    # ── State persistence ─────────────────────────────────────────────────────

    def _save_state(self):
        state = {
            'template_id': self.template_id_var.get(),
            'num_rounds': self.num_rounds_var.get(),
            'days_per_week': self.days_per_week_var.get(),
            'students': [row[0] for row in self.students_table.get_values()],
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

        for row_entries in list(self.students_table.rows):
            row_entries[0].master.destroy()
        self.students_table.rows.clear()
        for name in state.get('students', []):
            self.students_table.add_row([name])

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
        students = [row[0] for row in self.students_table.get_values() if row[0]]

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
        self.run_btn.configure(state='disabled', text='Running...')
        self._clear_log()
        self._log('Starting simulation...\n')

        def worker():
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

        self.slides_btn.configure(state='disabled', text='Creating...')
        self._log('\nBuilding replacements and creating Google Slides...')

        def worker():
            try:
                replacements = RoundsPresentation().build_replacements(self._rounds_result)
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
