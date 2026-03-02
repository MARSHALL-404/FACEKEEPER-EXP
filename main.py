"""
Digital Attendance System using Face Recognition
Main entry point with CLI interface
"""

import sys
import os
from database import AttendanceDatabase
from face_register import FaceRegistration
from attendance import AttendanceSystem
from utils.report_generator import ReportGenerator
from utils.helpers import (
    validate_roll_number,
    validate_name,
    get_current_date
)


def print_banner():
    """Display application banner."""
    print("\n" + "=" * 60)
    print("    DIGITAL ATTENDANCE SYSTEM - FACE RECOGNITION")
    print("=" * 60 + "\n")


def print_menu():
    """Display main menu options."""
    print("\n📋 MAIN MENU")
    print("━" * 50)
    print("1. Register New Face")
    print("2. Start Attendance System")
    print("3. View Today's Attendance")
    print("4. View All Registered Users")
    print("5. Generate Reports")
    print("6. View Statistics")
    print("7. Re-train Face Recognizer")
    print("8. Exit")
    print("━" * 50)


def register_new_face(db, face_reg):
    """Handle face registration process."""
    print("\n" + "=" * 60)
    print("FACE REGISTRATION")
    print("=" * 60)
    
    # Get user details
    while True:
        roll_number = input("\nEnter Roll Number/ID: ").strip()
        if validate_roll_number(roll_number):
            break
        print("✗ Invalid roll number. Please try again.")
    
    while True:
        name = input("Enter Full Name: ").strip()
        if validate_name(name):
            break
        print("✗ Invalid name. Please enter at least 2 characters.")
    
    # Capture face samples
    print(f"\nPreparing to capture face samples for {name}...")
    input("Press Enter when ready to start camera...")
    
    success = face_reg.capture_face_samples(roll_number, name)
    
    if success:
        print("\n" + "─" * 60)
        print("Training face recognizer with new data...")
        face_reg.train_recognizer()
        print("✓ Registration complete! User can now mark attendance.")
    else:
        print("\n✗ Registration failed. Please try again.")


def start_attendance_system(db, attendance_sys):
    """Start the attendance marking system."""
    print("\n" + "=" * 60)
    print("ATTENDANCE SYSTEM")
    print("=" * 60)
    
    attendance_sys.start_attendance()


def view_today_attendance(db, attendance_sys):
    """Display today's attendance records."""
    attendance_sys.view_today_attendance()


def view_all_users(db):
    """Display all registered users."""
    users = db.get_all_users()
    print("\n" + "=" * 60)
    print("REGISTERED USERS")
    print("=" * 60)
    
    if not users:
        print("\nNo users registered yet.")
    else:
        print(f"\n{'ID':<5} {'Roll Number':<15} {'Name':<30}")
        print("─" * 60)
        for user_id, roll_number, name in users:
            print(f"{user_id:<5} {roll_number:<15} {name:<30}")
    
    print("=" * 60 + "\n")


def generate_reports(db, report_gen):
    """Report generation submenu."""
    while True:
        print("\n📊 REPORT GENERATION")
        print("━" * 50)
        print("1. Generate Today's Report (CSV)")
        print("2. Generate Today's Report (Excel)")
        print("3. Generate Full Report (CSV)")
        print("4. Generate Full Report (Excel)")
        print("5. Generate User-specific Report")
        print("6. Back to Main Menu")
        print("━" * 50)
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            report_gen.generate_daily_report(export_format='csv')
        elif choice == '2':
            report_gen.generate_daily_report(export_format='excel')
        elif choice == '3':
            report_gen.generate_full_report(export_format='csv')
        elif choice == '4':
            report_gen.generate_full_report(export_format='excel')
        elif choice == '5':
            roll_number = input("\nEnter Roll Number: ").strip()
            format_choice = input("Format (csv/excel): ").strip().lower()
            if format_choice in ['csv', 'excel']:
                report_gen.generate_user_report(roll_number, format_choice)
            else:
                print("✗ Invalid format. Using CSV.")
                report_gen.generate_user_report(roll_number, 'csv')
        elif choice == '6':
            break
        else:
            print("✗ Invalid option. Please try again.")


def view_statistics(db, report_gen):
    """Display attendance statistics."""
    report_gen.display_statistics()


def retrain_recognizer(face_reg):
    """Re-train the face recognizer."""
    print("\n" + "=" * 60)
    print("RE-TRAINING FACE RECOGNIZER")
    print("=" * 60)
    
    print("\nThis will re-train the recognizer with all registered faces...")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm == 'y':
        recognizer, label_map = face_reg.train_recognizer()
        if recognizer:
            print("✓ Re-training successful!")
        else:
            print("✗ Re-training failed.")
    else:
        print("Cancelled.")


def main():
    """Main application loop."""
    # Initialize database
    db = AttendanceDatabase()
    
    # Initialize modules
    face_reg = FaceRegistration(db)
    attendance_sys = AttendanceSystem(db)
    report_gen = ReportGenerator(db)
    
    print_banner()
    print("Welcome to the Digital Attendance System!")
    print(f"Today's Date: {get_current_date()}\n")
    
    # Main application loop
    while True:
        print_menu()
        choice = input("\nSelect option (1-8): ").strip()
        
        try:
            if choice == '1':
                register_new_face(db, face_reg)
            elif choice == '2':
                start_attendance_system(db, attendance_sys)
            elif choice == '3':
                view_today_attendance(db, attendance_sys)
            elif choice == '4':
                view_all_users(db)
            elif choice == '5':
                generate_reports(db, report_gen)
            elif choice == '6':
                view_statistics(db, report_gen)
            elif choice == '7':
                retrain_recognizer(face_reg)
            elif choice == '8':
                print("\n" + "=" * 60)
                print("Thank you for using the Attendance System!")
                print("=" * 60 + "\n")
                db.close()
                sys.exit(0)
            else:
                print("\n✗ Invalid option. Please select 1-8.")
        except KeyboardInterrupt:
            print("\n\n✗ Operation cancelled by user.")
            continue
        except Exception as e:
            print(f"\n✗ An error occurred: {e}")
            continue


if __name__ == "__main__":
    main()
