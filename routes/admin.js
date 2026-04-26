const express = require('express');
const router = express.Router();
const { adminAuth } = require('../middleware/auth');
const store = require('../lib/store');

// Get overview stats
router.get('/stats', adminAuth, async (req, res) => {
    try {
        const totalUsers = await store.countUsers();
        const totalAnalyses = await store.countAnalyses();
        const doshaDistribution = await store.getDoshaDistribution();

        res.json({
            totalUsers,
            totalAnalyses,
            doshaDistribution
        });
    } catch (err) {
        res.status(500).json({ error: 'Failed to fetch admin stats' });
    }
});

// Get all users
router.get('/users', adminAuth, async (req, res) => {
    try {
        const users = await store.listUsers();
        res.json(users);
    } catch (err) {
        res.status(500).json({ error: 'Failed to fetch users' });
    }
});

// Delete a user
router.delete('/users/:id', adminAuth, async (req, res) => {
    try {
        await store.deleteUser(req.params.id);
        res.json({ message: 'User deleted' });
    } catch (err) {
        res.status(500).json({ error: 'Failed to delete user' });
    }
});

// Get all analyses
router.get('/analyses', adminAuth, async (req, res) => {
    try {
        const analyses = await store.getAllAnalyses();
        res.json(analyses);
    } catch (err) {
        res.status(500).json({ error: 'Failed to fetch analyses logs' });
    }
});

module.exports = router;
