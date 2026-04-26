const mongoose = require('mongoose');

const analysisSchema = new mongoose.Schema({
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    faceShape: { type: String, default: 'Unknown' },
    prakritiResult: { type: String, required: true },
    confidence: { type: Number, required: true },
    questionnaireData: { type: Object, required: true },
    timestamp: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Analysis', analysisSchema);
