// ============================================
//  📅 DATABASE JADWAL KULIAH (JSON-based)
// ============================================

const fs = require('fs');
const path = require('path');

const SCHEDULE_FILE = path.join(__dirname, '..', '..', 'jadwal.json');

let scheduleData = {};

function loadSchedule() {
    try {
        if (fs.existsSync(SCHEDULE_FILE)) {
            scheduleData = JSON.parse(fs.readFileSync(SCHEDULE_FILE, 'utf-8'));
        }
    } catch (err) {
        console.error('❌ Gagal membaca jadwal.json:', err.message);
        scheduleData = {};
    }
    return scheduleData;
}

function saveSchedule() {
    try {
        fs.writeFileSync(SCHEDULE_FILE, JSON.stringify(scheduleData, null, 2));
    } catch (err) {
        console.error('❌ Gagal menyimpan jadwal.json:', err.message);
    }
}

// Normalisasi nama hari
function normalizeDay(day) {
    const map = {
        'senin': 'Senin', 'monday': 'Senin', 'sen': 'Senin', 'mon': 'Senin',
        'selasa': 'Selasa', 'tuesday': 'Selasa', 'sel': 'Selasa', 'tue': 'Selasa',
        'rabu': 'Rabu', 'wednesday': 'Rabu', 'rab': 'Rabu', 'wed': 'Rabu',
        'kamis': 'Kamis', 'thursday': 'Kamis', 'kam': 'Kamis', 'thu': 'Kamis',
        'jumat': 'Jumat', 'friday': 'Jumat', 'jum': 'Jumat', 'fri': 'Jumat',
        'sabtu': 'Sabtu', 'saturday': 'Sabtu', 'sab': 'Sabtu', 'sat': 'Sabtu',
        'minggu': 'Minggu', 'sunday': 'Minggu', 'min': 'Minggu', 'sun': 'Minggu',
    };
    return map[day.toLowerCase()] || null;
}

function getTodayName() {
    const days = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
    return days[new Date().getDay()];
}

function getScheduleByDay(day) {
    return scheduleData[day] || [];
}

function addSchedule(day, entry) {
    if (!scheduleData[day]) scheduleData[day] = [];
    scheduleData[day].push(entry);
    // Sort by jam
    scheduleData[day].sort((a, b) => a.jam.localeCompare(b.jam));
    saveSchedule();
}

function removeSchedule(day, index) {
    if (!scheduleData[day] || index < 0 || index >= scheduleData[day].length) return null;
    const removed = scheduleData[day].splice(index, 1)[0];
    if (scheduleData[day].length === 0) delete scheduleData[day];
    saveSchedule();
    return removed;
}

function clearScheduleDay(day) {
    delete scheduleData[day];
    saveSchedule();
}

function getAllSchedule() {
    return { ...scheduleData };
}

// Init
loadSchedule();

module.exports = {
    normalizeDay,
    getTodayName,
    getScheduleByDay,
    addSchedule,
    removeSchedule,
    clearScheduleDay,
    getAllSchedule,
    loadSchedule,
};
