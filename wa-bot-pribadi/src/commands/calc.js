// ============================================
//  🧮 COMMAND: !calc — Kalkulator sederhana
// ============================================

module.exports = {
    name: 'calc',
    description: 'Kalkulator. Contoh: !calc 100 + 200 * 3',
    ownerOnly: false,

    async execute(message, args, { client }) {
        const expression = args.join(' ');

        if (!expression) {
            return message.reply(
                '❌ Format: *!calc [ekspresi]*\n\n' +
                'Contoh:\n' +
                '▸ !calc 100 + 200\n' +
                '▸ !calc (50 * 3) / 2\n' +
                '▸ !calc 2 ** 10'
            );
        }

        try {
            // Hanya izinkan karakter math yang aman
            const sanitized = expression.replace(/[^0-9+\-*/().%\s^]/g, '');
            
            if (sanitized !== expression.replace(/\s/g, '') && sanitized !== expression) {
                return message.reply('❌ Ekspresi mengandung karakter tidak valid.');
            }

            // Ganti ^ dengan ** untuk pangkat
            const jsExpr = sanitized.replace(/\^/g, '**');
            
            // Evaluasi dengan Function constructor (safer than eval)
            const result = new Function(`return (${jsExpr})`)();

            if (typeof result !== 'number' || !isFinite(result)) {
                return message.reply('❌ Hasil tidak valid. Periksa ekspresi kamu.');
            }

            // Format angka dengan pemisah ribuan
            const formatted = result.toLocaleString('id-ID', {
                maximumFractionDigits: 6,
            });

            message.reply(
                `🧮 *KALKULATOR*\n\n` +
                `📝 ${expression}\n` +
                `━━━━━━━━━━━━━━━━\n` +
                `✅ Hasil: *${formatted}*`
            );
        } catch (error) {
            message.reply('❌ Ekspresi tidak valid. Coba lagi.\nContoh: *!calc 100 + 200*');
        }
    },
};
