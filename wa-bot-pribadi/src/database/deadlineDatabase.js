// ============================================
//  📅 DATABASE DEADLINE (JSON-based)
// ============================================

const fs = require('fs');
const path = require('path');

const DEADLINE_FILE = path.join(__dirname, '..', '..', 'deadline.json');

let deadlines = [];

function loadDeadlines() {
    try {
        if (fs.existsSync(DEADLINE_FILE)) {
            deadlines = JSON.parse(fs.readFileSync(DEADLINE_FILE, 'utf-8'));
        }
    } catch (err) {
        console.error('❌ Gagal membaca deadline.json:', err.message);
        deadlines = [];
    }
    return deadlines;
}

function saveDeadlines() {
    try {
        fs.writeFileSync(DEADLINE_FILE, JSON.stringify(deadlines, null, 2));
    } catch (err) {
        console.error('❌ Gagal menyimpan deadline.json:', err.message);
    }
}

function getAll() {
    // Sort by date ascending (terdekat dulu)
    return [...deadlines].sort((a, b) => new Date(a.date) - new Date(b.date));
}

function add(item) {
    deadlines.push(item);
    saveDeadlines();
    return deadlines.length;
}

function remove(index) {
    const sorted = getAll();
    if (index < 0 || index >= sorted.length) return null;
    const target = sorted[index];
    // Hapus dari array asli
    const realIndex = deadlines.findIndex(d => d.date === target.date && d.task === target.task && d.matkul === target.matkul);
    if (realIndex === -1) return null;
    const removed = deadlines.splice(realIndex, 1)[0];
    saveDeadlines();
    return removed;
}

function clearDone() {
    const now = new Date();
    const before = deadlines.length;
    deadlines = deadlines.filter(d => new Date(d.date) >= now);
    saveDeadlines();
    return before - deadlines.length;
}

function clearAll() {
    deadlines = [];
    saveDeadlines();
}

function count() {
    return deadlines.length;
}

// Init
loadDeadlines();

module.exports = {
    getAll,
    add,
    remove,
    clearDone,
    clearAll,
    count,
    loadDeadlines,
};
