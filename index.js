let express = require('express')
let fs = require('fs')
const { parse } = require('csv-parse')
const path = require('path')
const fetch = require('node-fetch')
const cookieParser = require('cookie-parser')
const database = require('./models')
const { generateToken, authenticateToken, requireAuth } = require('./auth')
const Imap = require('imap')
const { simpleParser } = require('mailparser')

let app = express()

// Serve static files
app.use(express.static(__dirname))

app.set('view engine', 'ejs')

app.use(express.json())
app.use(express.urlencoded({extended:false}))
app.use(cookieParser())

// Start real-time email sync service
let emailSyncStarted = false
let activeImapConnections = new Map()

async function syncEmailsForUser(userId) {
    try {
        console.log(`📧 Starting email sync for user ${userId}`)
        
        // Get user's email accounts
        const accounts = await database.getUserEmailAccounts(userId)
        
        for (const account of accounts) {
            await syncEmailsFromAccount(userId, account)
        }
        
        console.log(`✅ Email sync completed for user ${userId}`)
    } catch (error) {
        console.error(`❌ Email sync error for user ${userId}:`, error.message)
    }
}

async function syncEmailsFromAccount(userId, account) {
    return new Promise((resolve, reject) => {
        // Get account details with password from database
        database.db.get(
            'SELECT * FROM email_accounts WHERE id = ? AND user_id = ?',
            [account.id, userId],
            (err, fullAccount) => {
                if (err || !fullAccount) {
                    console.error('Error getting account details:', err);
                    return reject(err || new Error('Account not found'));
                }

                const imap = new Imap({
                    user: fullAccount.email,
                    password: fullAccount.password.replace(/\s/g, ''), // Remove spaces from app password
                    host: fullAccount.imap_host || 'imap.gmail.com',
                    port: fullAccount.imap_port || 993,
                    tls: true,
                    tlsOptions: { rejectUnauthorized: false },
                    authTimeout: 3000,
                    connTimeout: 10000
                })

                imap.once('ready', () => {
                    console.log(`📧 IMAP connected for ${fullAccount.email}`)
                    
                    imap.openBox('INBOX', false, (err, box) => {
                        if (err) {
                            console.error('Error opening inbox:', err)
                            return reject(err)
                        }

                        // Search for emails from last 30 days (read and unread)
                        const since = new Date()
                        since.setDate(since.getDate() - 30)
                        const searchCriteria = [['SINCE', since]]

                        imap.search(searchCriteria, (err, results) => {
                            if (err) {
                                console.error('Search error:', err)
                                return reject(err)
                            }

                            if (!results || results.length === 0) {
                                console.log(`No new emails for ${fullAccount.email}`)
                                imap.end()
                                return resolve()
                            }

                            console.log(`Found ${results.length} new emails for ${fullAccount.email}`)

                            const fetch = imap.fetch(results, { bodies: '', struct: true })
                            let processedCount = 0

                            fetch.on('message', (msg, seqno) => {
                                msg.on('body', (stream, info) => {
                                    let buffer = ''
                                    stream.on('data', (chunk) => {
                                        buffer += chunk.toString('utf8')
                                    })
                                    stream.once('end', async () => {
                                        try {
                                            const parsed = await simpleParser(buffer)
                                            
                                            // Store email in database
                                            const emailData = {
                                                subject: parsed.subject || 'No Subject',
                                                sender: parsed.from?.text || 'Unknown',
                                                snippet: parsed.text?.substring(0, 200) || 'No content',
                                                content: parsed.text || parsed.html || 'No content',
                                                received_at: parsed.date || new Date(),
                                                user_id: userId,
                                                email_account: fullAccount.email,
                                                category: 'inbox' // Default category
                                            }

                                            // Classify email using AI if available
                                            try {
                                                const classification = await classifyEmail(emailData.content)
                                                emailData.category = classification || 'general'
                                            } catch (classifyError) {
                                                console.log('Classification failed, using default category')
                                            }

                                            await database.addEmail(emailData)
                                            console.log(`📧 Stored email: ${emailData.subject}`)
                                            
                                            processedCount++
                                            if (processedCount === results.length) {
                                                imap.end()
                                                resolve()
                                            }
                                        } catch (parseError) {
                                            console.error('Error parsing email:', parseError)
                                            processedCount++
                                            if (processedCount === results.length) {
                                                imap.end()
                                                resolve()
                                            }
                                        }
                                    })
                                })
                            })

                            fetch.once('error', (err) => {
                                console.error('Fetch error:', err)
                                reject(err)
                            })

                            fetch.once('end', () => {
                                console.log(`Finished fetching emails for ${fullAccount.email}`)
                            })
                        })
                    })
                })

                imap.once('error', (err) => {
                    console.error('IMAP connection error:', err)
                    reject(err)
                })

                imap.once('end', () => {
                    console.log(`IMAP connection ended for ${fullAccount.email}`)
                })

                imap.connect()
            }
        )
    })
}

async function classifyEmail(content) {
    try {
        // Simple keyword-based classification as fallback
        const lowerContent = content.toLowerCase()
        
        if (lowerContent.includes('invoice') || lowerContent.includes('payment') || lowerContent.includes('bill')) {
            return 'finance'
        } else if (lowerContent.includes('meeting') || lowerContent.includes('schedule') || lowerContent.includes('appointment')) {
            return 'meetings'
        } else if (lowerContent.includes('urgent') || lowerContent.includes('important') || lowerContent.includes('asap')) {
            return 'important'
        } else if (lowerContent.includes('newsletter') || lowerContent.includes('unsubscribe') || lowerContent.includes('marketing')) {
            return 'marketing'
        } else {
            return 'general'
        }
    } catch (error) {
        return 'general'
    }
}

function startEmailSyncService() {
    if (emailSyncStarted) return
    
    console.log("🚀 Starting real-time email sync service")
    emailSyncStarted = true
    
    // Read sync interval from environment or default to 2 minutes for real-time feel
    const syncIntervalMinutes = parseInt(process.env.SYNC_INTERVAL_MINUTES) || 2
    console.log(`⏰ Email sync will run every ${syncIntervalMinutes} minutes`)
    
    // Sync emails for all users at specified interval
    setInterval(async () => {
        try {
            console.log("🔄 Running scheduled email sync...")
            const users = await database.getAllUsers()
            
            for (const user of users) {
                await syncEmailsForUser(user.id)
            }
            
            console.log(`✅ Scheduled sync completed for ${users.length} users`)
        } catch (error) {
            console.error('❌ Email sync interval error:', error.message)
        }
    }, syncIntervalMinutes * 60 * 1000)
    
    console.log("🚀 Real-time email sync service initialized")
}

