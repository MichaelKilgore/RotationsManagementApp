COLORS = {
    'bg':             '#f0f4f8',   # main window
    'card':           '#ffffff',   # section cards
    'text':           '#1e293b',   # primary text
    'text_muted':     '#64748b',   # labels, hints
    'primary':        '#2563eb',   # blue accent
    'primary_active': '#1d4ed8',   # blue hover
    'success':        '#16a34a',   # green button
    'success_active': '#15803d',   # green hover
    'danger':         '#ef4444',   # remove button hover
    'entry_bg':       '#ffffff',
    'entry_border':   '#cbd5e1',
    'header_bg':      '#f1f5f9',   # table column headers
    'row_even':       '#ffffff',
    'row_odd':        '#f8fafc',
    'divider':        '#e2e8f0',
    'log_bg':         '#0f172a',
    'log_fg':         '#e2e8f0',
}

FONTS = {
    'h1':    ('Helvetica', 13, 'bold'),
    'h2':    ('Helvetica', 11, 'bold'),
    'body':  ('Helvetica', 10),
    'small': ('Helvetica', 9),
    'mono':  ('Courier', 10),
}


def bind_hover(widget, normal_bg, hover_bg, normal_fg='white', hover_fg='white'):
    """Attach mouse-enter/leave color transitions to a widget."""
    widget.bind('<Enter>', lambda e: widget.configure(bg=hover_bg, fg=hover_fg))
    widget.bind('<Leave>', lambda e: widget.configure(bg=normal_bg, fg=normal_fg))


def bind_text_hover(widget, normal_bg, hover_bg):
    """Hover for text-style (no fg change) widgets like Add Row buttons."""
    widget.bind('<Enter>', lambda e: widget.configure(bg=hover_bg))
    widget.bind('<Leave>', lambda e: widget.configure(bg=normal_bg))
