let express = require('express')
const {spawn} = require('child_process')
let fs = require('fs')
const { parse } = require('csv-parse')
const path = require('path')
const fetch = require('node-fetch')

let app = express()

app.set('view engine', 'ejs')

app.use(express.json())
app.use(express.urlencoded({extended:false}))

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

// JSON storage file path
const JSON_STORAGE_FILE = path.join(__dirname, 'emails_cache.json')

// Helper function to read emails from storage (JSON or Elasticsearch)
async function readEmailsFromStorage() {
    try {
        // For now, we'll read from JSON storage
        // In the future, this could query Elasticsearch directly
        if (fs.existsSync(JSON_STORAGE_FILE)) {
            const fileContent = fs.readFileSync(JSON_STORAGE_FILE, 'utf8')
            // Check if file is empty or contains incomplete JSON
            if (fileContent.trim() === '') {
                return []
            }
            const data = JSON.parse(fileContent)
            return data.emails || []
        }
    } catch (error) {
        console.error('Error reading email storage:', error)
        // If JSON is corrupted or being written, try again in a moment
        try {
            // Wait a bit and try one more time
            setTimeout(() => {}, 100)
            if (fs.existsSync(JSON_STORAGE_FILE)) {
                const fileContent = fs.readFileSync(JSON_STORAGE_FILE, 'utf8')
                if (fileContent.trim() !== '') {
                    const data = JSON.parse(fileContent)
                    return data.emails || []
                }
            }
        } catch (retryError) {
            console.error('Retry failed, returning empty array:', retryError)
        }
    }
    return []
}

// Alternative: Query Elasticsearch directly via HTTP
async function queryElasticsearch(query = {}) {
    try {
        const esUrl = 'http://localhost:9200/emails/_search'
        console.log('Querying Elasticsearch with:', JSON.stringify(query, null, 2))
        
        const response = await fetch(esUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query.query || { match_all: {} },
                sort: query.sort || [{ date_synced: { order: 'desc' } }],
                size: query.size || 100
            })
        })
        
        if (response.ok) {
            const data = await response.json()
            console.log(`Elasticsearch returned ${data.hits.hits.length} emails`)
            return data.hits.hits.map(hit => hit._source)
        } else {
            console.error('Elasticsearch response not ok:', response.status, response.statusText)
        }
    } catch (error) {
        console.error('Error querying Elasticsearch:', error)
    }
    
    // Fallback to JSON storage
    console.log('Falling back to JSON storage')
    return readEmailsFromStorage()
}

// Helper function to get unique accounts
function getAccounts(emails) {
    return [...new Set(emails.map(email => email.account_email))]
}

// Helper function to get unique categories
function getCategories(emails) {
    const categories = [...new Set(emails.map(email => email.category).filter(cat => cat))]
    return categories.length > 0 ? categories : ['Interested', 'Meeting Booked', 'Not Interested', 'Spam', 'Out of Office']
}

let emails = []

app.get('/', async (req,res) => {
    try {
        // Try Elasticsearch first
        let emails = await queryElasticsearch({
            query: { match_all: {} },
            size: 50
        })
        
        // Get all emails to extract accounts
        const allEmails = await queryElasticsearch({
            query: { match_all: {} },
            size: 10000
        })
        
        const accounts = getAccounts(allEmails)
        const categories = getCategories(allEmails)
        
        res.render('index', {
            emails: emails, 
            accounts: accounts,
            categories: categories,
            error: null,
            storageMode: 'Elasticsearch',
            totalEmails: allEmails.length
        })
    } catch (error) {
        console.error('Error loading emails:', error)
        res.render('index', {
            emails: [], 
            accounts: [], 
            categories: [],
            error: 'Failed to load emails',
            storageMode: 'Error',
            totalEmails: 0
        })
    }
})

// API endpoint for emails
app.get('/api/emails', async (req, res) => {
    try {
        const emails = await queryElasticsearch({
            query: { match_all: {} },
            size: 1000
        })
        
        res.json({
            success: true,
            emails: emails,
            count: emails.length
        })
    } catch (error) {
        console.error('Error fetching emails for API:', error)
        res.status(500).json({
            success: false,
            error: 'Failed to fetch emails',
            emails: []
        })
    }
})

