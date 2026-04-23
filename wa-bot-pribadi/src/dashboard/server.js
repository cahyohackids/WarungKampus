// ============================================
//  🌐 EXPRESS DASHBOARD SERVER v2
// ============================================

const express = require('express');
const path = require('path');
const fs = require('fs');
const db = require('../database/todoDatabase');
const config = require('../config');

// Try loading other databases
let deadlineDb, scheduleDb, notesDb;
try { deadlineDb = require('../database/deadlineDatabase'); } catch(e) {}
try { scheduleDb = require('../database/scheduleDatabase'); } catch(e) {}
try { notesDb = require('../database/notesDatabase'); } catch(e) {}

// Track message statistics
const stats = {
    totalMessages: 0,
    commandsUsed: 0,
    commandCounts: {},
    todayMessages: 0,
    lastReset: new Date().toDateString(),
    startTime: Date.now(),
};

function trackCommand(cmdName) {
    stats.totalMessages++;
    stats.commandsUsed++;
    stats.commandCounts[cmdName] = (stats.commandCounts[cmdName] || 0) + 1;

    // Reset daily counter
    const today = new Date().toDateString();
    if (today !== stats.lastReset) {
        stats.todayMessages = 0;
        stats.lastReset = today;
    }
    stats.todayMessages++;
}

function trackMessage() {
    stats.totalMessages++;
    const today = new Date().toDateString();
    if (today !== stats.lastReset) {
        stats.todayMessages = 0;
        stats.lastReset = today;
    }
    stats.todayMessages++;
}

function startDashboard(client) {
    const app = express();

    app.use(express.static(path.join(__dirname, 'public')));

    // --- API: Bot Status ---
    app.get('/api/status', (req, res) => {
        const uptime = process.uptime();
        const hours = Math.floor(uptime / 3600);
        const minutes = Math.floor((uptime % 3600) / 60);
        const seconds = Math.floor(uptime % 60);

        const mem = process.memoryUsage();
        const memMB = (mem.heapUsed / 1024 / 1024).toFixed(1);
        const memTotalMB = (mem.heapTotal / 1024 / 1024).toFixed(1);
        const memPercent = ((mem.heapUsed / mem.heapTotal) * 100).toFixed(0);

        let status = 'disconnected';
        let info = null;

        try {
            if (client && client.info && client.info.wid) {
                status = 'connected';
                info = {
                    number: client.info.wid.user,
                    platform: client.info.platform,
                    pushname: client.info.pushname,
                };
            }
        } catch (e) {
            status = 'disconnected';
        }

        res.json({
            status,
            botName: config.BOT_NAME,
            version: config.BOT_VERSION,
            uptime: { hours, minutes, seconds, raw: uptime },
            memory: { used: `${memMB} MB`, total: `${memTotalMB} MB`, percent: memPercent },
            nodeVersion: process.version,
            info,
            os: process.platform,
            pid: process.pid,
        });
    });

    // --- API: Statistics ---
    app.get('/api/stats', (req, res) => {
        const todoCount = db.getAll().length;
        const deadlineCount = deadlineDb ? deadlineDb.count() : 0;
        const notesCount = notesDb ? notesDb.count() : 0;
        
        let scheduleCount = 0;
        let todaySchedule = [];
        if (scheduleDb) {
            const all = scheduleDb.getAllSchedule();
            Object.values(all).forEach(items => scheduleCount += items.length);
            const todayName = scheduleDb.getTodayName();
            todaySchedule = scheduleDb.getScheduleByDay(todayName);
        }

        // Upcoming deadlines (next 7 days)
        let upcomingDeadlines = [];
        if (deadlineDb) {
            const now = new Date();
            upcomingDeadlines = deadlineDb.getAll()
                .filter(d => {
                    const diff = Math.ceil((new Date(d.date) - now) / (1000 * 60 * 60 * 24));
                    return diff >= 0 && diff <= 7;
                })
                .slice(0, 5);
        }

        // Top commands
        const topCommands = Object.entries(stats.commandCounts)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 8)
            .map(([name, count]) => ({ name, count }));

        res.json({
            messages: {
                total: stats.totalMessages,
                today: stats.todayMessages,
                commands: stats.commandsUsed,
            },
            data: {
                todos: todoCount,
                deadlines: deadlineCount,
                notes: notesCount,
                schedules: scheduleCount,
            },
            topCommands,
            todaySchedule: todaySchedule.map(s => ({
                jam: s.jam,
                matkul: s.matkul,
                ruang: s.ruang,
            })),
            upcomingDeadlines: upcomingDeadlines.map(d => ({
                matkul: d.matkul,
                task: d.task,
                date: d.date,
                daysLeft: Math.ceil((new Date(d.date) - new Date()) / (1000 * 60 * 60 * 24)),
            })),
        });
    });

    // --- API: Todos ---
    app.get('/api/todos', (req, res) => {
        const todos = db.getAll();
        res.json({
            count: todos.length,
            items: todos.map((item, index) => ({
                id: index + 1,
                text: item,
            })),
        });
    });

    // --- API: Commands ---
    app.get('/api/commands', (req, res) => {
        try {
            const cmdsDir = path.join(__dirname, '..', 'commands');
            const files = fs.readdirSync(cmdsDir).filter(f => f.endsWith('.js'));
            const commands = files.map(file => {
                const cmd = require(path.join(cmdsDir, file));
                return {
                    name: cmd.name,
                    description: cmd.description,
                    ownerOnly: cmd.ownerOnly,
                    hidden: cmd.hidden || false,
                };
            }).filter(c => !c.hidden);
            res.json({ count: commands.length, commands });
        } catch (error) {
            res.json({ count: 0, commands: [] });
        }
    });

    // Start server
    const server = app.listen(config.PORT, () => {
        console.log(`🌐 Dashboard aktif di http://localhost:${config.PORT}`);
    });

    return server;
}

module.exports = { startDashboard, trackCommand, trackMessage };
