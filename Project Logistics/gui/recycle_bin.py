"""
Recycle Bin Window
Handles viewing, restoring, and permanently deleting recycled items and deliveries.
"""
from tkinter import *
from tkinter import messagebox, ttk
import mysql.connector
from mysql.connector import Error

class RecycleBin:
    def __init__(self, master, main_window=None):
        self.window = master or Tk()
        self.main_window = main_window
        self.window.title("Recycle Bin")
        self.window.geometry("1000x600")
        self.window.config(bg="#2E4057")

        self.tab_control = ttk.Notebook(self.window)
        self.tab_control.pack(expand=1, fill="both")

        self.inventory_tab = Frame(self.tab_control, bg="#34495E")
        self.deliveries_tab = Frame(self.tab_control, bg="#34495E")
        self.tab_control.add(self.inventory_tab, text="Inventory")
        self.tab_control.add(self.deliveries_tab, text="Deliveries")

        self.setup_inventory_tab()
        self.setup_deliveries_tab()

    def setup_inventory_tab(self):
        columns = ("ID", "Name", "Category", "Brand", "Quantity")
        self.inv_tree = ttk.Treeview(self.inventory_tab, columns=columns, show="headings")
        for col, w in zip(columns, [60, 180, 120, 120, 80]):
            self.inv_tree.heading(col, text=col)
            self.inv_tree.column(col, width=w)
        self.inv_tree.pack(expand=1, fill="both", padx=10, pady=10)
        self.load_inventory()

        btn_frame = Frame(self.inventory_tab, bg="#34495E")
        btn_frame.pack(fill=X, padx=10, pady=5)
        Button(btn_frame, text="Restore", width=14, bg="#28A745", fg="white", command=self.restore_inventory).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Delete Permanently", width=18, bg="#8B0000", fg="white", command=self.delete_inventory).pack(side=LEFT, padx=5)

    def load_inventory(self):
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("SELECT ID, Name, Category, Brand, Quantity FROM inventory WHERE Deleted=1")
            for row in cursor.fetchall():
                self.inv_tree.insert("", "end", values=row)
            cursor.close()
            conn.close()
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading recycled inventory: {e}")

    def restore_inventory(self):
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "Please select an inventory item to restore.")
            return
        item_id = self.inv_tree.item(selected[0], 'values')[0]
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("UPDATE inventory SET Deleted=0 WHERE ID=%s", (item_id,))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Restored", "Inventory item restored.")
            self.inv_tree.delete(selected[0])
        except Error as e:
            messagebox.showerror("Database Error", f"Error restoring item: {e}")

    def delete_inventory(self):
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "Please select an inventory item to delete.")
            return
        item_id = self.inv_tree.item(selected[0], 'values')[0]
        if not messagebox.askyesno("Confirm Delete", "Permanently delete this inventory item?"):
            return
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inventory WHERE ID=%s", (item_id,))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Deleted", "Inventory item permanently deleted.")
            self.inv_tree.delete(selected[0])
        except Error as e:
            messagebox.showerror("Database Error", f"Error deleting item: {e}")

    def setup_deliveries_tab(self):
        columns = ("ID", "Name", "Truck", "Status", "Date")
        self.del_tree = ttk.Treeview(self.deliveries_tab, columns=columns, show="headings")
        for col, w in zip(columns, [60, 180, 120, 120, 140]):
            self.del_tree.heading(col, text=col)
            self.del_tree.column(col, width=w)
        self.del_tree.pack(expand=1, fill="both", padx=10, pady=10)
        self.load_deliveries()

        btn_frame = Frame(self.deliveries_tab, bg="#34495E")
        btn_frame.pack(fill=X, padx=10, pady=5)
        Button(btn_frame, text="Restore", width=14, bg="#28A745", fg="white", command=self.restore_delivery).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Delete Permanently", width=18, bg="#8B0000", fg="white", command=self.delete_delivery).pack(side=LEFT, padx=5)

    def load_deliveries(self):
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.ID, i.Name, t.license_plate, d.Status, d.Delivered_at
                FROM deliveries d
                LEFT JOIN inventory i ON d.inventory_id = i.ID
                LEFT JOIN trucks t ON d.truck_id = t.ID
                WHERE d.Deleted=1
                ORDER BY d.ID DESC
            """)
            for row in cursor.fetchall():
                delivery_id, name, truck, status, date = row
                truck_display = truck if truck else "Not Assigned"
                date_display = date.strftime("%Y-%m-%d %H:%M") if date else "Pending"
                self.del_tree.insert("", "end", values=(delivery_id, name or "Unknown Item", truck_display, status or "Pending", date_display))
            cursor.close()
            conn.close()
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading recycled deliveries: {e}")

    def restore_delivery(self):
        selected = self.del_tree.selection()
        if not selected:
            messagebox.showwarning("Select Delivery", "Please select a delivery to restore.")
            return
        delivery_id = self.del_tree.item(selected[0], 'values')[0]
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("UPDATE deliveries SET Deleted=0 WHERE ID=%s", (delivery_id,))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Restored", "Delivery restored.")
            self.del_tree.delete(selected[0])
        except Error as e:
            messagebox.showerror("Database Error", f"Error restoring delivery: {e}")

    def delete_delivery(self):
        selected = self.del_tree.selection()
        if not selected:
            messagebox.showwarning("Select Delivery", "Please select a delivery to delete.")
            return
        delivery_id = self.del_tree.item(selected[0], 'values')[0]
        if not messagebox.askyesno("Confirm Delete", "Permanently delete this delivery?"):
            return
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM deliveries WHERE ID=%s", (delivery_id,))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Deleted", "Delivery permanently deleted.")
            self.del_tree.delete(selected[0])
        except Error as e:
            messagebox.showerror("Database Error", f"Error deleting delivery: {e}")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    root = Tk()
    app = RecycleBin(root)
    app.run()