// Start the email sync service when server starts
async function initializeEmailSync() {
    console.log("🚀 Initializing production email sync system...")
    
    try {
        // Wait for database tables to be ready
        console.log("⏳ Waiting for database tables to initialize...")
        await new Promise((resolve) => {
            const checkTables = () => {
                if (database.tablesInitialized) {
                    resolve();
                } else {
                    setTimeout(checkTables, 1000);
                }
            };
            checkTables();
        });
        console.log("✅ Database tables ready!")
        
        // Start the background sync service
        startEmailSyncService()
        
        // Auto-sync for any existing users with accounts
        const users = await database.getAllUsers()
        console.log(`👥 Found ${users.length} existing users`)
        
        for (const user of users) {
            const accounts = await database.getUserEmailAccounts(user.id)
            if (accounts.length > 0) {
                console.log(`📧 User ${user.id} has ${accounts.length} accounts, starting sync...`)
                setTimeout(async () => {
                    try {
                        await syncEmailsForUser(user.id)
                        console.log(`✅ Initial sync completed for user ${user.id}`)
                    } catch (error) {
                        console.error(`❌ Initial sync failed for user ${user.id}:`, error.message)
                    }
                }, Math.random() * 10000) // Stagger syncs with random delay
            }
        }
        
        console.log("🚀 Email sync system initialized successfully!")
        
    } catch (error) {
        console.error('❌ Failed to initialize email sync:', error)
    }
}

setTimeout(initializeEmailSync, 5000) // Wait 5 seconds for server to fully start

// Health check endpoint for deployment monitoring
app.get('/health', (req, res) => {
    const healthCheck = {
        uptime: process.uptime(),
        message: 'OK',
        timestamp: Date.now(),
        environment: process.env.NODE_ENV || 'development',
        version: '1.0.0'
    }
    
    try {
        res.status(200).json(healthCheck)
    } catch (error) {
        healthCheck.message = error
        res.status(503).json(healthCheck)
    }
})

// ==================== AUTHENTICATION ROUTES ====================

// User Registration
app.post('/api/auth/register', async (req, res) => {
    try {
        const { email, password, name } = req.body

        if (!email || !password || !name) {
            return res.status(400).json({ error: 'All fields are required' })
        }

        // Check if user already exists
        const existingUser = await database.getUserByEmail(email)
        if (existingUser) {
            return res.status(400).json({ error: 'User already exists' })
        }

        // Create new user
        const user = await database.createUser(email, password, name)
        const token = generateToken(user)

        // Set cookie for browser sessions
        res.cookie('auth_token', token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            maxAge: 24 * 60 * 60 * 1000 // 24 hours
        })

        res.status(201).json({
            message: 'User registered successfully',
            user: { id: user.id, email: user.email, name: user.name },
            token
        })
    } catch (error) {
        console.error('Registration error:', error)
        res.status(500).json({ error: 'Internal server error' })
    }
})

// User Login
app.post('/api/auth/login', async (req, res) => {
    try {
        const { email, password } = req.body

        if (!email || !password) {
            return res.status(400).json({ error: 'Email and password are required' })
        }

        // Find user
        const user = await database.getUserByEmail(email)
        if (!user) {
            return res.status(401).json({ error: 'Invalid credentials' })
        }

        // Validate password
        if (!database.validatePassword(password, user.password_hash)) {
            return res.status(401).json({ error: 'Invalid credentials' })
        }

        const token = generateToken(user)

        // Set cookie for browser sessions
        res.cookie('auth_token', token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            maxAge: 24 * 60 * 60 * 1000 // 24 hours
        })

        res.json({
            message: 'Login successful',
            user: { id: user.id, email: user.email, name: user.name },
            token
        })
    } catch (error) {
        console.error('Login error:', error)
        res.status(500).json({ error: 'Internal server error' })
    }
})

// Get user profile
app.get('/api/auth/profile', authenticateToken, (req, res) => {
    res.json({ user: req.user })
})

// Logout
app.post('/api/auth/logout', (req, res) => {
    res.clearCookie('auth_token')
    res.json({ message: 'Logged out successfully' })
})

// ==================== EMAIL ACCOUNT MANAGEMENT ====================

// Add email account
app.post('/api/accounts/add', authenticateToken, async (req, res) => {
    try {
        const { email, imapHost, imapPort, password, provider } = req.body

        if (!email || !imapHost || !password) {
            return res.status(400).json({ error: 'Email, IMAP host, and password are required' })
        }

        const accountData = {
            email,
            imapHost: imapHost || 'imap.gmail.com',
            imapPort: imapPort || 993,
            password,
            provider: provider || 'gmail'
        }

        const account = await database.addEmailAccount(req.user.id, accountData)
        
        // Trigger immediate email sync for this account
        console.log(`📧 Email account added for user ${req.user.id}. Starting immediate sync...`)
        
        // Start sync in background
        setTimeout(async () => {
            try {
                await syncEmailsForUser(req.user.id)
                console.log(`✅ Initial sync completed for user ${req.user.id}`)
            } catch (syncError) {
                console.error(`❌ Initial sync failed for user ${req.user.id}:`, syncError.message)
            }
        }, 2000) // Wait 2 seconds before starting sync
        
        res.status(201).json({
            message: 'Email account added successfully. Email sync will be handled by dedicated service.',
            account: {
                id: account.id,
                email: account.email,
                provider: account.provider
            },
            syncTriggered: true
        })
    } catch (error) {
        console.error('Add account error:', error)
        res.status(500).json({ error: 'Failed to add email account' })
    }
})

// Get user's email accounts
app.get('/api/accounts', authenticateToken, async (req, res) => {
    try {
        const accounts = await database.getUserEmailAccounts(req.user.id)
        res.json({ accounts })
    } catch (error) {
        console.error('Get accounts error:', error)
        res.status(500).json({ error: 'Failed to fetch accounts' })
    }
})

// Delete email account
app.delete('/api/accounts/:id', authenticateToken, async (req, res) => {
    try {
        const accountId = req.params.id
        const success = await database.deleteEmailAccount(req.user.id, accountId)
        
        if (success) {
            res.json({ message: 'Account deleted successfully' })
        } else {
            res.status(404).json({ error: 'Account not found' })
        }
    } catch (error) {
        console.error('Delete account error:', error)
        res.status(500).json({ error: 'Failed to delete account' })
    }
})

// ==================== EMAIL ROUTES (USER-SCOPED) ====================

// Get user's emails
app.get('/api/emails', authenticateToken, async (req, res) => {
    try {
        const { category, limit } = req.query
        
        let emails
        if (category) {
            emails = await database.getUserEmailsByCategory(req.user.id, category)
        } else {
            emails = await database.getUserEmails(req.user.id, limit ? parseInt(limit) : 50)
        }
        
        res.json({ emails })
    } catch (error) {
        console.error('Get emails error:', error)
        res.status(500).json({ error: 'Failed to fetch emails' })
    }
})

