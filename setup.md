# Gmail Email Fetcher Setup Guide

## Prerequisites
1. Gmail account with 2-factor authentication enabled
2. Gmail App Password (not your regular password)
3. Node.js installed
4. Python 3.x installed

## Setup Steps

### 1. Python Environment Setup
The virtual environment is already created. Install required packages:
```bash
cd /home/vikas/Desktop/onebox(1)
./.venv/bin/pip install python-dateutil
```

### 2. Node.js Dependencies
Install Node.js dependencies:
```bash
npm install
```

### 3. Gmail Configuration
1. Go to your Google Account settings
2. Enable 2-factor authentication
3. Generate an App Password for "Mail"
4. Replace "your_app_password_here" in `get_messages.py` with your actual app password

### 4. Update Credentials
Edit `get_messages.py` line 16:
```python
M.login("your_email@gmail.com", "your_16_character_app_password")
```

## Running the Application

### Start the Server
```bash
node index.js
```

### Access the Application
Open your browser and go to: `http://localhost:4000`

## How to Use
1. Enter a subject keyword to search for
2. Set the number of emails to retrieve (1-50)
3. Set the date range
4. Click "Fetch Emails"
5. View the results in the table below

## Security Notes
- Never commit real credentials to version control
- Consider using environment variables for production
- The app password is different from your Gmail password
