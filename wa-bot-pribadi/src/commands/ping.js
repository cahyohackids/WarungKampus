// ============================================
//  📌 COMMAND: !ping
// ============================================

module.exports = {
    name: 'ping',
    description: 'Cek apakah bot sedang aktif',
    ownerOnly: false,

    async execute(message, args, { client }) {
        const uptime = process.uptime();
        const hours = Math.floor(uptime / 3600);
        const minutes = Math.floor((uptime % 3600) / 60);
        const seconds = Math.floor(uptime % 60);

        message.reply(
            `🏓 *Pong!*\n\n` +
            `Status: 🟢 Online\n` +
            `Uptime: ${hours}j ${minutes}m ${seconds}d\n` +
            `Response: _Instant_ ⚡`
        );
    },
};
