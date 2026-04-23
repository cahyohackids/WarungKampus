// ============================================
//  📢 COMMAND: !tagall — Tag Semua Anggota Grup
//  Mention semua peserta di grup WhatsApp
// ============================================

module.exports = {
    name: 'tagall',
    description: 'Tag semua anggota grup. Hanya bisa di grup',
    ownerOnly: true,

    async execute(message, args, { client }) {
        // Cek apakah di grup
        const chat = await message.getChat();
        if (!chat.isGroup) {
            return message.reply('❌ Perintah ini hanya bisa digunakan di *grup*.');
        }

        try {
            const customMsg = args.join(' ') || '📢 Perhatian semua!';

            // Ambil semua participants
            const participants = chat.participants;

            let text = `📢 *TAG ALL*\n\n`;
            text += `💬 ${customMsg}\n\n`;

            const mentions = [];

            participants.forEach(p => {
                const id = p.id._serialized;
                mentions.push(id);
                text += `@${p.id.user} `;
            });

            text += `\n\n_${participants.length} anggota di-tag_`;

            await chat.sendMessage(text, { mentions });

        } catch (error) {
            console.error('Tagall Error:', error);
            message.reply('❌ Gagal tag semua anggota. Pastikan bot adalah admin grup.');
        }
    },
};
