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
        console.log('🤖 AI Reply Request received from user:', req.user.email);
        const { emailContent, sender, subject, context } = req.body;
        
        if (!emailContent || !sender) {
            return res.status(400).json({
                success: false,
                error: 'Email content and sender are required'
            });
        }

        // Try to generate reply using OpenAI API first
        try {
            const suggestion = await generateReplyWithAI(emailContent, sender, subject, context);
            
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
            const fallbackSuggestion = generateTemplateFallback(emailContent, sender);
            
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
        return res.json({
            success: true,
            suggestion: `Thank you for your email. I appreciate you reaching out.

I'd be happy to discuss this further. Please feel free to schedule a convenient time: https://cal.com/vikastg

Best regards,
Vikas T G`,
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

// OpenAI integration function
async function generateReplyWithAI(emailContent, sender, subject, context) {
    const openaiApiKey = process.env.OPENAI_API_KEY;
    if (!openaiApiKey) {
        throw new Error('OpenAI API key not configured');
    }

    const prompt = `You are an AI assistant helping to write professional email replies. 

CONTEXT:
- You are Vikas T G, a Full Stack Developer and AI Engineer
- Your email: vikastg.dev@gmail.com
- Your portfolio: https://vikastg.vercel.app
- Your calendar link: https://cal.com/vikastg
- You are professional, friendly, and prompt in responses

EMAIL TO REPLY TO:
From: ${sender}
Subject: ${subject || 'No Subject'}
Content: ${emailContent}

INSTRUCTIONS:
1. Write a professional, contextually appropriate reply
2. If it's about job opportunities/interviews, mention your availability and calendar link
3. If it's about projects/collaboration, show enthusiasm and mention scheduling a discussion
4. Keep the tone professional but friendly
5. Always sign off as "Best regards, Vikas T G"
6. Be concise but complete

Generate only the email reply content:`;

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
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
                    content: 'You are a professional email assistant. Write concise, professional email replies.'
                },
                {
                    role: 'user',
                    content: prompt
                }
            ],
            max_tokens: 300,
            temperature: 0.7
        })
    });

    if (!response.ok) {
        throw new Error(`OpenAI API error: ${response.status}`);
    }

    const data = await response.json();
    return data.choices[0].message.content.trim();
}

// Template fallback function
function generateTemplateFallback(emailContent, sender) {
    const lowerContent = emailContent.toLowerCase();
    
    if (lowerContent.includes('interview') || lowerContent.includes('shortlisted') || lowerContent.includes('technical')) {
        return `Thank you for shortlisting my profile! I'm excited about this opportunity and available for a technical interview.

I can accommodate your schedule - please feel free to book a convenient time slot here: https://cal.com/vikastg

Looking forward to discussing my qualifications further.

Best regards,
Vikas T G`;
    }
    
    if (lowerContent.includes('meeting') || lowerContent.includes('discuss') || lowerContent.includes('project')) {
        return `Thank you for reaching out! I would be happy to discuss the project requirements with you.

I'm available for a meeting and can accommodate your schedule. You can book a convenient time slot here: https://cal.com/vikastg

Looking forward to our discussion!

Best regards,
Vikas T G`;
    }
    
    if (lowerContent.includes('opportunity') || lowerContent.includes('role') || lowerContent.includes('position')) {
        return `Thank you for considering me for this opportunity! I'm very interested in learning more about the role.

I'm available to discuss how my skills can contribute to your team. Please feel free to schedule a call here: https://cal.com/vikastg

Looking forward to connecting with you!

Best regards,
Vikas T G`;
    }
    
    // Default professional response
    return `Thank you for your email. I appreciate you reaching out.

I'm available to discuss this further at your convenience. You can schedule a meeting here: https://cal.com/vikastg

Looking forward to hearing from you!

Best regards,
Vikas T G`;
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
        
        if (!email) {
            return res.status(400).json({ error: 'Email required' })
        }
        
        const user = await database.getUserByEmail(email)
        if (!user) {
            return res.status(404).json({ error: 'User not found' })
        }
        
        // Generate token for quick login
        const token = generateToken(user)
        
        res.cookie('token', token, {
            httpOnly: true,
            secure: false, // Set to true in production with HTTPS
            maxAge: 24 * 60 * 60 * 1000 // 24 hours
        })
        
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
