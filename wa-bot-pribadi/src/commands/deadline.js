// ============================================
//  ⏰ COMMAND: !deadline — Tracker Deadline Tugas
//  Catat dan pantau deadline tugas kuliah
// ============================================

const deadlineDb = require('../database/deadlineDatabase');

module.exports = {
    name: 'deadline',
    description: 'Kelola deadline tugas. Ketik !deadline untuk bantuan',
    ownerOnly: true,

    async execute(message, args, { client }) {
        const sub = args[0]?.toLowerCase();

        // === !deadline (tanpa argumen) — tampilkan bantuan ===
        if (!sub) {
            return message.reply(
`⏰ *DEADLINE TRACKER — Panduan*

▸ *!deadline list* — Lihat semua deadline
▸ *!deadline add 2026-04-10 Kalkulus Tugas Integral*
    ↳ Tambah deadline (format: YYYY-MM-DD)
▸ *!deadline add 10/04 Kalkulus Tugas Integral*
    ↳ Tambah deadline (format: DD/MM)
▸ *!deadline hapus 1* — Hapus deadline no.1
▸ *!deadline bersih* — Hapus deadline yang sudah lewat
▸ *!deadline clear* — Hapus semua deadline

_⚡ Deadline terdekat muncul paling atas!_`
            );
        }

        // === !deadline list ===
        if (sub === 'list' || sub === 'lihat') {
            const items = deadlineDb.getAll();

            if (items.length === 0) {
                return message.reply('⏰ Tidak ada deadline. Santai dulu! ☕\n_Tambah: !deadline add 2026-04-10 Matkul Tugas_');
            }

            const now = new Date();
            let msg = `⏰ *DAFTAR DEADLINE*\n\n`;

            items.forEach((item, i) => {
                const dueDate = new Date(item.date);
                const diffMs = dueDate - now;
                const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

                let statusEmoji;
                let statusText;
                if (diffDays < 0) {
                    statusEmoji = '🔴';
                    statusText = `LEWAT ${Math.abs(diffDays)} hari`;
                } else if (diffDays === 0) {
                    statusEmoji = '🔴';
                    statusText = 'HARI INI!';
                } else if (diffDays === 1) {
                    statusEmoji = '🟠';
                    statusText = 'BESOK!';
                } else if (diffDays <= 3) {
                    statusEmoji = '🟡';
                    statusText = `${diffDays} hari lagi`;
                } else if (diffDays <= 7) {
                    statusEmoji = '🟢';
                    statusText = `${diffDays} hari lagi`;
                } else {
                    statusEmoji = '🔵';
                    statusText = `${diffDays} hari lagi`;
                }

                const dateStr = dueDate.toLocaleDateString('id-ID', {
                    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
                });

                msg += `  ${i + 1}. ${statusEmoji} *${item.matkul}*\n`;
                msg += `     📝 ${item.task}\n`;
                msg += `     📅 ${dateStr}\n`;
                msg += `     ⏳ ${statusText}\n\n`;
            });

            return message.reply(msg);
        }

        // === !deadline add [tanggal] [matkul] [tugas...] ===
        if (sub === 'add' || sub === 'tambah') {
            let dateStr = args[1];
            const matkul = args[2];
            const task = args.slice(3).join(' ');

            if (!dateStr || !matkul || !task) {
                return message.reply(
                    '❌ Format: *!deadline add [tanggal] [matkul] [deskripsi]*\n\n' +
                    'Contoh:\n' +
                    '▸ !deadline add 2026-04-10 Kalkulus Tugas Integral\n' +
                    '▸ !deadline add 10/04 Fisika Laporan Praktikum'
                );
            }

            // Parse tanggal
            let parsedDate;
            
            // Format DD/MM atau DD-MM (tahun otomatis)
            const shortMatch = dateStr.match(/^(\d{1,2})[\/\-](\d{1,2})$/);
            if (shortMatch) {
                const day = parseInt(shortMatch[1]);
                const month = parseInt(shortMatch[2]) - 1;
                const year = new Date().getFullYear();
                parsedDate = new Date(year, month, day);
                
                // Kalau tanggal sudah lewat, pakai tahun depan
                if (parsedDate < new Date()) {
                    parsedDate = new Date(year + 1, month, day);
                }
            } else {
                // Format YYYY-MM-DD
                parsedDate = new Date(dateStr);
            }

            if (isNaN(parsedDate.getTime())) {
                return message.reply('❌ Format tanggal tidak valid.\nGunakan: *YYYY-MM-DD* atau *DD/MM*');
            }

            const isoDate = parsedDate.toISOString().split('T')[0];
            deadlineDb.add({ date: isoDate, matkul, task });

            const diffDays = Math.ceil((parsedDate - new Date()) / (1000 * 60 * 60 * 24));
            const dateDisplay = parsedDate.toLocaleDateString('id-ID', {
                weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
            });

            message.reply(
                `✅ Deadline ditambahkan!\n\n` +
                `📚 *${matkul}*\n` +
                `📝 ${task}\n` +
                `📅 ${dateDisplay}\n` +
                `⏳ ${diffDays} hari lagi`
            );
        }

        // === !deadline hapus [nomor] ===
        else if (sub === 'hapus' || sub === 'delete') {
            const index = parseInt(args[1]) - 1;
            if (isNaN(index)) {
                return message.reply('❌ Format: *!deadline hapus [nomor]*\nKetik *!deadline list* dulu.');
            }

            const removed = deadlineDb.remove(index);
            if (removed) {
                message.reply(`🗑️ Dihapus: *${removed.matkul}* — ${removed.task}`);
            } else {
                message.reply('❌ Nomor tidak ditemukan.');
            }
        }

        // === !deadline bersih — hapus yang sudah lewat ===
        else if (sub === 'bersih' || sub === 'cleanup') {
            const count = deadlineDb.clearDone();
            message.reply(`🧹 ${count} deadline yang sudah lewat telah dihapus.`);
        }

        // === !deadline clear ===
        else if (sub === 'clear') {
            deadlineDb.clearAll();
            message.reply('🧹 Semua deadline telah dihapus.');
        }
    },
};
