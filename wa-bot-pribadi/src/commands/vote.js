// ============================================
//  📊 COMMAND: !vote — Polling / Voting
//  Buat voting cepat di grup atau chat
// ============================================

module.exports = {
    name: 'vote',
    description: 'Buat voting. !vote Judul? Opsi1, Opsi2, Opsi3',
    ownerOnly: false,

    async execute(message, args, { client }) {
        const input = args.join(' ');

        if (!input || !input.includes('?')) {
            return message.reply(
`📊 *QUICK VOTE — Panduan*

Format: *!vote [pertanyaan]? [opsi1], [opsi2], ...*

Contoh:
▸ !vote Makan dimana? Warteg, KFC, McD
▸ !vote Kapan kumpul? Senin, Rabu, Jumat
▸ !vote Setuju proposal? Ya, Tidak, Abstain

_Peserta reply dengan nomor pilihannya!_`
            );
        }

        // Parse pertanyaan dan opsi
        const [question, optionsStr] = input.split('?');
        
        if (!optionsStr || !optionsStr.trim()) {
            return message.reply('❌ Tambahkan opsi setelah tanda tanya (?).\nContoh: *!vote Makan apa? Nasi, Mie, Roti*');
        }

        const options = optionsStr.split(',').map(o => o.trim()).filter(o => o);

        if (options.length < 2) {
            return message.reply('❌ Minimal 2 opsi dipisahkan koma.');
        }
        if (options.length > 10) {
            return message.reply('❌ Maksimal 10 opsi.');
        }

        const numberEmoji = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟'];

        let msg = `📊 *VOTING*\n\n`;
        msg += `❓ *${question.trim()}?*\n\n`;

        options.forEach((opt, i) => {
            msg += `${numberEmoji[i]} ${opt}\n`;
        });

        msg += `\n━━━━━━━━━━━━━━━━━━\n`;
        msg += `_Reply dengan nomor pilihanmu!_\n`;
        msg += `_Contoh: ketik *1* untuk opsi pertama_`;

        message.reply(msg);
    },
};
