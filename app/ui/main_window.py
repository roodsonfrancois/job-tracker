"""Main CustomTkinter dashboard."""

from __future__ import annotations

import logging
import sqlite3
import webbrowser
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from app.config import APP_VERSION, DISPLAY_NAME, get_app_data_dir
from app.models import ALLOWED_STATUSES
from app.services.application_service import ApplicationService
from app.services.file_service import FileService
from app.services.url_service import validate_job_url
from app.ui.application_dialog import ApplicationDialog
from app.ui.help_window import HelpWindow

LOGGER = logging.getLogger(__name__)


class MainWindow(ctk.CTk):
    COLUMNS = (
        ("company", "Company"), ("position", "Position"), ("location", "Location"),
        ("status", "Status"), ("date_applied", "Date Applied"),
        ("follow_up_date", "Follow-up"),
    )

    def __init__(self, service: ApplicationService) -> None:
        super().__init__()
        self.service = service
        self.files = FileService(service.repository)
        self.selected_id: int | None = None
        self.sort_by = "created_at"
        self.sort_descending = True
        self.help_window: HelpWindow | None = None
        self.title(DISPLAY_NAME)
        self.geometry("1180x760")
        self.minsize(900, 600)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self._build_header()
        self._build_summary()
        self._build_controls()
        self._build_content()
        self.bind("<Delete>", lambda _event: self._delete_selected())
        self.refresh()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=28, pady=(22, 12), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header, text=DISPLAY_NAME, font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.grid(row=0, column=1, sticky="e")
        for text, command in (
            ("Export All CSV", self._export_csv), ("Create Backup", self._create_backup),
            ("Restore Backup", self._restore_backup), ("Help", self._show_help),
            ("About", self._show_about),
        ):
            ctk.CTkButton(actions, text=text, width=105, command=command).pack(
                side="left", padx=(0, 7)
            )
        ctk.CTkButton(
            actions, text="+ Add Application", width=150, command=self._open_add
        ).pack(side="left")

    def _build_summary(self) -> None:
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, padx=28, pady=(0, 12), sticky="ew")
        self.summary_labels: dict[str, ctk.CTkLabel] = {}
        for column, name in enumerate(("Total", "Applied", "Interviews", "Offers")):
            frame.grid_columnconfigure(column, weight=1)
            value = ctk.CTkLabel(
                frame, text="0", font=ctk.CTkFont(size=22, weight="bold")
            )
            value.grid(row=0, column=column, padx=8, pady=(9, 0))
            ctk.CTkLabel(frame, text=name, text_color=("gray35", "gray70")).grid(
                row=1, column=column, padx=8, pady=(0, 9)
            )
            self.summary_labels[name] = value

    def _build_controls(self) -> None:
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=2, column=0, padx=28, pady=(0, 12), sticky="ew")
        controls.grid_columnconfigure(0, weight=1)
        self.search_entry = ctk.CTkEntry(
            controls, placeholder_text="Search company, position, or location", height=38
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 12), sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda _event: self.refresh())
        self.status_filter = ctk.CTkOptionMenu(
            controls, values=["All", *ALLOWED_STATUSES], width=155, height=38,
            command=lambda _value: self.refresh(),
        )
        self.status_filter.set("All")
        self.status_filter.grid(row=0, column=1)

    def _build_content(self) -> None:
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=3, column=0, padx=28, pady=(0, 22), sticky="nsew")
        content.grid_columnconfigure(0, weight=7)
        content.grid_columnconfigure(1, weight=3)
        content.grid_rowconfigure(0, weight=1)
        table = ctk.CTkFrame(content)
        table.grid(row=0, column=0, padx=(0, 12), sticky="nsew")
        table.grid_columnconfigure(0, weight=1)
        table.grid_rowconfigure(1, weight=1)
        self.table_header = ctk.CTkFrame(table, fg_color=("gray80", "gray25"))
        self.table_header.grid(row=0, column=0, padx=8, pady=(8, 0), sticky="ew")
        for index, (key, title) in enumerate(self.COLUMNS):
            self.table_header.grid_columnconfigure(index, weight=1)
            ctk.CTkButton(
                self.table_header, text=title, anchor="w", fg_color="transparent",
                hover_color=("gray72", "gray32"),
                command=lambda field=key: self._sort(field),
            ).grid(row=0, column=index, padx=2, pady=3, sticky="ew")
        self.application_area = ctk.CTkScrollableFrame(table)
        self.application_area.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        self.application_area.grid_columnconfigure(0, weight=1)

        details = ctk.CTkFrame(content)
        details.grid(row=0, column=1, sticky="nsew")
        details.grid_columnconfigure(0, weight=1)
        details.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(
            details, text="Application Details", font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")
        self.details_label = ctk.CTkLabel(
            details, text="Select a row to view its details.", anchor="nw",
            justify="left", wraplength=300,
        )
        self.details_label.grid(row=1, column=0, padx=16, pady=8, sticky="nsew")
        self.open_url_button = ctk.CTkButton(
            details, text="Open Job Posting", command=self._open_job_url, state="disabled"
        )
        self.open_url_button.grid(row=2, column=0, padx=16, pady=(8, 4), sticky="ew")
        row = ctk.CTkFrame(details, fg_color="transparent")
        row.grid(row=3, column=0, padx=16, pady=(4, 16), sticky="ew")
        row.grid_columnconfigure((0, 1), weight=1)
        self.edit_button = ctk.CTkButton(row, text="Edit", command=self._open_edit, state="disabled")
        self.edit_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.delete_button = ctk.CTkButton(
            row, text="Delete", command=self._delete_selected, state="disabled", fg_color="#b33a3a"
        )
        self.delete_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def refresh(self) -> None:
        for widget in self.application_area.winfo_children():
            widget.destroy()
        status = self.status_filter.get()
        try:
            applications = self.service.list_applications(
                query=self.search_entry.get(), status=None if status == "All" else status,
                sort_by=self.sort_by, descending=self.sort_descending,
            )
            summary = self.service.get_summary()
        except (sqlite3.Error, ValueError):
            LOGGER.exception("Unable to refresh applications")
            messagebox.showerror("Database Error", "Job applications could not be loaded.", parent=self)
            return
        if not applications:
            ctk.CTkLabel(self.application_area, text="No matching applications.").grid(
                row=0, column=0, pady=45
            )
        for row_number, application in enumerate(applications):
            self._add_table_row(row_number, application)
        for name, count in summary.items():
            self.summary_labels[name].configure(text=str(count))
        if self.selected_id is not None:
            self._select(self.selected_id)

    def _add_table_row(self, row_number: int, application) -> None:
        follow_up = application["follow_up_date"] or "—"
        color = ("gray88", "gray22")
        if application["follow_up_date"]:
            try:
                follow_date = date.fromisoformat(application["follow_up_date"])
                if follow_date < date.today():
                    color = ("#f3d1d1", "#542b2b")
                elif follow_date == date.today():
                    color = ("#f5e7ba", "#55491f")
            except ValueError:
                LOGGER.warning("Application %s has an invalid follow-up date", application["id"])
        values = (
            application["company"], application["position"], application["location"] or "—",
            application["status"], application["date_applied"] or "—", follow_up,
        )
        row = ctk.CTkFrame(self.application_area, fg_color=color)
        row.grid(row=row_number, column=0, pady=2, sticky="ew")
        for column, value in enumerate(values):
            row.grid_columnconfigure(column, weight=1)
            label = ctk.CTkLabel(row, text=value, anchor="w", cursor="hand2")
            label.grid(row=0, column=column, padx=6, pady=7, sticky="ew")
            label.bind("<Button-1>", lambda _e, app_id=application["id"]: self._select(app_id))
            label.bind("<Double-Button-1>", lambda _e, app_id=application["id"]: self._edit_id(app_id))

    def _sort(self, field: str) -> None:
        if self.sort_by == field:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_by, self.sort_descending = field, False
        self.refresh()

    def _select(self, application_id: int) -> None:
        try:
            application = self.service.get_application(application_id)
        except sqlite3.Error:
            LOGGER.exception("Unable to load application %s", application_id)
            messagebox.showerror("Database Error", "The application could not be loaded.", parent=self)
            return
        if application is None:
            self._clear_selection()
            return
        self.selected_id = application_id
        self.edit_button.configure(state="normal")
        self.delete_button.configure(state="normal")
        self.open_url_button.configure(state="normal" if application["job_url"] else "disabled")
        self.details_label.configure(text=(
            f"Company: {application['company']}\n\nPosition: {application['position']}\n\n"
            f"Location: {application['location'] or '—'}\n\nStatus: {application['status']}\n\n"
            f"Date Applied: {application['date_applied'] or '—'}\n\n"
            f"Follow-up: {application['follow_up_date'] or '—'}\n\n"
            f"Job URL: {application['job_url'] or '—'}\n\nNotes:\n{application['notes'] or '—'}"
        ))

    def _clear_selection(self) -> None:
        self.selected_id = None
        self.details_label.configure(text="Select a row to view its details.")
        for button in (self.edit_button, self.delete_button, self.open_url_button):
            button.configure(state="disabled")

    def _open_add(self) -> None:
        ApplicationDialog(self, title="Add Application", on_save=self._create)

    def _edit_id(self, application_id: int) -> None:
        self._select(application_id)
        self._open_edit()

    def _open_edit(self) -> None:
        if self.selected_id is None:
            messagebox.showinfo("Select Application", "Select an application to edit.", parent=self)
            return
        try:
            application = self.service.get_application(self.selected_id)
        except sqlite3.Error:
            LOGGER.exception("Unable to load application %s", self.selected_id)
            messagebox.showerror("Database Error", "The application could not be loaded.", parent=self)
            return
        if application is None:
            self._clear_selection()
            return
        ApplicationDialog(
            self, title="Edit Application", application=application,
            on_save=lambda values: self._update(self.selected_id, values),
        )

    def _create(self, values: dict[str, str]) -> bool:
        try:
            self.selected_id = self.service.create_application(**values)
            self.refresh()
            return True
        except ValueError as error:
            messagebox.showerror("Invalid Application", str(error), parent=self)
        except sqlite3.Error:
            LOGGER.exception("Unable to create application")
            messagebox.showerror("Database Error", "The application could not be saved.", parent=self)
        return False

    def _update(self, application_id: int | None, values: dict[str, str]) -> bool:
        if application_id is None:
            return False
        try:
            if not self.service.update_application(application_id, **values):
                messagebox.showerror("Not Found", "The application no longer exists.", parent=self)
                return False
            self.refresh()
            return True
        except ValueError as error:
            messagebox.showerror("Invalid Application", str(error), parent=self)
        except sqlite3.Error:
            LOGGER.exception("Unable to update application %s", application_id)
            messagebox.showerror("Database Error", "The application could not be updated.", parent=self)
        return False

    def _delete_selected(self) -> None:
        if self.selected_id is None:
            return
        try:
            application = self.service.get_application(self.selected_id)
        except sqlite3.Error:
            LOGGER.exception("Unable to load application %s", self.selected_id)
            messagebox.showerror("Database Error", "The application could not be loaded.", parent=self)
            return
        if application is None or not messagebox.askyesno(
            "Delete Application",
            f"Delete {application['company']} — {application['position']}?\n\nThis cannot be undone.",
            parent=self,
        ):
            return
        try:
            self.service.delete_application(self.selected_id)
            self._clear_selection()
            self.refresh()
        except sqlite3.Error:
            LOGGER.exception("Unable to delete application %s", self.selected_id)
            messagebox.showerror("Database Error", "The application could not be deleted.", parent=self)

    def _open_job_url(self) -> None:
        try:
            application = self.service.get_application(self.selected_id) if self.selected_id else None
            url = validate_job_url(application["job_url"] if application else "")
            if not webbrowser.open(url):
                raise RuntimeError
        except ValueError as error:
            messagebox.showerror("Invalid Job URL", str(error), parent=self)
        except (sqlite3.Error, RuntimeError):
            LOGGER.exception("Unable to open job URL")
            messagebox.showerror("Open Job Posting", "The job posting could not be opened.", parent=self)

    def _export_csv(self) -> None:
        destination = filedialog.asksaveasfilename(
            parent=self, title="Export All Applications", defaultextension=".csv",
            filetypes=(("CSV files", "*.csv"),), initialfile="job_applications.csv",
        )
        if not destination:
            return
        try:
            count = self.files.export_csv(destination)
            if count == 0:
                messagebox.showinfo("Export CSV", "There are no applications to export.", parent=self)
            else:
                messagebox.showinfo("Export Complete", f"Exported {count} applications.", parent=self)
        except (OSError, sqlite3.Error):
            LOGGER.exception("CSV export failed")
            messagebox.showerror("Export Failed", "Applications could not be exported.", parent=self)

    def _create_backup(self) -> None:
        destination = filedialog.asksaveasfilename(
            parent=self, title="Create Backup", defaultextension=".db",
            filetypes=(("SQLite database", "*.db"),),
            initialfile=self.files.default_backup_name(),
        )
        if not destination:
            return
        try:
            self.files.create_backup(destination)
            messagebox.showinfo("Backup Complete", "The database backup was created.", parent=self)
        except (OSError, sqlite3.Error):
            LOGGER.exception("Database backup failed")
            messagebox.showerror("Backup Failed", "The database backup could not be created.", parent=self)

    def _restore_backup(self) -> None:
        source = filedialog.askopenfilename(
            parent=self, title="Restore Backup", filetypes=(("SQLite database", "*.db"),)
        )
        if not source:
            return
        try:
            self.files.validate_backup(source)
        except ValueError as error:
            messagebox.showerror("Invalid Backup", str(error), parent=self)
            return
        if not messagebox.askyesno(
            "Restore Backup", "Replace all current applications with this backup?\n\n"
            "A safety backup of the current database will be created first.", parent=self,
        ):
            return
        try:
            safety = self.files.restore_backup(source, get_app_data_dir())
            self._clear_selection()
            self.refresh()
            messagebox.showinfo(
                "Restore Complete", f"The backup was restored.\n\nSafety backup: {safety.name}", parent=self
            )
        except (OSError, sqlite3.Error, ValueError):
            LOGGER.exception("Database restore failed")
            messagebox.showerror(
                "Restore Failed", "The backup could not be restored. Current data was preserved when possible.",
                parent=self,
            )

    def _show_about(self) -> None:
        messagebox.showinfo(
            "About Job Tracker",
            f"Job Tracker\nVersion {APP_VERSION}\n\nSimple local desktop job application tracker",
            parent=self,
        )

    def _show_help(self) -> None:
        if self.help_window is not None and self.help_window.winfo_exists():
            self.help_window.lift()
            self.help_window.focus_set()
            return
        self.help_window = HelpWindow(self)
