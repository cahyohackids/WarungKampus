// ============================================
//  🎯 COMMAND: !pomodoro — Timer Belajar Pomodoro
//  Teknik fokus belajar 25/5 menit
// ============================================

module.exports = {
    name: 'pomodoro',
    description: 'Timer belajar Pomodoro (25 menit fokus + 5 istirahat)',
    ownerOnly: true,

    async execute(message, args, { client }) {
        const sub = args[0]?.toLowerCase();
        const customMinutes = parseInt(args[0]);

        // Custom duration
        let focusMinutes = 25;
        let breakMinutes = 5;

        if (!isNaN(customMinutes) && customMinutes > 0 && customMinutes <= 120) {
            focusMinutes = customMinutes;
            breakMinutes = Math.max(Math.round(customMinutes / 5), 3);
        }

        if (sub === 'help' || sub === 'bantuan') {
            return message.reply(
`🎯 *POMODORO TIMER — Panduan*

▸ *!pomodoro* — Mulai timer 25 menit (default)
▸ *!pomodoro 45* — Mulai timer 45 menit
▸ *!pomodoro 60* — Mulai timer 60 menit

_Teknik Pomodoro:_
1. 📚 Fokus belajar selama X menit
2. ☕ Istirahat sejenak
3. 🔄 Ulangi!

_Max 120 menit per sesi_`
            );
        }

        // Start Pomodoro
        message.reply(
            `🎯 *POMODORO DIMULAI!*\n\n` +
            `📚 Fokus selama *${focusMinutes} menit* dimulai SEKARANG!\n` +
            `⏰ Timer berjalan...\n\n` +
            `_Matikan HP dan konsentrasi!_ 💪🔥\n\n` +
            `Bot akan mengingatkan saat waktu habis.`
        );

        // Timer fokus
        setTimeout(() => {
            client.sendMessage(message.from,
                `⏰ *WAKTU FOKUS HABIS!* ⏰\n\n` +
                `✅ Kamu sudah belajar selama *${focusMinutes} menit*. Hebat! 🎉\n\n` +
                `☕ Sekarang istirahat *${breakMinutes} menit*.\n` +
                `Stretching, minum air, jalan-jalan sebentar~\n\n` +
                `_Bot akan mengingatkan saat istirahat selesai._`
            );

            // Timer istirahat
            setTimeout(() => {
                client.sendMessage(message.from,
                    `🔔 *ISTIRAHAT SELESAI!* 🔔\n\n` +
                    `Siap untuk sesi berikutnya? 💪\n` +
                    `Ketik *!pomodoro* untuk mulai lagi.\n\n` +
                    `_"Konsistensi mengalahkan intensitas"_ 📖`
                );
            }, breakMinutes * 60000);

        }, focusMinutes * 60000);
    },
};
