from tkinter import *
from tkinter import messagebox, simpledialog
from tkinter.ttk import Treeview, Combobox
import mysql.connector
from book_delivery import BookDeliveryWindow


class InventoryManagement:
    def __init__(self, parent_frame, main_window):
        self.parent_frame = parent_frame
        self.main_window = main_window
        self.username = main_window.username
        
    def show(self):
        """Display inventory management content"""
        # Clear parent frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Title with back button
        title_frame = Frame(self.parent_frame, bg="#34495E", height=60)
        title_frame.pack(fill=X)
        title_frame.pack_propagate(False)
        
        Button(title_frame, text="← Dashboard", bg="#3498db", fg="white",
               font=("Segoe UI", 10, "bold"), command=self.main_window.show_dashboard).pack(side=LEFT, padx=20, pady=15)
        
        # Center the title
        title_container = Frame(title_frame, bg="#34495E")
        title_container.place(relx=0.5, rely=0.5, anchor=CENTER)
        Label(title_container, text="📦 Inventory Management", bg="#34495E", fg="white",
              font=("Segoe UI", 16, "bold")).pack()
        
        # Content container for centering
        content_container = Frame(self.parent_frame, bg="#2E4057")
        content_container.pack(fill=BOTH, expand=True)
        
        # Center frame - auto-size based on content
        center_frame = Frame(content_container, bg="#2E4057")
        center_frame.pack(expand=True, pady=20, padx=50)
        
        # Action buttons
        action_frame = Frame(center_frame, bg="#2E4057")
        action_frame.pack(fill=X, pady=10)
        
        Button(action_frame, text="+ Add Item", bg="#28A745", fg="white", width=18,
               font=("Segoe UI", 10), command=self.show_add_form).pack(side=LEFT, padx=5)
        Button(action_frame, text="Update Item", bg="#007BFF", fg="white", width=18,
               font=("Segoe UI", 10), command=self.show_update_form).pack(side=LEFT, padx=5)
        Button(action_frame, text="Book Delivery", bg="#FFC107", fg="white", width=18,
               font=("Segoe UI", 10), command=self.open_book_delivery).pack(side=LEFT, padx=5)
        Button(action_frame, text="Remove Item", bg="#D9534F", fg="white", width=18,
               font=("Segoe UI", 10), command=self.show_remove_form).pack(side=LEFT, padx=5)
        
        # Inventory list
        list_frame = Frame(center_frame, bg="#2E4057")
        list_frame.pack(fill=BOTH, expand=True, pady=10)
        
        Label(list_frame, text="Inventory List", bg="#2E4057", fg="white",
              font=("Segoe UI", 12, "bold")).pack(anchor=W, pady=5)
        
        columns = ("ID", "Name", "Category", "Quantity", "Brand")
        self.inventory_tree = Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=150, anchor=CENTER)
        
        scrollbar = Scrollbar(list_frame, orient=VERTICAL, command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.inventory_tree.pack(fill=BOTH, expand=True)
        
        # Form frame
        self.form_frame = Frame(center_frame, bg="#34495E")
        
        # Bottom buttons
        bottom_frame = Frame(center_frame, bg="#2E4057")
        bottom_frame.pack(fill=X, pady=10)
        
        Button(bottom_frame, text="Refresh Dashboard", width=20, bg="#17A2B8", fg="white",
               font=("Segoe UI", 10), command=self.main_window.show_dashboard).pack(side=LEFT, padx=10)
        Button(bottom_frame, text="Logout", width=15, bg="#DC3545", fg="white",
               font=("Segoe UI", 10), command=self.main_window.logout).pack(side=LEFT, padx=10)
        
        self.load_inventory()
    
    def load_inventory(self):
        """Load inventory from database"""
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("SELECT id, Name, Category, Quantity, Brand FROM inventory WHERE Deleted=0 ORDER BY id DESC")
            
            for row in cursor.fetchall():
                self.inventory_tree.insert("", END, values=row)
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory: {e}")
    
    def show_add_form(self):
        """Show form to add new item"""
        self.clear_form()
        self.form_frame.pack(fill=X, pady=10, padx=20)
        
        Label(self.form_frame, text="Add New Item", bg="#34495E", fg="white",
              font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        input_frame = Frame(self.form_frame, bg="#34495E")
        input_frame.pack(pady=10)
        
        Label(input_frame, text="Name:", bg="#34495E", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        name_entry = Entry(input_frame, width=25)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        Label(input_frame, text="Category:", bg="#34495E", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        category_frame = Frame(input_frame, bg="#34495E")
        category_frame.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        
        category_combo = Combobox(category_frame, width=20, state="readonly")
        category_combo.pack(side=LEFT)
        
        # Load categories
        def load_categories():
            try:
                conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT name FROM categories ORDER BY name")
                categories = [row[0] for row in cursor.fetchall()]
                conn.close()
                category_combo['values'] = categories
                if categories:
                    category_combo.current(0)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load categories: {e}")
        
        def add_category():
            new_cat = simpledialog.askstring("Add Category", "Enter new category name:")
            if new_cat:
                try:
                    conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO categories (name) VALUES (%s)", (new_cat,))
                    conn.commit()
                    conn.close()
                    load_categories()
                    messagebox.showinfo("Success", "Category added!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add category: {e}")
        
        def remove_category():
            cat = category_combo.get()
            if cat and messagebox.askyesno("Confirm", f"Remove category '{cat}'?"):
                try:
                    conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM categories WHERE name=%s", (cat,))
                    conn.commit()
                    conn.close()
                    load_categories()
                    messagebox.showinfo("Success", "Category removed!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to remove category: {e}")
        
        Button(category_frame, text="+", bg="#28A745", fg="white", width=2, command=add_category).pack(side=LEFT, padx=2)
        Button(category_frame, text="-", bg="#D9534F", fg="white", width=2, command=remove_category).pack(side=LEFT, padx=2)
        
        load_categories()
        
        Label(input_frame, text="Quantity:", bg="#34495E", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        quantity_entry = Entry(input_frame, width=25)
        quantity_entry.grid(row=2, column=1, padx=5, pady=5)
        
        Label(input_frame, text="Brand:", bg="#34495E", fg="white").grid(row=3, column=0, padx=5, pady=5, sticky=W)
        brand_entry = Entry(input_frame, width=25)
        brand_entry.grid(row=3, column=1, padx=5, pady=5)
        
        def submit():
            name = name_entry.get().strip()
            category = category_combo.get().strip()
            quantity = quantity_entry.get().strip()
            brand = brand_entry.get().strip()
            
            if not name or not category or not quantity or not brand:
                messagebox.showwarning("Input Required", "Please fill all fields")
                return
            
            try:
                conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO inventory (Name, Category, Quantity, Brand, Deleted)
                    VALUES (%s, %s, %s, %s, 0)
                """, (name, category, quantity, brand))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Item added successfully!")
                self.clear_form()
                self.load_inventory()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add item: {e}")
        
        btn_frame = Frame(self.form_frame, bg="#34495E")
        btn_frame.pack(pady=10)
        
        Button(btn_frame, text="Add Item", bg="#28A745", fg="white", width=12, command=submit).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Cancel", bg="#6C757D", fg="white", width=12, command=self.clear_form).pack(side=LEFT, padx=5)
    
    def show_update_form(self):
        """Show form to update item"""
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to update")
            return
        
        item = self.inventory_tree.item(selected[0])
        item_id, name, category, quantity, brand = item['values']
        
        self.clear_form()
        self.form_frame.pack(fill=X, pady=10, padx=20)
        
        Label(self.form_frame, text=f"Update Item (ID: {item_id})", bg="#34495E", fg="white",
              font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        input_frame = Frame(self.form_frame, bg="#34495E")
        input_frame.pack(pady=10)
        
        Label(input_frame, text="Name:", bg="#34495E", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        name_entry = Entry(input_frame, width=25)
        name_entry.insert(0, name)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        Label(input_frame, text="Category:", bg="#34495E", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        category_combo = Combobox(input_frame, width=23, state="readonly")
        category_combo.grid(row=1, column=1, padx=5, pady=5)
        
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT name FROM categories ORDER BY name")
            categories = [row[0] for row in cursor.fetchall()]
            conn.close()
            category_combo['values'] = categories
            category_combo.set(category)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load categories: {e}")
        
        Label(input_frame, text="Quantity:", bg="#34495E", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        quantity_entry = Entry(input_frame, width=25)
        quantity_entry.insert(0, quantity)
        quantity_entry.grid(row=2, column=1, padx=5, pady=5)
        
        Label(input_frame, text="Brand:", bg="#34495E", fg="white").grid(row=3, column=0, padx=5, pady=5, sticky=W)
        brand_entry = Entry(input_frame, width=25)
        brand_entry.insert(0, brand)
        brand_entry.grid(row=3, column=1, padx=5, pady=5)
        
        def submit():
            new_name = name_entry.get().strip()
            new_category = category_combo.get().strip()
            new_quantity = quantity_entry.get().strip()
            new_brand = brand_entry.get().strip()
            
            if not new_name or not new_category or not new_quantity or not new_brand:
                messagebox.showwarning("Input Required", "Please fill all fields")
                return
            
            try:
                conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE inventory SET Name=%s, Category=%s, Quantity=%s, Brand=%s
                    WHERE id=%s
                """, (new_name, new_category, new_quantity, new_brand, item_id))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Item updated successfully!")
                self.clear_form()
                self.load_inventory()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update item: {e}")
        
        btn_frame = Frame(self.form_frame, bg="#34495E")
        btn_frame.pack(pady=10)
        
        Button(btn_frame, text="Update", bg="#007BFF", fg="white", width=12, command=submit).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Cancel", bg="#6C757D", fg="white", width=12, command=self.clear_form).pack(side=LEFT, padx=5)
    
    def show_remove_form(self):
        """Show form to remove item"""
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to remove")
            return
        
        item = self.inventory_tree.item(selected[0])
        item_id, name, category, quantity, brand = item['values']
        
        self.clear_form()
        self.form_frame.pack(fill=X, pady=10, padx=20)
        
        Label(self.form_frame, text=f"Remove Item (ID: {item_id})", bg="#34495E", fg="white",
              font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        info_frame = Frame(self.form_frame, bg="#34495E")
        info_frame.pack(fill=X, padx=20, pady=10)
        
        Label(info_frame, text=f"Name: {name}", bg="#34495E", fg="white", font=("Segoe UI", 10)).pack(anchor=W, pady=2)
        Label(info_frame, text=f"Category: {category}", bg="#34495E", fg="white", font=("Segoe UI", 10)).pack(anchor=W, pady=2)
        Label(info_frame, text=f"Quantity: {quantity}", bg="#34495E", fg="white", font=("Segoe UI", 10)).pack(anchor=W, pady=2)
        Label(info_frame, text=f"Brand: {brand}", bg="#34495E", fg="white", font=("Segoe UI", 10)).pack(anchor=W, pady=2)
        
        def submit_remove():
            if messagebox.askyesno("Confirm", "Move this item to Recycle Bin?"):
                try:
                    conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                    cursor = conn.cursor()
                    cursor.execute("UPDATE inventory SET Deleted=1 WHERE id=%s", (item_id,))
                    conn.commit()
                    conn.close()
                    
                    messagebox.showinfo("Success", "Item moved to Recycle Bin!")
                    self.clear_form()
                    self.load_inventory()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to remove item: {e}")
        
        def permanent_delete():
            if messagebox.askyesno("Confirm Permanent Delete", "This action cannot be undone. Delete permanently?"):
                try:
                    conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM inventory WHERE id=%s", (item_id,))
                    conn.commit()
                    conn.close()
                    
                    messagebox.showinfo("Success", "Item permanently deleted!")
                    self.clear_form()
                    self.load_inventory()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete item: {e}")
        
        btn_frame = Frame(info_frame, bg="#34495E")
        btn_frame.pack(pady=15)
        Button(btn_frame, text="Move to Recycle Bin", bg="#D9534F", fg="white", width=18, command=submit_remove).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Delete Permanently", bg="#8B0000", fg="white", width=18, command=permanent_delete).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Cancel", bg="#6C757D", fg="white", width=12, command=self.clear_form).pack(side=LEFT, padx=5)
    
    def open_book_delivery(self):
        """Open book delivery window"""
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to book delivery")
            return
        
        item = self.inventory_tree.item(selected[0])
        item_id = item['values'][0]
        
        # Pass callback to refresh inventory after booking
        BookDeliveryWindow(self.main_window.window, self.username, item_id, callback=self.load_inventory)
    
    def clear_form(self):
        """Clear and hide form"""
        try:
            for widget in self.form_frame.winfo_children():
                widget.destroy()
            self.form_frame.pack_forget()
        except:
            pass
