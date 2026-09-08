"""Reusable create/edit form for a job application."""

from __future__ import annotations

from collections.abc import Callable, Mapping
import tkinter as tk

import customtkinter as ctk

from app.models import ALLOWED_STATUSES, ApplicationStatus


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
        for key, label in (
            ("date_applied", "Date Applied (YYYY-MM-DD)"),
            ("follow_up_date", "Follow-up Date (YYYY-MM-DD)"),
        ):
            row = self._add_entry(form, row, key, label)
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
