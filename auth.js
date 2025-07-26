const jwt = require('jsonwebtoken');
const database = require('./models');

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';

const generateToken = (user) => {
    return jwt.sign(
        { userId: user.id, email: user.email },
        JWT_SECRET,
        { expiresIn: '24h' }
    );
};

const authenticateToken = async (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    // Also check for token in cookies for browser sessions (check both auth_token and token)
    const cookieToken = req.cookies?.auth_token || req.cookies?.token;
    const finalToken = token || cookieToken;

    if (!finalToken) {
        return res.status(401).json({ error: 'Access token required' });
    }

    try {
        const decoded = jwt.verify(finalToken, JWT_SECRET);
        const user = await database.getUserById(decoded.userId);
        
        if (!user) {
            return res.status(401).json({ error: 'Invalid token' });
        }

        req.user = user;
        next();
    } catch (error) {
        return res.status(403).json({ error: 'Invalid token' });
    }
};

// Middleware to check if user is authenticated for web pages
const requireAuth = async (req, res, next) => {
    const token = req.cookies?.auth_token;

    if (!token) {
        return res.redirect('/login');
    }

    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        const user = await database.getUserById(decoded.userId);
        
        if (!user) {
            res.clearCookie('auth_token');
            return res.redirect('/login');
        }

        req.user = user;
        next();
    } catch (error) {
        res.clearCookie('auth_token');
        return res.redirect('/login');
    }
};

module.exports = {
    generateToken,
    authenticateToken,
    requireAuth
};