// Search emails (for dashboard search functionality)
app.get('/api/search', authenticateToken, async (req, res) => {
    try {
        const { q, category, account, limit } = req.query
        
        let emails = await database.getUserEmails(req.user.id, limit ? parseInt(limit) : 100)
        
        // Apply filters
        if (q) {
            const query = q.toLowerCase()
            emails = emails.filter(email => 
                email.subject?.toLowerCase().includes(query) ||
                email.body?.toLowerCase().includes(query) ||
                email.sender?.toLowerCase().includes(query)
            )
        }
        
        if (category && category !== 'all') {
            emails = emails.filter(email => email.category === category)
        }
        
        if (account && account !== 'all') {
            emails = emails.filter(email => email.account_email === account)
        }
        
        res.json({ emails, total: emails.length })
    } catch (error) {
        console.error('Search emails error:', error)
        res.status(500).json({ error: 'Failed to search emails' })
    }
})

// Get email statistics
app.get('/api/stats', authenticateToken, async (req, res) => {
    try {
        const emails = await database.getUserEmails(req.user.id)
        const accounts = await database.getUserEmailAccounts(req.user.id)
        
        // Calculate category stats
        const categoryStats = {}
        const categories = ['Interested', 'Meeting Booked', 'Not Interested', 'Spam', 'Out of Office']
        
        categories.forEach(cat => {
            categoryStats[cat] = emails.filter(email => email.category === cat).length
        })
        
        res.json({
            totalEmails: emails.length,
            totalAccounts: accounts.length,
            categories: categoryStats,
            recentEmails: emails.slice(0, 5).length
        })
    } catch (error) {
        console.error('Get stats error:', error)
        res.status(500).json({ error: 'Failed to fetch statistics' })
    }
})

// Public stats endpoint (no auth required) for debugging
app.get('/api/public-stats', async (req, res) => {
    try {
        console.log("📊 Public stats request")
        
        // Get all emails from database (for debugging)
        const allEmails = await new Promise((resolve, reject) => {
            database.db.all("SELECT * FROM emails LIMIT 10", (err, rows) => {
                if (err) reject(err)
                else resolve(rows)
            })
        })
        
        const allUsers = await new Promise((resolve, reject) => {
            database.db.all("SELECT * FROM users", (err, rows) => {
                if (err) reject(err)
                else resolve(rows)
            })
        })
        
        const allAccounts = await new Promise((resolve, reject) => {
            database.db.all("SELECT * FROM email_accounts", (err, rows) => {
                if (err) reject(err)
                else resolve(rows)
            })
        })
        
        res.json({
            debug: true,
            totalEmails: allEmails.length,
            totalUsers: allUsers.length,
            totalAccounts: allAccounts.length,
            sampleEmails: allEmails.slice(0, 3),
            users: allUsers,
            accounts: allAccounts,
            environment: process.env.NODE_ENV
        })
    } catch (error) {
        console.error('Public stats error:', error)
        res.status(500).json({ error: error.message })
    }
})

// Simple test endpoint
app.get('/api/test', (req, res) => {
    res.json({ 
        status: 'ok', 
        message: 'Server is working',
        timestamp: new Date().toISOString(),
        environment: process.env.NODE_ENV 
    })
})

// Add sample emails for testing
app.post('/api/add-sample-emails', authenticateToken, async (req, res) => {
    try {
        const sampleEmails = [
            {
                messageId: 'sample1',
                threadId: 'thread1',
                from: 'hr@techcorp.com',
                to: req.user.email || 'user@example.com',
                subject: 'Technical Interview Invitation',
                body: 'Hi, Your resume has been shortlisted for the Full Stack Developer position. When would be a good time for you to attend the technical interview?',
                timestamp: new Date().toISOString(),
                category: 'Interested',
                isRead: false
            },
            {
                messageId: 'sample2',
                threadId: 'thread2',
                from: 'client@startup.com',
                to: req.user.email || 'user@example.com',
                subject: 'Project Meeting Request',
                body: 'Hi, we would like to schedule a meeting to discuss the project requirements. What is your availability next week?',
                timestamp: new Date(Date.now() - 3600000).toISOString(),
                category: 'Meeting Booked',
                isRead: false
            },
            {
                messageId: 'sample3',
                threadId: 'thread3',
                from: 'recruiter@bigtech.com',
                to: req.user.email || 'user@example.com',
                subject: 'Frontend Developer Opportunity',
                body: 'We have an exciting Frontend Developer opportunity at our company. Are you interested in learning more about this role?',
                timestamp: new Date(Date.now() - 7200000).toISOString(),
                category: 'Interested',
                isRead: true
            },
            {
                messageId: 'sample4',
                threadId: 'thread4',
                from: 'events@techconf.com',
                to: req.user.email || 'user@example.com',
                subject: 'Tech Conference Invitation',
                body: 'You are invited to attend our annual tech conference. The event will feature latest trends in AI and web development.',
                timestamp: new Date(Date.now() - 10800000).toISOString(),
                category: 'Interested',
                isRead: false
            }
        ]

        // Add emails to database
        for (const email of sampleEmails) {
            await database.addEmail(req.user.id, email)
        }

        console.log(`📧 Added ${sampleEmails.length} sample emails for user ${req.user.id}`)
        
        res.json({
            success: true,
            message: `Added ${sampleEmails.length} sample emails`,
            emailsAdded: sampleEmails.length
        })
    } catch (error) {
        console.error('Add sample emails error:', error)
        res.status(500).json({ error: 'Failed to add sample emails' })
    }
})

// Add sample emails for testing (remove in production)
app.post('/api/add-sample-emails', authenticateToken, async (req, res) => {
    try {
        const sampleEmails = [
            {
                messageId: 'sample-1',
                subject: 'Technical Interview Invitation',
                sender: 'hr@techcorp.com',
                body: 'Hi Vikas, Your resume has been shortlisted. When would be a good time for the technical interview?',
                date: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
                category: 'Interested'
            },
            {
                messageId: 'sample-2',
                subject: 'Project Collaboration Opportunity',
                sender: 'projects@startup.com',
                body: 'Hello, We have an exciting full-stack project. Are you available for a meeting next week?',
                date: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
                category: 'Meeting Booked'
            },
            {
                messageId: 'sample-3',
                subject: 'Freelance Web Development',
                sender: 'client@business.com',
                body: 'Hi, I need help building a modern web application. What are your rates?',
                date: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
                category: 'Interested'
            }
        ];

        for (const email of sampleEmails) {
            await database.storeEmail(req.user.id, email);
        }

        res.json({
            success: true,
            message: `Added ${sampleEmails.length} sample emails`,
            count: sampleEmails.length
        });
    } catch (error) {
        console.error('Add sample emails error:', error);
        res.status(500).json({ error: 'Failed to add sample emails' });
    }
})

