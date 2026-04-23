// ============================================
//  🌐 COMMAND: !terjemah — Terjemahkan teks
//  Multi-bahasa via AI
// ============================================

const genai = require('../services/genaiService');

module.exports = {
    name: 'terjemah',
    description: 'Terjemahkan teks. Contoh: !terjemah en Hello World',
    ownerOnly: false,

    async execute(message, args, { client }) {
        try {
            const langMap = {
                'en': 'English',
                'id': 'Bahasa Indonesia',
                'ms': 'Bahasa Melayu',
                'jv': 'Bahasa Jawa',
                'su': 'Bahasa Sunda',
                'ar': 'Bahasa Arab',
                'ja': 'Bahasa Jepang',
                'ko': 'Bahasa Korea',
                'zh': 'Bahasa Mandarin',
                'de': 'Bahasa Jerman',
                'fr': 'Bahasa Prancis',
                'es': 'Bahasa Spanyol',
                'pt': 'Bahasa Portugis',
                'nl': 'Bahasa Belanda',
                'th': 'Bahasa Thailand',
            };

            let targetLang = args[0]?.toLowerCase();
            let textToTranslate = '';

            // Cek apakah argumen pertama adalah kode bahasa
            if (targetLang && langMap[targetLang]) {
                // !terjemah en [teks] atau reply
                if (message.hasQuotedMsg) {
                    const quoted = await message.getQuotedMessage();
                    textToTranslate = quoted.body;
                } else {
                    textToTranslate = args.slice(1).join(' ');
                }
            } else if (message.hasQuotedMsg) {
                // !terjemah (tanpa kode bahasa, reply pesan) — default ke Indonesia
                const quoted = await message.getQuotedMessage();
                textToTranslate = quoted.body;
                targetLang = 'id';
            } else {
                return message.reply(
`🌐 *TERJEMAHAN — Panduan*

▸ *!terjemah en teks bahasa Indonesia*
    ↳ Terjemahkan ke English
▸ Reply pesan + *!terjemah en*
    ↳ Terjemahkan pesan ke English
▸ Reply pesan + *!terjemah*
    ↳ Otomatis terjemahkan ke B. Indonesia

*Kode bahasa:*
en=English | id=Indonesia | ms=Melayu
jv=Jawa | ar=Arab | ja=Jepang
ko=Korea | zh=Mandarin | de=Jerman
fr=Prancis | es=Spanyol | th=Thailand`
                );
            }

            if (!textToTranslate) {
                return message.reply('❌ Tidak ada teks untuk diterjemahkan.');
            }

            const langName = langMap[targetLang] || targetLang;

            const prompt = `Terjemahkan teks berikut ke ${langName}. Berikan HANYA terjemahannya saja tanpa penjelasan tambahan.

Teks:
"""
${textToTranslate}
"""`;

            const result = await genai.generateText(prompt);

            message.reply(
                `🌐 *TERJEMAHAN* → ${langName}\n\n` +
                `${result}\n\n` +
                `_Diterjemahkan via AI_ 🤖`
            );

        } catch (error) {
            console.error('Terjemah Error:', error);
            message.reply('❌ Gagal menerjemahkan. Coba lagi nanti.');
        }
    },
};