app.post('/fetch-emails', async (req, res) => {
    try {
        let subject = req.body.subject
        let total = parseInt(req.body.total) || 50
        let fromdate = req.body.fromdate || req.body.fromDate
        let toDate = req.body.toDate || req.body.todate
        let account = req.body.account || 'all'
        let category = req.body.category || 'all'

        // Build Elasticsearch query
        const esQuery = {
            query: {
                bool: {
                    must: []
                }
            },
            size: total,
            sort: [{ date_synced: { order: 'desc' } }]
        }
        
        // Add subject search
        if (subject && subject.trim() !== '') {
            esQuery.query.bool.must.push({
                multi_match: {
                    query: subject,
                    fields: ['subject', 'sender']
                }
            })
        }
        
        // Add account filter
        if (account && account !== 'all') {
            esQuery.query.bool.must.push({
                term: {
                    "account_email": account
                }
            })
        }
        
        // Add category filter
        if (category && category !== 'all') {
            esQuery.query.bool.must.push({
                match: {
                    "category": category
                }
            })
        }
        
        // Add date filters
        if (fromdate || toDate) {
            const dateRange = {}
            if (fromdate) dateRange.gte = fromdate
            if (toDate) dateRange.lte = toDate
            
            esQuery.query.bool.must.push({
                range: {
                    date_received: dateRange
                }
            })
        }
        
        // If no filters, just get all emails
        if (esQuery.query.bool.must.length === 0) {
            esQuery.query = { match_all: {} }
        }
        
        const emails = await queryElasticsearch(esQuery)
        
        // Get all emails to extract accounts
        const allEmails = await queryElasticsearch({
            query: { match_all: {} },
            size: 10000
        })
        const accounts = getAccounts(allEmails)
        const categories = getCategories(allEmails)
        
        res.render('index', {
            emails: emails, 
            accounts: accounts,
            categories: categories,
            error: null,
            storageMode: 'Elasticsearch',
            totalEmails: allEmails.length,
            searchQuery: subject || '',
            selectedAccount: account || 'all',
            selectedCategory: category || 'all'
        })
        
    } catch (error) {
        console.error('Error in fetch-emails:', error)
        res.render('index', {
            emails: [], 
            accounts: [], 
            categories: [],
            error: 'Search failed: ' + error.message,
            storageMode: 'Error',
            totalEmails: 0,
            searchQuery: subject || '',
            selectedAccount: account || 'all',
            selectedCategory: category || 'all'
        })
    }
})

// New route for real-time email count
app.get('/api/stats', async (req, res) => {
    try {
        const emails = await readEmailsFromStorage()
        const accounts = getAccounts(emails)
        
        const stats = accounts.map(account => ({
            account_email: account,
            count: emails.filter(email => email.account_email === account).length
        }))
        
        res.json(stats)
    } catch (error) {
        console.error('Error getting stats:', error)
        res.status(500).json({ error: 'Failed to get stats' })
    }
})

// Enhanced API endpoint for advanced search
app.get('/api/search', async (req, res) => {
    try {
        const { q, account, category, limit = 50 } = req.query;
        
        let esQuery = {
            query: { match_all: {} },
            size: parseInt(limit)
        };
        
        if (q || account !== 'all' || category !== 'all') {
            esQuery.query = { bool: { must: [] } };
            
            if (q) {
                esQuery.query.bool.must.push({
                    multi_match: {
                        query: q,
                        fields: ['subject^2', 'sender', 'body']
                    }
                });
            }
            
            if (account && account !== 'all') {
                esQuery.query.bool.must.push({
                    term: { 'account_email': account }
                });
            }
            
            if (category && category !== 'all') {
                esQuery.query.bool.must.push({
                    term: { 'category': category }
                });
            }
        }
        
        const emails = await queryElasticsearch(esQuery);
        res.json({ 
            success: true, 
            emails: emails,
            total: emails.length 
        });
        
    } catch (error) {
        console.error('Error in search API:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Search failed: ' + error.message 
        });
    }
})

// API endpoint for email categories and accounts
app.get('/api/filters', async (req, res) => {
    try {
        const emails = await readEmailsFromStorage();
        const accounts = getAccounts(emails);
        const categories = getCategories(emails);
        
        res.json({
            success: true,
            accounts: accounts,
            categories: categories,
            totalEmails: emails.length
        });
    } catch (error) {
        console.error('Error getting filters:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Failed to get filters' 
        });
    }
})

