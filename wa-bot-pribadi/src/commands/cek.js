// ============================================
//  ✏️ COMMAND: !cek — Cek Tata Bahasa & Grammar
//  Periksa dan perbaiki teks via AI
// ============================================

const genai = require('../services/genaiService');

module.exports = {
    name: 'cek',
    description: 'Cek grammar/tata bahasa. Reply teks + !cek',
    ownerOnly: false,

    async execute(message, args, { client }) {
        try {
            let textToCheck = '';

            if (message.hasQuotedMsg) {
                const quoted = await message.getQuotedMessage();
                textToCheck = quoted.body;
            } else {
                textToCheck = args.join(' ');
            }

            if (!textToCheck || textToCheck.length < 5) {
                return message.reply(
                    '✏️ *CEK TATA BAHASA — Panduan*\n\n' +
                    '▸ Reply pesan + *!cek* — Periksa teks yang di-reply\n' +
                    '▸ *!cek [teks]* — Periksa teks langsung\n\n' +
                    '_Bisa untuk Bahasa Indonesia maupun Inggris!_'
                );
            }

            const prompt = `Kamu adalah ahli bahasa. Periksa teks berikut dan berikan koreksi:

Teks: "${textToCheck}"

Berikan:
1. ✅ atau ❌ Status keseluruhan (benar/ada kesalahan)
2. Koreksi spesifik (jika ada) — tunjukkan bagian yang salah → yang benar
3. Versi teks yang sudah diperbaiki (jika ada perbaikan)
4. Skor keterbacaan (1-10)
5. Tips singkat

Format output rapi dengan emoji dan WhatsApp formatting. Jangan terlalu panjang.`;

            const result = await genai.generateText(prompt);
            message.reply(`✏️ *CEK TATA BAHASA*\n\n${result}`);

        } catch (error) {
            console.error('Cek Error:', error);
            message.reply('❌ Gagal memeriksa teks. Coba lagi nanti.');
        }
    },
};
