"""
app.py
------
SELOR — graphical interface (tkinter).
Entry point: python app.py
"""

import os
import sys
import calendar
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime

from db import (
    insert_case, fetch_cases, export_to_excel, DBError,
    CASE_TYPES, SP_TYPES, SP_TYPES_VIEW, BUSINESS_MODELS, MARKETPLACES,
    CASE_STATUSES, CASE_REASON_CODES, DEFAULT_SEARCH_LIMIT,
)

APP_TITLE = "SELOR"


def resource_path(*parts) -> str:
    """Resolve path to bundled asset (works both as script and PyInstaller exe)."""
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, *parts)


# Design tokens

COLORS = {
    "header_from": "#173A5E",
    "header_to": "#3E8E41",
    "green": "#4CAF50",
    "green_dark": "#1B5E20",
    "green_light": "#8BC34A",
    "green_tint": "#EAF5EA",
    "blue": "#1B4B72",
    "page_bg": "#F2F6F3",
    "card_bg": "#FFFFFF",
    "border": "#DCE6DE",
    "text": "#1E2B23",
    "text_muted": "#5C6F63",
    "success_bg": "#E6F4EA",
    "success_fg": "#1B5E20",
    "error_bg": "#FBEAEA",
    "error_fg": "#8A2C2C",
}


def pick_font_family(preferred: list) -> str:
    available = set(tkfont.families())
    for name in preferred:
        if name in available:
            return name
    return "TkDefaultFont"


