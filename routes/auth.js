const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const store = require('../lib/store');

// Register
router.post('/register', async (req, res) => {
    try {
        const { name, email, password } = req.body;
        const normalizedEmail = store.normalizeEmail(email);

        if (!name || !normalizedEmail || !password) {
            return res.status(400).json({ error: 'Name, email, and password are required' });
        }
        
        // Check if user exists
        let user = await store.findUserByEmail(normalizedEmail);
        if (user) return res.status(400).json({ error: 'User already exists' });

        // Hash password
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        // Make first user an admin for demo purposes (Optional)
        const userCount = await store.countUsers();
        const role = userCount === 0 ? 'admin' : 'user';

        user = await store.createUser({
            name,
            password: hashedPassword,
            email: normalizedEmail,
            role
        });
        res.status(201).json({ message: 'User registered successfully!' });
    } catch (err) {
        res.status(500).json({ error: 'Server error during registration' });
    }
});

// Login
router.post('/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        const normalizedEmail = store.normalizeEmail(email);

        // Check user
        const user = await store.findUserByEmail(normalizedEmail);
        if (!user) return res.status(400).json({ error: 'Invalid email or password' });

        // Validate password
        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) return res.status(400).json({ error: 'Invalid email or password' });

        // Create token
        const token = jwt.sign(
            { _id: user._id, role: user.role, name: user.name },
            process.env.JWT_SECRET || 'fallback_secret',
            { expiresIn: '1d' }
        );

        res.json({ token, role: user.role, name: user.name });
    } catch (err) {
        res.status(500).json({ error: 'Server error during login' });
    }
});

module.exports = router;
