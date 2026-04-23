// ============================================
//  💕 COMMAND: !ldr — Long Distance Relationship
//  Semarang (WIB) ↔ Tumpat, Kelantan (MYT)
// ============================================

const moment = require('moment-timezone');

module.exports = {
    name: 'ldr',
    description: 'Lihat waktu real-time Semarang ↔ Tumpat, Kelantan',
    ownerOnly: true,
    hidden: true,
    
    async execute(message, args, { client }) {
        const wib = moment().tz('Asia/Jakarta');
        const myt = moment().tz('Asia/Kuala_Lumpur');

        // Hitung selisih jam
        const wibOffset = wib.utcOffset() / 60; // +7
        const mytOffset = myt.utcOffset() / 60;  // +8
        const diffHours = Math.abs(mytOffset - wibOffset);

        // Tentukan emoji berdasarkan waktu MYT
        const mytHour = myt.hour();
        let timeEmoji = '🌙';
        if (mytHour >= 5 && mytHour < 10) timeEmoji = '🌅';
        else if (mytHour >= 10 && mytHour < 15) timeEmoji = '☀️';
        else if (mytHour >= 15 && mytHour < 18) timeEmoji = '🌤️';
        else if (mytHour >= 18 && mytHour < 20) timeEmoji = '🌇';

        // Format pesan
        const msg = 
`╔══════════════════════════╗
║    💕 *LDR TIME ZONE* 💕    ║
╚══════════════════════════╝

🇮🇩 *Semarang, Indonesia*
┃ ⏰ ${wib.format('HH:mm:ss')} WIB
┃ 📅 ${wib.format('dddd, DD MMMM YYYY')}
┃ 🕐 UTC${wibOffset >= 0 ? '+' : ''}${wibOffset}

🇲🇾 *Tumpat, Kelantan, Malaysia*
┃ ⏰ ${myt.format('HH:mm:ss')} MYT
┃ 📅 ${myt.format('dddd, DD MMMM YYYY')}
┃ 🕐 UTC${mytOffset >= 0 ? '+' : ''}${mytOffset}

━━━━━━━━━━━━━━━━━━━━━━━━━
${timeEmoji} Selisih waktu: *${diffHours} jam*
🇲🇾 Malaysia *lebih cepat* ${diffHours} jam dari 🇮🇩

_Jarak memisahkan, tapi waktu tetap berjalan bersama_ 💫`;

        message.reply(msg);
    },
};
