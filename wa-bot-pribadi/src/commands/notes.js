// ============================================
//  📝 COMMAND: !notes — Catatan Cepat
//  Simpan catatan dengan tag untuk organisasi
// ============================================

const notesDb = require('../database/notesDatabase');

module.exports = {
    name: 'notes',
    description: 'Catatan cepat dengan tag. Ketik !notes untuk bantuan',
    ownerOnly: true,

    async execute(message, args, { client }) {
        const sub = args[0]?.toLowerCase();

        // === !notes (bantuan) ===
        if (!sub) {
            return message.reply(
`📝 *CATATAN CEPAT — Panduan*

▸ *!notes add [catatan]* — Simpan catatan
▸ *!notes add #kuliah Integral parsial halaman 45*
    ↳ Simpan dengan tag
▸ *!notes list* — Lihat semua catatan
▸ *!notes tag kuliah* — Filter catatan per tag
▸ *!notes cari integral* — Cari catatan
▸ *!notes hapus 1* — Hapus catatan no.1
▸ *!notes clear* — Hapus semua catatan

_💡 Pakai #tag di awal untuk mengorganisir!_`
            );
        }

        // === !notes add [catatan] ===
        if (sub === 'add' || sub === 'tambah') {
            const text = args.slice(1).join(' ');
            if (!text) {
                return message.reply('❌ Format: *!notes add [catatan]*\nContoh: !notes add #kuliah Integral parsial hal 45');
            }

            // Deteksi tag dari #hashtag
            let tag = null;
            let cleanText = text;
            const tagMatch = text.match(/^#(\S+)\s+/);
            if (tagMatch) {
                tag = tagMatch[1];
                cleanText = text.replace(tagMatch[0], '');
            }

            const total = notesDb.add(cleanText, tag);
            let reply = `✅ Catatan disimpan! (#${total})\n📝 ${cleanText}`;
            if (tag) reply += `\n🏷️ Tag: *${tag}*`;

            message.reply(reply);
        }

        // === !notes list ===
        else if (sub === 'list' || sub === 'lihat') {
            const items = notesDb.getAll();

            if (items.length === 0) {
                return message.reply('📝 Belum ada catatan.\n_Tambah: !notes add #kuliah Catatan penting_');
            }

            let msg = `📝 *SEMUA CATATAN* (${items.length})\n\n`;
            items.forEach((item, i) => {
                const tag = item.tag ? `[${item.tag}]` : '';
                const date = new Date(item.createdAt).toLocaleDateString('id-ID', {
                    day: 'numeric', month: 'short'
                });
                msg += `  ${i + 1}. ${tag ? '🏷️' + tag + ' ' : ''}${item.text}\n     _${date}_\n\n`;
            });

            message.reply(msg);
        }

        // === !notes tag [nama tag] ===
        else if (sub === 'tag') {
            const tag = args[1];
            if (!tag) return message.reply('❌ Format: *!notes tag [nama]*\nContoh: !notes tag kuliah');

            const items = notesDb.getByTag(tag);
            if (items.length === 0) {
                return message.reply(`📝 Tidak ada catatan dengan tag *${tag}*.`);
            }

            let msg = `🏷️ *Catatan Tag: ${tag}* (${items.length})\n\n`;
            items.forEach((item, i) => {
                const date = new Date(item.createdAt).toLocaleDateString('id-ID', {
                    day: 'numeric', month: 'short'
                });
                msg += `  ${i + 1}. ${item.text}\n     _${date}_\n\n`;
            });

            message.reply(msg);
        }

        // === !notes cari [keyword] ===
        else if (sub === 'cari' || sub === 'search') {
            const keyword = args.slice(1).join(' ');
            if (!keyword) return message.reply('❌ Format: *!notes cari [kata kunci]*');

            const items = notesDb.search(keyword);
            if (items.length === 0) {
                return message.reply(`🔍 Tidak ditemukan catatan yang mengandung "${keyword}".`);
            }

            let msg = `🔍 *Hasil Pencarian: "${keyword}"* (${items.length})\n\n`;
            items.forEach((item, i) => {
                const tag = item.tag ? `[${item.tag}]` : '';
                msg += `  ${i + 1}. ${tag ? '🏷️' + tag + ' ' : ''}${item.text}\n\n`;
            });

            message.reply(msg);
        }

        // === !notes hapus [nomor] ===
        else if (sub === 'hapus' || sub === 'delete') {
            const index = parseInt(args[1]) - 1;
            if (isNaN(index)) return message.reply('❌ Format: *!notes hapus [nomor]*');

            const removed = notesDb.remove(index);
            if (removed) {
                message.reply(`🗑️ Dihapus: "${removed.text}"`);
            } else {
                message.reply('❌ Nomor tidak ditemukan.');
            }
        }

        // === !notes clear ===
        else if (sub === 'clear') {
            notesDb.clearAll();
            message.reply('🧹 Semua catatan telah dihapus.');
        }
    },
};
