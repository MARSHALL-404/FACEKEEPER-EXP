"""
Report Generator Module
Generate CSV/Excel reports of attendance records.
"""

import pandas as pd
from datetime import datetime
import os


class ReportGenerator:
    def __init__(self, db):
        """
        Initialize Report Generator.
        
        Args:
            db: AttendanceDatabase instance
        """
        self.db = db
        self.reports_dir = "attendance_reports"
        
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    def generate_daily_report(self, date=None, export_format='csv'):
        """
        Generate attendance report for a specific date.
        
        Args:
            date (str): Date in YYYY-MM-DD format (default: today)
            export_format (str): 'csv' or 'excel'
            
        Returns:
            str: Path to generated report file
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Get attendance records
        records = self.db.get_attendance_by_date(date)
        
        if not records:
            print(f"✗ No attendance records found for {date}")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(
            records,
            columns=['Name', 'Roll Number', 'Time', 'Status']
        )
        
        # Generate filename
        filename = f"attendance_{date}"
        
        if export_format.lower() == 'excel':
            filepath = os.path.join(self.reports_dir, f"{filename}.xlsx")
            df.to_excel(filepath, index=False, sheet_name='Attendance')
        else:
            filepath = os.path.join(self.reports_dir, f"{filename}.csv")
            df.to_csv(filepath, index=False)
        
        print(f"✓ Report generated: {filepath}")
        print(f"  Total records: {len(records)}\n")
        
        return filepath
    
    def generate_full_report(self, export_format='csv'):
        """
        Generate complete attendance report with all records.
        
        Args:
            export_format (str): 'csv' or 'excel'
            
        Returns:
            str: Path to generated report file
        """
        # Get all attendance records
        records = self.db.get_all_attendance_records()
        
        if not records:
            print("✗ No attendance records found")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(
            records,
            columns=['Name', 'Roll Number', 'Date', 'Time', 'Status']
        )
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"attendance_full_{timestamp}"
        
        if export_format.lower() == 'excel':
            filepath = os.path.join(self.reports_dir, f"{filename}.xlsx")
            df.to_excel(filepath, index=False, sheet_name='All Attendance')
        else:
            filepath = os.path.join(self.reports_dir, f"{filename}.csv")
            df.to_csv(filepath, index=False)
        
        print(f"✓ Full report generated: {filepath}")
        print(f"  Total records: {len(records)}\n")
        
        return filepath
    
    def generate_user_report(self, roll_number, export_format='csv'):
        """
        Generate attendance report for a specific user.
        
        Args:
            roll_number (str): User's roll number
            export_format (str): 'csv' or 'excel'
            
        Returns:
            str: Path to generated report file
        """
        # Get user info
        user = self.db.get_user_by_roll(roll_number)
        
        if not user:
            print(f"✗ User with roll number {roll_number} not found")
            return None
        
        user_id, roll_number, name = user
        
        # Get attendance records for this user
        try:
            self.db.cursor.execute('''
                SELECT date, time, status
                FROM attendance
                WHERE user_id = ?
                ORDER BY date DESC, time DESC
            ''', (user_id,))
            records = self.db.cursor.fetchall()
        except Exception as e:
            print(f"✗ Error fetching user records: {e}")
            return None
        
        if not records:
            print(f"✗ No attendance records found for {name}")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(
            records,
            columns=['Date', 'Time', 'Status']
        )
        
        # Add user info
        df.insert(0, 'Name', name)
        df.insert(1, 'Roll Number', roll_number)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"attendance_{roll_number}_{timestamp}"
        
        if export_format.lower() == 'excel':
            filepath = os.path.join(self.reports_dir, f"{filename}.xlsx")
            df.to_excel(filepath, index=False, sheet_name=name)
        else:
            filepath = os.path.join(self.reports_dir, f"{filename}.csv")
            df.to_csv(filepath, index=False)
        
        print(f"✓ User report generated: {filepath}")
        print(f"  Total attendance days: {len(records)}\n")
        
        return filepath
    
    def display_statistics(self):
        """Display attendance statistics."""
        users = self.db.get_all_users()
        
        if not users:
            print("✗ No users registered")
            return
        
        print("\n📊 Attendance Statistics")
        print("━" * 70)
        print(f"{'Name':<25} {'Roll Number':<15} {'Total Days Present':<20}")
        print("─" * 70)
        
        for user_id, roll_number, name in users:
            total_days = self.db.get_user_attendance_stats(user_id)
            print(f"{name:<25} {roll_number:<15} {total_days:<20}")
        
        print("━" * 70 + "\n")
