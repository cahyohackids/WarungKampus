// ============================================
//  🧠 GOOGLE GENERATIVE AI SERVICE
// ============================================

const { GoogleGenAI } = require('@google/genai');
const { GEMINI_API_KEY } = require('../config');

const ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY });

const MODEL = 'gemini-2.5-flash';

/**
 * Generate teks dari prompt
 */
async function generateText(prompt) {
    const result = await ai.models.generateContent({
        model: MODEL,
        contents: prompt,
    });
    return result.text;
}

/**
 * Generate dari gambar + prompt (Vision)
 */
async function generateVision(prompt, imageData, mimeType) {
    const imagePart = {
        inlineData: {
            data: imageData,
            mimeType: mimeType,
        },
    };
    const result = await ai.models.generateContent({
        model: MODEL,
        contents: [prompt || 'Jelaskan gambar ini', imagePart],
    });
    return result.text;
}

module.exports = {
    generateText,
    generateVision,
};
