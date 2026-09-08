"""Scrollable local help window."""

import customtkinter as ctk

from app.config import DISPLAY_NAME
from app.help_content import HELP_TOPICS


class HelpWindow(ctk.CTkToplevel):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.title(f"Help — {DISPLAY_NAME}")
        self.geometry("780x680")
        self.minsize(580, 460)
        self.transient(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        content = ctk.CTkScrollableFrame(self)
        content.grid(row=0, column=0, padx=18, pady=18, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        row = 0
        ctk.CTkLabel(
            content, text="Job Tracker Help", font=ctk.CTkFont(size=26, weight="bold")
        ).grid(row=row, column=0, padx=14, pady=(8, 16), sticky="w")
        row += 1
        for title, body in HELP_TOPICS:
            ctk.CTkLabel(
                content, text=title, font=ctk.CTkFont(size=18, weight="bold"), anchor="w"
            ).grid(row=row, column=0, padx=14, pady=(14, 4), sticky="ew")
            row += 1
            ctk.CTkLabel(
                content, text=body, justify="left", anchor="nw", wraplength=690
            ).grid(row=row, column=0, padx=14, pady=(0, 6), sticky="ew")
            row += 1
        ctk.CTkButton(self, text="Close", width=110, command=self.destroy).grid(
            row=1, column=0, padx=18, pady=(0, 18), sticky="e"
        )
        self.bind("<Escape>", lambda _event: self.destroy())
