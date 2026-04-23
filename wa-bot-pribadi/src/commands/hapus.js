// ============================================
//  🗑️ COMMAND: !hapus
// ============================================

module.exports = {
    name: 'hapus',
    description: 'Hapus tugas berdasarkan nomor. Contoh: !hapus 2',
    ownerOnly: true,

    async execute(message, args, { db }) {
        const index = parseInt(args[0]) - 1;

        if (isNaN(index)) {
            return message.reply('❌ Format: *!hapus [nomor]*\nContoh: !hapus 2\n\n_Ketik !list untuk melihat nomor tugas._');
        }

        const removed = db.remove(index);
        if (removed) {
            message.reply(`🗑️ Dihapus: "${removed}"\n📋 Sisa tugas: *${db.count()}*`);
        } else {
            message.reply('❌ Nomor tugas tidak ditemukan. Ketik *!list* untuk melihat daftar.');
        }
    },
};
