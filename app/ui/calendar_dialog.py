"""Reusable Tk-native calendar picker."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from datetime import date

import customtkinter as ctk
from tkcalendar import Calendar


def format_selected_date(selected: date) -> str:
    """Format calendar selections using the application's existing ISO format."""
    return selected.isoformat()


def initial_calendar_date(value: str, today: date | None = None) -> date:
    """Use an existing valid ISO date, otherwise default to today."""
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return today or date.today()


class CalendarDialog(ctk.CTkToplevel):
    """Small modal calendar that safely hands the grab back to its parent."""

    def __init__(self, parent, *, title: str, initial_value: str,
                 on_select: Callable[[str], None]) -> None:
        super().__init__(parent)
        self._parent = parent
        self._on_select = on_select
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._close)

        selected = initial_calendar_date(initial_value)
        self.calendar = Calendar(
            self, selectmode="day", year=selected.year, month=selected.month,
            day=selected.day, date_pattern="yyyy-mm-dd",
        )
        self.calendar.grid(row=0, column=0, columnspan=2, padx=16, pady=16)
        ctk.CTkButton(self, text="Cancel", fg_color="gray45", command=self._close).grid(
            row=1, column=0, padx=(16, 6), pady=(0, 16), sticky="ew"
        )
        ctk.CTkButton(self, text="Use Date", command=self._select).grid(
            row=1, column=1, padx=(6, 16), pady=(0, 16), sticky="ew"
        )
        self.bind("<Escape>", lambda _event: self._close())
        self.bind("<Return>", lambda _event: self._select())
        self._activate_modal()

    def _activate_modal(self) -> None:
        try:
            self.wait_visibility()
            self.lift()
            self.grab_set()
            self.calendar.focus_set()
        except tk.TclError:
            self._close()
            raise

    def _select(self) -> None:
        selected = self.calendar.selection_get()
        self._on_select(format_selected_date(selected))
        self._close()

    def _close(self) -> None:
        try:
            if self.grab_current() is self:
                self.grab_release()
        except tk.TclError:
            pass
        finally:
            try:
                self.destroy()
            except tk.TclError:
                pass
        try:
            if self._parent.winfo_exists() and self._parent.winfo_viewable():
                self._parent.grab_set()
                self._parent.lift()
        except tk.TclError:
            pass
