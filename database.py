"""
Database module for handling SQLite database operations.
Manages user information and attendance records.
"""

import sqlite3
from datetime import datetime
import os


class AttendanceDatabase:
    def __init__(self, db_name="attendance.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish connection to SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"✓ Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            print(f"✗ Database connection error: {e}")
    
    def create_tables(self):
        """Create users and attendance tables if they don't exist."""
        try:
            # Users table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    roll_number TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Attendance table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    time TIME NOT NULL,
                    status TEXT DEFAULT 'Present',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, date)
                )
            ''')
            
            self.conn.commit()
            print("✓ Database tables verified/created")
        except sqlite3.Error as e:
            print(f"✗ Error creating tables: {e}")
    
    def add_user(self, roll_number, name):
        """
        Add a new user to the database.
        
        Args:
            roll_number (str): Unique roll number/ID for the user
            name (str): Full name of the user
            
        Returns:
            int: User ID if successful, None otherwise
        """
        try:
            self.cursor.execute(
                "INSERT INTO users (roll_number, name) VALUES (?, ?)",
                (roll_number, name)
            )
            self.conn.commit()
            user_id = self.cursor.lastrowid
            print(f"✓ User added: {name} (Roll: {roll_number})")
            return user_id
        except sqlite3.IntegrityError:
            print(f"✗ User with roll number {roll_number} already exists")
            return None
        except sqlite3.Error as e:
            print(f"✗ Error adding user: {e}")
            return None
    
    def get_user_by_roll(self, roll_number):
        """Get user information by roll number."""
        try:
            self.cursor.execute(
                "SELECT id, roll_number, name FROM users WHERE roll_number = ?",
                (roll_number,)
            )
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"✗ Error fetching user: {e}")
            return None
    
    def get_all_users(self):
        """Get all registered users."""
        try:
            self.cursor.execute("SELECT id, roll_number, name FROM users ORDER BY name")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"✗ Error fetching users: {e}")
            return []
    
    def mark_attendance(self, user_id, date=None, time=None):
        """
        Mark attendance for a user. Prevents duplicate entries for the same day.
        
        Args:
            user_id (int): User ID
            date (str): Date in YYYY-MM-DD format (default: today)
            time (str): Time in HH:MM:SS format (default: now)
            
        Returns:
            bool: True if attendance marked, False if duplicate
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        if time is None:
            time = datetime.now().strftime("%H:%M:%S")
        
        try:
            self.cursor.execute(
                "INSERT INTO attendance (user_id, date, time) VALUES (?, ?, ?)",
                (user_id, date, time)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Duplicate entry - user already marked for this date
            return False
        except sqlite3.Error as e:
            print(f"✗ Error marking attendance: {e}")
            return False
    
    def get_attendance_by_date(self, date=None):
        """
        Get attendance records for a specific date.
        
        Args:
            date (str): Date in YYYY-MM-DD format (default: today)
            
        Returns:
            list: List of tuples (name, roll_number, time, status)
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            self.cursor.execute('''
                SELECT u.name, u.roll_number, a.time, a.status
                FROM attendance a
                JOIN users u ON a.user_id = u.id
                WHERE a.date = ?
                ORDER BY a.time
            ''', (date,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"✗ Error fetching attendance: {e}")
            return []
    
    def get_user_attendance_stats(self, user_id):
        """Get attendance statistics for a specific user."""
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM attendance WHERE user_id = ?",
                (user_id,)
            )
            total_days = self.cursor.fetchone()[0]
            return total_days
        except sqlite3.Error as e:
            print(f"✗ Error fetching stats: {e}")
            return 0
    
    def get_all_attendance_records(self):
        """Get all attendance records with user details."""
        try:
            self.cursor.execute('''
                SELECT u.name, u.roll_number, a.date, a.time, a.status
                FROM attendance a
                JOIN users u ON a.user_id = u.id
                ORDER BY a.date DESC, a.time DESC
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"✗ Error fetching all records: {e}")
            return []
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")
