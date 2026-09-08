"""Reusable create/edit form for a job application."""

from __future__ import annotations

from collections.abc import Callable, Mapping
import tkinter as tk

import customtkinter as ctk

from app.models import ALLOWED_STATUSES, ApplicationStatus
from app.ui.calendar_dialog import CalendarDialog


class ApplicationDialog(ctk.CTkToplevel):
    def __init__(self, parent, *, title: str, on_save: Callable[[dict[str, str]], bool],
                 application: Mapping[str, object] | None = None) -> None:
        super().__init__(parent)
        self.title(title)
        self.geometry("590x650")
        self.minsize(500, 560)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._on_save = on_save
        self._application = application
        self._entries: dict[str, ctk.CTkEntry] = {}

        form = ctk.CTkScrollableFrame(self)
        form.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        form.grid_columnconfigure(0, weight=1)
        fields = (
            ("company", "Company *"), ("position", "Position *"),
            ("location", "Location"), ("job_url", "Job URL"),
        )
        row = 0
        for key, label in fields:
            row = self._add_entry(form, row, key, label)
        ctk.CTkLabel(form, text="Status *", anchor="w").grid(
            row=row, column=0, pady=(10, 3), sticky="ew"
        )
        self.status = ctk.CTkOptionMenu(form, values=list(ALLOWED_STATUSES))
        self.status.grid(row=row + 1, column=0, sticky="ew")
        row += 2
        row = self._add_date_entry(
            form, row, "date_applied", "Date Applied",
            "When you submitted the application. Optional; use YYYY-MM-DD.",
        )
        row = self._add_date_entry(
            form, row, "follow_up_date", "Follow-up Date",
            "When you plan to contact the employer. Optional; no automatic notification.",
            allow_clear=True,
        )
        ctk.CTkLabel(form, text="Notes", anchor="w").grid(
            row=row, column=0, pady=(10, 3), sticky="ew"
        )
        self.notes = ctk.CTkTextbox(form, height=130)
        self.notes.grid(row=row + 1, column=0, sticky="ew")

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="e")
        ctk.CTkButton(buttons, text="Cancel", fg_color="gray45", command=self._close).pack(
            side="left", padx=(0, 8)
        )
        ctk.CTkButton(buttons, text="Save", command=self._save).pack(side="left")
        self._populate()
        self.bind("<Escape>", lambda _event: self._close())
        self.bind("<Control-Return>", lambda _event: self._save())
        self._activate_modal()

    def _activate_modal(self) -> None:
        """Map the window before taking the application-local modal grab."""
        try:
            self.wait_visibility()
            self.lift()
            self.grab_set()
            self._entries["company"].focus_set()
        except tk.TclError:
            self._close()
            raise

    def _close(self) -> None:
        """Release this dialog's grab, if any, and destroy it safely."""
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

    def _add_entry(self, parent, row: int, key: str, label: str) -> int:
        ctk.CTkLabel(parent, text=label, anchor="w").grid(
            row=row, column=0, pady=(10, 3), sticky="ew"
        )
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row + 1, column=0, sticky="ew")
        entry.bind("<Return>", lambda _event: self._save())
        self._entries[key] = entry
        return row + 2

    def _add_date_entry(self, parent, row: int, key: str, label: str,
                        explanation: str, *, allow_clear: bool = False) -> int:
        ctk.CTkLabel(parent, text=label, anchor="w").grid(
            row=row, column=0, pady=(10, 1), sticky="ew"
        )
        ctk.CTkLabel(
            parent, text=explanation, anchor="w", text_color=("gray40", "gray70")
        ).grid(row=row + 1, column=0, pady=(0, 3), sticky="ew")
        controls = ctk.CTkFrame(parent, fg_color="transparent")
        controls.grid(row=row + 2, column=0, sticky="ew")
        controls.grid_columnconfigure(0, weight=1)
        entry = ctk.CTkEntry(controls, placeholder_text="YYYY-MM-DD")
        entry.grid(row=0, column=0, padx=(0, 7), sticky="ew")
        entry.bind("<Return>", lambda _event: self._save())
        self._entries[key] = entry
        ctk.CTkButton(
            controls, text="Calendar", width=86,
            command=lambda: CalendarDialog(
                self, title=f"Select {label}", initial_value=entry.get(),
                on_select=lambda value: self._replace_entry(entry, value),
            ),
        ).grid(row=0, column=1, padx=(0, 7) if allow_clear else 0)
        if allow_clear:
            ctk.CTkButton(
                controls, text="Clear", width=58, fg_color="gray45",
                command=lambda: self._replace_entry(entry, ""),
            ).grid(row=0, column=2)
        return row + 3

    @staticmethod
    def _replace_entry(entry: ctk.CTkEntry, value: str) -> None:
        entry.delete(0, "end")
        entry.insert(0, value)

    def _populate(self) -> None:
        if self._application is None:
            self.status.set(ApplicationStatus.SAVED.value)
            return
        for key, entry in self._entries.items():
            value = self._application[key]
            if value is not None:
                entry.insert(0, str(value))
        self.status.set(str(self._application["status"]))
        if self._application["notes"]:
            self.notes.insert("1.0", str(self._application["notes"]))

    def _save(self) -> None:
        values = {key: entry.get() for key, entry in self._entries.items()}
        values["status"] = self.status.get()
        values["notes"] = self.notes.get("1.0", "end")
        if self._on_save(values):
            self._close()
