"""
Logistics Management System
Main entry point for the application

This application manages inventory, deliveries, fleet, and real-time tracking
for a logistics company.

Requirements:
- Python 
- tkinter
- mysql-connector-python
- MySQL/MariaDB server running on localhost

Database: inventories
Tables: inventory, trucks, deliveries, categories, locations

To run: python main.py
"""

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
gui_dir = os.path.join(current_dir, 'gui')
sys.path.insert(0, gui_dir)

if __name__ == "__main__":
    try:
        from login import LoginWindow  # type: ignore
        
        app = LoginWindow()
        app.window.mainloop()
    
    except ImportError as e:
        print(f"Error: Missing required module - {e}")
        print("\nPlease install required packages:")
        print("  pip install mysql-connector-python")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
