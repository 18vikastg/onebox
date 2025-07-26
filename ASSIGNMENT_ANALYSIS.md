# 🎯 ReachInbox Assignment: Multi-Tenant Implementation Plan

## Current State vs Required
- **Current**: Hardcoded single-user (your Gmail accounts)
- **Required**: Multi-tenant SaaS where users can add their own email accounts

## Implementation Strategy

### Phase 1: User Authentication & Account Management
1. **User Registration/Login System**
   - JWT-based authentication
   - User profiles and sessions
   
2. **Email Account Management**
   - Users can add/remove their email accounts
   - Secure credential storage per user
   - Support multiple IMAP providers (Gmail, Outlook, Yahoo, etc.)

### Phase 2: Multi-Tenant Data Architecture
1. **Database Schema Updates**
   - User table for authentication
   - EmailAccounts table (linked to users)
   - Emails table (scoped by user_id)
   - Categories/Labels per user

2. **API Endpoints**
   - `/auth/*` - Authentication endpoints
   - `/accounts/*` - Email account management
   - `/emails/*` - Email operations (scoped by user)
   - `/dashboard/*` - User-specific dashboard

### Phase 3: Dynamic Email Sync
1. **Per-User IMAP Connections**
   - Dynamic connection management
   - User-specific sync services
   - Real-time updates per user account

2. **Elasticsearch Multi-Tenancy**
   - User-scoped indices or filtering
   - Secure data isolation

## Key Features to Implement

### 1. Authentication System ✅
```javascript
// Login/Register endpoints
POST /api/auth/register
POST /api/auth/login
GET /api/auth/profile
```

### 2. Email Account Setup ✅
```javascript
// Email account management
POST /api/accounts/add      // Add new email account
GET /api/accounts          // List user's accounts
DELETE /api/accounts/:id   // Remove account
POST /api/accounts/test    // Test IMAP connection
```

### 3. Dynamic Configuration ✅
- Users input their own:
  - Email address
  - IMAP server settings
  - Authentication credentials
  - Sync preferences

### 4. User-Scoped Dashboard ✅
- Each user sees only their emails
- Personal AI categories and settings
- Individual Slack/webhook configurations

## Database Schema

```sql
-- Users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Email accounts per user
CREATE TABLE email_accounts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  email VARCHAR(255),
  imap_host VARCHAR(255),
  imap_port INTEGER,
  password VARCHAR(255), -- encrypted
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Emails scoped by user
CREATE TABLE emails (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  account_id INTEGER REFERENCES email_accounts(id),
  uid VARCHAR(255),
  subject TEXT,
  sender VARCHAR(255),
  content TEXT,
  category VARCHAR(50),
  date_received TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Frontend Flow

### 1. Landing Page
- **Sign Up / Login** buttons
- Demo video or screenshots
- Feature highlights

### 2. Onboarding Flow
```
Register → Verify Email → Add First Email Account → Sync Started → Dashboard
```

### 3. Email Account Setup
- **Step 1**: Choose provider (Gmail, Outlook, Yahoo)
- **Step 2**: Enter credentials
- **Step 3**: Test connection
- **Step 4**: Start syncing

### 4. Main Dashboard
- **Unified Inbox**: All user's emails
- **Account Switcher**: Filter by email account
- **AI Categories**: User's personalized labels
- **Search**: Elasticsearch-powered

## For ReachInbox Assignment Submission

### What Reviewers Expect to See:
1. **Multi-user capability** - Not hardcoded to your personal emails
2. **Account setup flow** - Users can add their own email accounts
3. **Data isolation** - Each user sees only their data
4. **Professional SaaS interface** - Similar to ReachInbox.ai
5. **Demo-ready** - They can test with their own email accounts

### Submission Format:
1. **GitHub Repository** (grant access to `Mitrajit`)
2. **Live Demo URL** (Railway deployment)
3. **Demo Video** (5 mins max showing multi-user flow)
4. **README** with setup instructions
5. **Postman Collection** for API testing

## Next Steps

**Option A: Quick Multi-Tenant Conversion** (Recommended)
- Add user authentication
- Convert to dynamic email account system
- Update frontend for multi-user experience

**Option B: Enhanced Single-User Demo**
- Keep current hardcoded approach
- Focus on feature completeness
- Add detailed documentation explaining scalability

## Recommendation: Go with Option A
This will demonstrate your ability to build **real production-ready SaaS applications** which is what ReachInbox actually does.
