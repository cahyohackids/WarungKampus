// ============================================
//  ➕ COMMAND: !add
// ============================================

module.exports = {
    name: 'add',
    description: 'Tambah tugas baru. Contoh: !add Belajar Node.js',
    ownerOnly: true,

    async execute(message, args, { db }) {
        const item = args.join(' ');
        if (!item) {
            return message.reply('❌ Format: *!add [tugas]*\nContoh: !add Belajar Node.js');
        }

        const total = db.add(item);
        message.reply(`✅ Disimpan: "${item}"\n📋 Total tugas: *${total}*`);
    },
};
