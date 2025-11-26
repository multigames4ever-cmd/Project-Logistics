"""
Fleet Management Window
Allows viewing, editing, and managing trucks and their status/routes.
"""
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Treeview
import mysql.connector


class FleetManagement:
        # Fleet Management window for trucks
    def __init__(self, parent_frame, main_window):
        self.parent_frame = parent_frame
        self.main_window = main_window
        self.username = main_window.username
        
    def show(self):
            # Show fleet management UI and truck list
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        title_frame = Frame(self.parent_frame, bg="#34495E", height=60)
        title_frame.pack(fill=X)
        title_frame.pack_propagate(False)
        
        Button(title_frame, text="← Dashboard", bg="#3498db", fg="white",
               font=("Segoe UI", 10, "bold"), command=self.main_window.show_dashboard).pack(side=LEFT, padx=20, pady=15)
        
        title_container = Frame(title_frame, bg="#34495E")
        title_container.place(relx=0.5, rely=0.5, anchor=CENTER)
        Label(title_container, text="🚚 Fleet Management", bg="#34495E", fg="white",
              font=("Segoe UI", 16, "bold")).pack()
        
        content_container = Frame(self.parent_frame, bg="#2E4057")
        content_container.pack(fill=BOTH, expand=True)
        
        center_frame = Frame(content_container, bg="#2E4057")
        center_frame.pack(expand=True, pady=20, padx=50)
        
        action_frame = Frame(center_frame, bg="#2E4057")
        action_frame.pack(fill=X, pady=10)
        
        Button(action_frame, text="+ Add Truck", bg="#5DADE2", fg="white", width=15,
               font=("Segoe UI", 10), command=self.show_add_truck_form).pack(side=LEFT, padx=5)
        Button(action_frame, text="Edit Truck", bg="#5DADE2", fg="white", width=15,
               font=("Segoe UI", 10), command=self.show_edit_truck_form).pack(side=LEFT, padx=5)
        Button(action_frame, text="Assign Location", bg="#5DADE2", fg="white", width=18,
               font=("Segoe UI", 10), command=self.show_assign_location_form).pack(side=LEFT, padx=5)
        Button(action_frame, text="Edit Route", bg="#5DADE2", fg="white", width=15,
               font=("Segoe UI", 10), command=self.show_edit_route_form).pack(side=LEFT, padx=5)
        Button(action_frame, text="Set Maintenance", bg="#ABB2B9", fg="white", width=18,
               font=("Segoe UI", 10), command=self.set_maintenance).pack(side=LEFT, padx=5)
        Button(action_frame, text="Set Available", bg="#52BE80", fg="white", width=15,
               font=("Segoe UI", 10), command=self.set_available).pack(side=LEFT, padx=5)
        
        list_frame = Frame(center_frame, bg="#2E4057")
        list_frame.pack(fill=BOTH, expand=True, pady=10)
        
        header_frame = Frame(list_frame, bg="#2E4057")
        header_frame.pack(fill=X, pady=5)
        
        Label(header_frame, text="Fleet List", bg="#2E4057", fg="white",
              font=("Segoe UI", 12, "bold")).pack(side=LEFT)
        
        search_frame = Frame(header_frame, bg="#2E4057")
        search_frame.pack(side=RIGHT)
        
        Label(search_frame, text="Search:", bg="#2E4057", fg="white",
              font=("Segoe UI", 10)).pack(side=LEFT, padx=(0, 5))
        
        self.search_var = StringVar()
        self.search_var.trace('w', lambda *args: self.filter_trucks())
        search_entry = Entry(search_frame, textvariable=self.search_var, width=30,
                           font=("Segoe UI", 10))
        search_entry.pack(side=LEFT)
        
        Button(search_frame, text="✖", bg="#EC7063", fg="white", width=3,
               font=("Segoe UI", 9), command=lambda: self.search_var.set("")).pack(side=LEFT, padx=5)
        
        columns = ("ID", "License Plate", "Model", "Capacity", "Status", "Deliveries")
        self.truck_tree = Treeview(list_frame, columns=columns, show="headings", height=15)
        
        widths = [50, 120, 120, 80, 100, 400]
        for col, width in zip(columns, widths):
            self.truck_tree.heading(col, text=col)
            self.truck_tree.column(col, width=width, anchor=W if col == "Deliveries" else CENTER)
        
        scrollbar = Scrollbar(list_frame, orient=VERTICAL, command=self.truck_tree.yview)
        self.truck_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.truck_tree.pack(fill=BOTH, expand=True)
        
        self.form_frame = Frame(center_frame, bg="#34495E")
        
        self.load_trucks()
    
    def load_trucks(self, search_text=""):
            # Load trucks from database and display in treeview
        for item in self.truck_tree.get_children():
            self.truck_tree.delete(item)
        
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("SELECT id, license_plate, model, capacity, status FROM trucks WHERE (Deleted=0 OR Deleted IS NULL) ORDER BY id")
            
            for row in cursor.fetchall():
                truck_id, plate, model, capacity, status = row
                
                # Apply search filter
                if search_text and not (search_text in str(truck_id).lower() or 
                                       search_text in str(plate).lower() or 
                                       search_text in str(model).lower() or 
                                       search_text in str(status).lower()):
                    continue
                
                status_icon = "✅" if status == "Available" else "🚚" if status == "In Use" else "🔧"
                
                delivery_info = ""
                if status == "In Use":
                    cursor.execute("""
                        SELECT i.Name, d.Delivery_Amount, l.origin, l.destination
                        FROM deliveries d
                        JOIN inventory i ON d.inventory_id = i.id
                        LEFT JOIN locations l ON l.delivery_id = d.id
                        WHERE d.truck_id = %s AND d.Status = 'In Transit' AND d.Deleted = 0
                    """, (truck_id,))
                    deliveries = cursor.fetchall()
                    
                    if deliveries:
                        items = []
                        destinations = set()
                        for item_name, amount, origin, destination in deliveries:
                            items.append(f"{item_name} (x{amount})")
                            if destination:
                                destinations.add(f"{origin} → {destination}")
                        
                        delivery_info = " | ".join(items)
                        if destinations:
                            delivery_info += " | Route: " + ", ".join(destinations)
                
                self.truck_tree.insert("", END, values=(truck_id, plate, model, capacity, f"{status_icon} {status}", delivery_info))
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load trucks: {e}")
    
    def filter_trucks(self):
            # Filter trucks based on search input
        search_text = self.search_var.get().lower()
        self.load_trucks(search_text)
    
    def show_add_truck_form(self):
            # Show form to add a new truck
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
                
                self.clear_form()
                self.load_trucks()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add truck: {e}")
        
        btn_frame = Frame(self.form_frame, bg="#34495E")
        btn_frame.pack(pady=10)
        
        Button(btn_frame, text="Add Truck", bg="#28A745", fg="white", width=12, command=submit).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Cancel", bg="#6C757D", fg="white", width=12, command=self.clear_form).pack(side=LEFT, padx=5)
    
    def show_edit_truck_form(self):
            # Show form to edit selected truck
        selected = self.truck_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a truck to edit")
            return
        truck_item = self.truck_tree.item(selected[0])
        truck_id, license_plate, model, capacity, status, deliveries = truck_item['values']
        if "Maintenance" in status:
            messagebox.showwarning("Unavailable", "This truck is on maintenance and cannot be selected.")
            return
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
                
                self.clear_form()
                self.load_trucks()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update truck: {e}")
        
        btn_frame = Frame(self.form_frame, bg="#34495E")
        btn_frame.pack(pady=10)
        
        Button(btn_frame, text="Update", bg="#007BFF", fg="white", width=12, command=submit).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Cancel", bg="#6C757D", fg="white", width=12, command=self.clear_form).pack(side=LEFT, padx=5)
    
    def show_assign_location_form(self):
            # Show form to assign location to selected truck
        selected = self.truck_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a truck first")
            return
        truck_item = self.truck_tree.item(selected[0])
        truck_id, license_plate, model, capacity, status, deliveries = truck_item['values']
        if "Maintenance" in status:
            messagebox.showwarning("Unavailable", "This truck is on maintenance and cannot be selected.")
            return
        
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
            
            cursor.execute("SELECT id, origin, destination, distance_km, estimated_hours FROM locations WHERE delivery_id IS NULL")
            locations = cursor.fetchall()
            conn.close()
            
            if not deliveries:
                return
            if not locations:
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            return
        
        self.clear_form()
        self.form_frame.pack(fill=X, pady=10, padx=20)
        
        Label(self.form_frame, text="Assign Location to Delivery", bg="#34495E", fg="white",
              font=("Segoe UI", 14, "bold")).pack(pady=15)
        
        delivery_section = Frame(self.form_frame, bg="#34495E")
        delivery_section.pack(pady=10, padx=20, fill=BOTH)
        
        Label(delivery_section, text="Select Deliveries (Multiple):", bg="#34495E", fg="white",
              font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=5)
        
        delivery_frame = Frame(delivery_section, bg="#34495E")
        delivery_frame.pack(fill=BOTH)
        
        delivery_scroll = Scrollbar(delivery_frame, orient=VERTICAL)
        delivery_listbox = Listbox(delivery_frame, height=8, width=70, font=("Segoe UI", 10),
                                   yscrollcommand=delivery_scroll.set, selectmode=MULTIPLE,
                                   exportselection=False)
        delivery_scroll.config(command=delivery_listbox.yview)
        delivery_scroll.pack(side=RIGHT, fill=Y)
        delivery_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        
        for delivery in deliveries:
            delivery_listbox.insert(END, f"ID: {delivery[0]} - {delivery[1]} - Amount: {delivery[2]} - Status: {delivery[3]}")
        
        route_section = Frame(self.form_frame, bg="#34495E")
        route_section.pack(pady=10, padx=20, fill=BOTH)
        
        Label(route_section, text="Select Route:", bg="#34495E", fg="white",
              font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=5)
        
        location_frame = Frame(route_section, bg="#34495E")
        location_frame.pack(fill=BOTH)
        
        location_scroll = Scrollbar(location_frame, orient=VERTICAL)
        location_listbox = Listbox(location_frame, height=10, width=70, font=("Segoe UI", 10),
                                   yscrollcommand=location_scroll.set, selectmode=SINGLE,
                                   exportselection=False)
        location_scroll.config(command=location_listbox.yview)
        location_scroll.pack(side=RIGHT, fill=Y)
        location_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        
        for loc in locations:
            location_listbox.insert(END, f"{loc[1]} → {loc[2]} ({loc[4]} hrs)")
        
        def submit():
            del_sel = delivery_listbox.curselection()
            loc_sel = location_listbox.curselection()
            if len(del_sel) == 0 or len(loc_sel) == 0:
                messagebox.showwarning("No Selection", "Please select at least one delivery and a route")
                return
            
            selected_location = locations[loc_sel[0]]
            origin = selected_location[1]
            destination = selected_location[2]
            distance_km = selected_location[3]
            estimated_hours = selected_location[4]
            
            try:
                conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                cursor = conn.cursor()
                
                success_count = 0
                for idx in del_sel:
                    delivery_id = deliveries[idx][0]
                    
                    # Check if location already exists for this delivery
                    cursor.execute("SELECT id FROM locations WHERE delivery_id = %s", (delivery_id,))
                    existing_location = cursor.fetchone()
                    
                    if existing_location:
                        # Update existing location
                        cursor.execute("""
                            UPDATE locations 
                            SET origin=%s, destination=%s, distance_km=%s, estimated_hours=%s, current_location='En Route'
                            WHERE delivery_id=%s
                        """, (origin, destination, distance_km, estimated_hours, delivery_id))
                    else:
                        # Insert new location
                        cursor.execute("""
                            INSERT INTO locations (origin, destination, distance_km, estimated_hours, current_location, delivery_id)
                            VALUES (%s, %s, %s, %s, 'En Route', %s)
                        """, (origin, destination, distance_km, estimated_hours, delivery_id))
                    
                    cursor.execute("UPDATE deliveries SET truck_id=%s, Status='In Transit' WHERE id=%s", (truck_id, delivery_id))
                    success_count += 1
                
                cursor.execute("UPDATE trucks SET status='In Use' WHERE id=%s", (truck_id,))
                conn.commit()
                conn.close()
                
                self.clear_form()
                self.load_trucks()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to assign: {e}")
        
        btn_frame = Frame(self.form_frame, bg="#34495E")
        btn_frame.pack(pady=10)
        Button(btn_frame, text="Assign", bg="#5DADE2", fg="white", width=12, command=submit).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Cancel", bg="#ABB2B9", fg="white", width=12, command=self.clear_form).pack(side=LEFT, padx=5)
    
    def show_edit_route_form(self):
            # Show form to edit route for selected truck
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.id, i.Name, d.Delivery_Amount, l.origin, l.destination, d.id
                FROM locations l
                JOIN deliveries d ON l.delivery_id = d.id
                JOIN inventory i ON d.inventory_id = i.id
                WHERE d.Status = 'In Transit' AND d.Deleted = 0
            """)
            active_routes = cursor.fetchall()
            
            cursor.execute("SELECT id, origin, destination, distance_km, estimated_hours FROM locations WHERE delivery_id IS NULL")
            all_locations = cursor.fetchall()
            conn.close()
            
            if not active_routes:
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load routes: {e}")
            return
        
        self.clear_form()
        self.form_frame.pack(fill=X, pady=10, padx=20)
        
        Label(self.form_frame, text="Edit Route", bg="#34495E", fg="white",
              font=("Segoe UI", 14, "bold")).pack(pady=15)
        
        current_section = Frame(self.form_frame, bg="#34495E")
        current_section.pack(pady=10, padx=20, fill=BOTH)
        
        Label(current_section, text="Select Active Delivery:", bg="#34495E", fg="white",
              font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=5)
        
        route_frame = Frame(current_section, bg="#34495E")
        route_frame.pack(fill=BOTH)
        
        route_scroll = Scrollbar(route_frame, orient=VERTICAL)
        route_listbox = Listbox(route_frame, height=8, width=70, font=("Segoe UI", 10),
                               yscrollcommand=route_scroll.set, selectmode=SINGLE,
                               exportselection=False)
        route_scroll.config(command=route_listbox.yview)
        route_scroll.pack(side=RIGHT, fill=Y)
        route_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        
        for route in active_routes:
            route_listbox.insert(END, f"{route[1]} - Amount: {route[2]} | Current: {route[3]} → {route[4]}")
        
        new_route_section = Frame(self.form_frame, bg="#34495E")
        new_route_section.pack(pady=10, padx=20, fill=BOTH)
        
        Label(new_route_section, text="Select New Route:", bg="#34495E", fg="white",
              font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=5)
        
        location_frame = Frame(new_route_section, bg="#34495E")
        location_frame.pack(fill=BOTH)
        
        location_scroll = Scrollbar(location_frame, orient=VERTICAL)
        location_listbox = Listbox(location_frame, height=10, width=70, font=("Segoe UI", 10),
                                   yscrollcommand=location_scroll.set, selectmode=SINGLE,
                                   exportselection=False)
        location_scroll.config(command=location_listbox.yview)
        location_scroll.pack(side=RIGHT, fill=Y)
        location_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        
        for loc in all_locations:
            location_listbox.insert(END, f"{loc[1]} → {loc[2]} ({loc[4]} hrs)")
        
        def submit():
            route_sel = route_listbox.curselection()
            loc_sel = location_listbox.curselection()
            if len(route_sel) == 0 or len(loc_sel) == 0:
                messagebox.showwarning("No Selection", "Please select both delivery and new route")
                return
            
            old_location_id = active_routes[route_sel[0]][0]
            delivery_id = active_routes[route_sel[0]][5]
            new_location = all_locations[loc_sel[0]]
            new_origin = new_location[1]
            new_destination = new_location[2]
            new_distance_km = new_location[3]
            new_estimated_hours = new_location[4]
            
            try:
                conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM locations WHERE id=%s", (old_location_id,))
                cursor.execute("""
                    INSERT INTO locations (origin, destination, distance_km, estimated_hours, current_location, delivery_id)
                    VALUES (%s, %s, %s, %s, 'En Route', %s)
                """, (new_origin, new_destination, new_distance_km, new_estimated_hours, delivery_id))
                conn.commit()
                conn.close()
                
                self.clear_form()
                self.load_trucks()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update route: {e}")
        
        btn_frame = Frame(self.form_frame, bg="#34495E")
        btn_frame.pack(pady=10)
        Button(btn_frame, text="Update", bg="#5DADE2", fg="white", width=12, command=submit).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Cancel", bg="#ABB2B9", fg="white", width=12, command=self.clear_form).pack(side=LEFT, padx=5)
    
    def set_maintenance(self):
            # Set selected truck status to Maintenance
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
            
            self.load_trucks()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update truck: {e}")
    
    def set_available(self):
            # Set selected truck status to Available
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
            
            self.load_trucks()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update truck: {e}")
    
    def clear_form(self):
        try:
            for widget in self.form_frame.winfo_children():
                widget.destroy()
            self.form_frame.pack_forget()
        except:
            pass
