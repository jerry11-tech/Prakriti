const fs = require('fs/promises');
const path = require('path');
const crypto = require('crypto');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const User = require('../models/User');
const Analysis = require('../models/Analysis');

const dataDir = path.join(__dirname, '..', 'data');
const dataFile = path.join(dataDir, 'app-data.json');

let mode = 'file';

function normalizeEmail(email = '') {
    return String(email).trim().toLowerCase();
}

async function ensureDataFile() {
    await fs.mkdir(dataDir, { recursive: true });
    try {
        await fs.access(dataFile);
    } catch {
        await fs.writeFile(dataFile, JSON.stringify({ users: [], analyses: [] }, null, 2));
    }
}

async function readData() {
    await ensureDataFile();
    const content = await fs.readFile(dataFile, 'utf8');
    return JSON.parse(content);
}

async function writeData(data) {
    await ensureDataFile();
    await fs.writeFile(dataFile, JSON.stringify(data, null, 2));
}

async function ensureSeedAdmin() {
    const email = normalizeEmail(process.env.SEED_ADMIN_EMAIL || 'admin@gmail.com');
    const password = process.env.SEED_ADMIN_PASSWORD || '12345';

    if (mode === 'mongo') {
        let adminUser = await User.findOne({ email });
        if (!adminUser) {
            adminUser = new User({
                name: 'Admin',
                email,
                password: await bcrypt.hash(password, 10),
                role: 'admin'
            });
            await adminUser.save();
        }
        return;
    }

    const data = await readData();
    const existing = data.users.find((user) => user.email === email);

    if (!existing) {
        data.users.push({
            _id: crypto.randomUUID(),
            name: 'Admin',
            email,
            password: await bcrypt.hash(password, 10),
            role: 'admin',
            createdAt: new Date().toISOString()
        });
        await writeData(data);
    }
}

async function initStore() {
    const mongoUri = process.env.MONGODB_URI;

    if (mongoUri) {
        try {
            await mongoose.connect(mongoUri);
            mode = 'mongo';
            console.log('Connected to MongoDB');
        } catch (error) {
            mode = 'file';
            console.warn('MongoDB connection failed. Falling back to local file storage.');
            console.warn(error.message);
        }
    } else {
        mode = 'file';
        console.log('MONGODB_URI not set. Using local file storage.');
    }

    await ensureSeedAdmin();
    return mode;
}

async function findUserByEmail(email) {
    const normalizedEmail = normalizeEmail(email);

    if (mode === 'mongo') {
        return User.findOne({ email: normalizedEmail });
    }

    const data = await readData();
    return data.users.find((user) => user.email === normalizedEmail) || null;
}

async function getUserById(userId) {
    if (mode === 'mongo') {
        return User.findById(userId).select('-password');
    }

    const data = await readData();
    const user = data.users.find((user) => user._id === userId);
    if (user) {
        const { password, ...userWithoutPassword } = user;
        return userWithoutPassword;
    }
    return null;
}

async function countUsers() {
    if (mode === 'mongo') {
        return User.countDocuments();
    }

    const data = await readData();
    return data.users.length;
}

async function createUser({ name, email, password, role }) {
    const normalizedEmail = normalizeEmail(email);

    if (mode === 'mongo') {
        const user = new User({ name, email: normalizedEmail, password, role });
        await user.save();
        return user;
    }

    const data = await readData();
    const user = {
        _id: crypto.randomUUID(),
        name,
        email: normalizedEmail,
        password,
        role,
        createdAt: new Date().toISOString()
    };
    data.users.push(user);
    await writeData(data);
    return user;
}

async function countAnalyses() {
    if (mode === 'mongo') {
        return Analysis.countDocuments();
    }

    const data = await readData();
    return data.analyses.length;
}

async function getDoshaDistribution() {
    if (mode === 'mongo') {
        return Analysis.aggregate([
            { $group: { _id: '$prakritiResult', count: { $sum: 1 } } }
        ]);
    }

    const data = await readData();
    const counts = data.analyses.reduce((acc, item) => {
        acc[item.prakritiResult] = (acc[item.prakritiResult] || 0) + 1;
        return acc;
    }, {});

    return Object.entries(counts).map(([result, count]) => ({
        _id: result,
        count
    }));
}

async function listUsers() {
    if (mode === 'mongo') {
        return User.find().select('-password').sort({ createdAt: -1 });
    }

    const data = await readData();
    return [...data.users]
        .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
        .map(({ password, ...user }) => user);
}

async function deleteUser(userId) {
    if (mode === 'mongo') {
        await User.findByIdAndDelete(userId);
        await Analysis.deleteMany({ userId });
        return;
    }

    const data = await readData();
    data.users = data.users.filter((user) => user._id !== userId);
    data.analyses = data.analyses.filter((item) => item.userId !== userId);
    await writeData(data);
}

async function createAnalysis({ userId, faceShape, prakritiResult, confidence, questionnaireData }) {
    if (mode === 'mongo') {
        const analysis = new Analysis({
            userId,
            faceShape,
            prakritiResult,
            confidence,
            questionnaireData
        });
        await analysis.save();
        return analysis;
    }

    const data = await readData();
    const analysis = {
        _id: crypto.randomUUID(),
        userId,
        faceShape,
        prakritiResult,
        confidence,
        questionnaireData,
        timestamp: new Date().toISOString()
    };
    data.analyses.push(analysis);
    await writeData(data);
    return analysis;
}

// Dedicated Face Analysis saving for full CV metrics
async function createFaceAnalysis(faceData) {
    // If using mongo, we could create a new model, but for local testing just push to JSON
    const data = await readData();
    if (!data.face_analyses) data.face_analyses = [];
    const entry = {
        _id: crypto.randomUUID(),
        ...faceData,
        timestamp: new Date().toISOString()
    };
    data.face_analyses.push(entry);
    await writeData(data);
    return entry;
}

async function getAnalysisHistory(userId) {
    if (mode === 'mongo') {
        return Analysis.find({ userId }).sort({ timestamp: -1 });
    }

    const data = await readData();
    return data.analyses
        .filter((item) => item.userId === userId)
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
}

async function getAllAnalyses() {
    if (mode === 'mongo') {
        return Analysis.find()
            .populate('userId', 'name email')
            .sort({ timestamp: -1 });
    }

    const data = await readData();
    return data.analyses
        .map((item) => {
            const user = data.users.find((entry) => entry._id === item.userId);
            return {
                ...item,
                userId: user ? { _id: user._id, name: user.name, email: user.email } : null
            };
        })
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
}

module.exports = {
    createAnalysis,
    createUser,
    countAnalyses,
    countUsers,
    deleteUser,
    findUserByEmail,
    getUserById,
    getAllAnalyses,
    getAnalysisHistory,
    getDoshaDistribution,
    initStore,
    listUsers,
    normalizeEmail,
    createFaceAnalysis
};