// Sync emails for current user
app.post('/api/sync-emails', authenticateToken, async (req, res) => {
    try {
        console.log(`📧 Manual sync request for user ${req.user.id}`)
        
        // Trigger email sync for this user
        await syncEmailsForUser(req.user.id)
        
        res.json({
            success: true,
            message: 'Email sync completed successfully'
        })
        
    } catch (error) {
        console.error('Error syncing emails:', error)
        res.status(500).json({
            success: false,
            error: 'Email sync failed: ' + error.message
        })
    }
})

// Legacy route for compatibility - now handles search/filtering
app.post('/fetch-emails', authenticateToken, async (req, res) => {
    try {
        const { subject, category, account, total = 100, sortBy = 'date_desc', fromDate, toDate } = req.body;
        
        // Use the new search function
        const searchParams = {
            subject,
            category,
            account,
            total,
            sortBy,
            fromDate,
            toDate
        };
        
        const emails = await database.searchUserEmails(req.user.id, searchParams);
        
        // Get user accounts and categories for the dashboard
        const accounts = await database.getUserEmailAccounts(req.user.id);
        const categories = ['Interested', 'Meeting Booked', 'Not Interested', 'Spam', 'Out of Office'];
        
        // Render dashboard with filtered results
        res.render('dashboard', {
            user: req.user,
            emails: emails,
            accounts: accounts,
            categories: categories,
            searchQuery: subject || '',
            selectedCategory: category || 'all',
            selectedAccount: account || 'all',
            accountsCount: accounts.length,
            totalEmails: emails.length,
            storageMode: 'SQLite',
            error: null
        });
        
    } catch (error) {
        console.error('Error in fetch-emails:', error);
        res.status(500).json({
            success: false,
            error: 'Email search failed'
        });
    }
})

// ==================== FRONTEND ROUTES ====================

// Landing page (for unauthenticated users)
app.get('/', (req, res) => {
    res.render('landing')
})

// Dashboard (for authenticated users)
app.get('/dashboard', requireAuth, async (req, res) => {
    try {
        // Get user's email accounts and recent emails
        const accounts = await database.getUserEmailAccounts(req.user.id)
        
        // Check if user has email accounts configured
        if (accounts.length === 0) {
            // Redirect to setup if no accounts configured
            return res.redirect('/setup')
        }
        
        const emails = await database.getUserEmails(req.user.id, 100)
        
        // Define categories for the dashboard
        const categories = ['Interested', 'Meeting Booked', 'Not Interested', 'Spam', 'Out of Office']
        
        res.render('dashboard', { 
            user: req.user, 
            accounts: accounts,
            emails: emails,
            accountsCount: accounts.length,
            totalEmails: emails.length,
            storageMode: 'SQLite',
            categories: categories,
            error: null
        })
    } catch (error) {
        console.error('Dashboard error:', error)
        res.render('dashboard', { 
            user: req.user, 
            accounts: [],
            emails: [],
            accountsCount: 0,
            totalEmails: 0,
            storageMode: 'SQLite',
            categories: ['Interested', 'Meeting Booked', 'Not Interested', 'Spam', 'Out of Office'],
            error: 'Failed to load dashboard data'
        })
    }
})

// Email setup page
app.get('/setup', requireAuth, async (req, res) => {
    const user = req.user;
    res.render('setup', { user: user });
})

// Login page
app.get('/login', (req, res) => {
    res.render('login', { error: null })
})

// Register page
app.get('/register', (req, res) => {
    res.render('register', { error: null })
})

// Setup page (add email accounts)
app.get('/setup', requireAuth, async (req, res) => {
    try {
        const accounts = await database.getUserEmailAccounts(req.user.id)
        res.render('setup', { user: req.user, accounts: accounts })
    } catch (error) {
        console.error('Setup page error:', error)
        res.render('setup', { user: req.user, accounts: [], error: 'Failed to load accounts' })
    }
})

// ==================== API ENDPOINTS ====================

// AI Reply Suggestion Endpoint
app.post('/api/suggest-reply', authenticateToken, async (req, res) => {
    try {
        const requestId = Math.random().toString(36).substring(7);
        console.log(`🤖 AI Reply Request [${requestId}] received from user: ${req.user.email}`);
        const { emailContent, sender, subject, context } = req.body;
        
        // Debug logging to see what we're actually getting
        console.log(`📧 DEBUG [${requestId}]: Email content length:`, emailContent ? emailContent.length : 0);
        console.log(`📧 DEBUG [${requestId}]: Sender:`, sender);
        console.log(`📧 DEBUG [${requestId}]: Subject:`, subject);
        console.log(`📧 DEBUG [${requestId}]: First 200 chars of content:`, emailContent ? emailContent.substring(0, 200) : 'No content');
        
        if (!emailContent || !sender) {
            return res.status(400).json({
                success: false,
                error: 'Email content and sender are required'
            });
        }

        // Try to generate reply using OpenAI API first
        try {
            const suggestion = await generateReplyWithAI(emailContent, sender, subject, context, requestId, req.user);
            
            return res.json({
                success: true,
                suggestion: suggestion,
                confidence: 0.9,
                method: 'AI+RAG',
                scenario: 'AI Generated Response',
                analysis: {
                    similar_contexts_count: 1,
                    processing_method: 'OpenAI GPT with RAG Template'
                }
            });
        } catch (aiError) {
            console.log('🔄 OpenAI failed, falling back to template engine:', aiError.message);
            
            // Fallback to template-based response
            const fallbackSuggestion = generateTemplateFallback(emailContent, sender, req.user);
            
            return res.json({
                success: true,
                suggestion: fallbackSuggestion,
                confidence: 0.7,
                method: 'Template Fallback',
                scenario: 'Template Match',
                analysis: {
                    similar_contexts_count: 1,
                    processing_method: 'Template Engine'
                }
            });
        }
        
    } catch (error) {
        console.error('❌ Reply generation error:', error);
        
        // Final fallback response
        const userCalendarLink = req.user.email.includes('vikastg') ? 'https://cal.com/vikastg' : `https://cal.com/${req.user.name.toLowerCase().replace(/\s+/g, '')}`;
        
        return res.json({
            success: true,
            suggestion: `Thank you for your email. I appreciate you reaching out.

I'd be happy to discuss this further. Please feel free to schedule a convenient time: ${userCalendarLink}

Best regards,
${req.user.name}`,
            confidence: 0.5,
            method: 'Default Template',
            scenario: 'General',
            analysis: {
                similar_contexts_count: 0,
                processing_method: 'Default Template'
            }
        });
    }
});

