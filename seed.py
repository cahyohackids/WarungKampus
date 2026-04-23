"""
seed.py — Isi database dengan data contoh untuk testing
Jalankan sekali: python seed.py
"""
import asyncio
import database as db


async def seed():
    await db.init_db()
    print("🌱 Seeding database...")

    # Categories
    cat1 = await db.add_category("Netflix & Streaming", "🎬", "Berbagai layanan streaming premium")
    cat2 = await db.add_category("Music Premium", "🎵", "Layanan musik tanpa iklan")
    cat3 = await db.add_category("Productivity", "💼", "Aplikasi kerja dan produktivitas")
    cat4 = await db.add_category("Canva Pro", "🎨", "Design grafis profesional")
    cat5 = await db.add_category("AI Tools", "🤖", "Alat kecerdasan buatan premium")
    print(f"✅ {5} kategori dibuat")

    # Products
    p1 = await db.add_product(cat1, "Netflix Private 1 Bulan", "Akun Netflix private profile",
                               price=15000, duration="1 Bulan",
                               wholesale_price=13000, wholesale_min_qty=5)
    p2 = await db.add_product(cat1, "Netflix Private 3 Bulan", "Akun Netflix private profile",
                               price=40000, duration="3 Bulan")
    p3 = await db.add_product(cat2, "Spotify Premium 1 Bulan", "Akun Spotify individual",
                               price=12000, duration="1 Bulan",
                               wholesale_price=10000, wholesale_min_qty=5)
    p4 = await db.add_product(cat4, "Canva Pro 1 Bulan", "Canva Pro akun team invite",
                               price=8000, duration="1 Bulan")
    p5 = await db.add_product(cat5, "ChatGPT Plus 1 Bulan", "Akun ChatGPT Plus premium",
                               price=75000, duration="1 Bulan")
    print(f"✅ 5 produk dibuat")

    # Sample accounts (demo)
    await db.add_accounts_bulk(p1, [
        "netflix_demo1@gmail.com:pass123",
        "netflix_demo2@gmail.com:pass456",
        "netflix_demo3@gmail.com:pass789",
    ])
    await db.add_accounts_bulk(p3, [
        "spotify_demo1@gmail.com:pass123",
        "spotify_demo2@gmail.com:pass456",
    ])
    await db.add_accounts_bulk(p4, [
        "canva_team_invite_link_1: https://canva.com/invite/abc123",
        "canva_team_invite_link_2: https://canva.com/invite/def456",
    ])
    print("✅ Sample akun ditambahkan")
    print("\n🎉 Seeding selesai! Jalankan: python main.py")


if __name__ == "__main__":
    asyncio.run(seed())
