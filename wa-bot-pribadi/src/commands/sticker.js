// ============================================
//  🖼️ COMMAND: !sticker — Convert gambar ke stiker
// ============================================

const { MessageMedia } = require('whatsapp-web.js');

module.exports = {
    name: 'sticker',
    description: 'Ubah gambar menjadi stiker. Kirim/reply gambar + !sticker',
    ownerOnly: false,

    async execute(message, args, { client }) {
        try {
            let mediaMsg = null;

            if (message.hasMedia) {
                mediaMsg = message;
            } else if (message.hasQuotedMsg) {
                const quoted = await message.getQuotedMessage();
                if (quoted.hasMedia) {
                    mediaMsg = quoted;
                }
            }

            if (!mediaMsg) {
                return message.reply(
                    '❌ Kirim gambar dengan caption *!sticker*\n' +
                    'atau reply gambar dengan *!sticker*'
                );
            }

            const media = await mediaMsg.downloadMedia();

            await client.sendMessage(message.from, media, {
                sendMediaAsSticker: true,
                stickerAuthor: 'WA Bot',
                stickerName: 'Bot Sticker',
            });

        } catch (error) {
            console.error('Sticker Error:', error);
            message.reply('❌ Gagal membuat stiker. Pastikan file-nya gambar ya.');
        }
    },
};
