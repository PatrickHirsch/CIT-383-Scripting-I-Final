#!/usr/bin/env python3

# Import standard modules used for system tasks, file handling, process execution, and logging
import argparse
import os
import shutil
import csv
import subprocess
import time
import psutil
import logging

# Configure logging to capture both INFO and ERROR messages in a logfile
logFile = 'error_log_group_4.log'
logging.basicConfig(filename=logFile, level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Handle the "user" subcommand and route to the appropriate function based on argument
def handle_user(args):
    if args.create:
        create_user(args.username, args.role)
    elif args.create_batch:
        create_users_from_csv(args.csv)
    elif args.delete:
        delete_user(args.username)
    elif args.update:
        update_user(args.username, args.password)

# Handle the "organize" subcommand
def handle_organize(args):
    if args.dir:
        organize_directory(args.dir)
    elif args.log_monitor:
        monitor_log(args.log_monitor)

# Handle the "monitor" subcommand
def handle_monitor(args):
    if args.system:
        monitor_system()
    elif args.disk:
        check_disk_space(args.dir, args.threshold)

# Function to create a single user with a specific role
# Adds user to admin group if specified
# Assumes this script is run with sudo permissions

def create_user(username, role):
    try:
        if ' ' in username:
            raise ValueError("Invalid username format. Usernames should not contain spaces.")
        print(f"[INFO] Creating user '{username}' with role '{role}'.")
        logging.info(f"Creating user '{username}' with role '{role}'.")
        subprocess.run(['sudo', 'useradd', '-m', username], check=True)
        print(f"[INFO] User '{username}' created successfully with home directory /home/{username}")
        logging.info(f"User '{username}' created successfully with home directory /home/{username}")
        if role == 'admin':
            subprocess.run(['sudo', 'usermod', '-aG', 'wheel', username], check=True)
            print(f"[INFO] Role 'admin' assigned with full access permissions.")
            logging.info(f"Role 'admin' assigned with full access permissions.")
    except Exception as e:
        logging.error(str(e))
        print(f"[ERROR] {e}")
        print(f"[INFO] Error logged to {logFile}.")

# Function to create multiple users from a CSV file
# Adds validation for CSV format, roles, and password strength

def create_users_from_csv(csv_path):
    try:
        with open(csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames
            required_headers = {'username', 'role', 'password'}
            if not required_headers.issubset(set(headers)):
                raise ValueError("CSV missing required headers: username, role, password")

            print(f"[INFO] Creating users from CSV file: {csv_path}")
            logging.info(f"Creating users from CSV file: {csv_path}")

            for row in reader:
                username = row['username']
                role = row['role'].lower()
                password = row['password']

                # Reject if role is not one of the accepted values
                if role not in ['admin', 'user']:
                    error_msg = f"Invalid role specified for user '{username}' in CSV file."
                    print(f"[ERROR] {error_msg}")
                    logging.error(error_msg)
                    print(f"[INFO] Skipping user '{username}'.")
                    logging.info(f"Skipping user '{username}'.")
                    continue

                # Reject if password is blank or too short
                if not password or len(password) < 8:
                    error_msg = f"Invalid password for user '{username}': must be at least 8 characters."
                    print(f"[ERROR] {error_msg}")
                    logging.error(error_msg)
                    print(f"[INFO] Skipping user '{username}'.")
                    logging.info(f"Skipping user '{username}'.")
                    continue

                try:
                    subprocess.run(['sudo', 'useradd', '-m', username], check=True)
                    # More secure password setting via subprocess with piped input
                    proc = subprocess.Popen(['sudo', 'chpasswd'], stdin=subprocess.PIPE)
                    proc.communicate(f"{username}:{password}\n".encode())
                    if role == 'admin':
                        subprocess.run(['sudo', 'usermod', '-aG', 'wheel', username], check=True)
                    print(f"[INFO] Creating user '{username}' with role '{role}'.")
                    logging.info(f"Creating user '{username}' with role '{role}'.")
                except Exception as e:
                    logging.error(str(e))
                    print(f"[ERROR] Skipping {username}: {e}")
        print("[INFO] Batch user creation completed successfully.")
        logging.info("Batch user creation completed successfully.")
    except FileNotFoundError:
        logging.error("CSV file not found.")
        print("[ERROR] CSV file not found.")
    except Exception as e:
        logging.error(str(e))
        print(f"[ERROR] {e}")

# Function to delete a user account and their home directory

def delete_user(username):
    try:
        print(f"[INFO] Deletng user '{username}'.")
        logging.info(f"Deleting user '{username}'.")
        subprocess.run(['sudo', 'userdel', '-r', username], check=True)
        print(f"[INFO] User '{username}' deleted successfully.")
        logging.info(f"User '{username}' deleted successfully.")
    except Exception as e:
        logging.error(str(e))
        print(f"[ERROR] {e}")

# Function to update the password of an existing user
# Uses subprocess and stdin to safely set password

def update_user(username, password=None):
    try:
        print(f"[INFO] Updating information for user '{username}'")
        logging.info(f"Updating information for user '{username}'")
        if password:
            proc = subprocess.Popen(['sudo', 'chpasswd'], stdin=subprocess.PIPE)
            proc.communicate(f"{username}:{password}\n".encode())
            print(f"[INFO] Password updated successfully for '{username}'.")
            logging.info(f"Password updated successfully for '{username}'.")
        else:
            print("[INFO] No password provided. Nothing updated.")
            logging.info("No password provided. Nothing updated.")
    except Exception as e:
        logging.error(str(e))
        print(f"[ERROR] {e}")

# Function to organize all files in a directory by file extension
# Files are moved into folders named like "txt_files", "log_files", etc.

def organize_directory(directory):
    try:
        if not os.path.isdir(directory):
            raise ValueError("Invalid directory.")
        print(f"[INFO] Organizing files in {directory} by type")
        logging.info(f"Organizing files in {directory} by type")
        seenExtentions = []
        for filename in os.listdir(directory):
            path = os.path.join(directory, filename)
            if os.path.isfile(path):
                ext = filename.split('.')[-1]
                folder = os.path.join(directory, f"{ext}_files")
                if not os.path.exists(folder):
                    os.makedirs(folder)
                shutil.move(path, os.path.join(folder, filename))
                if ext not in seenExtentions:
                    print(f"[INFO] Moved .{ext} files to {folder}")
                    logging.info(f"Moved .{ext} files to {folder}")
                    seenExtentions.append(ext)
        print(f"[INFO] Directory organization complete.")
        logging.info(f"Directory organization complete.")
    except Exception as e:
        logging.error(str(e))
        print(f"[ERROR] {e}")

# Function to summarize a log file for errors, warnings, and critical messages

def monitor_log(log_path):
    try:
        print(f"[INFO] Monitoring {log_path} for critical messages")
        logging.info(f"Monitoring {log_path} for critical messages")
        errors = 0
        criticals = 0
        warnings = 0
        with open(log_path, 'r') as file:
            for line in file:
                if 'error' in line.lower():
                    errors += 1
                elif 'critical' in line.lower():
                    criticals += 1
                elif 'warning' in line.lower():
                    warnings += 1
        print(f"[INFO] Errors: {errors}; Criticals: {criticals}; Warnings: {warnings}.")
        logging.info(f"Errors: {errors}; Criticals: {criticals}; Warnings: {warnings}.")
    except Exception as e:
        logging.error(str(e))
        print(f"[ERROR] {e}")

# Monitor and report system CPU and memory usage over 10 minutes
# Alerts if CPU usage exceeds 80%

def monitor_system():
    checks = 10
    frequency = 1
    try:
        print(f"[INFO] System health check every {frequency} minute for {checks} minutes")
        logging.info(f"System health check every {frequency} minute for {checks} minutes")
        for _ in range(checks):
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            print(f"[INFO] CPU Usage: {cpu}% | Memory Usage: {mem}%")
            logging.info(f"CPU Usage: {cpu}% | Memory Usage: {mem}%")
            if cpu > 80:
                print(f"[ALERT] High CPU usage detected: {cpu}%")
                logging.info(f"High CPU usage detected: {cpu}%")
            time.sleep(60 * frequency)
    except Exception as e:
        logging.error(str(e))
        print(f"[ERROR] {e}")

# Check disk space usage of a directory and log alerts if usage exceeds threshold

def check_disk_space(directory, threshold):
    try:
        print(f"[INFO] Checking disk space for directory {directory}")
        logging.info(f"Checking disk space for directory {directory}")
        usage = shutil.disk_usage(directory)
        percent = (usage.used / usage.total) * 100
        print(f"[INFO] Disk Usage: {percent:.2f}%")
        logging.info(f"Disk Usage: {percent:.2f}%")
        if percent > threshold:
            print(f"[ALERT] Disk usage at {percent:.2f}% - consider freeing up space.")
            logging.info(f"Disk usage at {percent:.2f}% - consider freeing up space.")
    except Exception as e:
        logging.error(str(e))
        print(f"[ERROR] {e}")

# Main entry point: defines and processes command-line arguments

def main():
    parser = argparse.ArgumentParser(description='System Administration Script')
    subparsers = parser.add_subparsers(dest='subcommand')

    # User management commands
    user_parser = subparsers.add_parser('user', help='Manage users')
    user_parser.add_argument('--create', action='store_true', help='Create a single user (requires --username and --role).')
    user_parser.add_argument('--create-batch', action='store_true', help='Create multiple users from a CSV file (requires --csv).')
    user_parser.add_argument('--delete', action='store_true', help='Delete a user (requires --username).')
    user_parser.add_argument('--update', action='store_true', help='Update user details (requires --username, optional --password).')
    user_parser.add_argument('--username', type=str)
    user_parser.add_argument('--role', type=str)
    user_parser.add_argument('--csv', type=str)
    user_parser.add_argument('--password', type=str)

    # File organization and log monitoring
    organize_parser = subparsers.add_parser('organize', help='Organize files or monitor logs')
    organize_parser.add_argument('--dir', type=str, help='Organize files based on file types (accepts a path to directory).')
    organize_parser.add_argument('--log-monitor', type=str, help='Monitor specific logs for critical messages and summarize them (accepts a path to a log file).')

    # System health monitoring
    monitor_parser = subparsers.add_parser('monitor', help='Monitor system health')
    monitor_parser.add_argument('--system', action='store_true', help='Log CPU and memory usage every minute for 10 minutes.')
    monitor_parser.add_argument('--disk', action='store_true', help='Alert if disk usage exceeds a threshold (requires --dir and --threshold).')
    monitor_parser.add_argument('--dir', type=str)
    monitor_parser.add_argument('--threshold', type=int)

    args = parser.parse_args()

    # Dispatch to the correct subcommand
    if args.subcommand == 'user':
        handle_user(args)
    elif args.subcommand == 'organize':
        handle_organize(args)
    elif args.subcommand == 'monitor':
        handle_monitor(args)
    else:
        parser.print_help()

# Entry point for script
if __name__ == '__main__':
    main()
