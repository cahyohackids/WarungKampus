// ============================================
//  🧠 COMMAND: !rumus — Referensi Rumus Cepat
//  Rumus matematika, fisika, kimia via AI
// ============================================

const genai = require('../services/genaiService');

module.exports = {
    name: 'rumus',
    description: 'Cari rumus. Contoh: !rumus luas lingkaran',
    ownerOnly: false,

    async execute(message, args, { client }) {
        const topic = args.join(' ');

        if (!topic) {
            return message.reply(
`🧠 *REFERENSI RUMUS — Panduan*

Ketik *!rumus [topik]* untuk mencari rumus.

Contoh:
▸ !rumus luas lingkaran
▸ !rumus hukum newton
▸ !rumus mol dan molaritas
▸ !rumus turunan dan integral
▸ !rumus bunga majemuk
▸ !rumus hukum ohm
▸ !rumus deret geometri

_Bisa untuk Matematika, Fisika, Kimia, Ekonomi, dll_ 🎓`
            );
        }

        try {
            const prompt = `Kamu adalah tutor sains dan matematika untuk mahasiswa. Berikan rumus tentang "${topic}" dengan format yang jelas.

Sertakan:
1. Nama rumus lengkap
2. Rumus utama (tulis dengan simbol yang jelas, gunakan teks karena ini WhatsApp jadi tidak bisa render LaTeX)
3. Keterangan setiap variabel
4. Contoh soal sederhana beserta penyelesaiannya langkah demi langkah
5. Tips atau catatan penting

Gunakan emoji dan formatting WhatsApp (*bold*, _italic_) agar mudah dibaca.
Tulis rumus matematika dalam bentuk teks yang jelas, contoh: "V = 4/3 × π × r³"`;

            const result = await genai.generateText(prompt);

            message.reply(`🧠 *RUMUS — ${topic.toUpperCase()}*\n\n${result}`);
        } catch (error) {
            console.error('Rumus Error:', error);
            message.reply('❌ Gagal mencari rumus. Coba lagi nanti.');
        }
    },
};
