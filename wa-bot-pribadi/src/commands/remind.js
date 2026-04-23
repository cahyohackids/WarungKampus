// ============================================
//  ⏳ COMMAND: !remind
// ============================================

module.exports = {
    name: 'remind',
    description: 'Atur pengingat. Contoh: !remind 30 Makan siang',
    ownerOnly: true,

    async execute(message, args, { client }) {
        const menit = parseInt(args[0]);
        const pesan = args.slice(1).join(' ');

        if (isNaN(menit) || !pesan) {
            return message.reply('❌ Format: *!remind [menit] [pesan]*\nContoh: !remind 30 Makan siang');
        }

        message.reply(`⏳ Mengingatkan "*${pesan}*" dalam *${menit} menit*.\n_Timer dimulai sekarang!_ ⏱️`);

        setTimeout(() => {
            client.sendMessage(message.from, 
                `*⏰ WAKTUNYA!*\n\n` +
                `📌 ${pesan}\n\n` +
                `_Pengingat dari ${menit} menit yang lalu_`
            );
        }, menit * 60000);
    },
};
