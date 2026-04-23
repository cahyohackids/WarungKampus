// ============================================
//  📋 COMMAND: !list
// ============================================

module.exports = {
    name: 'list',
    description: 'Lihat semua tugas yang tersimpan',
    ownerOnly: true,

    async execute(message, args, { db }) {
        const todos = db.getAll();

        if (todos.length === 0) {
            return message.reply('📋 Tugas kosong. Santai dulu! ☕');
        }

        let txt = '*📋 DAFTAR TUGAS:*\n\n';
        todos.forEach((item, i) => {
            txt += `  ${i + 1}. ${item}\n`;
        });
        txt += `\n_Total: ${todos.length} tugas_`;
        
        message.reply(txt);
    },
};
