// ============================================
//  📐 COMMAND: !konversi — Konversi Satuan
//  Konversi antar satuan (panjang, berat, suhu, dll)
// ============================================

module.exports = {
    name: 'konversi',
    description: 'Konversi satuan. Contoh: !konversi 100 cm ke m',
    ownerOnly: false,

    async execute(message, args, { client }) {
        if (args.length < 4) {
            return message.reply(
`📐 *KONVERSI SATUAN — Panduan*

Format: *!konversi [angka] [dari] ke [tujuan]*

*📏 Panjang:*
▸ !konversi 100 cm ke m
▸ !konversi 5 km ke mi

*⚖️ Berat:*
▸ !konversi 1000 g ke kg
▸ !konversi 5 kg ke lbs

*🌡️ Suhu:*
▸ !konversi 100 C ke F
▸ !konversi 212 F ke C

*💾 Digital:*
▸ !konversi 1024 MB ke GB
▸ !konversi 1 TB ke GB

*⏱️ Waktu:*
▸ !konversi 120 menit ke jam
▸ !konversi 3 jam ke detik`
            );
        }

        const value = parseFloat(args[0]);
        const fromUnit = args[1].toLowerCase();
        // args[2] is "ke"
        const toUnit = args[3]?.toLowerCase();

        if (isNaN(value) || !toUnit) {
            return message.reply('❌ Format: *!konversi [angka] [dari] ke [tujuan]*');
        }

        // Conversion tables
        const conversions = {
            // Panjang (base: meter)
            length: {
                mm: 0.001, cm: 0.01, m: 1, km: 1000,
                in: 0.0254, ft: 0.3048, yd: 0.9144, mi: 1609.344,
                inch: 0.0254, feet: 0.3048, yard: 0.9144, mile: 1609.344,
            },
            // Berat (base: gram)
            weight: {
                mg: 0.001, g: 1, kg: 1000, ton: 1000000,
                oz: 28.3495, lbs: 453.592, lb: 453.592,
                ons: 100,
            },
            // Volume (base: liter)
            volume: {
                ml: 0.001, l: 1, liter: 1, gal: 3.78541, gallon: 3.78541,
                cc: 0.001,
            },
            // Digital (base: byte)
            digital: {
                b: 1, byte: 1, kb: 1024, mb: 1024**2, gb: 1024**3, tb: 1024**4,
            },
            // Waktu (base: detik)
            time: {
                detik: 1, s: 1, sec: 1, second: 1,
                menit: 60, min: 60, minute: 60,
                jam: 3600, h: 3600, hour: 3600,
                hari: 86400, day: 86400,
                minggu: 604800, week: 604800,
                bulan: 2592000, month: 2592000,
                tahun: 31536000, year: 31536000,
            },
            // Luas (base: m²)
            area: {
                'cm2': 0.0001, 'm2': 1, 'km2': 1000000, 'ha': 10000, 'hektar': 10000,
                'are': 100, 'ft2': 0.092903, 'acre': 4046.86,
            },
        };

        // Suhu (special case)
        const tempConvert = (val, from, to) => {
            let celsius;
            if (from === 'c' || from === 'celsius') celsius = val;
            else if (from === 'f' || from === 'fahrenheit') celsius = (val - 32) * 5/9;
            else if (from === 'k' || from === 'kelvin') celsius = val - 273.15;
            else return null;

            if (to === 'c' || to === 'celsius') return celsius;
            if (to === 'f' || to === 'fahrenheit') return celsius * 9/5 + 32;
            if (to === 'k' || to === 'kelvin') return celsius + 273.15;
            return null;
        };

        // Cek suhu dulu
        const tempUnits = ['c', 'f', 'k', 'celsius', 'fahrenheit', 'kelvin'];
        if (tempUnits.includes(fromUnit) && tempUnits.includes(toUnit)) {
            const result = tempConvert(value, fromUnit, toUnit);
            if (result !== null) {
                return message.reply(
                    `📐 *KONVERSI SATUAN*\n\n` +
                    `🌡️ ${value} ${fromUnit.toUpperCase()} = *${result.toFixed(2)} ${toUnit.toUpperCase()}*`
                );
            }
        }

        // Cari kategori yang cocok
        let result = null;
        let category = '';

        for (const [cat, units] of Object.entries(conversions)) {
            if (units[fromUnit] !== undefined && units[toUnit] !== undefined) {
                // Convert: value * (from_base / to_base)
                result = value * units[fromUnit] / units[toUnit];
                category = cat;
                break;
            }
        }

        if (result === null) {
            return message.reply(`❌ Satuan "${fromUnit}" atau "${toUnit}" tidak dikenali.\nKetik *!konversi* untuk lihat satuan yang didukung.`);
        }

        const categoryEmoji = {
            length: '📏', weight: '⚖️', volume: '🧪',
            digital: '💾', time: '⏱️', area: '📐',
        };

        // Format angka
        const formatted = result < 0.01 || result > 999999
            ? result.toExponential(4)
            : result.toLocaleString('id-ID', { maximumFractionDigits: 6 });

        message.reply(
            `📐 *KONVERSI SATUAN*\n\n` +
            `${categoryEmoji[category] || '📐'} ${value.toLocaleString('id-ID')} ${fromUnit.toUpperCase()} = *${formatted} ${toUnit.toUpperCase()}*`
        );
    },
};