class Theme:


    def __init__(self, root: tk.Tk):
        self.root = root
        sans = pick_font_family(["Segoe UI", "Helvetica Neue", "Helvetica", "Arial"])
        mono = pick_font_family(["Consolas", "Menlo", "Courier New"])

        self.font_title = tkfont.Font(family=sans, size=20, weight="bold")
        self.font_subtitle = tkfont.Font(family=sans, size=10)
        self.font_section = tkfont.Font(family=sans, size=12, weight="bold")
        self.font_body = tkfont.Font(family=sans, size=10)
        self.font_body_bold = tkfont.Font(family=sans, size=10, weight="bold")
        self.font_small = tkfont.Font(family=sans, size=9)
        self.font_mono = tkfont.Font(family=mono, size=9)

        style = ttk.Style(root)
        style.theme_use("clam")
        c = COLORS

        style.configure(".", background=c["card_bg"], foreground=c["text"], font=self.font_body)
        style.configure("TFrame", background=c["card_bg"])
        style.configure("TLabel", background=c["card_bg"], foreground=c["text"], font=self.font_body)
        style.configure("Section.TLabel", background=c["card_bg"], foreground=c["blue"], font=self.font_section)
        style.configure("Hint.TLabel", background=c["card_bg"], foreground=c["text_muted"], font=self.font_small)
        style.configure("Muted.TLabel", background=c["card_bg"], foreground=c["text_muted"], font=self.font_small)

        style.configure("TCheckbutton", background=c["card_bg"], foreground=c["text"], font=self.font_body)
        style.map("TCheckbutton", background=[("active", c["card_bg"])])
        style.configure("TRadiobutton", background=c["card_bg"], foreground=c["text"], font=self.font_body)
        style.map("TRadiobutton", background=[("active", c["card_bg"])])

        style.configure("TEntry", fieldbackground="white", foreground=c["text"],
                         bordercolor=c["border"], lightcolor=c["border"], darkcolor=c["border"],
                         padding=5)
        style.map("TEntry", bordercolor=[("focus", c["green"])])

        style.configure("TCombobox", fieldbackground="white", foreground=c["text"],
                         arrowcolor=c["blue"], bordercolor=c["border"], padding=4)
        style.map("TCombobox",
                   fieldbackground=[("readonly", "white")],
                   foreground=[("readonly", c["text"])],
                   bordercolor=[("focus", c["green"])])

        style.configure("TLabelframe", background=c["card_bg"], bordercolor=c["border"])
        style.configure("TLabelframe.Label", background=c["card_bg"], foreground=c["blue"], font=self.font_section)

        style.configure("Primary.TButton", background=c["green"], foreground="white",
                         font=self.font_body_bold, padding=(14, 8), borderwidth=0, relief="flat")
        style.map("Primary.TButton",
                   background=[("active", c["green_dark"]), ("disabled", c["border"])],
                   foreground=[("disabled", c["text_muted"])])

        style.configure("Secondary.TButton", background=c["green_tint"], foreground=c["blue"],
                         font=self.font_body, padding=(12, 7), borderwidth=0, relief="flat")
        style.map("Secondary.TButton", background=[("active", c["border"])])

        style.configure("Icon.TButton", background=c["green_tint"], foreground=c["blue"],
                         font=self.font_body, padding=(4, 3), borderwidth=0, relief="flat")
        style.map("Icon.TButton", background=[("active", c["border"])])

        style.configure("TNotebook", background=c["page_bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=c["page_bg"], foreground=c["text_muted"],
                         font=self.font_body_bold, padding=(18, 10), borderwidth=0)
        style.map("TNotebook.Tab",
                   background=[("selected", c["green"])],
                   foreground=[("selected", "white")])

        style.configure("Treeview", background="white", fieldbackground="white",
                         foreground=c["text"], font=self.font_body, rowheight=26, borderwidth=0)
        style.configure("Treeview.Heading", background=c["blue"], foreground="white",
                         font=self.font_body_bold, relief="flat", padding=(6, 6))
        style.map("Treeview.Heading", background=[("active", c["green_dark"])])
        style.map("Treeview", background=[("selected", c["green_light"])],
                   foreground=[("selected", "white")])


def make_card(parent: tk.Widget, accent: str = COLORS["green"]) -> ttk.Frame:
    """Card panel with accent bar. Returns (outer_frame, inner_frame)."""
    outer = tk.Frame(parent, bg=COLORS["page_bg"])
    tk.Frame(outer, bg=accent, height=4).pack(fill="x")
    inner = ttk.Frame(outer, padding=18)
    inner.pack(fill="both", expand=True)
    return outer, inner


def make_status_badge(parent: tk.Widget) -> ttk.Label:
    """Status banner label with .set_success(), .set_error(), .clear()."""
    label = ttk.Label(parent, text="", justify="left", wraplength=520, padding=(12, 10))

    def set_success(text):
        label.configure(text=text, background=COLORS["success_bg"], foreground=COLORS["success_fg"])

    def set_error(text):
        label.configure(text=text, background=COLORS["error_bg"], foreground=COLORS["error_fg"])

    def clear():
        label.configure(text="", background=COLORS["card_bg"])

    label.set_success = set_success
    label.set_error = set_error
    label.clear = clear
    label.clear()
    return label



class CalendarPopup(tk.Toplevel):
    def __init__(self, master, on_pick, initial=None):
        super().__init__(master)
        self.title("Pick a date")
        self.configure(bg=COLORS["page_bg"])
        self.resizable(False, False)
        self.on_pick = on_pick
        today = initial or date.today()
        self.today = date.today()
        self.year_var = tk.IntVar(value=today.year)
        self.month_var = tk.StringVar(value=calendar.month_name[today.month])

        nav = ttk.Frame(self, padding=10)
        nav.pack(fill="x")

        ttk.Button(nav, text="\u00AB", width=3, style="Icon.TButton", command=self._prev_year).grid(row=0, column=0)
        ttk.Button(nav, text="\u2039", width=3, style="Icon.TButton", command=self._prev_month).grid(row=0, column=1, padx=(2, 6))

        month_cb = ttk.Combobox(nav, textvariable=self.month_var, values=list(calendar.month_name)[1:],
                                 state="readonly", width=11)
        month_cb.grid(row=0, column=2, padx=4)
        month_cb.bind("<<ComboboxSelected>>", lambda e: self._draw())

        year_cb = ttk.Combobox(nav, textvariable=self.year_var,
                                values=[str(y) for y in range(1990, 2101)],
                                state="readonly", width=6)
        year_cb.grid(row=0, column=3, padx=4)
        year_cb.bind("<<ComboboxSelected>>", lambda e: self._draw())

        ttk.Button(nav, text="\u203A", width=3, style="Icon.TButton", command=self._next_month).grid(row=0, column=4, padx=(6, 2))
        ttk.Button(nav, text="\u00BB", width=3, style="Icon.TButton", command=self._next_year).grid(row=0, column=5)

        self.grid_frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        self.grid_frame.pack()
        self._draw()

        self.transient(master)
        self.grab_set()

    @property
    def _month_num(self):
        return list(calendar.month_name).index(self.month_var.get())

    def _prev_month(self):
        m = self._month_num - 1
        if m == 0:
            self.month_var.set(calendar.month_name[12])
            self.year_var.set(self.year_var.get() - 1)
        else:
            self.month_var.set(calendar.month_name[m])
        self._draw()

    def _next_month(self):
        m = self._month_num + 1
        if m == 13:
            self.month_var.set(calendar.month_name[1])
            self.year_var.set(self.year_var.get() + 1)
        else:
            self.month_var.set(calendar.month_name[m])
        self._draw()

    def _prev_year(self):
        self.year_var.set(self.year_var.get() - 1)
        self._draw()

    def _next_year(self):
        self.year_var.set(self.year_var.get() + 1)
        self._draw()

    def _draw(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        year, month = self.year_var.get(), self._month_num

        for i, day_name in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            ttk.Label(self.grid_frame, text=day_name, width=4, anchor="center",
                      style="Muted.TLabel").grid(row=0, column=i)

        cal = calendar.Calendar(firstweekday=0)
        row = 1
        for week in cal.monthdayscalendar(year, month):
            for col, day in enumerate(week):
                if day == 0:
                    ttk.Label(self.grid_frame, text="", width=4).grid(row=row, column=col)
                else:
                    is_today = date(year, month, day) == self.today
                    btn_style = "Primary.TButton" if is_today else "Icon.TButton"
                    ttk.Button(self.grid_frame, text=str(day), width=4, style=btn_style,
                               command=lambda d=day: self._pick(d)).grid(row=row, column=col, padx=1, pady=1)
            row += 1

    def _pick(self, day):
        self.on_pick(date(self.year_var.get(), self._month_num, day))
        self.destroy()


def attach_calendar_button(parent, entry_var, row, column):

    def open_calendar():
        def on_pick(d):
            entry_var.set(d.isoformat())
        CalendarPopup(parent, on_pick)
    ttk.Button(parent, text="\U0001F4C5", width=3, style="Icon.TButton", command=open_calendar).grid(
        row=row, column=column, padx=(4, 0))


def parse_iso_date(value):
    value = value.strip()
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()



class DataEntryFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORS["page_bg"])
        self._build_scrollable()
        self._build_form()

    def _build_scrollable(self):
        """Scrollable canvas wrapper for small screens."""
        self._canvas = tk.Canvas(self, bg=COLORS["page_bg"], highlightthickness=0)
        self._vsb = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vsb.set)

        self._vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(self._canvas, bg=COLORS["page_bg"])
        self._canvas_win = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")

        self._inner.bind("<Configure>", lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(self._canvas_win, width=e.width))

        def _on_mousewheel(event):
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self._canvas.bind_all("<MouseWheel>", _on_mousewheel, add="+")

    def _build_form(self):
        card_outer, card = make_card(self._inner, accent=COLORS["green"])
        card_outer.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(card, text="New case", style="Section.TLabel").grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 14))

        row = 1

        ttk.Label(card, text="Case ID *").grid(row=row, column=0, sticky="w", pady=6)
        self.case_id_var = tk.StringVar()
        ttk.Entry(card, textvariable=self.case_id_var, width=30).grid(row=row, column=1, sticky="w")
        row += 1

        ttk.Label(card, text="Case Date (YYYY-MM-DD) *").grid(row=row, column=0, sticky="w", pady=6)
        self.case_date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(card, textvariable=self.case_date_var, width=26).grid(row=row, column=1, sticky="w")
        attach_calendar_button(card, self.case_date_var, row, 2)
        row += 1

        ttk.Label(card, text="Case Type *").grid(row=row, column=0, sticky="w", pady=6)
        self.case_type_var = tk.StringVar()
        case_type_cb = ttk.Combobox(card, textvariable=self.case_type_var, values=CASE_TYPES,
                                     state="readonly", width=27)
        case_type_cb.grid(row=row, column=1, sticky="w")
        case_type_cb.bind("<<ComboboxSelected>>", self._on_case_type_change)
        row += 1

        ttk.Label(card, text="SP Type *").grid(row=row, column=0, sticky="w", pady=6)
        self.sp_type_var = tk.StringVar()
        ttk.Combobox(card, textvariable=self.sp_type_var, values=SP_TYPES,
                     state="readonly", width=27).grid(row=row, column=1, sticky="w")
        row += 1

        ttk.Label(card, text="Selling Partner ID / Vendor Code *").grid(row=row, column=0, sticky="w", pady=6)
        self.sp_id_var = tk.StringVar()
        self.sp_id_entry = ttk.Entry(card, textvariable=self.sp_id_var, width=30)
        self.sp_id_entry.grid(row=row, column=1, sticky="w")
        self.sp_id_na = tk.BooleanVar()
        ttk.Checkbutton(card, text="N/A", variable=self.sp_id_na,
                         command=lambda: self._toggle(self.sp_id_entry, self.sp_id_na)
                         ).grid(row=row, column=2, sticky="w")
        row += 1

        ttk.Label(card, text="Seller Business Model *").grid(row=row, column=0, sticky="w", pady=6)
        self.business_model_var = tk.StringVar()
        ttk.Combobox(card, textvariable=self.business_model_var, values=BUSINESS_MODELS,
                     state="readonly", width=27).grid(row=row, column=1, sticky="w")
        row += 1

        ttk.Label(card, text="SP Name (DR cases)").grid(row=row, column=0, sticky="w", pady=6)
        self.sp_name_var = tk.StringVar()
        self.sp_name_entry = ttk.Entry(card, textvariable=self.sp_name_var, width=30)
        self.sp_name_entry.grid(row=row, column=1, sticky="w")
        self.sp_name_na = tk.BooleanVar()
        ttk.Checkbutton(card, text="N/A", variable=self.sp_name_na,
                         command=lambda: self._toggle(self.sp_name_entry, self.sp_name_na)
                         ).grid(row=row, column=2, sticky="w")
        row += 1

        ttk.Label(card, text="ASIN (SA cases)").grid(row=row, column=0, sticky="w", pady=6)
        self.asin_var = tk.StringVar()
        self.asin_entry = ttk.Entry(card, textvariable=self.asin_var, width=30)
        self.asin_entry.grid(row=row, column=1, sticky="w")
        self.asin_na = tk.BooleanVar()
        ttk.Checkbutton(card, text="N/A", variable=self.asin_na,
                         command=lambda: self._toggle(self.asin_entry, self.asin_na)
                         ).grid(row=row, column=2, sticky="w")
        row += 1

        ttk.Label(card, text="MP *").grid(row=row, column=0, sticky="w", pady=6)
        self.mp_var = tk.StringVar()
        ttk.Combobox(card, textvariable=self.mp_var, values=MARKETPLACES,
                     state="readonly", width=27).grid(row=row, column=1, sticky="w")
        row += 1

        ttk.Label(card, text="Case Status *").grid(row=row, column=0, sticky="w", pady=6)
        self.case_status_var = tk.StringVar()
        status_cb = ttk.Combobox(card, textvariable=self.case_status_var, values=CASE_STATUSES,
                                  state="readonly", width=27)
        status_cb.grid(row=row, column=1, sticky="w")
        status_cb.bind("<<ComboboxSelected>>", self._on_status_change)
        row += 1

        ttk.Label(card, text="Case Reason Code *").grid(row=row, column=0, sticky="w", pady=6)
        self.reason_code_var = tk.StringVar(value="Please choose Case Status first")
        self.reason_code_cb = ttk.Combobox(card, textvariable=self.reason_code_var,
                                            values=[], state="readonly", width=45)
        self.reason_code_cb.grid(row=row, column=1, columnspan=2, sticky="w")
        row += 1

        ttk.Label(card, text="Expiry Date (YYYY-MM-DD)").grid(row=row, column=0, sticky="w", pady=6)
        self.expiry_var = tk.StringVar()
        self.expiry_entry = ttk.Entry(card, textvariable=self.expiry_var, width=26)
        self.expiry_entry.grid(row=row, column=1, sticky="w")
        attach_calendar_button(card, self.expiry_var, row, 2)
        self.expiry_na = tk.BooleanVar()
        self.expiry_na_check = ttk.Checkbutton(card, text="N/A", variable=self.expiry_na,
                                                command=lambda: self._toggle(self.expiry_entry, self.expiry_na))
        self.expiry_na_check.grid(row=row, column=3, sticky="w")
        row += 1

        self.not_approved_note = ttk.Label(card, text="", style="Hint.TLabel")
        self.not_approved_note.grid(row=row, column=1, columnspan=2, sticky="w")
        row += 1

        btn_row = ttk.Frame(card)
        btn_row.grid(row=row, column=0, columnspan=3, pady=(18, 12), sticky="w")
        ttk.Button(btn_row, text="Upload Data", style="Primary.TButton", command=self._on_upload).pack(side="left")
        ttk.Button(btn_row, text="Clear Template", style="Secondary.TButton", command=self._clear_form).pack(
            side="left", padx=(10, 0))
        row += 1

        self.status_label = make_status_badge(card)
        self.status_label.grid(row=row, column=0, columnspan=4, sticky="ew", pady=(4, 0))

    def _toggle(self, entry_widget, na_var):
        entry_widget.configure(state="disabled" if na_var.get() else "normal")

    def _on_case_type_change(self, event=None):
        case_type = self.case_type_var.get()
        if case_type == "DR":
            self.sp_name_entry.configure(state="normal")
            self.sp_name_na.set(False)
            self.asin_var.set("")
            self.asin_entry.configure(state="disabled")
            self.asin_na.set(True)
        elif case_type == "SA":
            self.asin_entry.configure(state="normal")
            self.asin_na.set(False)
            self.sp_name_var.set("")
            self.sp_name_entry.configure(state="disabled")
            self.sp_name_na.set(True)

    def _on_status_change(self, event=None):
        status = self.case_status_var.get()
        codes = CASE_REASON_CODES.get(status, [])
        self.reason_code_cb.configure(values=codes)
        if status == "Other":
            self.reason_code_var.set(codes[0])
        else:
            self.reason_code_var.set("")

        if status == "Not Approved":
            self.expiry_var.set("")
            self.expiry_na.set(True)
            self.expiry_entry.configure(state="disabled")
            self.not_approved_note.configure(
                text="Expiry Date automatically set to N/A (Case Status = Not Approved)")
        else:
            self.expiry_na.set(False)
            self.expiry_entry.configure(state="normal")
            self.not_approved_note.configure(text="")

    def _validate(self):
        errors = []
        if not self.case_id_var.get().strip():
            errors.append("- No Case ID entered")
        if not self.case_date_var.get().strip():
            errors.append("- No Case Date entered")
        else:
            try:
                parse_iso_date(self.case_date_var.get())
            except ValueError:
                errors.append("- Case Date must be in YYYY-MM-DD format")
        if not self.case_type_var.get():
            errors.append("- No Case Type selected")
        if not self.sp_type_var.get():
            errors.append("- No SP Type selected")
        if not self.sp_id_na.get() and not self.sp_id_var.get().strip():
            errors.append("- No Selling Partner ID / Vendor Code entered")
        if not self.business_model_var.get():
            errors.append("- No Seller Business Model selected")
        if self.case_type_var.get() == "DR" and not self.sp_name_na.get() and not self.sp_name_var.get().strip():
            errors.append("- No SP Name entered (required for DR cases)")
        if self.case_type_var.get() == "SA" and not self.asin_na.get() and not self.asin_var.get().strip():
            errors.append("- No ASIN entered (required for SA cases)")
        if not self.mp_var.get():
            errors.append("- No MP selected")
        if not self.case_status_var.get():
            errors.append("- No Case Status selected")
        if not self.reason_code_var.get() or self.reason_code_var.get() == "Please choose Case Status first":
            errors.append("- No Case Reason Code selected")
        if not self.expiry_na.get() and self.expiry_var.get().strip():
            try:
                parse_iso_date(self.expiry_var.get())
            except ValueError:
                errors.append("- Expiry Date must be in YYYY-MM-DD format")
        return "\n".join(errors) if errors else None

    def _on_upload(self):
        error = self._validate()
        if error:
            messagebox.showerror("Unable to upload", f"Unable to upload due to the following error(s):\n{error}")
            return

        expiry = None if self.expiry_na.get() else parse_iso_date(self.expiry_var.get())

        data = {
            "case_type": self.case_type_var.get(),
            "case_id": self.case_id_var.get().strip(),
            "case_date": parse_iso_date(self.case_date_var.get()).isoformat(),
            "sp_type": self.sp_type_var.get(),
            "sp_identifier": None if self.sp_id_na.get() else self.sp_id_var.get().strip(),
            "sp_identifier_na": int(self.sp_id_na.get()),
            "seller_business_model": self.business_model_var.get(),
            "sp_name": None if self.sp_name_na.get() else (self.sp_name_var.get().strip() or None),
            "sp_name_na": int(self.sp_name_na.get()),
            "asin": None if self.asin_na.get() else (self.asin_var.get().strip() or None),
            "asin_na": int(self.asin_na.get()),
            "marketplace": self.mp_var.get(),
            "case_status": self.case_status_var.get(),
            "case_reason_code": self.reason_code_var.get(),
            "expiry_date": expiry.isoformat() if expiry else None,
            "expiry_na": int(self.expiry_na.get()),
            "notes": None,
        }

        try:
            insert_case(data)
            summary = (
                "Upload successful.\n\n"
                f"Case Type: {data['case_type']}   |   Case ID: {data['case_id']}   |   Case Date: {data['case_date']}\n"
                f"SP Type: {data['sp_type']}   |   Selling Partner ID/Vendor Code: {data['sp_identifier'] or 'N/A'}   |   "
                f"Business Model: {data['seller_business_model']}\n"
                f"SP Name: {data['sp_name'] or 'N/A'}   |   ASIN: {data['asin'] or 'N/A'}   |   MP: {data['marketplace']}\n"
                f"Case Status: {data['case_status']}   |   Reason Code: {data['case_reason_code']}\n"
                f"Expiry Date: {expiry.isoformat() if expiry else 'N/A'}"
            )
            self.status_label.set_success(summary)
        except DBError as e:
            self.status_label.set_error(f"Upload failed.\n{e}")
            messagebox.showerror("Unable to upload", str(e))

    def _clear_form(self):
        self.case_id_var.set("")
        self.case_date_var.set(date.today().isoformat())
        self.case_type_var.set("")
        self.sp_type_var.set("")
        self.sp_id_var.set("")
        self.sp_id_na.set(False)
        self.sp_id_entry.configure(state="normal")
        self.business_model_var.set("")
        self.sp_name_var.set("")
        self.sp_name_na.set(False)
        self.sp_name_entry.configure(state="normal")
        self.asin_var.set("")
        self.asin_na.set(False)
        self.asin_entry.configure(state="normal")
        self.mp_var.set("")
        self.case_status_var.set("")
        self.reason_code_var.set("Please choose Case Status first")
        self.reason_code_cb.configure(values=[])
        self.expiry_var.set("")
        self.expiry_na.set(False)
        self.expiry_entry.configure(state="normal")
        self.not_approved_note.configure(text="")
        self.status_label.clear()



