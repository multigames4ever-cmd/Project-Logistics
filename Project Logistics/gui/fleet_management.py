from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Treeview
import mysql.connector


class FleetManagement:
    def __init__(self, parent_frame, main_window):
        self.parent_frame = parent_frame
        self.main_window = main_window
        self.username = main_window.username
        
    def show(self):
        """Display fleet management content"""
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
        Label(title_container, text="🚚 Fleet Management", bg="#34495E", fg="white",
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
        
        Button(action_frame, text="+ Add Truck", bg="#28A745", fg="white", width=18,
               font=("Segoe UI", 10), command=self.show_add_truck_form).pack(side=LEFT, padx=5)
        Button(action_frame, text="Edit Truck", bg="#FFC107", fg="black", width=18,
               font=("Segoe UI", 10), command=self.show_edit_truck_form).pack(side=LEFT, padx=5)
        Button(action_frame, text="Assign Truck", bg="#007BFF", fg="white", width=18,
               font=("Segoe UI", 10), command=self.show_assign_truck_form).pack(side=LEFT, padx=5)
        Button(action_frame, text="Set Maintenance", bg="#6C757D", fg="white", width=20,
               font=("Segoe UI", 10), command=self.set_maintenance).pack(side=LEFT, padx=5)
        Button(action_frame, text="Set Available", bg="#17A2B8", fg="white", width=18,
               font=("Segoe UI", 10), command=self.set_available).pack(side=LEFT, padx=5)
        
        # Trucks list
        list_frame = Frame(center_frame, bg="#2E4057")
        list_frame.pack(fill=BOTH, expand=True, pady=10)
        
        Label(list_frame, text="Fleet List", bg="#2E4057", fg="white",
              font=("Segoe UI", 12, "bold")).pack(anchor=W, pady=5)
        
        columns = ("ID", "License Plate", "Model", "Capacity", "Status")
        self.truck_tree = Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.truck_tree.heading(col, text=col)
            self.truck_tree.column(col, width=150, anchor=CENTER)
        
        scrollbar = Scrollbar(list_frame, orient=VERTICAL, command=self.truck_tree.yview)
        self.truck_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.truck_tree.pack(fill=BOTH, expand=True)
        
        # Form frame for add/assign operations
        self.form_frame = Frame(center_frame, bg="#34495E")
        
        # Bottom buttons
        bottom_frame = Frame(center_frame, bg="#2E4057")
        bottom_frame.pack(fill=X, pady=10)
        
        Button(bottom_frame, text="Refresh Dashboard", width=20, bg="#17A2B8", fg="white",
               font=("Segoe UI", 10), command=self.main_window.show_dashboard).pack(side=LEFT, padx=10)
        Button(bottom_frame, text="Logout", width=15, bg="#DC3545", fg="white",
               font=("Segoe UI", 10), command=self.main_window.logout).pack(side=LEFT, padx=10)
        
        self.load_trucks()
    
    def load_trucks(self):
        """Load trucks from database"""
        for item in self.truck_tree.get_children():
            self.truck_tree.delete(item)
        
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("SELECT id, license_plate, model, capacity, status FROM trucks WHERE (Deleted=0 OR Deleted IS NULL) ORDER BY id")
            
            for row in cursor.fetchall():
                truck_id, plate, model, capacity, status = row
                status_icon = "✅" if status == "Available" else "🚚" if status == "In Use" else "🔧"
                self.truck_tree.insert("", END, values=(truck_id, plate, model, capacity, f"{status_icon} {status}"))
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load trucks: {e}")
    
    def show_add_truck_form(self):
        """Show form to add new truck"""
        self.clear_form()
        self.form_frame.pack(fill=X, pady=10, padx=20)
        
        Label(self.form_frame, text="Add New Truck", bg="#34495E", fg="white",
              font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        input_frame = Frame(self.form_frame, bg="#34495E")
        input_frame.pack(pady=10)
        
        Label(input_frame, text="License Plate:", bg="#34495E", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        plate_entry = Entry(input_frame, width=25)
        plate_entry.grid(row=0, column=1, padx=5, pady=5)
        
        Label(input_frame, text="Model:", bg="#34495E", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        model_entry = Entry(input_frame, width=25)
        model_entry.grid(row=1, column=1, padx=5, pady=5)
        
        Label(input_frame, text="Capacity:", bg="#34495E", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        capacity_entry = Entry(input_frame, width=25)
        capacity_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def submit():
            plate = plate_entry.get().strip()
            model = model_entry.get().strip()
            capacity = capacity_entry.get().strip()
            
            if not plate or not model or not capacity:
                messagebox.showwarning("Input Required", "Please fill all fields")
                return
            
            try:
                capacity_val = float(capacity)
                if capacity_val <= 0:
                    messagebox.showwarning("Invalid Capacity", "Capacity must be greater than 0")
                    return
            except ValueError:
                messagebox.showwarning("Invalid Capacity", "Capacity must be a number")
                return
            
            try:
                conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO trucks (license_plate, model, capacity, status, Deleted)
                    VALUES (%s, %s, %s, 'Available', 0)
                """, (plate, model, capacity_val))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Truck added successfully!")
                self.clear_form()
                self.load_trucks()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add truck: {e}")
        
        btn_frame = Frame(self.form_frame, bg="#34495E")
        btn_frame.pack(pady=10)
        
        Button(btn_frame, text="Add Truck", bg="#28A745", fg="white", width=12, command=submit).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Cancel", bg="#6C757D", fg="white", width=12, command=self.clear_form).pack(side=LEFT, padx=5)
    
    def show_edit_truck_form(self):
        """Show form to edit truck"""
        selected = self.truck_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a truck to edit")
            return
        
        truck_item = self.truck_tree.item(selected[0])
        truck_id, license_plate, model, capacity, status = truck_item['values']
        
        # Handle None/N/A values
        if license_plate == "N/A":
            license_plate = ""
        if model == "N/A":
            model = ""
        if capacity == 0 or capacity is None:
            capacity = ""
        
        self.clear_form()
        self.form_frame.pack(fill=X, pady=10, padx=20)
        
        Label(self.form_frame, text=f"Edit Truck (ID: {truck_id})", bg="#34495E", fg="white",
              font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        input_frame = Frame(self.form_frame, bg="#34495E")
        input_frame.pack(pady=10)
        
        Label(input_frame, text="License Plate:", bg="#34495E", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        plate_entry = Entry(input_frame, width=25)
        plate_entry.insert(0, license_plate or "")
        plate_entry.grid(row=0, column=1, padx=5, pady=5)
        
        Label(input_frame, text="Model:", bg="#34495E", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        model_entry = Entry(input_frame, width=25)
        model_entry.insert(0, model or "")
        model_entry.grid(row=1, column=1, padx=5, pady=5)
        
        Label(input_frame, text="Capacity:", bg="#34495E", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        capacity_entry = Entry(input_frame, width=25)
        capacity_entry.insert(0, capacity or "")
        capacity_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def submit():
            plate = plate_entry.get().strip()
            model = model_entry.get().strip()
            capacity = capacity_entry.get().strip()
            
            if not plate or not model or not capacity:
                messagebox.showwarning("Input Required", "Please fill all fields")
                return
            
            try:
                capacity_val = float(capacity)
                if capacity_val <= 0:
                    messagebox.showwarning("Invalid Capacity", "Capacity must be greater than 0")
                    return
            except ValueError:
                messagebox.showwarning("Invalid Capacity", "Capacity must be a number")
                return
            
            try:
                conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE trucks SET license_plate=%s, model=%s, capacity=%s
                    WHERE id=%s
                """, (plate, model, capacity_val, truck_id))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Truck updated successfully!")
                self.clear_form()
                self.load_trucks()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update truck: {e}")
        
        btn_frame = Frame(self.form_frame, bg="#34495E")
        btn_frame.pack(pady=10)
        
        Button(btn_frame, text="Update", bg="#007BFF", fg="white", width=12, command=submit).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Cancel", bg="#6C757D", fg="white", width=12, command=self.clear_form).pack(side=LEFT, padx=5)
    
    def show_assign_truck_form(self):
        """Show form to assign truck to delivery"""
        selected = self.truck_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a truck to assign")
            return
        
        truck_item = self.truck_tree.item(selected[0])
        truck_id = truck_item['values'][0]
        
        # Get available deliveries
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.id, i.Name, d.Delivery_Amount, d.Status
                FROM deliveries d
                JOIN inventory i ON d.inventory_id = i.id
                WHERE d.Status = 'Pending' AND d.Deleted = 0
            """)
            deliveries = cursor.fetchall()
            conn.close()
            
            if not deliveries:
                messagebox.showinfo("No Deliveries", "No pending deliveries available to assign")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load deliveries: {e}")
            return
        
        self.clear_form()
        self.form_frame.pack(fill=X, pady=10, padx=20)
        
        Label(self.form_frame, text="Assign Truck to Delivery", bg="#34495E", fg="white",
              font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        Label(self.form_frame, text="Select Delivery:", bg="#34495E", fg="white").pack(pady=5)
        
        delivery_listbox = Listbox(self.form_frame, height=8, width=60)
        delivery_listbox.pack(pady=10)
        
        for delivery in deliveries:
            delivery_listbox.insert(END, f"ID: {delivery[0]} - {delivery[1]} - Amount: {delivery[2]} - Status: {delivery[3]}")
        
        def submit():
            selection = delivery_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a delivery")
                return
            
            delivery_id = deliveries[selection[0]][0]
            
            try:
                conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                cursor = conn.cursor()
                cursor.execute("UPDATE deliveries SET truck_id=%s, Status='In Transit' WHERE id=%s", (truck_id, delivery_id))
                cursor.execute("UPDATE trucks SET status='In Use' WHERE id=%s", (truck_id,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Truck assigned successfully!")
                self.clear_form()
                self.load_trucks()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to assign truck: {e}")
        
        btn_frame = Frame(self.form_frame, bg="#34495E")
        btn_frame.pack(pady=10)
        
        Button(btn_frame, text="Assign", bg="#007BFF", fg="white", width=12, command=submit).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Cancel", bg="#6C757D", fg="white", width=12, command=self.clear_form).pack(side=LEFT, padx=5)
    
    def set_maintenance(self):
        """Set selected truck to maintenance status"""
        selected = self.truck_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a truck")
            return
        
        truck_id = self.truck_tree.item(selected[0])['values'][0]
        
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("UPDATE trucks SET status='Maintenance' WHERE id=%s", (truck_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Truck set to maintenance")
            self.load_trucks()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update truck: {e}")
    
    def set_available(self):
        """Set selected truck to available status"""
        selected = self.truck_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a truck")
            return
        
        truck_id = self.truck_tree.item(selected[0])['values'][0]
        
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("UPDATE trucks SET status='Available' WHERE id=%s", (truck_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Truck set to available")
            self.load_trucks()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update truck: {e}")
    
    def clear_form(self):
        """Clear and hide form"""
        try:
            for widget in self.form_frame.winfo_children():
                widget.destroy()
            self.form_frame.pack_forget()
        except:
            pass
