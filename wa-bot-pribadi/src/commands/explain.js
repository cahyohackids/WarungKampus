// ============================================
//  ✍️ COMMAND: !explain — Penjelasan Materi
//  Minta AI menjelaskan konsep dengan cara mudah
// ============================================

const genai = require('../services/genaiService');

module.exports = {
    name: 'explain',
    description: 'Minta AI jelaskan konsep. Contoh: !explain hukum termodinamika',
    ownerOnly: false,

    async execute(message, args, { client }) {
        const topic = args.join(' ');

        if (!topic) {
            return message.reply(
`✍️ *PENJELASAN MATERI — Panduan*

Ketik *!explain [topik/konsep]* untuk penjelasan lengkap.

Contoh:
▸ !explain hukum termodinamika ke-2
▸ !explain perbedaan DNA dan RNA
▸ !explain konsep OOP dalam pemrograman
▸ !explain supply and demand ekonomi
▸ !explain teori relativitas einstein

_AI akan menjelaskan dengan bahasa yang mudah dipahami_ 🎓`
            );
        }

        try {
            const contact = await message.getContact();
            const senderName = contact.pushname || 'Kak';

            const prompt = `Kamu adalah dosen/tutor yang sangat baik dan sabar. Jelaskan topik "${topic}" untuk mahasiswa dengan cara yang SANGAT mudah dipahami.

Gunakan format:

📌 *Definisi Singkat*
[1-2 kalimat definisi]

🔍 *Penjelasan Detail*
[penjelasan lengkap dengan bahasa sederhana, gunakan analogi kehidupan sehari-hari jika memungkinkan]

💡 *Contoh Nyata*
[berikan 1-2 contoh yang relatable untuk mahasiswa]

📝 *Poin Penting untuk Diingat*
[3-5 poin key takeaway]

🔗 *Hubungan dengan Topik Lain*
[bagaimana topik ini berkaitan dengan konsep lain]

Gunakan emoji dan formatting WhatsApp (*bold*, _italic_) untuk keterbacaan.`;

            const result = await genai.generateText(prompt);

            message.reply(`Halo *${senderName}*! ✍️\n\n${result}`);

        } catch (error) {
            console.error('Explain Error:', error);
            message.reply('❌ Gagal menjelaskan topik. Coba lagi nanti.');
        }
    },
};
