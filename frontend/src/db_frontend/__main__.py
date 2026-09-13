import tkinter as tk
from db_frontend import api
from db_frontend.connection_dialog import ConnectionDialog
from db_frontend.ui import App

def main():
    root = tk.Tk()
    root.withdraw()

    dialog = ConnectionDialog(root)
    root.wait_window(dialog)

    if not dialog.confirmed:
        root.destroy()
        return

    # Set session credentials
    api.BASE_URL = dialog.url
    api.HEADERS = {"X-API-Key": dialog.token, "X-API-Token": dialog.token}

    root.destroy()
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
