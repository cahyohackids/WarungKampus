// ============================================
//  🕌 COMMAND: !sholat — Jadwal Sholat
//  Estimasi waktu sholat berdasarkan kota via AI
// ============================================

const genai = require('../services/genaiService');

module.exports = {
    name: 'sholat',
    description: 'Jadwal sholat hari ini. Contoh: !sholat Semarang',
    ownerOnly: false,

    async execute(message, args, { client }) {
        const city = args.join(' ') || 'Semarang';

        try {
            const today = new Date().toLocaleDateString('id-ID', {
                weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
                timeZone: 'Asia/Jakarta'
            });

            const prompt = `Berikan jadwal waktu sholat untuk kota ${city}, Indonesia pada tanggal ${today}.

Format output yang rapi seperti ini (gunakan estimasi yang akurat berdasarkan pengetahuanmu tentang waktu sholat di kota tersebut):

🕌 *JADWAL SHOLAT*
📍 ${city} — ${today}

┃ 🌅 Subuh    : [waktu]
┃ 🌄 Terbit   : [waktu]
┃ ☀️ Dzuhur   : [waktu]
┃ 🌤️ Ashar    : [waktu]
┃ 🌅 Maghrib  : [waktu]
┃ 🌙 Isya     : [waktu]

Catatan: Estimasi waktu sholat. Untuk jadwal resmi silahkan cek Kemenag.

PENTING: Berikan estimasi yang masuk akal berdasarkan lokasi geografis kota tersebut. Jangan berikan disclaimer panjang, cukup formatnya saja.`;

            const result = await genai.generateText(prompt);
            message.reply(result);

        } catch (error) {
            console.error('Sholat Error:', error);
            message.reply('❌ Gagal mengambil jadwal sholat. Coba lagi nanti.');
        }
    },
};
