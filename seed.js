const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const User = require('./models/User');

const MONGODB_URI = 'mongodb://localhost:27017/prakritiai';

async function seed() {
    await mongoose.connect(MONGODB_URI);
    console.log('Connected to MongoDB');

    let user = await User.findOne({ email: 'Admin@gmail.com' });
    if (!user) {
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash('12345', salt);
        user = new User({
            name: 'Admin',
            email: 'Admin@gmail.com',
            password: hashedPassword,
            role: 'admin'
        });
        await user.save();
        console.log('Admin user created');
    } else {
        user.role = 'admin'; // ensure role
        const salt = await bcrypt.genSalt(10);
        user.password = await bcrypt.hash('12345', salt);
        await user.save();
        console.log('Admin user updated');
    }
    await mongoose.disconnect();
}

seed().catch(console.error);
