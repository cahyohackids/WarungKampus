// ============================================
//  📚 COMMAND: !kbbi — Definisi Kata (via AI)
//  Cari arti kata dalam bahasa Indonesia
// ============================================

const genai = require('../services/genaiService');

module.exports = {
    name: 'kbbi',
    description: 'Cari arti kata. Contoh: !kbbi paradigma',
    ownerOnly: false,

    async execute(message, args, { client }) {
        const kata = args.join(' ');

        if (!kata) {
            return message.reply('❌ Format: *!kbbi [kata]*\nContoh: !kbbi paradigma');
        }

        try {
            const prompt = `Berikan definisi kata "${kata}" dalam format kamus bahasa Indonesia (mirip KBBI). Sertakan:
1. Kelas kata (nomina/verba/adjektiva/dll)
2. Definisi utama (bisa lebih dari satu makna)
3. Contoh kalimat untuk setiap definisi
4. Sinonim dan antonim jika ada
5. Etimologi singkat jika menarik

Format output yang rapi dengan numbering dan emoji yang relevan. Gunakan gaya penulisan kamus resmi.`;

            const result = await genai.generateText(prompt);

            message.reply(`📚 *KBBI — "${kata}"*\n\n${result}`);
        } catch (error) {
            console.error('KBBI Error:', error);
            message.reply('❌ Gagal mencari definisi. Coba lagi nanti.');
        }
    },
};