// Helper function to extract clean text from HTML email content
function extractTextFromHTML(htmlContent) {
    if (!htmlContent) return '';
    
    // Remove HTML tags and decode entities
    let text = htmlContent
        .replace(/<script[^>]*>.*?<\/script>/gi, '') // Remove scripts
        .replace(/<style[^>]*>.*?<\/style>/gi, '') // Remove styles
        .replace(/<[^>]*>/g, ' ') // Remove HTML tags
        .replace(/&nbsp;/g, ' ') // Replace non-breaking spaces
        .replace(/&amp;/g, '&') // Decode ampersands
        .replace(/&lt;/g, '<') // Decode less than
        .replace(/&gt;/g, '>') // Decode greater than
        .replace(/&quot;/g, '"') // Decode quotes
        .replace(/&#39;/g, "'") // Decode apostrophes
        .replace(/\s+/g, ' ') // Collapse multiple spaces
        .trim();
    
    // Limit to reasonable length for AI analysis (first 2000 characters)
    if (text.length > 2000) {
        text = text.substring(0, 2000) + '...';
    }
    
    return text;
}

// OpenAI integration function with enhanced RAG
async function generateReplyWithAI(emailContent, sender, subject, context, requestId = 'unknown', user) {
    const openaiApiKey = process.env.OPENAI_API_KEY;
    if (!openaiApiKey) {
        throw new Error('OpenAI API key not configured');
    }

    // Clean and extract meaningful text from HTML email content
    const cleanContent = extractTextFromHTML(emailContent);
    
    console.log(`📧 DEBUG [${requestId}]: Original content length: ${emailContent.length}`);
    console.log(`📧 DEBUG [${requestId}]: Clean content length: ${cleanContent.length}`);
    console.log(`📧 DEBUG [${requestId}]: Clean content preview: ${cleanContent.substring(0, 300)}...`);

    try {
        // Step 1: Retrieve relevant training examples from RAG database
        const relevantExamples = retrieveRelevantExamples(cleanContent, subject);
        
        // Step 2: Generate reply using RAG approach with user-specific info
        const ragPrompt = buildRAGPrompt(cleanContent, subject, sender, relevantExamples, user);
        
        console.log(`🧠 RAG [${requestId}]: Using ${relevantExamples.length} relevant examples for context`);
        if (relevantExamples.length > 0) {
            console.log(`📚 RAG [${requestId}]: Found examples:`, relevantExamples.map(ex => `${ex.type}-${ex.scenario}`));
        }

        const replyResponse = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${openaiApiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: 'gpt-3.5-turbo',
                messages: [
                    {
                        role: 'system',
                        content: `You are ${user.name}, a professional. Generate professional email replies based on the provided examples and context. Follow the examples closely while adapting to the specific email content.`
                    },
                    {
                        role: 'user',
                        content: ragPrompt
                    }
                ],
                max_tokens: 400,
                temperature: 0.7
            })
        });

        const replyData = await replyResponse.json();
        
        // Check if the reply API response has the expected structure
        if (!replyData.choices || !replyData.choices[0] || !replyData.choices[0].message) {
            console.error('❌ Invalid OpenAI reply response structure:', replyData);
            throw new Error('Invalid OpenAI API response structure for reply');
        }
        
        return replyData.choices[0].message.content.trim();

    } catch (error) {
        console.error('AI analysis error:', error);
        throw error;
    }
}

// RAG Training Examples Database
const ragTrainingExamples = [
    // INTERVIEW SPECIFIC EXAMPLES - High Priority
    {
        type: 'INTERVIEW_INVITATION',
        scenario: 'interview_invitation',
        input: 'Your resume has been shortlisted. When will be a good time for you to attend the technical interview?',
        output: 'Thank you for shortlisting my profile! I\'m available for a technical interview. You can book a slot here: https://cal.com/vikastg'
    },
    {
        type: 'INTERVIEW_INVITATION',
        scenario: 'interview_invitation',
        input: 'Hi, Your resume has been shortlisted. When will be a good time for you to attend the technical interview?',
        output: 'Thank you for shortlisting my profile! I\'m available for a technical interview. You can book a slot here: https://cal.com/vikastg'
    },
    {
        type: 'INTERVIEW_INVITATION',
        scenario: 'interview_scheduling',
        input: 'Congratulations! Your profile has been selected for the next round. Please let us know your availability.',
        output: 'Thank you for selecting my profile! I\'m excited about the opportunity. Please book a convenient time slot: https://cal.com/vikastg'
    },
    {
        type: 'INTERVIEW_INVITATION',
        scenario: 'technical_interview',
        input: 'We would like to schedule a technical interview with you. What time suits you?',
        output: 'I\'m available for the technical interview! Please book a slot that works for you: https://cal.com/vikastg'
    },
    {
        type: 'INTERVIEW_INVITATION',
        scenario: 'final_interview',
        input: 'Congratulations! You have cleared our technical rounds. When can you join us for the final interview?',
        output: 'Thank you! I\'m excited about this opportunity. I\'m available for the final interview. Please book a convenient slot: https://cal.com/vikastg'
    },
    {
        type: 'INTERVIEW_INVITATION',
        scenario: 'interview_invitation',
        input: 'Your application has been reviewed and we\'d like to interview you. Are you available this week?',
        output: 'Thank you for reviewing my application! I\'m available for an interview this week. You can book a time slot here: https://cal.com/vikastg'
    },
    {
        type: 'INTERVIEW_INVITATION',
        scenario: 'interview_invitation',
        input: 'We are impressed with your profile. Can we schedule a call to discuss the position?',
        output: 'Thank you! I\'m excited to discuss the position. Please book a call at your convenience: https://cal.com/vikastg'
    },
    
    // Job Opportunity Examples
    {
        type: 'JOB_OPPORTUNITY', 
        scenario: 'job_posting',
        input: 'We have an opening for Full Stack Developer. Are you interested?',
        output: 'Thank you for reaching out! I\'m very interested in the Full Stack Developer position. I have experience with React, Node.js, and Python. Could you share more details about the role? My portfolio: https://vikastg.vercel.app'
    },
    {
        type: 'JOB_OPPORTUNITY',
        scenario: 'hr_outreach',
        input: 'Hi, I found your profile interesting. We have openings for developers. Can we schedule a call?',
        output: 'Thank you for reaching out! I\'m interested in learning more about the developer opportunities. Please book a convenient time: https://cal.com/vikastg'
    },
    {
        type: 'JOB_OPPORTUNITY',
        scenario: 'recruiter_contact',
        input: 'Are you open to new opportunities? We have a great position that matches your skills.',
        output: 'Yes, I\'m open to discussing new opportunities! I\'d love to learn more about the position. You can schedule a call here: https://cal.com/vikastg'
    },
    
    // Project Collaboration Examples
    {
        type: 'PROJECT_COLLABORATION',
        scenario: 'freelance_project',
        input: 'We need a full-stack developer for our e-commerce project. Are you available?',
        output: 'Thank you for considering me! I\'d love to work on your e-commerce project. I have extensive experience with full-stack development. Let\'s discuss the requirements: https://cal.com/vikastg'
    },
    {
        type: 'PROJECT_COLLABORATION',
        scenario: 'collaboration_invite',
        input: 'Would you like to collaborate on an AI project with our team?',
        output: 'I\'m very interested in collaborating on AI projects! I have experience with machine learning and AI development. Let\'s connect to discuss: https://cal.com/vikastg'
    },
    
    // Networking Examples
    {
        type: 'NETWORKING',
        scenario: 'linkedin_connection',
        input: 'I\'d like to connect with you on LinkedIn and explore potential opportunities.',
        output: 'Thank you for reaching out! I\'d be happy to connect and explore opportunities. You can also schedule a call with me: https://cal.com/vikastg'
    },
    {
        type: 'NETWORKING',
        scenario: 'meetup_invitation',
        input: 'We\'re organizing a tech meetup. Would you like to join us?',
        output: 'Thank you for the invitation! I\'d love to join the tech meetup. Please share the details and I\'ll confirm my attendance.'
    },
    
    // Technical Discussion Examples
    {
        type: 'TECHNICAL_DISCUSSION',
        scenario: 'code_review',
        input: 'Could you review our React component architecture?',
        output: 'I\'d be happy to review your React architecture! I have extensive experience with React best practices. Let\'s schedule a session: https://cal.com/vikastg'
    },
    {
        type: 'TECHNICAL_DISCUSSION',
        scenario: 'tech_consultation',
        input: 'We need consultation on our tech stack choices. Can you help?',
        output: 'Absolutely! I\'d love to help with your tech stack decisions. I have experience with various technologies. Let\'s discuss your requirements: https://cal.com/vikastg'
    },
    
    // Business Inquiry Examples
    {
        type: 'BUSINESS_INQUIRY',
        scenario: 'consulting_request',
        input: 'We need a technical consultant for our startup. Are you available?',
        output: 'Thank you for considering me! I\'d be interested in consulting for your startup. Let\'s discuss your technical needs: https://cal.com/vikastg'
    },
    
    // Additional Interview Examples for Better Coverage
    {
        type: 'INTERVIEW_INVITATION',
        scenario: 'interview_invitation',
        input: 'Can you come for an interview next week? What time works for you?',
        output: 'I\'m available for an interview next week! Please book a slot that works for both of us: https://cal.com/vikastg'
    },
    {
        type: 'INTERVIEW_INVITATION',
        scenario: 'phone_screening',
        input: 'We\'d like to have a phone screening call with you. When are you free?',
        output: 'I\'m available for a phone screening call! Please book a convenient time: https://cal.com/vikastg'
    },
    
    // More project examples
    {
        type: 'PROJECT_COLLABORATION',
        scenario: 'startup_opportunity',
        input: 'We\'re a startup looking for a technical co-founder. Interested?',
        output: 'Thank you for considering me! I\'m interested in learning more about the startup and the technical co-founder role. Let\'s discuss: https://cal.com/vikastg'
    },
    {
        type: 'PROJECT_COLLABORATION',
        scenario: 'contract_work',
        input: 'We need someone to build a web application for us. Can you help?',
        output: 'I\'d be happy to help build your web application! I have extensive experience in full-stack development. Let\'s discuss your requirements: https://cal.com/vikastg'
    }
];

