// ============================================
//  📊 COMMAND: !gpa — Hitung IPK / GPA
//  Kalkulator IPK dari nilai huruf
// ============================================

module.exports = {
    name: 'gpa',
    description: 'Hitung IPK. Contoh: !gpa A,3 B+,2 B,3 A-,4',
    ownerOnly: false,

    async execute(message, args, { client }) {
        if (args.length === 0) {
            return message.reply(
`📊 *KALKULATOR IPK — Panduan*

Format: *!gpa [Nilai,SKS] [Nilai,SKS] ...*

Contoh:
▸ !gpa A,3 B+,2 B,3 A-,4
▸ !gpa A,3 A,3 B+,2 C,2

*Konversi Nilai:*
A = 4.00 | A- = 3.70
B+ = 3.30 | B = 3.00 | B- = 2.70
C+ = 2.30 | C = 2.00 | C- = 1.70
D+ = 1.30 | D = 1.00
E = 0.00

_Masukkan semua matkul yang diambil semester ini!_`
            );
        }

        const gradeMap = {
            'A': 4.00, 'A-': 3.70,
            'B+': 3.30, 'B': 3.00, 'B-': 2.70,
            'C+': 2.30, 'C': 2.00, 'C-': 1.70,
            'D+': 1.30, 'D': 1.00,
            'E': 0.00,
            // Alternatif lowercase
            'a': 4.00, 'a-': 3.70,
            'b+': 3.30, 'b': 3.00, 'b-': 2.70,
            'c+': 2.30, 'c': 2.00, 'c-': 1.70,
            'd+': 1.30, 'd': 1.00,
            'e': 0.00,
        };

        let totalBobot = 0;
        let totalSKS = 0;
        const entries = [];
        const errors = [];

        args.forEach((arg, i) => {
            const parts = arg.split(',');
            if (parts.length !== 2) {
                errors.push(`Entri ${i + 1}: "${arg}" — format salah`);
                return;
            }

            const grade = parts[0];
            const sks = parseInt(parts[1]);
            const bobot = gradeMap[grade];

            if (bobot === undefined) {
                errors.push(`Entri ${i + 1}: Nilai "${grade}" tidak valid`);
                return;
            }
            if (isNaN(sks) || sks <= 0 || sks > 8) {
                errors.push(`Entri ${i + 1}: SKS "${parts[1]}" tidak valid`);
                return;
            }

            entries.push({ grade: grade.toUpperCase(), sks, bobot });
            totalBobot += bobot * sks;
            totalSKS += sks;
        });

        if (errors.length > 0) {
            return message.reply('❌ *Ada kesalahan:*\n' + errors.join('\n') + '\n\n_Format: Nilai,SKS (contoh: A,3 B+,2)_');
        }

        if (totalSKS === 0) {
            return message.reply('❌ Tidak ada data yang valid.');
        }

        const ipk = totalBobot / totalSKS;

        // Predikat
        let predikat, emoji;
        if (ipk >= 3.76) { predikat = 'Cumlaude / Pujian'; emoji = '🏆'; }
        else if (ipk >= 3.51) { predikat = 'Sangat Memuaskan'; emoji = '🌟'; }
        else if (ipk >= 2.76) { predikat = 'Memuaskan'; emoji = '👍'; }
        else if (ipk >= 2.00) { predikat = 'Cukup'; emoji = '📘'; }
        else { predikat = 'Kurang'; emoji = '⚠️'; }

        let msg = `📊 *KALKULASI IPK*\n\n`;
        msg += `*Detail Matkul:*\n`;
        entries.forEach((e, i) => {
            msg += `  ${i + 1}. Nilai ${e.grade} × ${e.sks} SKS = ${(e.bobot * e.sks).toFixed(2)}\n`;
        });

        msg += `\n━━━━━━━━━━━━━━━━━━\n`;
        msg += `📚 Total SKS: *${totalSKS}*\n`;
        msg += `🧮 Total Bobot: *${totalBobot.toFixed(2)}*\n`;
        msg += `\n🎓 *IPK: ${ipk.toFixed(2)}*\n`;
        msg += `${emoji} Predikat: *${predikat}*`;

        message.reply(msg);
    },
};
