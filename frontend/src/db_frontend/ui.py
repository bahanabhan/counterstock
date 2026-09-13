import tkinter as tk
from tkinter import messagebox, ttk
from db_frontend import api

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CounterStock Counter Application")
        self.geometry("640x500")

        # Top Navigation Bar
        nav = tk.Frame(self, pady=6, bg="#ECEFF1")
        nav.pack(fill=tk.X)
        tk.Button(nav, text="Menu & Ordering", command=self.show_menu_view).pack(side=tk.LEFT, padx=10)
        tk.Button(nav, text="Stock & Restock", command=self.show_stock_view).pack(side=tk.LEFT, padx=10)

        # Content Container
        self.container = tk.Frame(self, padx=15, pady=15)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.show_menu_view()

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # Screen 1 & 2: Menu Overview and Order Form
    def show_menu_view(self):
        self._clear_container()

        tk.Label(self.container, text="Menu Items", font=("Helvetica", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # Menu Table
        cols = ("ID", "Name", "Category", "Price", "Available")
        self.menu_tree = ttk.Treeview(self.container, columns=cols, show="headings", height=7)
        for col in cols:
            self.menu_tree.heading(col, text=col)
            self.menu_tree.column(col, width=110, anchor=tk.CENTER)
        self.menu_tree.pack(fill=tk.X)

        # Order Form Area
        form = tk.LabelFrame(self.container, text="Place Order (POST /orders)", padx=10, pady=10)
        form.pack(fill=tk.X, pady=15)

        tk.Label(form, text="Selected Menu Item ID:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.item_id_entry = tk.Entry(form, width=10)
        self.item_id_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Label(form, text="Quantity:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.qty_entry = tk.Entry(form, width=10)
        self.qty_entry.insert(0, "1")
        self.qty_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Button(form, text="Submit Order", bg="#2E7D32", fg="white", command=self._submit_order).grid(
            row=2, column=0, columnspan=2, pady=10
        )

        self._refresh_menu()

    def _refresh_menu(self):
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)
        try:
            items = api.get_menu()
            for m in items:
                self.menu_tree.insert("", tk.END, values=(m["id"], m["name"], m["category"], f"€{m['price']:.2f}", m["available"]))
        except Exception as e:
            messagebox.showerror("Network Error", f"Failed to load menu: {e}")

    def _submit_order(self):
        item_id = self.item_id_entry.get().strip()
        qty = self.qty_entry.get().strip()

        if not item_id or not qty:
            messagebox.showwarning("Validation Error", "Please provide both Menu Item ID and Quantity.")
            return

        try:
            res = api.place_order(int(item_id), int(qty))
            messagebox.showinfo("Order Placed", f"Order #{res['order_id']} successfully placed!")
            self._refresh_menu()
        except Exception as e:
            messagebox.showerror("Order Failed", f"Order rejected: {e}")

    # Screen 3: Low-stock and Restock View
    def show_stock_view(self):
        self._clear_container()

        tk.Label(self.container, text="Low-Stock Ingredients (GET /ingredients/low-stock)", font=("Helvetica", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        cols = ("ID", "Name", "Stock", "Threshold", "Unit")
        self.stock_tree = ttk.Treeview(self.container, columns=cols, show="headings", height=7)
        for col in cols:
            self.stock_tree.heading(col, text=col)
            self.stock_tree.column(col, width=110, anchor=tk.CENTER)
        self.stock_tree.pack(fill=tk.X)

        form = tk.LabelFrame(self.container, text="Restock Ingredient (POST /ingredients/{id}/restock)", padx=10, pady=10)
        form.pack(fill=tk.X, pady=15)

        tk.Label(form, text="Ingredient ID:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.ing_id_entry = tk.Entry(form, width=10)
        self.ing_id_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Label(form, text="Amount to Add:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.restock_qty_entry = tk.Entry(form, width=10)
        self.restock_qty_entry.insert(0, "20.0")
        self.restock_qty_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Button(form, text="Restock", bg="#1976D2", fg="white", command=self._submit_restock).grid(
            row=2, column=0, columnspan=2, pady=10
        )

        self._refresh_stock()

    def _refresh_stock(self):
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        try:
            items = api.get_low_stock()
            for row in items:
                self.stock_tree.insert("", tk.END, values=(row["id"], row["name"], row["stock_quantity"], row["reorder_threshold"], row["unit"]))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stock: {e}")

    def _submit_restock(self):
        ing_id = self.ing_id_entry.get().strip()
        amt = self.restock_qty_entry.get().strip()

        if not ing_id or not amt:
            messagebox.showwarning("Validation Error", "Please provide Ingredient ID and Amount.")
            return

        try:
            res = api.restock_ingredient(int(ing_id), float(amt))
            messagebox.showinfo("Success", f"Updated stock for {res['name']} to {res['stock_quantity']}!")
            self._refresh_stock()
        except Exception as e:
            messagebox.showerror("Error", f"Restock failed: {e}")
