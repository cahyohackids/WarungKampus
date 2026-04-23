// ============================================
//  🔧 KONFIGURASI UTAMA BOT
// ============================================

const path = require('path');

// --- API KEY ---
const GEMINI_API_KEY = process.env.GEMINI_API_KEY || 'YOUR_GEMINI_API_KEY_HERE';

// --- OWNER & AUTHORIZED USERS ---
// Nomor-nomor yang memiliki akses ke fitur Owner-only
const OWNER_ID = '6285710999204@c.us';
const AUTHORIZED_USERS = [
    '6285710999204@c.us',   // Owner utama
    '6282117196408@c.us',   // User kedua (authorized)
];

// --- PARTNER (untuk fitur LDR) ---
// Bisa diubah saat bot berjalan nanti
let PARTNER_ID = OWNER_ID; // Default ke owner, ganti nanti

// --- FILE DATABASE ---
const DATA_FILE = path.join(__dirname, '..', '..', 'todolist.json');

// --- PUPPETEER CONFIG ---
const PUPPETEER_ARGS = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--no-first-run',
    '--no-zygote',
    '--disable-gpu',
    '--single-process',
];

// Untuk Docker/VPS: gunakan Chromium dari sistem
const PUPPETEER_EXECUTABLE_PATH = process.env.PUPPETEER_EXECUTABLE_PATH || null;

// --- DASHBOARD ---
const PORT = process.env.PORT || 3000;

// --- BOT INFO ---
const BOT_NAME = '🤖 WA Bot Pribadi';
const BOT_VERSION = '2.0.0';
const BOT_START_TIME = Date.now();

module.exports = {
    GEMINI_API_KEY,
    OWNER_ID,
    AUTHORIZED_USERS,
    PARTNER_ID,
    setPartnerId: (id) => { PARTNER_ID = id; },
    getPartnerId: () => PARTNER_ID,
    DATA_FILE,
    PUPPETEER_ARGS,
    PUPPETEER_EXECUTABLE_PATH,
    PORT,
    BOT_NAME,
    BOT_VERSION,
    BOT_START_TIME,
};
