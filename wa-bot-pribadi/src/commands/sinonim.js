// ============================================
//  💡 COMMAND: !sinonim — Sinonim & Antonim
//  Cari padanan kata dan lawan kata
// ============================================

const genai = require('../services/genaiService');

module.exports = {
    name: 'sinonim',
    description: 'Cari sinonim & antonim. Contoh: !sinonim cantik',
    ownerOnly: false,

    async execute(message, args, { client }) {
        const kata = args.join(' ');

        if (!kata) {
            return message.reply('❌ Format: *!sinonim [kata]*\nContoh: !sinonim cantik');
        }

        try {
            const prompt = `Berikan sinonim (persamaan kata) dan antonim (lawan kata) untuk kata "${kata}" dalam Bahasa Indonesia.

Format output:
💡 *SINONIM & ANTONIM*
📝 Kata: *${kata}*

✅ *Sinonim (Persamaan):*
[daftar 5-8 sinonim, dipisah koma]

❌ *Antonim (Lawan):*
[daftar 3-5 antonim, dipisah koma]

📌 *Contoh Kalimat:*
[1-2 contoh kalimat menggunakan kata tersebut]

Jawab dengan singkat dan rapi. Jika kata tidak memiliki antonim, sebutkan.`;

            const result = await genai.generateText(prompt);
            message.reply(result);

        } catch (error) {
            console.error('Sinonim Error:', error);
            message.reply('❌ Gagal mencari sinonim. Coba lagi nanti.');
        }
    },
};