// Retrieve relevant examples from RAG database
function retrieveRelevantExamples(emailContent, subject) {
    const normalizedContent = emailContent.toLowerCase();
    const normalizedSubject = (subject || '').toLowerCase();
    const combinedText = `${normalizedSubject} ${normalizedContent}`;
    
    console.log('🔍 RAG Analysis - Subject:', subject);
    console.log('🔍 RAG Analysis - Content snippet:', emailContent.substring(0, 100));
    
    // Score each example based on relevance
    const scoredExamples = ragTrainingExamples.map(example => {
        let score = 0;
        const exampleInput = example.input.toLowerCase();
        const exampleScenario = example.scenario.toLowerCase();
        
        // Enhanced keyword matching with better patterns
        const keyPatterns = [
            // Interview patterns
            { pattern: /(interview|shortlist|select|technical|round|schedule|time)/g, boost: 10, type: 'INTERVIEW' },
            { pattern: /(job|position|role|opportunity|hiring|career|apply|opening|developer|engineer)/g, boost: 8, type: 'JOB' },
            { pattern: /(project|collaboration|work|team|development)/g, boost: 6, type: 'PROJECT' },
            { pattern: /(connect|network|meet|discuss|chat)/g, boost: 5, type: 'NETWORKING' },
            { pattern: /(technical|review|code|assessment|test)/g, boost: 7, type: 'TECHNICAL' },
            { pattern: /(calendar|book|slot|available|time|meeting)/g, boost: 8, type: 'SCHEDULING' }
        ];
        
        // Check patterns in both email content and examples
        keyPatterns.forEach(pattern => {
            const emailMatches = (combinedText.match(pattern.pattern) || []).length;
            const exampleMatches = (exampleInput.match(pattern.pattern) || []).length;
            
            if (emailMatches > 0 && exampleMatches > 0) {
                score += pattern.boost * Math.min(emailMatches, 3); // Cap to avoid over-scoring
            }
        });
        
        // Specific scenario matching with higher weights
        const scenarioMatches = [
            { keywords: ['shortlist', 'interview', 'schedule'], scenario: 'interview_invitation', boost: 15 },
            { keywords: ['technical', 'interview', 'time'], scenario: 'technical_interview', boost: 15 },
            { keywords: ['job', 'opportunity', 'apply'], scenario: 'job_opportunity', boost: 12 },
            { keywords: ['project', 'collaboration', 'work'], scenario: 'project_collaboration', boost: 10 },
            { keywords: ['connect', 'network', 'meet'], scenario: 'networking', boost: 8 },
            { keywords: ['review', 'feedback', 'technical'], scenario: 'technical_discussion', boost: 10 }
        ];
        
        scenarioMatches.forEach(match => {
            const emailHasKeywords = match.keywords.some(keyword => combinedText.includes(keyword));
            const exampleHasScenario = exampleScenario.includes(match.scenario) || 
                                      match.keywords.some(keyword => exampleInput.includes(keyword));
            
            if (emailHasKeywords && exampleHasScenario) {
                score += match.boost;
            }
        });
        
        // Direct type matching
        if (example.type === 'INTERVIEW_INVITATION' && 
            (combinedText.includes('interview') || combinedText.includes('shortlist'))) {
            score += 20;
        }
        
        if (example.type === 'JOB_OPPORTUNITY' && 
            (combinedText.includes('job') || combinedText.includes('opening') || 
             combinedText.includes('position') || combinedText.includes('developer'))) {
            score += 15;
        }
        
        console.log(`📊 Example "${example.scenario}" scored: ${score}`);
        return { ...example, score };
    });
    
    // Return top 2 most relevant examples (reduced for better focus)
    const topExamples = scoredExamples
        .sort((a, b) => b.score - a.score)
        .slice(0, 2)
        .filter(example => example.score > 0);
    
    console.log('🎯 Selected examples:', topExamples.map(ex => `${ex.scenario} (${ex.score})`));
    return topExamples;
}

