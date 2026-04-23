// ============================================
//  🧹 COMMAND: !clear
// ============================================

module.exports = {
    name: 'clear',
    description: 'Hapus semua tugas sekaligus',
    ownerOnly: true,

    async execute(message, args, { db }) {
        const count = db.count();
        db.clear();
        message.reply(`🧹 Semua *${count} tugas* telah disapu bersih!\n_Mulai dari awal yang fresh_ ✨`);
    },
};
