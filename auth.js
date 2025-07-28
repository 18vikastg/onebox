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

    console.log('🔐 Auth check - Header token:', token ? 'present' : 'none');
    console.log('🔐 Auth check - Cookie tokens:', {
        auth_token: req.cookies?.auth_token ? 'present' : 'none',
        token: req.cookies?.token ? 'present' : 'none'
    });
    console.log('🔐 Auth check - Final token:', finalToken ? 'present' : 'none');

    if (!finalToken) {
        console.log('🔐 Auth failed - No token found');
        return res.status(401).json({ error: 'Access token required' });
    }

    try {
        const decoded = jwt.verify(finalToken, JWT_SECRET);
        const user = await database.getUserById(decoded.userId);
        
        if (!user) {
            console.log('🔐 Auth failed - Invalid user');
            return res.status(401).json({ error: 'Invalid token' });
        }

        console.log('🔐 Auth success for user:', user.name);
        req.user = user;
        next();
    } catch (error) {
        console.log('🔐 Auth failed - Token verification error:', error.message);
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
