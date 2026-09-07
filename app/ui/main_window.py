"""Main CustomTkinter application shell."""

from __future__ import annotations

import customtkinter as ctk

from app.models import ALLOWED_STATUSES
from app.services.application_service import ApplicationService


class MainWindow(ctk.CTk):
    def __init__(self, service: ApplicationService) -> None:
        super().__init__()
        self.service = service
        self.title("Job Tracker")
        self.geometry("1050x680")
        self.minsize(760, 520)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_controls()
        self._build_application_area()
        self._build_summary()
        self.refresh()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=28, pady=(24, 14), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header, text="Job Tracker", font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(header, text="+ Add Application", width=155).grid(
            row=0, column=1, sticky="e"
        )

    def _build_controls(self) -> None:
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=1, column=0, padx=28, pady=(0, 14), sticky="ew")
        controls.grid_columnconfigure(0, weight=1)
        self.search_entry = ctk.CTkEntry(
            controls, placeholder_text="Search applications...", height=38
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 12), sticky="ew")
        self.status_filter = ctk.CTkOptionMenu(
            controls, values=["All statuses", *ALLOWED_STATUSES], width=160, height=38
        )
        self.status_filter.grid(row=0, column=1)

    def _build_application_area(self) -> None:
        self.application_area = ctk.CTkScrollableFrame(
            self, label_text="Applications", label_font=ctk.CTkFont(size=16, weight="bold")
        )
        self.application_area.grid(row=2, column=0, padx=28, pady=(0, 14), sticky="nsew")
        self.application_area.grid_columnconfigure(0, weight=1)

    def _build_summary(self) -> None:
        self.summary_frame = ctk.CTkFrame(self)
        self.summary_frame.grid(row=3, column=0, padx=28, pady=(0, 24), sticky="ew")
        self.summary_labels: dict[str, ctk.CTkLabel] = {}
        for column, name in enumerate(("Total", "Applied", "Interviews", "Offers")):
            self.summary_frame.grid_columnconfigure(column, weight=1)
            cell = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
            cell.grid(row=0, column=column, padx=8, pady=12, sticky="ew")
            value = ctk.CTkLabel(cell, text="0", font=ctk.CTkFont(size=22, weight="bold"))
            value.pack()
            ctk.CTkLabel(cell, text=name, text_color=("gray35", "gray70")).pack()
            self.summary_labels[name] = value

    def refresh(self) -> None:
        for widget in self.application_area.winfo_children():
            widget.destroy()
        applications = self.service.list_applications()
        if not applications:
            ctk.CTkLabel(
                self.application_area,
                text="No applications yet. Add one to get started.",
                text_color=("gray40", "gray65"),
            ).grid(row=0, column=0, pady=50)
        else:
            for row_number, application in enumerate(applications):
                text = f"{application['company']}  ·  {application['position']}  ·  {application['status']}"
                ctk.CTkLabel(self.application_area, text=text, anchor="w").grid(
                    row=row_number, column=0, padx=12, pady=8, sticky="ew"
                )
        for name, count in self.service.get_summary().items():
            self.summary_labels[name].configure(text=str(count))
