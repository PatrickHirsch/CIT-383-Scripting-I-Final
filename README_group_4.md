# CIT 383 Final Project - Group 4

## Overview
This project is a Python script that automates system administration tasks. It handles user management, file organization, and system health monitoring on a CentOS 9 virtual machine.

## Setup
- Make sure Python 3 is installed.
- Install `psutil` if needed:  
  `pip install psutil`
- Give the script executable permission if running directly:  
  `chmod +x sys_admin_group_4.py`

## Usage Instructions

### User Management
Create a single user:
```
./sys_admin_group_4.py user --create --username johndoe --role admin
```

Create users from a CSV:
```
./sys_admin_group_4.py user --create-batch --csv users.csv
```

Delete a user:
```
./sys_admin_group_4.py user --delete --username johndoe
```

Update a user’s password:
```
./sys_admin_group_4.py user --update --username johndoe --password newpassword
```

### File Organization
Organize files by type:
```
./sys_admin_group_4.py organize --dir /home/user/documents
```

Monitor a log file:
```
./sys_admin_group_4.py organize --log-monitor /var/log/syslog
```

### System Monitoring
Monitor CPU and Memory:
```
./sys_admin_group_4.py monitor --system
```

Check disk space and alert if full:
```
./sys_admin_group_4.py monitor --disk --dir /home/user --threshold 85
```

## Output Files
- `error_log_group_4.log`: Stores any error messages
- `system_health.log`: Stores system health monitoring results

## Notes
- The script must be run with sudo or administrator rights to create/delete users.
- Input validation and error handling are included for safety.