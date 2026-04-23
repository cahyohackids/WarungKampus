// ============================================
//  ℹ️ COMMAND: !info — Info bot & sistem
// ============================================

const os = require('os');
const config = require('../config');

module.exports = {
    name: 'info',
    description: 'Tampilkan informasi detail sistem bot',
    ownerOnly: false,

    async execute(message, args, { client, db }) {
        const uptime = process.uptime();
        const hours = Math.floor(uptime / 3600);
        const minutes = Math.floor((uptime % 3600) / 60);
        const seconds = Math.floor(uptime % 60);

        const memUsage = process.memoryUsage();
        const memMB = (memUsage.heapUsed / 1024 / 1024).toFixed(1);
        const totalMemGB = (os.totalmem() / 1024 / 1024 / 1024).toFixed(1);

        const msg = 
`╔══════════════════════════╗
║     ℹ️ *SYSTEM INFO* ℹ️      ║
╚══════════════════════════╝

*🤖 Bot*
┃ Nama: ${config.BOT_NAME}
┃ Versi: v${config.BOT_VERSION}
┃ Uptime: ${hours}j ${minutes}m ${seconds}d

*💻 Server*
┃ OS: ${os.type()} ${os.release()}
┃ Platform: ${os.platform()} ${os.arch()}
┃ Hostname: ${os.hostname()}

*🧠 Resource*
┃ CPU: ${os.cpus()[0]?.model || 'Unknown'}
┃ RAM: ${memMB} MB / ${totalMemGB} GB
┃ Node.js: ${process.version}

*📊 Stats*
┃ Total Tugas: ${db.count()}
┃ Dashboard: http://localhost:${config.PORT}

━━━━━━━━━━━━━━━━━━━━━━━━━
_Running 24/7 on your server_ 🚀`;

        message.reply(msg);
    },
};