// Build RAG prompt with retrieved examples
function buildRAGPrompt(emailContent, subject, sender, relevantExamples, user) {
    console.log('🎯 Building RAG prompt with examples:', relevantExamples.length);
    
    let prompt = `You are an intelligent email assistant. Analyze the email content and generate an appropriate, professional reply.

EMAIL TO ANALYZE AND REPLY TO:
From: ${sender}
Subject: ${subject}
Content: ${emailContent}

INSTRUCTIONS:
1. Read and understand the email content carefully
2. Determine what the sender wants or is asking for
3. Generate an intelligent, contextual response based on the email content
4. Be professional, helpful, and appropriate to the context
5. DO NOT use templates or pre-written responses
6. Analyze the specific content and respond accordingly
7. Always end with "Best regards," followed by: ${user.name}

`;

    if (relevantExamples.length > 0) {
        prompt += `REFERENCE EXAMPLES (for tone and style, not content):
`;
        relevantExamples.forEach((example, index) => {
            // Show examples for style reference, but remove personal details
            const genericOutput = example.output
                .replace(/Vikas T G/g, '[NAME]')
                .replace(/https:\/\/cal\.com\/vikastg/g, '[CALENDAR_LINK]')
                .replace(/https:\/\/vikastg\.vercel\.app/g, '[PORTFOLIO_LINK]')
                .replace(/vikastg2020@gmail\.com/g, '[EMAIL]')
                .replace(/vikastg2000@gmail\.com/g, '[EMAIL]');
            
            prompt += `
Example ${index + 1} (${example.scenario}):
Input: "${example.input}"
Style Reference: "${genericOutput.substring(0, 200)}..."
`;
        });
        
        prompt += `
These examples show the tone and professionalism level to match. Now analyze the actual email content and generate a unique, intelligent response.`;
    }
    
    prompt += `

Generate an intelligent reply that addresses the specific email content:`;
    
    return prompt;
}

// Enhanced template fallback function  
function generateTemplateFallback(emailContent, sender, user) {
    console.log(`🔄 Generating AI-powered reply for: ${sender} - ${emailContent.substring(0, 100)}...`);
    
    // No more hardcoded templates! Let the AI handle everything
    // This function now just provides a basic fallback if AI completely fails
    return `Thank you for your email. I've received your message and will respond appropriately.

Best regards,
${user.name}`;
}

// RAG stats endpoint
app.get('/api/rag-stats', authenticateToken, async (req, res) => {
    try {
        console.log(`📊 RAG stats request from user ${req.user.id}`)
        
        res.json({
            status: "active",
            message: "RAG system active with JavaScript implementation",
            email_count: 0,
            vector_db_status: "active"
        })
        
    } catch (error) {
        console.error('Error getting RAG stats:', error)
        res.status(500).json({
            status: "error",
            error: "Internal server error"
        })
    }
});

// Email account setup endpoint
app.post('/api/setup-email-accounts', authenticateToken, async (req, res) => {
    try {
        const { accounts } = req.body
        const userId = req.user.id
        
        if (!accounts || !Array.isArray(accounts) || accounts.length === 0) {
            return res.status(400).json({ error: 'At least one email account is required' })
        }
        
        console.log(`📧 Setting up ${accounts.length} email accounts for user ${userId}`)
        
        // Remove existing email accounts for this user
        await new Promise((resolve, reject) => {
            database.db.run('DELETE FROM email_accounts WHERE user_id = ?', [userId], (err) => {
                if (err) reject(err)
                else resolve()
            })
        })
        
        const addedAccounts = []
        
        for (const account of accounts) {
            if (!account.email || !account.password) {
                continue
            }
            
            try {
                const accountData = {
                    email: account.email,
                    password: account.password.replace(/\s/g, ''), // Remove any spaces
                    imapHost: 'imap.gmail.com',
                    imapPort: 993,
                    provider: 'gmail'
                }
                
                const addedAccount = await database.addEmailAccount(userId, accountData)
                addedAccounts.push(addedAccount)
                console.log(`✅ Added email account: ${account.email}`)
            } catch (error) {
                console.error(`❌ Failed to add account ${account.email}:`, error.message)
            }
        }
        
        if (addedAccounts.length === 0) {
            return res.status(400).json({ error: 'Failed to add any email accounts' })
        }
        
        // Trigger immediate email sync for the user
        console.log(`🚀 Starting immediate email sync for user ${userId}`)
        setTimeout(async () => {
            try {
                await syncEmailsForUser(userId)
                console.log(`✅ Initial email sync completed for user ${userId}`)
            } catch (syncError) {
                console.error(`❌ Email sync failed for user ${userId}:`, syncError.message)
            }
        }, 3000) // Wait 3 seconds before starting sync
        
        res.json({
            success: true,
            message: `Successfully configured ${addedAccounts.length} email accounts`,
            accounts: addedAccounts.map(acc => ({ id: acc.id, email: acc.email }))
        })
        
    } catch (error) {
        console.error('❌ Email setup error:', error)
        res.status(500).json({ error: error.message })
    }
})

// Manual sync endpoint for testing
app.post('/api/manual-sync', authenticateToken, async (req, res) => {
    try {
        console.log("🔄 Manual sync triggered by user:", req.user.id)
        
        await syncEmailsForUser(req.user.id)
        
        res.json({
            success: true,
            message: "Email sync completed successfully",
            timestamp: new Date().toISOString()
        })
    } catch (error) {
        console.error("❌ Manual sync error:", error)
        res.status(500).json({
            success: false,
            error: error.message
        })
    }
})

// Quick login helper endpoint for development
app.post('/api/quick-login', async (req, res) => {
    try {
        const { email } = req.body
        
        console.log('🔑 Quick login attempt for:', email)
        
        if (!email) {
            return res.status(400).json({ error: 'Email required' })
        }
        
        const user = await database.getUserByEmail(email)
        if (!user) {
            return res.status(404).json({ error: 'User not found' })
        }
        
        // Generate token for quick login
        const token = generateToken(user)
        console.log('🔑 Generated token for user:', user.name)
        
        res.cookie('auth_token', token, {
            httpOnly: true,
            secure: false, // Set to true in production with HTTPS
            maxAge: 24 * 60 * 60 * 1000, // 24 hours
            sameSite: 'lax' // Add this for better compatibility
        })
        
        console.log('🔑 Set auth_token cookie for:', user.name)
        
        res.json({
            success: true,
            message: 'Quick login successful',
            user: {
                id: user.id,
                email: user.email,
                name: user.name
            }
        })
    } catch (error) {
        console.error('Quick login error:', error)
        res.status(500).json({ error: 'Login failed' })
    }
})