class DataViewFrame(tk.Frame):
    COLUMNS = ("id", "case_type", "case_id", "case_date", "sp_type", "sp_identifier",
               "seller_business_model", "sp_name", "asin", "marketplace",
               "case_status", "case_reason_code", "expiry_date", "cert_status",
               "has_valid_cert_any_row", "uploader")

    HEADERS = {
        "id": "ID", "case_type": "Case Type", "case_id": "Case ID", "case_date": "Case Date",
        "sp_type": "SP Type", "sp_identifier": "Selling Partner", "seller_business_model": "Business Model",
        "sp_name": "SP Name", "asin": "ASIN", "marketplace": "MP", "case_status": "Status",
        "case_reason_code": "Reason Code", "expiry_date": "Expiry Date",
        "cert_status": "Certificate", "has_valid_cert_any_row": "Valid cert. anywhere",
        "uploader": "User",
    }

    def __init__(self, master):
        super().__init__(master, bg=COLORS["page_bg"])
        self.last_rows = []
        self.last_filters = {}
        self._build_scrollable()
        self._build_filters()
        self._build_table()

    def _build_scrollable(self):
        """Scrollable canvas wrapper for small screens."""
        self._canvas = tk.Canvas(self, bg=COLORS["page_bg"], highlightthickness=0)
        self._vsb = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vsb.set)

        self._vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(self._canvas, bg=COLORS["page_bg"])
        self._canvas_win = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")

        self._inner.bind("<Configure>", lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(self._canvas_win, width=e.width))

        def _on_mousewheel(event):
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self._canvas.bind_all("<MouseWheel>", _on_mousewheel, add="+")

    def _build_filters(self):
        card_outer, bar = make_card(self._inner, accent=COLORS["blue"])
        card_outer.pack(fill="x", padx=20, pady=(20, 10))

        ttk.Label(bar, text="Filters", style="Section.TLabel").grid(
            row=0, column=0, columnspan=8, sticky="w", pady=(0, 12))

        ttk.Label(bar, text="Selling Partner:").grid(row=1, column=0, sticky="w")
        self.f_sp = tk.StringVar()
        ttk.Entry(bar, textvariable=self.f_sp, width=16).grid(row=1, column=1, padx=(2, 10), pady=4)

        ttk.Label(bar, text="Case ID:").grid(row=1, column=2, sticky="w")
        self.f_case_id = tk.StringVar()
        ttk.Entry(bar, textvariable=self.f_case_id, width=14).grid(row=1, column=3, padx=(2, 10))

        ttk.Label(bar, text="ASIN:").grid(row=1, column=4, sticky="w")
        self.f_asin = tk.StringVar()
        ttk.Entry(bar, textvariable=self.f_asin, width=14).grid(row=1, column=5, padx=(2, 10))

        ttk.Label(bar, text="Case Type:").grid(row=1, column=6, sticky="w")
        self.f_case_type = tk.StringVar(value="All")
        ttk.Combobox(bar, textvariable=self.f_case_type, values=["All"] + CASE_TYPES,
                     state="readonly", width=10).grid(row=1, column=7, padx=(2, 0))

        ttk.Label(bar, text="SP Type:").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.f_sp_type = tk.StringVar(value="All")
        ttk.Combobox(bar, textvariable=self.f_sp_type, values=["All"] + SP_TYPES_VIEW,
                     state="readonly", width=13).grid(row=2, column=1, pady=(8, 0))

        ttk.Label(bar, text="MP:").grid(row=2, column=2, sticky="w", pady=(8, 0))
        self.f_mp = tk.StringVar(value="All")
        ttk.Combobox(bar, textvariable=self.f_mp, values=["All"] + MARKETPLACES,
                     state="readonly", width=13).grid(row=2, column=3, pady=(8, 0))

        ttk.Label(bar, text="Certificate:").grid(row=2, column=4, sticky="w", pady=(8, 0))
        self.f_cert_status = tk.StringVar(value="All")
        ttk.Combobox(bar, textvariable=self.f_cert_status, values=["All", "Valid", "Expired", "N/A"],
                     state="readonly", width=13).grid(row=2, column=5, pady=(8, 0))

        ttk.Label(bar, text="Case Status:").grid(row=3, column=0, sticky="nw", pady=(10, 0))
        status_frame = ttk.Frame(bar)
        status_frame.grid(row=3, column=1, columnspan=5, sticky="w", pady=(10, 0))
        self.status_vars = {}
        for i, status in enumerate(CASE_STATUSES):
            v = tk.BooleanVar()
            self.status_vars[status] = v
            ttk.Checkbutton(status_frame, text=status, variable=v,
                             command=self._refresh_reason_codes).grid(row=0, column=i, padx=(0, 12))

        ttk.Label(bar, text="Reason Code:").grid(row=4, column=0, sticky="nw", pady=(8, 0))
        self.reason_frame = ttk.Frame(bar)
        self.reason_frame.grid(row=4, column=1, columnspan=7, sticky="w", pady=(8, 0))
        self.reason_vars = {}

        ttk.Label(bar, text="Expiry date - custom interval:").grid(row=5, column=0, sticky="w", pady=(10, 0))
        self.f_date_from = tk.StringVar()
        ttk.Entry(bar, textvariable=self.f_date_from, width=11).grid(row=5, column=1, pady=(10, 0))
        attach_calendar_button(bar, self.f_date_from, 5, 2)
        ttk.Label(bar, text="\u2013").grid(row=5, column=3, pady=(10, 0))
        self.f_date_to = tk.StringVar()
        ttk.Entry(bar, textvariable=self.f_date_to, width=11).grid(row=5, column=4, sticky="w", pady=(10, 0))
        attach_calendar_button(bar, self.f_date_to, 5, 5)

        ttk.Label(bar, text="Case date - custom interval:").grid(row=6, column=0, sticky="w", pady=(10, 0))
        self.f_case_date_from = tk.StringVar()
        ttk.Entry(bar, textvariable=self.f_case_date_from, width=11).grid(row=6, column=1, pady=(10, 0))
        attach_calendar_button(bar, self.f_case_date_from, 6, 2)
        ttk.Label(bar, text="\u2013").grid(row=6, column=3, pady=(10, 0))
        self.f_case_date_to = tk.StringVar()
        ttk.Entry(bar, textvariable=self.f_case_date_to, width=11).grid(row=6, column=4, sticky="w", pady=(10, 0))
        attach_calendar_button(bar, self.f_case_date_to, 6, 5)
        ttk.Label(bar, text="(date the case was worked)", style="Hint.TLabel").grid(
            row=6, column=6, columnspan=2, sticky="w", padx=(10, 0), pady=(10, 0))

        ttk.Label(bar, text="Display mode:").grid(row=7, column=0, sticky="w", pady=(14, 0))
        self.historical_var = tk.BooleanVar(value=True)
        mode_frame = ttk.Frame(bar)
        mode_frame.grid(row=7, column=1, columnspan=5, sticky="w", pady=(14, 0))
        ttk.Radiobutton(mode_frame, text="Historical Data (all rows)",
                         variable=self.historical_var, value=True).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(mode_frame, text="Only Latest Certificate (per Selling Partner)",
                         variable=self.historical_var, value=False).grid(row=0, column=1, sticky="w", padx=(16, 0))

        btn_row = ttk.Frame(bar)
        btn_row.grid(row=8, column=0, columnspan=8, sticky="w", pady=(16, 0))
        ttk.Button(btn_row, text="Search", style="Primary.TButton", command=self._on_search).pack(side="left")
        ttk.Button(btn_row, text="Export Excel", style="Secondary.TButton", command=self._on_export).pack(
            side="left", padx=(10, 0))
        ttk.Button(btn_row, text="Reset filters", style="Secondary.TButton", command=self._reset_filters).pack(
            side="left", padx=(10, 0))

        self.results_hint = ttk.Label(bar, text="", style="Hint.TLabel")
        self.results_hint.grid(row=9, column=0, columnspan=8, sticky="w", pady=(10, 0))

    def _refresh_reason_codes(self):
        for w in self.reason_frame.winfo_children():
            w.destroy()
        self.reason_vars.clear()

        active_statuses = [s for s, v in self.status_vars.items() if v.get()]
        codes = []
        for s in active_statuses:
            codes.extend(CASE_REASON_CODES.get(s, []))
        seen = set()
        codes = [c for c in codes if not (c in seen or seen.add(c))]

        for i, code in enumerate(codes):
            v = tk.BooleanVar()
            self.reason_vars[code] = v
            ttk.Checkbutton(self.reason_frame, text=code, variable=v).grid(
                row=i // 2, column=i % 2, sticky="w", padx=(0, 16), pady=1)

    def _build_table(self):
        card_outer, card = make_card(self._inner, accent=COLORS["green_light"])
        card_outer.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        container = ttk.Frame(card)
        container.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(container, columns=self.COLUMNS, show="headings", height=13)
        for col in self.COLUMNS:
            self.tree.heading(col, text=self.HEADERS[col])
            self.tree.column(col, width=95, anchor="w")
        self.tree.tag_configure("odd", background=COLORS["green_tint"])
        self.tree.tag_configure("even", background="white")

        vsb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self._ctx_menu = tk.Menu(self.tree, tearoff=0)
        self._ctx_menu.add_command(label="\U0001F4CB  Copy row (all columns)", command=self._copy_row)
        self._ctx_menu.add_command(label="\U0001F4CB  Copy cell value", command=self._copy_cell)
        self._ctx_menu.add_separator()
        self._ctx_menu.add_command(label="\U0001F4CB  Copy all visible rows", command=self._copy_all_rows)

        self.tree.bind("<Button-3>", self._show_ctx_menu)   # right-click on Windows
        self.tree.bind("<Double-1>", self._on_double_click)  # double-click copies cell

        self._toast = None

    def _show_ctx_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self._click_col = self.tree.identify_column(event.x)
            self._ctx_menu.tk_popup(event.x_root, event.y_root)

    def _copy_row(self):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        header_line = "\t".join(self.HEADERS[c] for c in self.COLUMNS)
        data_line = "\t".join(str(v) for v in values)
        text = f"{header_line}\n{data_line}"
        self.clipboard_clear()
        self.clipboard_append(text)
        self._show_toast("Row copied to clipboard!")

    def _copy_cell(self):
        sel = self.tree.selection()
        if not sel or not hasattr(self, "_click_col"):
            return
        col_idx = int(self._click_col.replace("#", "")) - 1
        values = self.tree.item(sel[0], "values")
        if 0 <= col_idx < len(values):
            self.clipboard_clear()
            self.clipboard_append(str(values[col_idx]))
            col_name = self.COLUMNS[col_idx] if col_idx < len(self.COLUMNS) else "?"
            self._show_toast(f"Copied: {values[col_idx]}")

    def _copy_all_rows(self):
        children = self.tree.get_children()
        if not children:
            return
        lines = ["\t".join(self.HEADERS[c] for c in self.COLUMNS)]
        for child in children:
            values = self.tree.item(child, "values")
            lines.append("\t".join(str(v) for v in values))
        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))
        self._show_toast(f"All {len(children)} row(s) copied!")

    def _on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if item and col:
            col_idx = int(col.replace("#", "")) - 1
            values = self.tree.item(item, "values")
            if 0 <= col_idx < len(values):
                self.clipboard_clear()
                self.clipboard_append(str(values[col_idx]))
                self._show_toast(f"Copied: {values[col_idx]}")

    def _show_toast(self, msg):
    
        if self._toast is not None:
            self._toast.destroy()
        self._toast = tk.Label(self, text=f"  \u2714 {msg}  ", bg=COLORS["success_bg"],
                                fg=COLORS["success_fg"], font=("Segoe UI", 9),
                                relief="solid", bd=1, padx=8, pady=4)
        self._toast.place(relx=0.5, rely=0.95, anchor="center")
        self.after(1800, lambda: self._toast.destroy() if self._toast else None)

    def _collect_filters(self):
        filters = {"historical": self.historical_var.get()}

        if self.f_sp.get().strip():
            filters["sp_identifier"] = self.f_sp.get().strip()
        if self.f_case_id.get().strip():
            filters["case_id"] = self.f_case_id.get().strip()
        if self.f_asin.get().strip():
            filters["asin"] = self.f_asin.get().strip()
        if self.f_case_type.get() != "All":
            filters["case_type"] = self.f_case_type.get()
        if self.f_sp_type.get() != "All":
            filters["sp_type"] = self.f_sp_type.get()
        if self.f_mp.get() != "All":
            filters["marketplace"] = self.f_mp.get()
        if self.f_cert_status.get() != "All":
            filters["cert_status"] = self.f_cert_status.get()

        selected_status = [k for k, v in self.status_vars.items() if v.get()]
        if selected_status:
            filters["case_statuses"] = selected_status
        selected_reasons = [k for k, v in self.reason_vars.items() if v.get()]
        if selected_reasons:
            filters["reason_codes"] = selected_reasons

        if self.f_date_from.get().strip():
            filters["exp_date_from"] = parse_iso_date(self.f_date_from.get())
        if self.f_date_to.get().strip():
            filters["exp_date_to"] = parse_iso_date(self.f_date_to.get())

        if self.f_case_date_from.get().strip():
            filters["case_date_from"] = parse_iso_date(self.f_case_date_from.get())
        if self.f_case_date_to.get().strip():
            filters["case_date_to"] = parse_iso_date(self.f_case_date_to.get())

        return filters

    def _on_search(self):
        try:
            filters = self._collect_filters()
        except ValueError:
            messagebox.showerror("Invalid filter", "Please check the date format (YYYY-MM-DD).")
            return

        try:
            rows = fetch_cases(filters)
        except DBError as e:
            messagebox.showerror("Database error", str(e))
            return

        self.last_filters = filters
        self.last_rows = rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not rows:
            self.results_hint.configure(text="")
            messagebox.showinfo("No results", "No data found for selected criteria")
            return

        for i, r in enumerate(rows):
            values = [r.get(c, "") for c in self.COLUMNS]
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=values, tags=(tag,))

        if len(rows) >= DEFAULT_SEARCH_LIMIT:
            self.results_hint.configure(
                text=f"Showing the first {DEFAULT_SEARCH_LIMIT} matching rows on screen. "
                     f"Use \u201cExport Excel\u201d to get the complete matching set, however large.")
        else:
            self.results_hint.configure(text=f"{len(rows)} row(s) found.")

    def _on_export(self):
        if not self.last_rows:
            messagebox.showwarning("Nothing to export", "Run a search first.")
            return

        default_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Selor")
        os.makedirs(default_dir, exist_ok=True)
        default_name = f"Selor Export - {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

        path = filedialog.asksaveasfilename(
            initialdir=default_dir, initialfile=default_name,
            defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")],
        )
        if not path:
            return

        try:
            export_rows = fetch_cases(self.last_filters, limit=None)
        except DBError as e:
            messagebox.showerror("Database error", str(e))
            return

        try:
            export_to_excel(export_rows, path)
            messagebox.showinfo(
                "Export successful",
                f"Excel Export completed successfully!\n{len(export_rows)} row(s) exported.\nLocation: {path}")
        except Exception as e:
            messagebox.showerror("Export error", str(e))

    def _reset_filters(self):
        for var in (self.f_sp, self.f_case_id, self.f_asin, self.f_date_from, self.f_date_to,
                    self.f_case_date_from, self.f_case_date_to):
            var.set("")
        self.f_case_type.set("All")
        self.f_sp_type.set("All")
        self.f_mp.set("All")
        self.f_cert_status.set("All")
        for v in self.status_vars.values():
            v.set(False)
        self._refresh_reason_codes()
        self.historical_var.set(True)
        self.results_hint.configure(text="")



