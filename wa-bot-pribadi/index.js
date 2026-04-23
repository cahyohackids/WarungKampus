// ============================================
//  🚀 WA BOT PRIBADI v2.0 — MODULAR EDITION
//  Entry point: Dynamic command loader + client
// ============================================

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');

// --- Import Modules ---
const config = require('./src/config');
const db = require('./src/database/todoDatabase');
const { initCrons } = require('./src/services/cronService');
const { startDashboard, trackCommand, trackMessage } = require('./src/dashboard/server');
const welcome = require('./src/services/welcomeHandler');

// ─────────────────────────────────────────────
//  📦 DYNAMIC COMMAND LOADER
// ─────────────────────────────────────────────
const commands = new Map();
const commandsDir = path.join(__dirname, 'src', 'commands');
const commandFiles = fs.readdirSync(commandsDir).filter(f => f.endsWith('.js'));

console.log('📦 Loading commands...');
for (const file of commandFiles) {
    try {
        const cmd = require(path.join(commandsDir, file));
        commands.set(cmd.name, cmd);
        console.log(`   ✅ !${cmd.name} — ${cmd.description}`);
    } catch (err) {
        console.error(`   ❌ Gagal load ${file}:`, err.message);
    }
}
console.log(`📦 ${commands.size} commands loaded!\n`);

// ─────────────────────────────────────────────
//  🤖 WHATSAPP CLIENT SETUP
// ─────────────────────────────────────────────
const puppeteerConfig = {
    headless: true,
    args: config.PUPPETEER_ARGS,
};

// Untuk Docker/VPS: gunakan Chromium dari sistem
if (config.PUPPETEER_EXECUTABLE_PATH) {
    puppeteerConfig.executablePath = config.PUPPETEER_EXECUTABLE_PATH;
}

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: puppeteerConfig,
});

// --- QR Code Event ---
client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
    console.log('📱 Scan QR Code di atas menggunakan WhatsApp Anda!');
});

// --- Ready Event ---
client.on('ready', () => {
    console.log('');
    console.log('╔══════════════════════════════════════════╗');
    console.log('║   🔥 BOT v2.0 AKTIF DAN SIAP 24/7! 🔥  ║');
    console.log('╚══════════════════════════════════════════╝');
    console.log('');

    // Inisialisasi cron jobs
    initCrons(client);

    // Start Express dashboard
    startDashboard(client);
});

// --- Auth failure ---
client.on('auth_failure', (msg) => {
    console.error('❌ Auth gagal:', msg);
});

// --- Disconnected ---
client.on('disconnected', (reason) => {
    console.log('⚠️ Client disconnected:', reason);
});

// ─────────────────────────────────────────────
//  💬 MESSAGE HANDLER
// ─────────────────────────────────────────────
const PREFIX = '!';

// Daftar command yang owner-only (untuk pesan akses ditolak)
const ownerCommands = new Set();
commands.forEach((cmd) => {
    if (cmd.ownerOnly) ownerCommands.add(cmd.name);
});

client.on('message', async (message) => {
    const chat = message.body.trim();

    // Track semua pesan masuk untuk statistik
    trackMessage();
    
    // --- WELCOME HANDLER: Greeting / Salam ---
    if (welcome.isGreeting(chat)) {
        return welcome.sendWelcome(message, client);
    }

    // --- MENU REPLY: Angka 1-5 ---
    if (welcome.isMenuReply(chat)) {
        return welcome.handleMenuReply(message, chat.trim(), commands);
    }

    // Abaikan jika bukan command
    if (!chat.startsWith(PREFIX)) return;

    // Parse command & arguments
    const parts = chat.slice(PREFIX.length).split(/\s+/);
    const commandName = parts[0].toLowerCase();
    const args = parts.slice(1);

    // Cari command di Map
    const command = commands.get(commandName);
    if (!command) return; // Command tidak ditemukan, abaikan saja

    // Cek apakah pengirim authorized
    const isAuthorized = config.AUTHORIZED_USERS.includes(message.from) ||
                         message.from === (client.info?.wid?._serialized);

    // Jika command owner-only tapi pengirim bukan authorized
    if (command.ownerOnly && !isAuthorized) {
        return message.reply('⛔ Akses ditolak. Fitur ini hanya untuk administrator (Owner).');
    }

    // Execute command
    try {
        // Track command usage
        trackCommand(commandName);

        await command.execute(message, args, {
            client,
            db,
            config,
            commands,
        });
    } catch (error) {
        console.error(`❌ Error di command !${commandName}:`, error);
        message.reply('❌ Terjadi error saat menjalankan command. Coba lagi nanti.');
    }
});

// ─────────────────────────────────────────────
//  🚀 INISIALISASI
// ─────────────────────────────────────────────
console.log('🚀 Menginisialisasi WhatsApp Bot...\n');
client.initialize();