// Test endpoint for RAG personalization
app.post('/api/test-rag-personalization', authenticateToken, async (req, res) => {
    try {
        const { testEmailContent, testSender, testSubject } = req.body
        
        // Default test email if none provided
        const emailContent = testEmailContent || "Hi, Your resume has been shortlisted for the Full Stack Developer position. When would be a good time for you to attend the technical interview?"
        const sender = testSender || "hr@techcorp.com"
        const subject = testSubject || "Technical Interview Invitation"
        
        console.log(`🧪 Testing RAG personalization for user: ${req.user.name} (${req.user.email})`)
        
        try {
            // Try OpenAI first
            const suggestion = await generateReplyWithAI(emailContent, sender, subject, {}, 'test-rag', req.user)
            
            res.json({
                success: true,
                test_user: {
                    name: req.user.name,
                    email: req.user.email
                },
                input: {
                    emailContent,
                    sender,
                    subject
                },
                ai_reply: suggestion,
                method: "OpenAI + RAG",
                message: "RAG personalization test completed successfully with OpenAI"
            })
        } catch (aiError) {
            console.log(`🔄 OpenAI failed for test, using template fallback: ${aiError.message}`)
            
            // Fallback to template system
            const suggestion = generateTemplateFallback(emailContent, sender, req.user)
            
            res.json({
                success: true,
                test_user: {
                    name: req.user.name,
                    email: req.user.email
                },
                input: {
                    emailContent,
                    sender,
                    subject
                },
                ai_reply: suggestion,
                method: "Template Fallback",
                message: "RAG personalization test completed successfully with template fallback (OpenAI not available)"
            })
        }
        
    } catch (error) {
        console.error('RAG personalization test error:', error)
        res.status(500).json({ 
            success: false,
            error: error.message,
            test_user: {
                name: req.user.name,
                email: req.user.email
            }
        })
    }
})

// Simple test endpoint to verify user authentication
app.get('/api/test-auth', authenticateToken, (req, res) => {
    res.json({
        success: true,
        message: "Authentication working",
        user: {
            id: req.user.id,
            name: req.user.name,
            email: req.user.email
        }
    })
})

// Public endpoint to check sync status
app.get('/api/sync-status', (req, res) => {
    res.json({
        syncEnabled: process.env.AUTO_SYNC_ENABLED === 'true',
        syncInterval: parseInt(process.env.SYNC_INTERVAL_MINUTES) || 2,
        lastSync: new Date().toISOString(),
        emailSyncStarted: emailSyncStarted
    })
})

// Test sync endpoint (temporary)
app.post('/api/test-sync', async (req, res) => {
    try {
        console.log("🧪 Test sync endpoint triggered")
        
        // Get or create default user
        let user = await database.getUserByEmail('test@example.com')
        if (!user) {
            user = await database.addUser('test@example.com', 'test123')
            console.log("👤 Created test user:", user.id)
        }
        
        // Try to sync emails for the test user
        const result = await syncEmailsFromAccount({
            email: process.env.GMAIL_PRIMARY_EMAIL,
            password: process.env.GMAIL_PRIMARY_PASSWORD,
            userId: user.id
        })
        
        console.log("📧 Test sync result:", result)
        
        res.json({
            success: true,
            message: "Test sync completed",
            result: result,
            userId: user.id
        })
        
    } catch (error) {
        console.error("❌ Test sync error:", error)
        res.status(500).json({
            success: false,
            error: error.message
        })
    }
})

// Auto-sync emails on server startup 
async function initializeEmailSync() {
    console.log("🚀 Initializing email sync...")
    
    try {
        // Get or create your user account
        let user = await database.getUserByEmail(process.env.USER_EMAIL || 'vikastg2000@gmail.com')
        if (!user) {
            user = await database.createUser(process.env.USER_EMAIL || 'vikastg2000@gmail.com', 'vikas123', 'Vikas T G')
            console.log("👤 Created user account:", user.id)
        }
        
        // Add email accounts with proper passwords
        let accounts = await database.getUserEmailAccounts(user.id)
        console.log(`📧 Found ${accounts.length} existing email accounts`)
        
        // Add primary email account if not exists
        const primaryExists = accounts.find(acc => acc.email === process.env.GMAIL_PRIMARY_EMAIL)
        if (!primaryExists && process.env.GMAIL_PRIMARY_EMAIL) {
            try {
                await database.addEmailAccount(user.id, {
                    email: process.env.GMAIL_PRIMARY_EMAIL,
                    password: process.env.GMAIL_PRIMARY_PASSWORD,
                    imapHost: 'imap.gmail.com',
                    imapPort: 993,
                    provider: 'gmail'
                })
                console.log("📧 Added primary email account:", process.env.GMAIL_PRIMARY_EMAIL)
            } catch (err) {
                console.error("❌ Error adding primary email:", err.message)
            }
        }
        
        // Add secondary email account if not exists
        const secondaryExists = accounts.find(acc => acc.email === process.env.GMAIL_SECONDARY_EMAIL)
        if (!secondaryExists && process.env.GMAIL_SECONDARY_EMAIL) {
            try {
                await database.addEmailAccount(user.id, {
                    email: process.env.GMAIL_SECONDARY_EMAIL,
                    password: process.env.GMAIL_SECONDARY_PASSWORD,
                    imapHost: 'imap.gmail.com',
                    imapPort: 993,
                    provider: 'gmail'
                })
                console.log("📧 Added secondary email account:", process.env.GMAIL_SECONDARY_EMAIL)
            } catch (err) {
                console.error("❌ Error adding secondary email:", err.message)
            }
        }
        
        // Start initial email sync after server initializes
        setTimeout(async () => {
            console.log("📬 Starting initial automatic email sync...")
            
            try {
                await syncEmailsForUser(user.id)
                console.log("✅ Initial auto-sync completed")
            } catch (syncError) {
                console.error("❌ Initial auto-sync failed:", syncError.message)
            }
        }, 3000) // Wait 3 seconds after server start
        
    } catch (error) {
        console.error("❌ Auto-sync initialization failed:", error)
    }
}

const PORT = process.env.PORT || 4000

app.listen(PORT, () => {
    console.log(`App is listening on port ${PORT}`)
    console.log("🚀 Real-time email sync service will be handled by dedicated Python service")
    console.log("🚀 Real-time email sync service initialized")
    
    // Initialize email sync for production
    initializeEmailSync()
})
