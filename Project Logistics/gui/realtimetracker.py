from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Treeview
import mysql.connector


class RealTimeTracker:
    def __init__(self, parent_frame, main_window):
        self.parent_frame = parent_frame
        self.main_window = main_window
        
    def show(self):
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        title_frame = Frame(self.parent_frame, bg="#34495E", height=60)
        title_frame.pack(fill=X)
        title_frame.pack_propagate(False)
        
        if self.main_window:
            Button(title_frame, text="← Dashboard", bg="#3498db", fg="white",
                   font=("Segoe UI", 10, "bold"), command=self.main_window.show_dashboard).pack(side=LEFT, padx=20, pady=15)
        
        title_container = Frame(title_frame, bg="#34495E")
        title_container.place(relx=0.5, rely=0.5, anchor=CENTER)
        Label(title_container, text="📍 Real-Time Tracker", bg="#34495E", fg="white",
              font=("Segoe UI", 16, "bold")).pack()
        
        content_container = Frame(self.parent_frame, bg="#2E4057")
        content_container.pack(fill=BOTH, expand=True)
        
        center_frame = Frame(content_container, bg="#2E4057")
        center_frame.pack(expand=True, pady=20, padx=50)
        
        action_frame = Frame(center_frame, bg="#2E4057")
        action_frame.pack(fill=X, pady=10)
        
        Button(action_frame, text="Refresh", bg="#5DADE2", fg="white", width=18,
               font=("Segoe UI", 10), command=self.refresh_all).pack(side=LEFT, padx=5)
        Button(action_frame, text="Add Location", bg="#52BE80", fg="white", width=18,
               font=("Segoe UI", 10), command=self.show_add_location_form).pack(side=LEFT, padx=5)
        
        list_frame = Frame(center_frame, bg="#2E4057")
        list_frame.pack(fill=BOTH, expand=True, pady=10)
        
        header_frame = Frame(list_frame, bg="#2E4057")
        header_frame.pack(fill=X, pady=5)
        
        Label(header_frame, text="Active Deliveries", bg="#2E4057", fg="white",
              font=("Segoe UI", 12, "bold")).pack(side=LEFT)
        
        search_frame = Frame(header_frame, bg="#2E4057")
        search_frame.pack(side=RIGHT)
        
        Label(search_frame, text="Search:", bg="#2E4057", fg="white",
              font=("Segoe UI", 10)).pack(side=LEFT, padx=(0, 5))
        
        self.search_var = StringVar()
        self.search_var.trace('w', lambda *args: self.filter_tracker())
        search_entry = Entry(search_frame, textvariable=self.search_var, width=30,
                           font=("Segoe UI", 10))
        search_entry.pack(side=LEFT)
        
        Button(search_frame, text="✖", bg="#EC7063", fg="white", width=3,
               font=("Segoe UI", 9), command=lambda: self.search_var.set("")).pack(side=LEFT, padx=5)
        
        columns = ("Delivery ID", "Item", "Amount", "Truck ID", "License Plate", "Status")
        self.tracker_tree = Treeview(list_frame, columns=columns, show="headings", height=8)
        
        widths = [100, 200, 80, 80, 120, 100]
        for col, width in zip(columns, widths):
            self.tracker_tree.heading(col, text=col)
            self.tracker_tree.column(col, width=width, anchor=CENTER)
        
        scrollbar = Scrollbar(list_frame, orient=VERTICAL, command=self.tracker_tree.yview)
        self.tracker_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tracker_tree.pack(fill=BOTH, expand=True)
        
        header_frame2 = Frame(list_frame, bg="#2E4057")
        header_frame2.pack(fill=X, pady=(15, 5))
        
        Label(header_frame2, text="Delivery Routes & Locations", bg="#2E4057", fg="white",
              font=("Segoe UI", 12, "bold")).pack(side=LEFT)
        
        search_frame2 = Frame(header_frame2, bg="#2E4057")
        search_frame2.pack(side=RIGHT)
        
        Label(search_frame2, text="Search:", bg="#2E4057", fg="white",
              font=("Segoe UI", 10)).pack(side=LEFT, padx=(0, 5))
        
        self.search_location_var = StringVar()
        self.search_location_var.trace('w', lambda *args: self.filter_locations())
        search_entry2 = Entry(search_frame2, textvariable=self.search_location_var, width=30,
                           font=("Segoe UI", 10))
        search_entry2.pack(side=LEFT)
        
        Button(search_frame2, text="✖", bg="#EC7063", fg="white", width=3,
               font=("Segoe UI", 9), command=lambda: self.search_location_var.set("")).pack(side=LEFT, padx=5)
        
        location_columns = ("Truck", "Origin", "Destination", "Current Location", "Est. Hours")
        self.location_tree = Treeview(list_frame, columns=location_columns, show="headings", height=8)
        
        location_widths = [200, 200, 200, 150, 100]
        for col, width in zip(location_columns, location_widths):
            self.location_tree.heading(col, text=col)
            self.location_tree.column(col, width=width, anchor=CENTER)
        
        location_scrollbar = Scrollbar(list_frame, orient=VERTICAL, command=self.location_tree.yview)
        self.location_tree.configure(yscroll=location_scrollbar.set)
        location_scrollbar.pack(side=RIGHT, fill=Y)
        self.location_tree.pack(fill=BOTH, expand=True)
        
        stats_frame = Frame(center_frame, bg="#34495E", relief=RAISED, bd=2)
        stats_frame.pack(fill=X, pady=10)
        
        Label(stats_frame, text="📊 Statistics", bg="#34495E", fg="white",
              font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        self.stats_container = Frame(stats_frame, bg="#34495E")
        self.stats_container.pack(pady=10, padx=20, fill=X)
        
        self.load_active_deliveries()
        self.load_locations()
        self.load_statistics()
    
    def refresh_all(self):
        self.load_active_deliveries()
        self.load_locations()
        self.load_statistics()
    
    def load_active_deliveries(self, search_text=""):
        for item in self.tracker_tree.get_children():
            self.tracker_tree.delete(item)
        
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.id, i.Name, d.Delivery_Amount, d.truck_id, 
                       t.license_plate, d.Status
                FROM deliveries d
                LEFT JOIN inventory i ON d.inventory_id = i.id
                LEFT JOIN trucks t ON d.truck_id = t.id
                WHERE d.Status = 'In Transit' AND d.Deleted = 0
                ORDER BY d.id DESC
            """)
            
            for row in cursor.fetchall():
                delivery_id, name, amount, truck_id, license_plate, status = row
                
                # Apply search filter
                if search_text and not (search_text in str(delivery_id).lower() or 
                                       search_text in str(name).lower() or 
                                       search_text in str(truck_id).lower() or 
                                       search_text in str(license_plate).lower() or 
                                       search_text in str(status).lower()):
                    continue
                
                self.tracker_tree.insert("", END, values=(
                    delivery_id,
                    name or "N/A",
                    amount,
                    truck_id if truck_id else "N/A",
                    license_plate or "N/A",
                    status
                ))
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load active deliveries: {e}")
    
    def load_locations(self, search_text=""):
        for item in self.location_tree.get_children():
            self.location_tree.delete(item)
        
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.origin, l.destination, l.current_location, 
                       l.estimated_hours, t.license_plate, t.model
                FROM locations l
                INNER JOIN deliveries d ON l.delivery_id = d.id
                LEFT JOIN trucks t ON d.truck_id = t.id
                WHERE d.Status = 'In Transit' AND d.Deleted = 0
                ORDER BY l.id ASC
            """)
            
            for row in cursor.fetchall():
                origin, destination, current_loc, est_hours, license_plate, model = row
                truck_display = f"{license_plate} ({model})" if license_plate else "No Truck"
                
                # Apply search filter
                if search_text and not (search_text in str(origin).lower() or 
                                       search_text in str(destination).lower() or 
                                       search_text in str(current_loc).lower() or 
                                       search_text in str(license_plate).lower() or 
                                       search_text in str(model).lower()):
                    continue
                
                self.location_tree.insert("", END, values=(
                    truck_display,
                    origin or "N/A",
                    destination or "N/A",
                    current_loc or "En Route",
                    f"{est_hours:.1f}" if est_hours else "N/A"
                ))
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load locations: {e}")
    
    def filter_tracker(self):
        search_text = self.search_var.get().lower()
        self.load_active_deliveries(search_text)
    
    def filter_locations(self):
        search_text = self.search_location_var.get().lower()
        self.load_locations(search_text)
    
    def load_statistics(self):
        for widget in self.stats_container.winfo_children():
            widget.destroy()
        
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM deliveries WHERE Deleted=0")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM deliveries WHERE Status='Pending' AND Deleted=0")
            pending = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM deliveries WHERE Status='In Transit' AND Deleted=0")
            in_transit = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM deliveries WHERE Status='Delivered' AND Deleted=0")
            delivered = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM trucks WHERE status='Available' AND deleted=0")
            available_trucks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM trucks WHERE status='In Use' AND deleted=0")
            trucks_in_use = cursor.fetchone()[0]
            
            conn.close()
            
            stats = [
                ("Total Deliveries", total, "#3498db"),
                ("Pending", pending, "#f39c12"),
                ("In Transit", in_transit, "#e74c3c"),
                ("Delivered", delivered, "#2ecc71"),
                ("Available Trucks", available_trucks, "#1abc9c"),
                ("Trucks in Use", trucks_in_use, "#9b59b6")
            ]
            
            for label_text, value, color in stats:
                stat_frame = Frame(self.stats_container, bg=color, relief=RAISED, bd=1)
                stat_frame.pack(side=LEFT, padx=10, pady=5, ipadx=20, ipady=10)
                
                Label(stat_frame, text=label_text, bg=color, fg="white",
                      font=("Segoe UI", 10, "bold")).pack()
                Label(stat_frame, text=str(value), bg=color, fg="white",
                      font=("Segoe UI", 18, "bold")).pack()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load statistics: {e}")
    
    def show_add_location_form(self):
        add_window = Toplevel(self.main_window.window)
        add_window.title("Add Location")
        add_window.geometry("500x400")
        add_window.resizable(False, False)
        add_window.config(bg="#34495E")
        
        x = (add_window.winfo_screenwidth() // 2) - 250
        y = (add_window.winfo_screenheight() // 2) - 200
        add_window.geometry(f"500x400+{x}+{y}")
        
        Label(add_window, text="Add New Route", bg="#34495E", fg="white",
              font=("Segoe UI", 14, "bold")).pack(pady=20)
        
        form_frame = Frame(add_window, bg="#34495E")
        form_frame.pack(pady=10, padx=40, fill=BOTH)
        
        Label(form_frame, text="Origin:", bg="#34495E", fg="white",
              font=("Segoe UI", 11)).grid(row=0, column=0, sticky=W, pady=10)
        origin_entry = Entry(form_frame, width=30, font=("Segoe UI", 10))
        origin_entry.grid(row=0, column=1, pady=10, padx=10)
        
        Label(form_frame, text="Destination:", bg="#34495E", fg="white",
              font=("Segoe UI", 11)).grid(row=1, column=0, sticky=W, pady=10)
        destination_entry = Entry(form_frame, width=30, font=("Segoe UI", 10))
        destination_entry.grid(row=1, column=1, pady=10, padx=10)
        
        Label(form_frame, text="Distance (km):", bg="#34495E", fg="white",
              font=("Segoe UI", 11)).grid(row=2, column=0, sticky=W, pady=10)
        distance_entry = Entry(form_frame, width=30, font=("Segoe UI", 10))
        distance_entry.grid(row=2, column=1, pady=10, padx=10)
        
        Label(form_frame, text="Estimated Hours:", bg="#34495E", fg="white",
              font=("Segoe UI", 11)).grid(row=3, column=0, sticky=W, pady=10)
        hours_entry = Entry(form_frame, width=30, font=("Segoe UI", 10))
        hours_entry.grid(row=3, column=1, pady=10, padx=10)
        
        def save_location():
            origin = origin_entry.get().strip()
            destination = destination_entry.get().strip()
            distance = distance_entry.get().strip()
            hours = hours_entry.get().strip()
            
            if not all([origin, destination, distance, hours]):
                messagebox.showwarning("Validation Error", "Please fill all fields")
                return
            
            try:
                distance_km = float(distance)
                estimated_hours = float(hours)
            except ValueError:
                messagebox.showerror("Error", "Distance and Hours must be numbers")
                return
            
            try:
                conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO locations (origin, destination, distance_km, estimated_hours, current_location)
                    VALUES (%s, %s, %s, %s, 'En Route')
                """, (origin, destination, distance_km, estimated_hours))
                conn.commit()
                conn.close()
                
                add_window.destroy()
                self.load_locations()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add location: {e}")
        
        btn_frame = Frame(add_window, bg="#34495E")
        btn_frame.pack(pady=20)
        
        Button(btn_frame, text="Save", bg="#52BE80", fg="white",
               font=("Segoe UI", 11, "bold"), width=12, command=save_location).pack(side=LEFT, padx=10)
        Button(btn_frame, text="Cancel", bg="#ABB2B9", fg="white",
               font=("Segoe UI", 11, "bold"), width=12, command=add_window.destroy).pack(side=LEFT, padx=10)