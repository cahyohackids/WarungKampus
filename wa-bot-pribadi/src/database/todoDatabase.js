// ============================================
//  📦 DATABASE TODOLIST (JSON-based)
// ============================================

const fs = require('fs');
const { DATA_FILE } = require('../config');

let todoList = [];

// Load data dari file
function loadData() {
    try {
        if (fs.existsSync(DATA_FILE)) {
            const raw = fs.readFileSync(DATA_FILE, 'utf-8');
            todoList = JSON.parse(raw);
        }
    } catch (err) {
        console.error('❌ Gagal membaca todolist.json:', err.message);
        todoList = [];
    }
    return todoList;
}

// Simpan data ke file
function saveData() {
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(todoList, null, 2));
    } catch (err) {
        console.error('❌ Gagal menyimpan todolist.json:', err.message);
    }
}

// --- PUBLIC API ---

function getAll() {
    return [...todoList];
}

function add(item) {
    todoList.push(item);
    saveData();
    return todoList.length;
}

function remove(index) {
    if (index < 0 || index >= todoList.length) return null;
    const removed = todoList.splice(index, 1)[0];
    saveData();
    return removed;
}

function clear() {
    todoList = [];
    saveData();
}

function count() {
    return todoList.length;
}

// Inisialisasi: load data saat module dimuat
loadData();

module.exports = {
    getAll,
    add,
    remove,
    clear,
    count,
    loadData,
};
