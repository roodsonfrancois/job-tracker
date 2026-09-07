"""Main CustomTkinter application window."""

from __future__ import annotations

import sqlite3
from tkinter import messagebox

import customtkinter as ctk

from app.models import ALLOWED_STATUSES
from app.services.application_service import ApplicationService
from app.ui.application_dialog import ApplicationDialog


class MainWindow(ctk.CTk):
    COLUMNS = ("Company", "Position", "Location", "Status", "Date Applied")

    def __init__(self, service: ApplicationService) -> None:
        super().__init__()
        self.service = service
        self.selected_id: int | None = None
        self.title("Job Tracker")
        self.geometry("1100x720")
        self.minsize(780, 560)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._build_header()
        self._build_controls()
        self._build_content()
        self._build_summary()
        self.refresh()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=28, pady=(24, 14), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header, text="Job Tracker", font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            header, text="+ Add Application", width=155, command=self._open_add
        ).grid(row=0, column=1, sticky="e")

    def _build_controls(self) -> None:
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=1, column=0, padx=28, pady=(0, 14), sticky="ew")
        controls.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(
            controls, placeholder_text="Search (coming soon)", height=38, state="disabled"
        ).grid(row=0, column=0, padx=(0, 12), sticky="ew")
        ctk.CTkOptionMenu(
            controls, values=["All statuses", *ALLOWED_STATUSES], width=160,
            height=38, state="disabled",
        ).grid(row=0, column=1)

    def _build_content(self) -> None:
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, padx=28, pady=(0, 14), sticky="nsew")
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        table_frame = ctk.CTkFrame(content)
        table_frame.grid(row=0, column=0, padx=(0, 12), sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)
        header = ctk.CTkFrame(table_frame, fg_color=("gray80", "gray25"))
        header.grid(row=0, column=0, padx=8, pady=(8, 0), sticky="ew")
        for index, title in enumerate(self.COLUMNS):
            header.grid_columnconfigure(index, weight=1)
            ctk.CTkLabel(
                header, text=title, font=ctk.CTkFont(weight="bold"), anchor="w"
            ).grid(row=0, column=index, padx=6, pady=7, sticky="ew")
        self.application_area = ctk.CTkScrollableFrame(table_frame)
        self.application_area.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        self.application_area.grid_columnconfigure(0, weight=1)

        details = ctk.CTkFrame(content)
        details.grid(row=0, column=1, sticky="nsew")
        details.grid_columnconfigure(0, weight=1)
        details.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(
            details, text="Application Details",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")
        self.details_label = ctk.CTkLabel(
            details, text="Select an application to view its details.", anchor="nw",
            justify="left", wraplength=330,
        )
        self.details_label.grid(row=1, column=0, padx=16, pady=8, sticky="nsew")
        actions = ctk.CTkFrame(details, fg_color="transparent")
        actions.grid(row=2, column=0, padx=16, pady=16, sticky="ew")
        actions.grid_columnconfigure((0, 1), weight=1)
        self.edit_button = ctk.CTkButton(
            actions, text="Edit", command=self._open_edit, state="disabled"
        )
        self.edit_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.delete_button = ctk.CTkButton(
            actions, text="Delete", command=self._delete_selected,
            state="disabled", fg_color="#b33a3a",
        )
        self.delete_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def _build_summary(self) -> None:
        frame = ctk.CTkFrame(self)
        frame.grid(row=3, column=0, padx=28, pady=(0, 24), sticky="ew")
        self.summary_labels = {}
        for column, name in enumerate(("Total", "Applied", "Interviews", "Offers")):
            frame.grid_columnconfigure(column, weight=1)
            value = ctk.CTkLabel(
                frame, text="0", font=ctk.CTkFont(size=22, weight="bold")
            )
            value.grid(row=0, column=column, padx=8, pady=(10, 0))
            ctk.CTkLabel(
                frame, text=name, text_color=("gray35", "gray70")
            ).grid(row=1, column=column, padx=8, pady=(0, 10))
            self.summary_labels[name] = value

    def refresh(self) -> None:
        for widget in self.application_area.winfo_children():
            widget.destroy()
        try:
            applications = self.service.list_applications()
            summary = self.service.get_summary()
        except sqlite3.Error:
            messagebox.showerror(
                "Database Error", "Job applications could not be loaded.", parent=self
            )
            return
        if not applications:
            ctk.CTkLabel(
                self.application_area,
                text="No applications yet. Add one to get started.",
            ).grid(row=0, column=0, pady=45)
        for row_number, application in enumerate(applications):
            self._add_table_row(row_number, application)
        for name, count in summary.items():
            self.summary_labels[name].configure(text=str(count))
        if self.selected_id is not None:
            self._select(self.selected_id)

    def _add_table_row(self, row_number: int, application) -> None:
        values = (
            application["company"], application["position"], application["location"] or "—",
            application["status"], application["date_applied"] or "—",
        )
        row = ctk.CTkFrame(self.application_area, fg_color=("gray88", "gray22"))
        row.grid(row=row_number, column=0, pady=2, sticky="ew")
        for column, value in enumerate(values):
            row.grid_columnconfigure(column, weight=1)
            label = ctk.CTkLabel(row, text=value, anchor="w", cursor="hand2")
            label.grid(row=0, column=column, padx=6, pady=7, sticky="ew")
            label.bind(
                "<Button-1>",
                lambda _event, app_id=application["id"]: self._select(app_id),
            )
        row.bind(
            "<Button-1>",
            lambda _event, app_id=application["id"]: self._select(app_id),
        )

    def _select(self, application_id: int) -> None:
        try:
            application = self.service.get_application(application_id)
        except sqlite3.Error:
            messagebox.showerror(
                "Database Error", "The application could not be loaded.", parent=self
            )
            return
        if application is None:
            self._clear_selection()
            return
        self.selected_id = application_id
        self.edit_button.configure(state="normal")
        self.delete_button.configure(state="normal")
        details = (
            f"Company: {application['company']}\n\nPosition: {application['position']}\n\n"
            f"Location: {application['location'] or '—'}\n\nStatus: {application['status']}\n\n"
            f"Date Applied: {application['date_applied'] or '—'}\n\n"
            f"Follow-up Date: {application['follow_up_date'] or '—'}\n\n"
            f"Job URL: {application['job_url'] or '—'}\n\nNotes:\n{application['notes'] or '—'}"
        )
        self.details_label.configure(text=details)

    def _clear_selection(self) -> None:
        self.selected_id = None
        self.details_label.configure(text="Select an application to view its details.")
        self.edit_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")

    def _open_add(self) -> None:
        ApplicationDialog(self, title="Add Application", on_save=self._create)

    def _open_edit(self) -> None:
        if self.selected_id is None:
            messagebox.showinfo(
                "Select Application", "Select an application to edit.", parent=self
            )
            return
        try:
            application = self.service.get_application(self.selected_id)
        except sqlite3.Error:
            messagebox.showerror(
                "Database Error", "The application could not be loaded.", parent=self
            )
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
            application_id = self.service.create_application(**values)
        except ValueError as error:
            messagebox.showerror("Invalid Application", str(error), parent=self)
            return False
        except sqlite3.Error:
            messagebox.showerror(
                "Database Error", "The application could not be saved.", parent=self
            )
            return False
        self.selected_id = application_id
        self.refresh()
        return True

    def _update(self, application_id: int | None, values: dict[str, str]) -> bool:
        if application_id is None:
            return False
        try:
            updated = self.service.update_application(application_id, **values)
        except ValueError as error:
            messagebox.showerror("Invalid Application", str(error), parent=self)
            return False
        except sqlite3.Error:
            messagebox.showerror(
                "Database Error", "The application could not be updated.", parent=self
            )
            return False
        if not updated:
            messagebox.showerror(
                "Not Found", "The selected application no longer exists.", parent=self
            )
            return False
        self.refresh()
        return True

    def _delete_selected(self) -> None:
        if self.selected_id is None:
            messagebox.showinfo(
                "Select Application", "Select an application to delete.", parent=self
            )
            return
        try:
            application = self.service.get_application(self.selected_id)
        except sqlite3.Error:
            messagebox.showerror(
                "Database Error", "The application could not be loaded.", parent=self
            )
            return
        if application is None:
            self._clear_selection()
            return
        if not messagebox.askyesno(
            "Delete Application",
            f"Delete {application['company']} — {application['position']}?\n\n"
            "This cannot be undone.",
            parent=self,
        ):
            return
        try:
            self.service.delete_application(self.selected_id)
        except sqlite3.Error:
            messagebox.showerror(
                "Database Error", "The application could not be deleted.", parent=self
            )
            return
        self._clear_selection()
        self.refresh()