class HeaderBar(tk.Canvas):
    HEIGHT = 92

    def __init__(self, master, theme: Theme):
        super().__init__(master, height=self.HEIGHT, highlightthickness=0, bd=0)
        self.theme = theme
        self._logo_img = None
        self._load_logo()
        self.bind("<Configure>", self._redraw)

    def _load_logo(self):
        try:
            img = tk.PhotoImage(file=resource_path("assets", "logo.png"))
            # Original is 500x500; shrink to roughly fit the header height.
            factor = max(1, img.width() // 64)
            self._logo_img = img.subsample(factor, factor)
        except Exception:
            self._logo_img = None

    @staticmethod
    def _lerp_color(c1, c2, t):
        c1 = c1.lstrip("#")
        c2 = c2.lstrip("#")
        r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
        r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
        r = round(r1 + (r2 - r1) * t)
        g = round(g1 + (g2 - g1) * t)
        b = round(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _redraw(self, event=None):
        self.delete("all")
        width = self.winfo_width()
        if width <= 1:
            width = 1150

        step = 3
        for x in range(0, width, step):
            t = x / max(width, 1)
            color = self._lerp_color(COLORS["header_from"], COLORS["header_to"], t)
            self.create_rectangle(x, 0, x + step, self.HEIGHT, fill=color, outline=color)

        y_center = self.HEIGHT // 2
        if self._logo_img is not None:
            self.create_image(28, y_center, image=self._logo_img, anchor="w")
            text_x = 28 + self._logo_img.width() + 14
        else:
            text_x = 28

        self.create_text(text_x, y_center - 12, text="SELOR", anchor="w",
                          font=self.theme.font_title, fill="white")
        self.create_text(text_x, y_center + 14, text="Compliance case tracker",
                          anchor="w", font=self.theme.font_subtitle, fill="#EAF5EA")



class SelorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1150x820")
        self.minsize(900, 600)
        self.configure(bg=COLORS["page_bg"])

        theme = Theme(self)

        try:
            icon_img = tk.PhotoImage(file=resource_path("assets", "logo.png"))
            self.iconphoto(True, icon_img)
            self._icon_ref = icon_img  # keep a reference
        except Exception:
            pass

        header = HeaderBar(self, theme)
        header.pack(fill="x", side="top")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        entry_tab = DataEntryFrame(notebook)
        view_tab = DataViewFrame(notebook)

        notebook.add(entry_tab, text="Data Entry")
        notebook.add(view_tab, text="Data View")


if __name__ == "__main__":
    app = SelorApp()
    app.mainloop()
