import tkinter as tk
from tkinter import messagebox

class ConnectionDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("CounterStock - Connect")
        self.geometry("380x170")
        self.resizable(False, False)
        
        self.confirmed = False
        self._url = tk.StringVar(value="http://localhost:8000")
        self._token = tk.StringVar(value="secret_counterstock_key")

        tk.Label(self, text="API URL:").grid(row=0, column=0, padx=14, pady=10, sticky=tk.E)
        tk.Entry(self, textvariable=self._url, width=30).grid(row=0, column=1, padx=10)

        tk.Label(self, text="X-API-Key:").grid(row=1, column=0, padx=14, pady=10, sticky=tk.E)
        tk.Entry(self, textvariable=self._token, width=30, show="*").grid(row=1, column=1, padx=10)

        tk.Button(self, text="Connect", bg="#1976D2", fg="white", command=self._confirm).grid(
            row=2, column=0, columnspan=2, pady=14
        )

        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _confirm(self):
        if not self._url.get().startswith("http"):
            messagebox.showwarning("Input Error", "Please provide a valid URL.")
            return
        self.confirmed = True
        self.destroy()

    def _cancel(self):
        self.confirmed = False
        self.destroy()

    @property
    def url(self) -> str:
        return self._url.get().rstrip("/")

    @property
    def token(self) -> str:
        return self._token.get().strip()
