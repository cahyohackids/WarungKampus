// ============================================
//  💰 COMMAND: !kurs — Konversi Mata Uang
//  Konversi kurs via AI
// ============================================

const genai = require('../services/genaiService');

module.exports = {
    name: 'kurs',
    description: 'Konversi mata uang. Contoh: !kurs 100 USD ke IDR',
    ownerOnly: false,

    async execute(message, args, { client }) {
        const input = args.join(' ');

        if (!input) {
            return message.reply(
`💰 *KONVERSI KURS — Panduan*

▸ *!kurs 100 USD ke IDR*
▸ *!kurs 1000000 IDR ke MYR*
▸ *!kurs 50 EUR ke USD*
▸ *!kurs 100 JPY ke IDR*

_Kurs menggunakan estimasi AI berdasarkan data terbaru yang tersedia._
_Untuk transaksi resmi, cek kurs bank!_ 🏦`
            );
        }

        try {
            const prompt = `Kamu adalah asisten konversi mata uang. Konversikan: "${input}".

Berikan jawaban dengan format yang rapi:
1. Jumlah asal dan mata uang
2. Hasil konversi
3. Kurs yang digunakan (per 1 unit)
4. Catatan bahwa ini estimasi

Gunakan emoji dan formatting WhatsApp. Jawab singkat dan jelas.
PENTING: Jika kamu tidak yakin kurs terkini, berikan estimasi berdasarkan data terakhir yang kamu ketahui dan sebutkan tanggal referensinya.`;

            const result = await genai.generateText(prompt);
            message.reply(`💰 *KONVERSI KURS*\n\n${result}`);

        } catch (error) {
            console.error('Kurs Error:', error);
            message.reply('❌ Gagal mengkonversi. Coba lagi nanti.');
        }
    },
};
