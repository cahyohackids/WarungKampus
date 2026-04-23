// ============================================
//  💬 COMMAND: !quote — Kutipan motivasi random
// ============================================

const QUOTES = [
    { text: 'Satu-satunya cara untuk melakukan pekerjaan hebat adalah mencintai apa yang kamu lakukan.', author: 'Steve Jobs' },
    { text: 'Kesuksesan adalah kemampuan untuk pergi dari kegagalan ke kegagalan tanpa kehilangan semangat.', author: 'Winston Churchill' },
    { text: 'Jangan menunggu. Waktunya tidak akan pernah tepat.', author: 'Napoleon Hill' },
    { text: 'Kegagalan adalah bumbu yang memberi rasa pada kesuksesan.', author: 'Truman Capote' },
    { text: 'Mulailah dari mana kamu berada. Gunakan apa yang kamu punya. Lakukan apa yang kamu bisa.', author: 'Arthur Ashe' },
    { text: 'Hidup ini 10% apa yang terjadi padamu dan 90% bagaimana kamu meresponsnya.', author: 'Charles R. Swindoll' },
    { text: 'Pendidikan adalah senjata paling ampuh yang bisa kamu gunakan untuk mengubah dunia.', author: 'Nelson Mandela' },
    { text: 'Kamu tidak harus menjadi hebat untuk memulai, tapi kamu harus memulai untuk menjadi hebat.', author: 'Zig Ziglar' },
    { text: 'Jatuh itu biasa. Bangkit itu luar biasa.', author: 'Pepatah' },
    { text: 'Waktu terbaik untuk menanam pohon adalah 20 tahun yang lalu. Waktu terbaik kedua adalah sekarang.', author: 'Peribahasa Cina' },
    { text: 'Satu langkah kecil hari ini bisa jadi lompatan besar di masa depan.', author: 'Unknown' },
    { text: 'Disiplin adalah jembatan antara tujuan dan pencapaian.', author: 'Jim Rohn' },
    { text: 'Yang membedakanmu bukan keadaanmu, tapi pilihanmu.', author: 'J.K. Rowling' },
    { text: 'Jadilah perubahan yang ingin kamu lihat di dunia ini.', author: 'Mahatma Gandhi' },
    { text: 'Impian tidak bekerja kecuali kamu yang bekerja.', author: 'John C. Maxwell' },
    { text: 'Rintangan adalah hal menakutkan yang kamu lihat ketika kamu mengalihkan pandangan dari tujuanmu.', author: 'Henry Ford' },
    { text: 'Sesuatu yang belum dikerjakan seringkali tampak mustahil. Kita baru yakin kalau kita telah berhasil melakukannya dengan baik.', author: 'Evelyn Underhill' },
    { text: 'Kerja keras mengalahkan bakat ketika bakat tidak bekerja keras.', author: 'Tim Notke' },
    { text: 'Jangan biarkan apa yang tidak bisa kamu lakukan menghalangi apa yang bisa kamu lakukan.', author: 'John Wooden' },
    { text: 'Orang yang berhasil di dunia ini adalah orang-orang yang bangkit dan mencari keadaan yang mereka inginkan.', author: 'George Bernard Shaw' },
];

module.exports = {
    name: 'quote',
    description: 'Dapatkan kutipan motivasi secara acak',
    ownerOnly: false,

    async execute(message, args, { client }) {
        const q = QUOTES[Math.floor(Math.random() * QUOTES.length)];

        const msg = 
`╔══════════════════════════╗
║      💬 *MOTIVASI*  💬       ║
╚══════════════════════════╝

_"${q.text}"_

— *${q.author}*

━━━━━━━━━━━━━━━━━━━━━━━━━
💪 Semangat hari ini!`;

        message.reply(msg);
    },
};
