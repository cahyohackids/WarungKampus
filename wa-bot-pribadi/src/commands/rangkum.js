// ============================================
//  📖 COMMAND: !rangkum — Rangkuman AI
//  Ringkas teks panjang / materi kuliah via AI
// ============================================

const genai = require('../services/genaiService');

module.exports = {
    name: 'rangkum',
    description: 'Rangkum teks panjang dengan AI. Reply teks + !rangkum',
    ownerOnly: false,

    async execute(message, args, { client }) {
        try {
            let textToSummarize = '';

            // Ambil teks dari reply atau dari argumen
            if (message.hasQuotedMsg) {
                const quoted = await message.getQuotedMessage();
                textToSummarize = quoted.body;
            } else {
                textToSummarize = args.join(' ');
            }

            if (!textToSummarize || textToSummarize.length < 20) {
                return message.reply(
                    '❌ *Cara pakai !rangkum:*\n\n' +
                    '1️⃣ Reply pesan panjang + ketik *!rangkum*\n' +
                    '2️⃣ Atau: *!rangkum [teks panjang]*\n\n' +
                    '_Minimal 20 karakter untuk dirangkum._'
                );
            }

            const contact = await message.getContact();
            const senderName = contact.pushname || 'Kak';

            const prompt = `Kamu adalah asisten mahasiswa yang ahli merangkum materi. Rangkum teks berikut menjadi poin-poin penting yang mudah dipahami. Gunakan bahasa Indonesia yang jelas dan ringkas. Jika memungkinkan, kelompokkan menjadi beberapa kategori. Berikan emoji yang relevan di setiap poin.

Teks yang perlu dirangkum:
"""
${textToSummarize}
"""

Format output:
📌 *RANGKUMAN*

[poin-poin hasil rangkuman]

📊 *Statistik:*
- Panjang asli: X kata
- Poin rangkuman: Y poin`;

            const result = await genai.generateText(prompt);
            message.reply(`Halo *${senderName}*! 📖\n\n${result}`);

        } catch (error) {
            console.error('Rangkum Error:', error);
            message.reply('❌ Gagal merangkum. Coba lagi nanti.');
        }
    },
};
