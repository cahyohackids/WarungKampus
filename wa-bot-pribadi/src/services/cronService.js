// ============================================
//  ⏰ CRON SCHEDULER SERVICE
// ============================================

const cron = require('node-cron');
const moment = require('moment-timezone');
const db = require('../database/todoDatabase');
const deadlineDb = require('../database/deadlineDatabase');
const config = require('../config');

/**
 * Inisialisasi semua cron job setelah client ready
 */
function initCrons(client) {
    console.log('⏰ Menginisialisasi Cron Jobs...');

    // ─────────────────────────────────────────────
    // 1. Pengingat Pagi — 07:00 WIB setiap hari
    // ─────────────────────────────────────────────
    cron.schedule('0 7 * * *', () => {
        const todos = db.getAll();
        let msg = '*🌞 PENGINGAT PAGI 🌞*\n\nSemangat pagi boss! 🚀\n\n';

        if (todos.length > 0) {
            msg += '*Prioritas Hari Ini:*\n';
            todos.forEach((item, i) => msg += `${i + 1}. ${item}\n`);
        } else {
            msg += 'Tidak ada tugas hari ini. Santai dulu!';
        }

        // Kirim ke semua authorized users
        config.AUTHORIZED_USERS.forEach(userId => {
            client.sendMessage(userId, msg);
        });
        console.log('📨 Pengingat pagi terkirim!');
    }, {
        timezone: 'Asia/Jakarta'
    });

    // ─────────────────────────────────────────────
    // 2. Pengingat Deadline — 08:00 WIB
    //    Alert jika ada deadline dalam 3 hari
    // ─────────────────────────────────────────────
    cron.schedule('0 8 * * *', () => {
        const deadlines = deadlineDb.getAll();
        const now = new Date();
        const urgent = deadlines.filter(d => {
            const diff = Math.ceil((new Date(d.date) - now) / (1000 * 60 * 60 * 24));
            return diff >= 0 && diff <= 3;
        });

        if (urgent.length === 0) return;

        let msg = '*🚨 DEADLINE MENDEKAT! 🚨*\n\n';
        urgent.forEach((d, i) => {
            const diff = Math.ceil((new Date(d.date) - now) / (1000 * 60 * 60 * 24));
            const emoji = diff === 0 ? '🔴 HARI INI!' : diff === 1 ? '🟠 BESOK!' : `🟡 ${diff} hari lagi`;
            msg += `${i + 1}. *${d.matkul}* — ${d.task}\n   ${emoji}\n\n`;
        });
        msg += '_Ketik !deadline list untuk detail lengkap_';

        config.AUTHORIZED_USERS.forEach(userId => {
            client.sendMessage(userId, msg);
        });
        console.log('📨 Pengingat deadline terkirim!');
    }, {
        timezone: 'Asia/Jakarta'
    });

    // ─────────────────────────────────────────────
    // 3. Good Night — 23:00 MYT (Malaysia Time) 
    // ─────────────────────────────────────────────
    cron.schedule('0 23 * * *', () => {
        const now = moment().tz('Asia/Kuala_Lumpur');
        const partnerId = config.getPartnerId();
        
        const msg = `*🌙 Selamat Malam 🌙*\n\n` +
            `Sudah jam ${now.format('HH:mm')} di Malaysia.\n` +
            `Waktunya istirahat ya sayang~ 💤\n\n` +
            `_Jangan lupa mimpi indah!_ ✨🌟`;

        client.sendMessage(partnerId, msg);
        console.log(`🌙 Good night message terkirim ke ${partnerId} (23:00 MYT)`);
    }, {
        timezone: 'Asia/Kuala_Lumpur'
    });

    // ─────────────────────────────────────────────
    // 4. Pengingat Malam — 21:00 WIB (Review tugas)
    // ─────────────────────────────────────────────
    cron.schedule('0 21 * * *', () => {
        const todos = db.getAll();
        if (todos.length === 0) return;

        let msg = '*🌃 REVIEW MALAM 🌃*\n\n';
        msg += `Kamu masih punya *${todos.length} tugas* yang belum selesai:\n\n`;
        todos.forEach((item, i) => msg += `${i + 1}. ${item}\n`);
        msg += '\n_Sudah selesai? Ketik !hapus [nomor] atau !clear_ 💪';

        config.AUTHORIZED_USERS.forEach(userId => {
            client.sendMessage(userId, msg);
        });
        console.log('📨 Review malam terkirim!');
    }, {
        timezone: 'Asia/Jakarta'
    });

    console.log('✅ Cron Jobs aktif: Pagi (07:00), Deadline (08:00), Malam (21:00), Good Night (23:00 MYT)');
}

module.exports = { initCrons };

