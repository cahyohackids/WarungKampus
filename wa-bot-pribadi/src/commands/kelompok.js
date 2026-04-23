// ============================================
//  🎲 COMMAND: !kelompok — Pembagian Kelompok Acak
//  Bagi nama-nama menjadi kelompok secara random
// ============================================

module.exports = {
    name: 'kelompok',
    description: 'Bagi kelompok acak. Contoh: !kelompok 4 Andi,Budi,Citra,Dian,...',
    ownerOnly: false,

    async execute(message, args, { client }) {
        // Parse: !kelompok [jumlah kelompok] [nama1,nama2,nama3,...]
        const groupCount = parseInt(args[0]);
        const namesStr = args.slice(1).join(' ');

        if (!groupCount || !namesStr) {
            return message.reply(
`🎲 *PEMBAGIAN KELOMPOK — Panduan*

Format: *!kelompok [jumlah] [nama-nama]*

Contoh:
▸ !kelompok 4 Andi,Budi,Citra,Dian,Eka,Fani,Gina,Hadi
▸ !kelompok 3 Andi, Budi, Citra, Dian, Eka, Fani

_Nama dipisahkan dengan koma (,)_
_Hasil diacak secara random setiap kali!_ 🎰`
            );
        }

        // Parse nama (pisah by koma)
        const names = namesStr.split(',').map(n => n.trim()).filter(n => n.length > 0);

        if (names.length < groupCount) {
            return message.reply(`❌ Jumlah nama (${names.length}) harus lebih banyak dari jumlah kelompok (${groupCount}).`);
        }

        if (groupCount < 2 || groupCount > 20) {
            return message.reply('❌ Jumlah kelompok harus antara 2-20.');
        }

        // Shuffle (Fisher-Yates)
        const shuffled = [...names];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }

        // Distribusi ke kelompok
        const groups = Array.from({ length: groupCount }, () => []);
        shuffled.forEach((name, i) => {
            groups[i % groupCount].push(name);
        });

        // Format output
        let msg = `🎲 *PEMBAGIAN KELOMPOK*\n`;
        msg += `📊 ${names.length} orang → ${groupCount} kelompok\n\n`;

        groups.forEach((group, i) => {
            msg += `━━ *Kelompok ${i + 1}* (${group.length} orang) ━━\n`;
            group.forEach((name, j) => {
                msg += `  ${j + 1}. ${name}\n`;
            });
            msg += '\n';
        });

        msg += `_🎰 Diacak pada ${new Date().toLocaleTimeString('id-ID')}_`;

        message.reply(msg);
    },
};
