// ============================================
//  📅 COMMAND: !jadwal — Jadwal Kuliah
//  Kelola jadwal perkuliahan per hari
// ============================================

const scheduleDb = require('../database/scheduleDatabase');

module.exports = {
    name: 'jadwal',
    description: 'Kelola jadwal kuliah. Ketik !jadwal untuk bantuan',
    ownerOnly: true,

    async execute(message, args, { client }) {
        const sub = args[0]?.toLowerCase();

        // === !jadwal (tanpa argumen) — tampilkan bantuan ===
        if (!sub) {
            return message.reply(
`📅 *JADWAL KULIAH — Panduan*

▸ *!jadwal hari ini* — Lihat jadwal hari ini
▸ *!jadwal senin* — Lihat jadwal hari Senin
▸ *!jadwal semua* — Lihat jadwal semua hari
▸ *!jadwal add Senin 08:00 Kalkulus Ruang A301*
    ↳ Tambah jadwal
▸ *!jadwal hapus Senin 1* — Hapus jadwal no.1 hari Senin
▸ *!jadwal clear Senin* — Hapus semua jadwal hari Senin

_Format tambah: !jadwal add [hari] [jam] [matkul] [ruang]_`
            );
        }

        // === !jadwal hari ini / !jadwal today ===
        if (sub === 'hari' || sub === 'today' || sub === 'ini') {
            const actualSub = sub === 'hari' ? (args[1]?.toLowerCase() === 'ini' ? 'today' : args[1]) : sub;
            
            let dayName;
            if (sub === 'hari' && args[1]?.toLowerCase() === 'ini') {
                dayName = scheduleDb.getTodayName();
            } else if (sub === 'today' || sub === 'ini') {
                dayName = scheduleDb.getTodayName();
            } else {
                dayName = scheduleDb.normalizeDay(actualSub);
            }

            if (!dayName) return message.reply('❌ Hari tidak valid.');

            const items = scheduleDb.getScheduleByDay(dayName);
            if (items.length === 0) {
                return message.reply(`📅 Tidak ada jadwal hari *${dayName}*. Hari libur! 🎉`);
            }

            let msg = `📅 *JADWAL HARI ${dayName.toUpperCase()}*\n\n`;
            items.forEach((item, i) => {
                msg += `  ${i + 1}. ⏰ *${item.jam}* — ${item.matkul}\n     📍 ${item.ruang}\n\n`;
            });

            return message.reply(msg);
        }

        // === !jadwal [nama hari] ===
        const dayCheck = scheduleDb.normalizeDay(sub);
        if (dayCheck && args.length === 1) {
            const items = scheduleDb.getScheduleByDay(dayCheck);
            if (items.length === 0) {
                return message.reply(`📅 Tidak ada jadwal hari *${dayCheck}*. Hari libur! 🎉`);
            }

            let msg = `📅 *JADWAL HARI ${dayCheck.toUpperCase()}*\n\n`;
            items.forEach((item, i) => {
                msg += `  ${i + 1}. ⏰ *${item.jam}* — ${item.matkul}\n     📍 ${item.ruang}\n\n`;
            });

            return message.reply(msg);
        }

        // === !jadwal semua / !jadwal all ===
        if (sub === 'semua' || sub === 'all') {
            const all = scheduleDb.getAllSchedule();
            const days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'];
            let msg = `📅 *JADWAL KULIAH LENGKAP*\n\n`;
            let hasAny = false;

            days.forEach(day => {
                const items = all[day];
                if (items && items.length > 0) {
                    hasAny = true;
                    msg += `━━ *${day.toUpperCase()}* ━━\n`;
                    items.forEach((item, i) => {
                        msg += `  ${i + 1}. ⏰ ${item.jam} — ${item.matkul} (📍${item.ruang})\n`;
                    });
                    msg += '\n';
                }
            });

            if (!hasAny) {
                return message.reply('📅 Belum ada jadwal apapun. Tambah dengan:\n*!jadwal add Senin 08:00 Kalkulus Ruang A301*');
            }

            return message.reply(msg);
        }

        // === !jadwal add [hari] [jam] [matkul] [ruang] ===
        if (sub === 'add' || sub === 'tambah') {
            const day = scheduleDb.normalizeDay(args[1] || '');
            const jam = args[2];
            const rest = args.slice(3).join(' ');

            if (!day || !jam || !rest) {
                return message.reply('❌ Format: *!jadwal add [hari] [jam] [matkul] [ruang]*\nContoh: !jadwal add Senin 08:00 Kalkulus Ruang A301');
            }

            // Pisahkan matkul dan ruang (ruang biasanya setelah kata terakhir atau setelah "Ruang"/"R.")
            let matkul = rest;
            let ruang = '-';

            // Coba deteksi ruang dari kata "Ruang", "R.", "GKB", atau kode ruang
            const ruangPatterns = [/\b(Ruang\s+\S+)/i, /\b(R\.\s*\S+)/i, /\b(GKB\s*\S+)/i, /\b([A-Z]\d{2,})/];
            for (const pattern of ruangPatterns) {
                const match = rest.match(pattern);
                if (match) {
                    ruang = match[1];
                    matkul = rest.replace(match[0], '').trim();
                    break;
                }
            }

            // Jika tidak terdeteksi, gunakan 2 kata terakhir sebagai ruang jika >3 kata
            if (ruang === '-' && rest.split(' ').length > 3) {
                const words = rest.split(' ');
                ruang = words.slice(-2).join(' ');
                matkul = words.slice(0, -2).join(' ');
            }

            scheduleDb.addSchedule(day, { jam, matkul, ruang });
            message.reply(`✅ Jadwal ditambahkan!\n📅 *${day}* ⏰ ${jam}\n📚 ${matkul}\n📍 ${ruang}`);
        }

        // === !jadwal hapus [hari] [nomor] ===
        else if (sub === 'hapus' || sub === 'delete') {
            const day = scheduleDb.normalizeDay(args[1] || '');
            const index = parseInt(args[2]) - 1;

            if (!day || isNaN(index)) {
                return message.reply('❌ Format: *!jadwal hapus [hari] [nomor]*\nContoh: !jadwal hapus Senin 1');
            }

            const removed = scheduleDb.removeSchedule(day, index);
            if (removed) {
                message.reply(`🗑️ Dihapus: *${removed.matkul}* (${day} ${removed.jam})`);
            } else {
                message.reply('❌ Jadwal tidak ditemukan. Ketik *!jadwal [hari]* untuk lihat nomor.');
            }
        }

        // === !jadwal clear [hari] ===
        else if (sub === 'clear') {
            const day = scheduleDb.normalizeDay(args[1] || '');
            if (!day) return message.reply('❌ Format: *!jadwal clear [hari]*');
            scheduleDb.clearScheduleDay(day);
            message.reply(`🧹 Jadwal hari *${day}* telah dikosongkan.`);
        }
    },
};
