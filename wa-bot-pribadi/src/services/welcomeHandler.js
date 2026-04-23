// ============================================
//  👋 WELCOME HANDLER
//  Greeting untuk pengguna baru + menu interaktif
//  Trigger: hai, halo, hello, hi, start, p, bot
// ============================================

const { MessageMedia } = require('whatsapp-web.js');
const fs = require('fs');
const path = require('path');
const config = require('../config');

// Path gambar welcome
const WELCOME_IMAGE = path.join(__dirname, '..', 'assets', 'welcome_banner.png');

// Kata-kata trigger untuk welcome
const GREETINGS = [
    'hai', 'halo', 'hello', 'hi', 'hey', 'p', 'start',
    'bot', 'hallo', 'hy', 'assalamualaikum', 'assalamu', 'selamat',
];

/**
 * Cek apakah pesan adalah greeting
 */
function isGreeting(text) {
    const lower = text.toLowerCase().trim();
    return GREETINGS.includes(lower) || GREETINGS.some(g => lower === g + '!') || GREETINGS.some(g => lower === g + '.');
}

/**
 * Kirim welcome message dengan gambar + menu interaktif
 */
async function sendWelcome(message, client) {
    try {
        const contact = await message.getContact();
        const name = contact.pushname || 'Kak';

        // Cek waktu untuk salam yang sesuai
        const hour = new Date().getHours();
        let salam;
        if (hour >= 3 && hour < 11) salam = 'Selamat Pagi 🌅';
        else if (hour >= 11 && hour < 15) salam = 'Selamat Siang ☀️';
        else if (hour >= 15 && hour < 18) salam = 'Selamat Sore 🌤️';
        else salam = 'Selamat Malam 🌙';

        // Pesan welcome dengan menu interaktif
        const welcomeText = 
`${salam}, *${name}*! 👋

Terima kasih telah menghubungi *${config.BOT_NAME}*!
Saya adalah asisten pintar yang siap membantu kamu 24/7.

━━━━━━━━━━━━━━━━━━━━

📌 *PILIH MENU:*

*[1]* 🤖 AI & Bahasa
_Tanya AI, rangkum, terjemah, cek grammar_

*[2]* 📚 Akademik
_Jadwal, deadline, IPK, rumus, pomodoro_

*[3]* 📝 Produktivitas
_To-do list, catatan, pengingat, voting_

*[4]* 🎲 Utilitas
_Kalkulator, stiker, kurs, konversi, sholat_

*[5]* 📖 Semua Menu Lengkap

━━━━━━━━━━━━━━━━━━━━

💡 _Balas angka *1-5* untuk lihat detail_
💡 _Atau langsung ketik command, contoh: *!ai halo*_`;

        // Kirim gambar + caption jika gambar tersedia
        if (fs.existsSync(WELCOME_IMAGE)) {
            const media = MessageMedia.fromFilePath(WELCOME_IMAGE);
            await client.sendMessage(message.from, media, { caption: welcomeText });
        } else {
            await message.reply(welcomeText);
        }

    } catch (error) {
        console.error('Welcome Error:', error);
    }
}

/**
 * Handle menu reply (angka 1-5)
 */
function isMenuReply(text) {
    const trimmed = text.trim();
    return ['1', '2', '3', '4', '5'].includes(trimmed);
}

async function handleMenuReply(message, choice, commands) {
    const categories = {
        '1': {
            title: '🤖 AI & BAHASA',
            names: ['ai', 'rangkum', 'explain', 'terjemah', 'kbbi', 'sinonim', 'cek'],
        },
        '2': {
            title: '📚 AKADEMIK',
            names: ['jadwal', 'deadline', 'gpa', 'rumus', 'pomodoro', 'kelompok'],
        },
        '3': {
            title: '📝 PRODUKTIVITAS',
            names: ['add', 'list', 'hapus', 'clear', 'notes', 'remind', 'vote'],
        },
        '4': {
            title: '🎲 UTILITAS',
            names: ['ping', 'calc', 'sticker', 'quote', 'random', 'kurs', 'konversi', 'sholat', 'tagall', 'info'],
        },
    };

    // Pilihan 5 = Semua Menu (!menu)
    if (choice === '5') {
        const menuCmd = commands.get('menu');
        if (menuCmd) {
            return menuCmd.execute(message, [], { commands });
        }
        return;
    }

    const cat = categories[choice];
    if (!cat) return;

    let msg = `┌──「 ${cat.title} 」\n│\n`;

    cat.names.forEach(name => {
        const cmd = commands.get(name);
        if (cmd && !cmd.hidden) {
            const lock = cmd.ownerOnly ? ' 🔐' : '';
            msg += `│ ▸ *!${cmd.name}*${lock}\n`;
            msg += `│   _${cmd.description}_\n│\n`;
        }
    });

    msg += `└────────────────\n\n`;
    msg += `_🔐 = Khusus Owner_\n`;
    msg += `_💡 Ketik perintah untuk mulai, contoh: *!${cat.names[0]}*_\n`;
    msg += `_↩️ Ketik *hai* untuk kembali ke menu utama_`;

    message.reply(msg);
}

module.exports = {
    isGreeting,
    sendWelcome,
    isMenuReply,
    handleMenuReply,
};
