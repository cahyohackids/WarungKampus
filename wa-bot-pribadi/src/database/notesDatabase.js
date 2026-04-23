// ============================================
//  📝 DATABASE CATATAN (JSON-based)
// ============================================

const fs = require('fs');
const path = require('path');

const NOTES_FILE = path.join(__dirname, '..', '..', 'catatan.json');

let notes = [];

function loadNotes() {
    try {
        if (fs.existsSync(NOTES_FILE)) {
            notes = JSON.parse(fs.readFileSync(NOTES_FILE, 'utf-8'));
        }
    } catch (err) {
        console.error('❌ Gagal membaca catatan.json:', err.message);
        notes = [];
    }
    return notes;
}

function saveNotes() {
    try {
        fs.writeFileSync(NOTES_FILE, JSON.stringify(notes, null, 2));
    } catch (err) {
        console.error('❌ Gagal menyimpan catatan.json:', err.message);
    }
}

function getAll() {
    return [...notes];
}

function getByTag(tag) {
    return notes.filter(n => n.tag && n.tag.toLowerCase() === tag.toLowerCase());
}

function search(keyword) {
    const kw = keyword.toLowerCase();
    return notes.filter(n =>
        n.text.toLowerCase().includes(kw) ||
        (n.tag && n.tag.toLowerCase().includes(kw))
    );
}

function add(text, tag = null) {
    const note = {
        text,
        tag,
        createdAt: new Date().toISOString(),
    };
    notes.push(note);
    saveNotes();
    return notes.length;
}

function remove(index) {
    if (index < 0 || index >= notes.length) return null;
    const removed = notes.splice(index, 1)[0];
    saveNotes();
    return removed;
}

function clearAll() {
    notes = [];
    saveNotes();
}

function count() {
    return notes.length;
}

// Init
loadNotes();

module.exports = {
    getAll,
    getByTag,
    search,
    add,
    remove,
    clearAll,
    count,
    loadNotes,
};
