const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcryptjs');
const path = require('path');

class Database {
    constructor() {
        this.db = new sqlite3.Database(path.join(__dirname, 'reachinbox.db'));
        this.initTables();
    }

    initTables() {
        // Users table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Email accounts table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS email_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                imap_host TEXT NOT NULL,
                imap_port INTEGER DEFAULT 993,
                password TEXT NOT NULL,
                provider TEXT DEFAULT 'gmail',
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        `);

        // Emails table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                account_id INTEGER NOT NULL,
                uid TEXT NOT NULL,
                subject TEXT,
                sender TEXT,
                content TEXT,
                category TEXT,
                confidence_score REAL,
                date_received DATETIME,
                date_synced DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (account_id) REFERENCES email_accounts (id)
            )
        `);

        console.log('Database tables initialized');
    }

    // User methods
    async createUser(email, password, name) {
        return new Promise((resolve, reject) => {
            const passwordHash = bcrypt.hashSync(password, 10);
            this.db.run(
                'INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)',
                [email, passwordHash, name],
                function(err) {
                    if (err) reject(err);
                    else resolve({ id: this.lastID, email, name });
                }
            );
        });
    }

    async getUserByEmail(email) {
        return new Promise((resolve, reject) => {
            this.db.get(
                'SELECT * FROM users WHERE email = ?',
                [email],
                (err, row) => {
                    if (err) reject(err);
                    else resolve(row);
                }
            );
        });
    }

    async getUserById(id) {
        return new Promise((resolve, reject) => {
            this.db.get(
                'SELECT id, email, name, created_at FROM users WHERE id = ?',
                [id],
                (err, row) => {
                    if (err) reject(err);
                    else resolve(row);
                }
            );
        });
    }

    async getAllUsers() {
        return new Promise((resolve, reject) => {
            this.db.all(
                'SELECT id, email, name, created_at FROM users',
                [],
                (err, rows) => {
                    if (err) reject(err);
                    else resolve(rows || []);
                }
            );
        });
    }

    // Email account methods
    async addEmailAccount(userId, accountData) {
        return new Promise((resolve, reject) => {
            const { email, imapHost, imapPort, password, provider } = accountData;
            this.db.run(
                `INSERT INTO email_accounts (user_id, email, imap_host, imap_port, password, provider) 
                 VALUES (?, ?, ?, ?, ?, ?)`,
                [userId, email, imapHost, imapPort, password, provider],
                function(err) {
                    if (err) reject(err);
                    else resolve({ id: this.lastID, ...accountData });
                }
            );
        });
    }

    async getUserEmailAccounts(userId) {
        return new Promise((resolve, reject) => {
            this.db.all(
                'SELECT id, email, imap_host, imap_port, provider, is_active, created_at FROM email_accounts WHERE user_id = ? AND is_active = 1',
                [userId],
                (err, rows) => {
                    if (err) reject(err);
                    else resolve(rows);
                }
            );
        });
    }

    async deleteEmailAccount(userId, accountId) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'UPDATE email_accounts SET is_active = 0 WHERE id = ? AND user_id = ?',
                [accountId, userId],
                function(err) {
                    if (err) reject(err);
                    else resolve(this.changes > 0);
                }
            );
        });
    }

    // Email methods
    async saveEmail(userId, accountId, emailData) {
        return new Promise((resolve, reject) => {
            const { uid, subject, sender, content, category, confidence_score, date_received } = emailData;
            this.db.run(
                `INSERT OR REPLACE INTO emails 
                 (user_id, account_id, uid, subject, sender, content, category, confidence_score, date_received) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                [userId, accountId, uid, subject, sender, content, category, confidence_score, date_received],
                function(err) {
                    if (err) reject(err);
                    else resolve({ id: this.lastID, ...emailData });
                }
            );
        });
    }

    async addEmail(emailData) {
        return new Promise((resolve, reject) => {
            const { 
                subject, 
                sender, 
                snippet, 
                content, 
                received_at, 
                user_id, 
                email_account, 
                category, 
                is_read 
            } = emailData;
            
            // Generate a unique UID from content hash
            const uid = require('crypto').createHash('md5').update(content + sender + subject).digest('hex');
            
            this.db.run(
                `INSERT OR REPLACE INTO emails 
                 (user_id, account_id, uid, subject, sender, content, category, confidence_score, date_received, is_read) 
                 VALUES (?, 1, ?, ?, ?, ?, ?, 0.8, ?, ?)`,
                [user_id, uid, subject, sender, content, category, received_at, is_read ? 1 : 0],
                function(err) {
                    if (err) reject(err);
                    else resolve({ id: this.lastID, ...emailData });
                }
            );
        });
    }

    async getUserEmails(userId, limit = 50) {
        return new Promise((resolve, reject) => {
            this.db.all(
                `SELECT e.*, ea.email as account_email 
                 FROM emails e 
                 JOIN email_accounts ea ON e.account_id = ea.id 
                 WHERE e.user_id = ? 
                 ORDER BY e.date_received DESC 
                 LIMIT ?`,
                [userId, limit],
                (err, rows) => {
                    if (err) reject(err);
                    else resolve(rows);
                }
            );
        });
    }

    async getUserEmailsByCategory(userId, category) {
        return new Promise((resolve, reject) => {
            this.db.all(
                `SELECT e.*, ea.email as account_email 
                 FROM emails e 
                 JOIN email_accounts ea ON e.account_id = ea.id 
                 WHERE e.user_id = ? AND e.category = ? 
                 ORDER BY e.date_received DESC`,
                [userId, category],
                (err, rows) => {
                    if (err) reject(err);
                    else resolve(rows);
                }
            );
        });
    }

    async searchUserEmails(userId, searchParams = {}) {
        return new Promise((resolve, reject) => {
            let query = `SELECT e.*, ea.email as account_email 
                        FROM emails e 
                        JOIN email_accounts ea ON e.account_id = ea.id 
                        WHERE e.user_id = ?`;
            let params = [userId];

            // Add search filters
            if (searchParams.subject && searchParams.subject.trim()) {
                query += ' AND (e.subject LIKE ? OR e.sender LIKE ? OR e.content LIKE ?)';
                const searchTerm = `%${searchParams.subject.trim()}%`;
                params.push(searchTerm, searchTerm, searchTerm);
            }

            if (searchParams.category && searchParams.category !== 'all') {
                query += ' AND e.category = ?';
                params.push(searchParams.category);
            }

            if (searchParams.account && searchParams.account !== 'all') {
                query += ' AND ea.email = ?';
                params.push(searchParams.account);
            }

            if (searchParams.fromDate) {
                query += ' AND date(e.date_received) >= ?';
                params.push(searchParams.fromDate);
            }

            if (searchParams.toDate) {
                query += ' AND date(e.date_received) <= ?';
                params.push(searchParams.toDate);
            }

            // Add sorting
            switch (searchParams.sortBy) {
                case 'date_asc':
                    query += ' ORDER BY e.date_received ASC';
                    break;
                case 'subject':
                    query += ' ORDER BY e.subject ASC';
                    break;
                case 'sender':
                    query += ' ORDER BY e.sender ASC';
                    break;
                default:
                    query += ' ORDER BY e.date_received DESC';
            }

            // Add limit
            const limit = parseInt(searchParams.total) || 100;
            query += ' LIMIT ?';
            params.push(limit);

            this.db.all(query, params, (err, rows) => {
                if (err) reject(err);
                else resolve(rows || []);
            });
        });
    }

    validatePassword(password, hash) {
        return bcrypt.compareSync(password, hash);
    }
}

module.exports = new Database();
