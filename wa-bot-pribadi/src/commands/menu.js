// ============================================
//  📖 COMMAND: !menu — Daftar Semua Perintah
//  Tampilan rapi dengan kategori
// ============================================

const config = require('../config');

module.exports = {
    name: 'menu',
    description: 'Tampilkan daftar semua perintah bot',
    ownerOnly: false,

    async execute(message, args, { client, commands }) {
        const uptime = process.uptime();
        const hours = Math.floor(uptime / 3600);
        const minutes = Math.floor((uptime % 3600) / 60);

        // Ambil nama pengirim
        const contact = await message.getContact();
        const name = contact.pushname || 'User';

        // Kategorisasi command
        const categories = {
            '🤖 AI & Bahasa': ['ai', 'rangkum', 'explain', 'terjemah', 'kbbi', 'sinonim', 'cek'],
            '📚 Akademik': ['jadwal', 'deadline', 'gpa', 'rumus', 'pomodoro', 'kelompok'],
            '📝 Produktivitas': ['add', 'list', 'hapus', 'clear', 'notes', 'remind', 'vote'],
            '🎲 Utilitas': ['ping', 'calc', 'sticker', 'quote', 'random', 'kurs', 'konversi', 'sholat', 'tagall', 'info'],
        };

        // Waktu sekarang
        const now = new Date();
        const timeStr = now.toLocaleTimeString('id-ID', {
            hour: '2-digit', minute: '2-digit',
            timeZone: 'Asia/Jakarta'
        });
        const dateStr = now.toLocaleDateString('id-ID', {
            weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
            timeZone: 'Asia/Jakarta'
        });

        let msg = `Halo *${name}*! 👋\n\n`;
        msg += `┌──「 ${config.BOT_NAME} 」\n`;
        msg += `│ 📅 ${dateStr}\n`;
        msg += `│ ⏰ ${timeStr} WIB\n`;
        msg += `│ 🟢 Online — ${hours}j ${minutes}m\n`;
        msg += `│ 📊 v${config.BOT_VERSION}\n`;
        msg += `└────────────────\n\n`;

        // Render setiap kategori
        for (const [categoryName, cmdNames] of Object.entries(categories)) {
            // Filter: hanya tampilkan yg benar-benar loaded & tidak hidden
            const visibleCmds = cmdNames.filter(name => {
                const cmd = commands.get(name);
                return cmd && !cmd.hidden;
            });

            if (visibleCmds.length === 0) continue;

            msg += `┌──「 ${categoryName} 」\n`;

            visibleCmds.forEach(name => {
                const cmd = commands.get(name);
                const lock = cmd.ownerOnly ? ' 🔐' : '';
                msg += `│ ▸ *!${cmd.name}*${lock}\n`;
                msg += `│   _${cmd.description}_\n`;
            });

            msg += `└────────────────\n\n`;
        }

        // Command yang belum dikategorikan
        const categorized = new Set(Object.values(categories).flat());
        const uncategorized = [];
        commands.forEach(cmd => {
            if (!categorized.has(cmd.name) && !cmd.hidden) {
                uncategorized.push(cmd);
            }
        });

        if (uncategorized.length > 0) {
            msg += `┌──「 ⚙️ Lainnya 」\n`;
            uncategorized.forEach(cmd => {
                const lock = cmd.ownerOnly ? ' 🔐' : '';
                msg += `│ ▸ *!${cmd.name}*${lock}\n`;
                msg += `│   _${cmd.description}_\n`;
            });
            msg += `└────────────────\n\n`;
        }

        msg += `_🔐 = Khusus Owner_\n`;
        msg += `_💡 Ketik nama command untuk panduan detail_\n`;
        msg += `_📊 Dashboard: localhost:${config.PORT}_`;

        message.reply(msg);
    },
};
