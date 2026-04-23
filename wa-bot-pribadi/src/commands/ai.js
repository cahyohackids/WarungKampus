// ============================================
//  🤖 COMMAND: !ai
// ============================================

const genai = require('../services/genaiService');

module.exports = {
    name: 'ai',
    description: 'Tanya AI (teks & gambar). Contoh: !ai jelaskan cuaca hari ini',
    ownerOnly: false,

    async execute(message, args, { client }) {
        const prompt = args.join(' ');

        if (!prompt && !message.hasMedia) {
            return message.reply('❌ Tulis pertanyaan setelah !ai\nContoh: *!ai apa itu JavaScript?*');
        }

        try {
            const contact = await message.getContact();
            const senderName = contact.pushname || 'Kak';

            // Cek apakah ada gambar (langsung atau di-reply)
            const hasImage = message.hasMedia || 
                (message.hasQuotedMsg && (await message.getQuotedMessage()).hasMedia);

            if (hasImage) {
                const targetMsg = message.hasMedia ? message : await message.getQuotedMessage();
                const media = await targetMsg.downloadMedia();

                const result = await genai.generateVision(
                    prompt || 'Jelaskan gambar ini',
                    media.data,
                    media.mimetype
                );

                message.reply(`Halo *${senderName}*! 🤖\n\n${result}`);
            } else {
                const result = await genai.generateText(prompt);
                message.reply(`Halo *${senderName}*! 🤖\n\n${result}`);
            }
        } catch (error) {
            console.error('AI Error:', error);
            message.reply('❌ Waduh, otak AI-nya sedang kelebihan beban nih. Coba lagi nanti ya.');
        }
    },
};