// API endpoint for reply suggestions using RAG
app.post('/api/suggest-reply', async (req, res) => {
    try {
        const { emailContent, sender, subject, context } = req.body;
        
        if (!emailContent || !sender) {
            return res.status(400).json({
                success: false,
                error: 'Email content and sender are required'
            });
        }
        
        // Call Python RAG engine for reply suggestion
        const pythonProcess = spawn('./.venv/bin/python', ['-c', `
import sys
import json
sys.path.append('.')
from reply_suggestion_engine import suggest_email_reply

try:
    email_content = """${emailContent.replace(/"/g, '\\"')}"""
    sender = "${sender.replace(/"/g, '\\"')}"
    subject = "${subject ? subject.replace(/"/g, '\\"') : ''}"
    
    result = suggest_email_reply(email_content, sender, subject)
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}))
        `]);
        
        let resultData = '';
        let errorData = '';
        
        pythonProcess.stdout.on('data', (data) => {
            resultData += data.toString();
        });
        
        pythonProcess.stderr.on('data', (data) => {
            errorData += data.toString();
        });
        
        pythonProcess.on('close', (code) => {
            try {
                if (code === 0 && resultData.trim()) {
                    const result = JSON.parse(resultData.trim());
                    res.json(result);
                } else {
                    console.error('Python process error:', errorData);
                    res.status(500).json({
                        success: false,
                        error: 'Failed to generate reply suggestion',
                        details: errorData
                    });
                }
            } catch (parseError) {
                console.error('JSON parse error:', parseError, 'Raw data:', resultData);
                res.status(500).json({
                    success: false,
                    error: 'Failed to parse reply suggestion response'
                });
            }
        });
        
    } catch (error) {
        console.error('Error generating reply suggestion:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});

// API endpoint to add custom reply templates
app.post('/api/add-template', async (req, res) => {
    try {
        const { scenario, emailPattern, replyTemplate, category } = req.body;
        
        if (!scenario || !emailPattern || !replyTemplate) {
            return res.status(400).json({
                success: false,
                error: 'Scenario, email pattern, and reply template are required'
            });
        }
        
        // Call Python to add template
        const pythonProcess = spawn('./.venv/bin/python', ['-c', `
import sys
import json
sys.path.append('.')
from reply_suggestion_engine import rag_engine

try:
    success = rag_engine.add_user_template(
        "${scenario.replace(/"/g, '\\"')}", 
        "${emailPattern.replace(/"/g, '\\"')}", 
        "${replyTemplate.replace(/"/g, '\\"')}", 
        "${category || 'custom'}"
    )
    print(json.dumps({"success": success}))
except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}))
        `]);
        
        let resultData = '';
        
        pythonProcess.stdout.on('data', (data) => {
            resultData += data.toString();
        });
        
        pythonProcess.on('close', (code) => {
            try {
                if (code === 0 && resultData.trim()) {
                    const result = JSON.parse(resultData.trim());
                    res.json(result);
                } else {
                    res.status(500).json({
                        success: false,
                        error: 'Failed to add template'
                    });
                }
            } catch (parseError) {
                res.status(500).json({
                    success: false,
                    error: 'Failed to parse response'
                });
            }
        });
        
    } catch (error) {
        console.error('Error adding template:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});

// API endpoint to get RAG engine statistics
app.get('/api/rag-stats', async (req, res) => {
    try {
        const pythonProcess = spawn('./.venv/bin/python', ['-c', `
import sys
import json
sys.path.append('.')
from reply_suggestion_engine import rag_engine

try:
    stats = rag_engine.get_stats()
    print(json.dumps(stats))
except Exception as e:
    print(json.dumps({"status": "error", "error": str(e)}))
        `]);
        
        let resultData = '';
        
        pythonProcess.stdout.on('data', (data) => {
            resultData += data.toString();
        });
        
        pythonProcess.on('close', (code) => {
            try {
                if (code === 0 && resultData.trim()) {
                    const result = JSON.parse(resultData.trim());
                    res.json(result);
                } else {
                    res.status(500).json({
                        status: "error",
                        error: "Failed to get RAG stats"
                    });
                }
            } catch (parseError) {
                res.status(500).json({
                    status: "error",
                    error: "Failed to parse response"
                });
            }
        });
        
    } catch (error) {
        console.error('Error getting RAG stats:', error);
        res.status(500).json({
            status: "error",
            error: "Internal server error"
        });
    }
});

app.listen(4000, () => {
    console.log("App is listening on port 4000")
})
