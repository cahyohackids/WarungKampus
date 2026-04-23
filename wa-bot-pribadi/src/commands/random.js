// ============================================
//  🎲 COMMAND: !random — Tools Acak
//  Lempar koin, dadu, pilih opsi, angka acak
// ============================================

module.exports = {
    name: 'random',
    description: 'Lempar koin, dadu, atau pilih acak. Ketik !random',
    ownerOnly: false,

    async execute(message, args, { client }) {
        const sub = args[0]?.toLowerCase();

        // === !random (bantuan) ===
        if (!sub) {
            return message.reply(
`🎲 *RANDOM TOOLS — Panduan*

▸ *!random koin* — Lempar koin (Heads/Tails)
▸ *!random dadu* — Lempar dadu (1-6)
▸ *!random angka 1 100* — Angka acak 1-100
▸ *!random pilih Nasi Goreng, Mie Ayam, Bakso*
    ↳ Pilih satu opsi secara acak
▸ *!random warna* — Warna acak (HEX)

_Cocok untuk ambil keputusan!_ 🎰`
            );
        }

        // === !random koin ===
        if (sub === 'koin' || sub === 'coin' || sub === 'flip') {
            const result = Math.random() < 0.5 ? 'HEADS 🪙' : 'TAILS 🪙';
            return message.reply(
                `🪙 *Lempar Koin!*\n\n` +
                `Hasil: *${result}*\n\n` +
                `_Lemparan adil & acak_ 🎲`
            );
        }

        // === !random dadu ===
        if (sub === 'dadu' || sub === 'dice' || sub === 'roll') {
            const count = Math.min(parseInt(args[1]) || 1, 5);
            const results = [];
            const diceEmoji = ['', '⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];

            for (let i = 0; i < count; i++) {
                const val = Math.floor(Math.random() * 6) + 1;
                results.push({ val, emoji: diceEmoji[val] });
            }

            const total = results.reduce((sum, r) => sum + r.val, 0);
            let msg = `🎲 *Lempar ${count} Dadu!*\n\n`;
            results.forEach((r, i) => {
                msg += `  Dadu ${i + 1}: ${r.emoji} = *${r.val}*\n`;
            });
            if (count > 1) msg += `\n  Total: *${total}*`;

            return message.reply(msg);
        }

        // === !random angka [min] [max] ===
        if (sub === 'angka' || sub === 'number') {
            const min = parseInt(args[1]) || 1;
            const max = parseInt(args[2]) || 100;
            const result = Math.floor(Math.random() * (max - min + 1)) + min;

            return message.reply(
                `🔢 *Angka Acak*\n\n` +
                `Range: ${min} - ${max}\n` +
                `Hasil: *${result}*`
            );
        }

        // === !random pilih [opsi1, opsi2, ...] ===
        if (sub === 'pilih' || sub === 'pick' || sub === 'choose') {
            const options = args.slice(1).join(' ').split(',').map(o => o.trim()).filter(o => o);

            if (options.length < 2) {
                return message.reply('❌ Minimal 2 opsi dipisahkan koma.\nContoh: *!random pilih Nasi Goreng, Mie Ayam, Bakso*');
            }

            const picked = options[Math.floor(Math.random() * options.length)];

            let msg = `🎯 *Pilihan Acak!*\n\n`;
            msg += `Opsi: ${options.join(' | ')}\n\n`;
            msg += `Terpilih: *${picked}* 🎉`;

            return message.reply(msg);
        }

        // === !random warna ===
        if (sub === 'warna' || sub === 'color') {
            const hex = '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0').toUpperCase();
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);

            return message.reply(
                `🎨 *Warna Acak*\n\n` +
                `HEX: *${hex}*\n` +
                `RGB: *rgb(${r}, ${g}, ${b})*\n\n` +
                `_Cocok untuk inspirasi desain!_ 🖌️`
            );
        }

        message.reply('❌ Sub-command tidak dikenal. Ketik *!random* untuk bantuan.');
    },
};
