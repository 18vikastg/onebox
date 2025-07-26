# 🚀 Complete SAAS Email Platform Setup Guide

This guide will help you set up the complete automated email fetching system where users can register, add their real email accounts, and automatically fetch & categorize emails with AI.

## 📋 Prerequisites

### 1. **OpenAI API Key** (Required for AI categorization)
- Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
- Create a new secret key
- Copy the key (starts with `sk-proj-...`)

### 2. **Gmail App Password** (For testing with real emails)
- Go to your Google Account settings
- Enable 2-factor authentication
- Generate an App Password for "Mail"
- Use this instead of your regular password

## 🔧 Setup Instructions

### Step 1: Environment Configuration

1. **Copy the environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file and add your OpenAI API key:**
   ```bash
   nano .env
   ```
   
   Replace this line:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   With your actual key:
   ```
   OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
   ```

### Step 2: Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Start the Platform

```bash
npm start
```

The server will start on `http://localhost:4000` with:
- ✅ Real-time email synchronization
- ✅ AI-powered email categorization
- ✅ Multi-tenant user system
- ✅ Automatic email fetching

## 🎯 How to Use the Platform

### For Platform Users:

1. **Register an Account:**
   - Go to `http://localhost:4000/register`
   - Create your account with any email address

2. **Add Your Email Account:**
   - Go to `http://localhost:4000/setup`
   - Add your Gmail account with:
     - **Email:** your-email@gmail.com
     - **Password:** your-app-password (not regular password)
     - **IMAP Host:** imap.gmail.com (default)
     - **IMAP Port:** 993 (default)

3. **Automatic Email Sync:**
   - Emails will be fetched automatically when you add the account
   - Real-time sync runs every 5 minutes
   - AI categorizes emails into: Interested, Meeting Booked, Not Interested, Spam, Out of Office

4. **View Your Dashboard:**
   - Go to `http://localhost:4000/dashboard`
   - See all your emails categorized
   - Search and filter emails
   - Use AI-powered reply suggestions

## 🔄 Real-Time Features

### Automatic Email Synchronization:
- **Immediate Sync:** When you add an email account
- **Periodic Sync:** Every 5 minutes for all users
- **Background Processing:** Runs continuously
- **AI Classification:** Automatic categorization of all emails

### Multi-Tenant Support:
- Each user sees only their own emails
- Complete user isolation
- Individual email account management
- Personal AI categorization

## 📊 Testing with Real Data

### Test with Your Own Gmail:

1. **Enable App Passwords in Gmail:**
   ```
   Google Account → Security → 2-Step Verification → App passwords
   ```

2. **Add Your Gmail Account:**
   - Email: your-real-email@gmail.com
   - Password: your-16-character-app-password
   - The system will immediately fetch your real emails

3. **See Real Results:**
   - Your actual emails will appear in the dashboard
   - AI will categorize them based on content
   - You can search and generate replies

## 🔐 Security Features

- **Secure Password Storage:** Bcrypt hashing
- **JWT Authentication:** Token-based security
- **Cookie Sessions:** Secure browser sessions
- **IMAP SSL:** Encrypted email connections
- **User Isolation:** Complete data separation

## 🛠️ Configuration Options

### Email Sync Settings (in `.env`):
```bash
# Enable/disable auto-sync
AUTO_SYNC_ENABLED=true

# Sync interval (minutes)
SYNC_INTERVAL_MINUTES=5

# How many days back to fetch
SYNC_DAYS_BACK=30
```

### Server Settings:
```bash
# Server port
PORT=4000

# JWT secret (change in production)
JWT_SECRET=your-super-secret-key
```

## 📈 System Architecture

### Real-Time Email Processing:
1. **User Registration** → Create account
2. **Add Email Account** → Store credentials securely
3. **Immediate Sync** → Fetch emails right away
4. **Background Sync** → Continue fetching every 5 minutes
5. **AI Processing** → Categorize all emails automatically
6. **Dashboard Display** → Show categorized emails to user

### Multi-Tenant Database:
```
users (id, email, password_hash)
├── email_accounts (user_id, email, imap_settings)
└── emails (user_id, account_id, subject, content, category)
```

## 🎯 Production Deployment

### Environment Variables for Production:
```bash
NODE_ENV=production
OPENAI_API_KEY=your_production_openai_key
JWT_SECRET=your_super_secure_production_secret
AUTO_SYNC_ENABLED=true
SYNC_INTERVAL_MINUTES=5
```

### Deployment Commands:
```bash
# Build for production
npm run build

# Start production server
npm run start:production
```

## 🔍 Troubleshooting

### Common Issues:

1. **"Access token required" error:**
   - Make sure you're logged in at `/login`
   - Check browser cookies for `auth_token`

2. **Email sync not working:**
   - Verify OpenAI API key in `.env`
   - Check Gmail app password is correct
   - Ensure IMAP is enabled in Gmail

3. **No emails appearing:**
   - Check that auto-sync is enabled
   - Verify email account credentials
   - Look at server logs for errors

### Debug Commands:
```bash
# Test email sync manually
python test_email_flow.py

# Test authentication
python test_authentication.py

# Check server logs
npm start
```

## ✅ Success Checklist

- [ ] OpenAI API key configured
- [ ] Gmail app password created
- [ ] Server running on port 4000
- [ ] User can register and login
- [ ] User can add Gmail account
- [ ] Emails sync automatically
- [ ] AI categorization working
- [ ] Dashboard shows real emails
- [ ] Search and filters work
- [ ] Reply suggestions generate

## 🎉 You're Ready!

Your complete SAAS email platform is now running with:
- **Real-time email synchronization**
- **AI-powered categorization**
- **Multi-user support**
- **Secure authentication**
- **Automatic processing**

Users can now register, add their email accounts, and see their emails automatically fetched and categorized in real-time!
