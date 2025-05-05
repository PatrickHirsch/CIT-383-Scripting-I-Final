#!/usr/bin/env python3

# Import needed modules
import argparse
import os
import shutil
import csv
import subprocess
import time
import psutil
import logging

# Setup logging for errors
logFile='error_log_group_4.log'
logging.basicConfig(filename=logFile, level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Function to handle user subcommands
def handle_user(args):
    if args.create:
        create_user(args.username, args.role)
    elif args.create_batch:
        create_users_from_csv(args.csv)
    elif args.delete:
        delete_user(args.username)
    elif args.update:
        update_user(args.username, args.password)

# Function to handle organize subcommands
def handle_organize(args):
    if args.dir:
        organize_directory(args.dir)
    elif args.log_monitor:
        monitor_log(args.log_monitor)

# Function to handle monitor subcommands
def handle_monitor(args):
    if args.system:
        monitor_system()
    elif args.disk:
        check_disk_space(args.dir, args.threshold)

# Create a single user
def create_user(username, role):
    try:
        if ' ' in username:
            raise ValueError("Invalid username format. Usernames should not contain spaces.")
        print(f"[INFO] Creating user '{username}' with role '{role}'.")
        subprocess.run(['sudo', 'useradd', '-m', username], check=True)
        print(f"[INFO] User '{username}' created successfully with home directory /home/{username}")
        if role == 'admin':
            subprocess.run(['sudo', 'usermod', '-aG', 'wheel', username], check=True)
            print(f"[INFO] Role 'admin' assigned with full access permissions.")
    except Exception as e:
        logging.error(str(e))
        print(f"[ERROR] {e}")
        print(f"[INFO] Error logged to {logFile}.")

# Create multiple users from CSV
def create_users_from_csv(csv_path):
    try:
        with open(csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            print(f"[INFO] Creating users from CSV file: {csv_path}")
            for row in reader:
                username = row['username']
                role = row['role']
                password = row['password']
                try:
                    subprocess.run(['sudo', 'useradd', '-m', username], check=True)
                    subprocess.run(['bash', '-c', f"echo '{username}:{password}' | sudo chpasswd"], check=True)
                    if role == 'admin':
                        subprocess.run(['sudo', 'usermod', '-aG', 'wheel', username], check=True)
                    print(f"[INFO] Creating user '{username}' with role '{role}'.")
                except Exception as e:
                    logging.error(str(e))
                    print(f"[ERROR] Skipping {username}: {e}")
        print("[INFO] Batch user creation completed successfully.")
    except FileNotFoundError:
        logging.error("CSV file not found.")
        print("[ERROR] CSV file not found.")

# Delete a user
def delete_user(username):
    try:
        print(f"[INFO] Deletng user '{username}'.")
        subprocess.run(['sudo', 'userdel', '-r', username], check=True)
        print(f"[INFO] User '{username}' deleted successfully.")
    except Exception as e:
        logging.error(str(e))
        print(f"[ERROR] {e}")

# Update user password
def update_user(username, password=None):
    try:
        print(f"[INFO] Updating information for user '{username}'")
        if password:
            subprocess.run(['bash', '-c', f"echo '{username}:{password}' | sudo chpasswd"], check=True)
            print(f"[INFO] Password updated successfully for '{username}'.")
        else:
            print("[INFO] No password provided. Nothing updated.")
    except Exception as e:
        logging.error(str(e))
        print(f"[ERROR] {e}")

# Organize files in directory
def organize_directory(directory):
    try:
        if not os.path.isdir(directory):
            raise ValueError("Invalid directory.")
        print(f"[INFO] Organizing files in {directory} by type")
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
                    seenExtentions.append(ext)
        print(f"[INFO] Directory organization complete.")
    except Exception as e:
        logging.error(str(e))
        print(f"[ERROR] {e}")

# Monitor a log file
def monitor_log(log_path):
    try:
        print(f"[INFO] Monitoring {log_path} for critical messages")
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
    except Exception as e:
        logging.error(str(e))
        print(f"[ERROR] {e}")

# Monitor CPU and memory usage
def monitor_system():
    checks=10
    frequency=1
    try:
        print(f"[INFO] System health check every {frequency} minute for {checks} minutes")
        for _ in range(checks):
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            print(f"[INFO] CPU Usage: {cpu}% | Memory Usage: {mem}%")
            if cpu > 80:
                print(f"[ALERT] High CPU usage detected: {cpu}%")
            time.sleep(60*frequency)
    except Exception as e:
        logging.error(str(e))
        print(f"[ERROR] {e}")

# Check disk space usage
def check_disk_space(directory, threshold):
    try:
        print(f"INFO] Checking disk space for directory {directory}")
        usage = shutil.disk_usage(directory)
        percent = (usage.used / usage.total) * 100
        print(f"[INFO] Disk Usage: {percent:.2f}%")
        if percent > threshold:
            print(f"[ALERT] Disk usage at {percent:.2f}% - consider freeing up space.")
    except Exception as e:
        logging.error(str(e))
        print(f"[ERROR] {e}")

# Setup the main argument parser
def main():
    parser = argparse.ArgumentParser(description='System Administration Script')
    subparsers = parser.add_subparsers(dest='subcommand')

    user_parser = subparsers.add_parser('user', help='Manage users')
    user_parser.add_argument('--create', action='store_true', help='Create a single user (requires --username and --role).')
    user_parser.add_argument('--create-batch', action='store_true', help='Create multiple users from a CSV file (requires --csv).')
    user_parser.add_argument('--delete', action='store_true', help='Delete a user (requires --username).')
    user_parser.add_argument('--update', action='store_true', help='Update user details (requires --username, optional --password).')
    
    user_parser.add_argument('--username', type=str)
    user_parser.add_argument('--role', type=str)
    user_parser.add_argument('--csv', type=str)
    user_parser.add_argument('--password', type=str)

    organize_parser = subparsers.add_parser('organize', help='Organize files or monitor logs')
    organize_parser.add_argument('--dir', type=str, help='Organize files based on file types (accepts a path to directory).')
    organize_parser.add_argument('--log-monitor', type=str, help='Monitor specific logs for critical messages and summarize them (accepts a path to a log file).')

    monitor_parser = subparsers.add_parser('monitor', help='Monitor system health')
    monitor_parser.add_argument('--system', action='store_true', help='Log CPU and memory usage every minute for 10 minutes.')
    monitor_parser.add_argument('--disk', action='store_true', help='Alert if disk usage exceeds a threshold (requires --dir and --threshold).')
    
    monitor_parser.add_argument('--dir', type=str)
    monitor_parser.add_argument('--threshold', type=int)

    args = parser.parse_args()

    if args.subcommand == 'user':
        handle_user(args)
    elif args.subcommand == 'organize':
        handle_organize(args)
    elif args.subcommand == 'monitor':
        handle_monitor(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
