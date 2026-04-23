import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import database as db

log = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/data")
async def get_data(user_id: int = 0):
    user = await db.get_user(user_id) if user_id else None
    balance = user.get("balance", 0) if user else 0
    
    categories = await db.get_categories()
    
    products = []
    for cat in categories:
        cat_prods = await db.get_products(category_id=cat["id"])
        cat_name = cat["name"].lower()
        
        for p in cat_prods:
            p_name_lower = p["name"].lower()
            domain = "example.com"
            
            if "netflix" in p_name_lower:
                domain = "netflix.com"
            elif "spotify" in p_name_lower:
                domain = "spotify.com"
            elif "prime" in p_name_lower:
                domain = "primevideo.com"
            elif "youtube" in p_name_lower:
                domain = "youtube.com"
            elif "canva" in p_name_lower:
                domain = "canva.com"
            elif "chatgpt" in p_name_lower or "openai" in p_name_lower:
                domain = "chatgpt.com"
            elif "valorant" in p_name_lower:
                domain = "playvalorant.com"
            elif "disney" in p_name_lower:
                domain = "disneyplus.com"
                
            if domain != "example.com":
                logo_html = f'<img src="https://www.google.com/s2/favicons?domain={domain}&sz=128" alt="{domain}" style="width:100%; height:100%; object-fit:contain; border-radius: 8px;">'
            else:
                logo_html = "🛍️" 

            price = p["price"]
            if user and user.get("is_reseller") and p.get("reseller_price"):
                price = p["reseller_price"]
                
            products.append({
                "id": p["id"],
                "category_id": cat["id"],
                "name": p["name"],
                "price": price,
                "stock": p["stock"],
                "icon": logo_html
            })
            
    return {
        "balance": balance,
        "categories": [{"id": c["id"], "name": c["name"]} for c in categories],
        "products": products
    }

@app.get("/api/history")
async def get_history(user_id: int = 0):
    if not user_id:
        return {"orders": []}
        
    orders = await db.get_user_orders(user_id, limit=50)
    history = []
    
    for o in orders:
        history.append({
            "id": o["id"],
            "code": o["order_code"],
            "product_name": o["product_name"],
            "qty": o["qty"],
            "unit_price": o["unit_price"],
            "total_price": o["total_price"],
            "status": o["status"],
            "result_data": o["result_data"],
            "created_at": o["created_at"]
        })
        
    return {"orders": history}

from pydantic import BaseModel
import httpx
from config import BOT_TOKEN

class OrderItem(BaseModel):
    product_id: int
    qty: int

class CheckoutRequest(BaseModel):
    user_id: int
    items: list[OrderItem]
    payment_method: str = "balance"

bot_instance = None # Will be set by main.py

@app.post("/api/checkout")
async def checkout(req: CheckoutRequest):
    if not bot_instance:
        raise HTTPException(status_code=500, detail="Bot not initialized")
        
    user = await db.get_user(req.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    total_cost = 0
    order_details = []
    
    # Calculate costs
    for item in req.items:
        p = await db.get_product(item.product_id)
        if not p or p["stock"] < item.qty:
            raise HTTPException(status_code=400, detail=f"Stok {p['name'] if p else 'produk'} tidak cukup")
            
        price = p["price"]
        if item.qty >= (p.get("wholesale_min_qty") or 999) and p.get("wholesale_price"):
            price = p["wholesale_price"]
        elif user.get("is_reseller") and p.get("reseller_price"):
            price = p["reseller_price"]
            
        total_cost += price * item.qty
        order_details.append({"prod": p, "qty": item.qty, "price": price})
        
    if req.payment_method == "balance" and user.get("balance", 0) < total_cost:
        raise HTTPException(status_code=400, detail="Saldo tidak mencukupi")
        
    # Process orders based on method
    if req.payment_method == "qris":
        order_ids = []
        receipt_items = ""
        for item in order_details:
            p = item["prod"]
            qty = item["qty"]
            
            order = await db.create_order(
                user_id=req.user_id, product_id=p["id"],
                product_name=p["name"], qty=qty, unit_price=item["price"]
            )
            # Mark as pending_qris, stock won't be deducted until admin approves
            await db.update_order_status(order["id"], "pending_qris", payment_proof="")
            order_ids.append(str(order["id"]))
            receipt_items += f"🔹 *{p['name']}* (x{qty})\n"
            
        joined_ids = ",".join(order_ids)
        
        # Send QRIS to user via Telegram
        from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        from config import QRIS_PATH
        import os
        import messages as msg
        
        text = (
            f"🧾 *INVOICE PEMBELIAN (QRIS)*\n\n"
            f"{receipt_items}\n"
            f"💰 Total Tagihan: *Rp {total_cost:,.0f}*\n\n"
            f"Silakan scan kode QRIS di atas untuk melakukan transfer sejumlah tagihan.\n"
            f"⚠️ Pastikan transfer *sesuai nominal* agar pesanan dapat diproses.\n\n"
            f"Tekan tombol di bawah untuk mengirim bukti transfer."
        )
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("📤 Upload Bukti Transfer", callback_data=f"qrisproof_{joined_ids}")]])
        
        try:
            if os.path.exists(QRIS_PATH):
                with open(QRIS_PATH, "rb") as f:
                    await bot_instance.send_photo(chat_id=req.user_id, photo=f, caption=msg._e(text), parse_mode="MarkdownV2", reply_markup=markup)
            else:
                await bot_instance.send_message(chat_id=req.user_id, text=msg._e(text), parse_mode="MarkdownV2", reply_markup=markup)
        except Exception as e:
            log.error("Failed sending QRIS receipt: %s", e)
            
        return {"status": "ok_qris"}

    else:
        # BALANCE FLOW (Original)
        await db.deduct_balance(req.user_id, total_cost)
        
        import io
        import messages as msg
        from telegram import InputFile
        from config import ADMIN_WA, BOT_USERNAME, STORE_NAME
        
        for item in order_details:
            p = item["prod"]
            qty = item["qty"]
            
            order = await db.create_order(
                user_id=req.user_id, product_id=p["id"],
                product_name=p["name"], qty=qty, unit_price=item["price"]
            )
            await db.update_order_status(order["id"], "paid", payment_proof="balance_webapp")
            
            accounts = await db.take_accounts(p["id"], qty)
            if accounts:
                result_data = "\n".join(accounts)
                await db.complete_order(order["id"], result_data)
                
                # 1) Send .txt file
                filename = f"{req.user_id}-{order['order_code']}.txt"
                txt_file = io.BytesIO(result_data.encode("utf-8"))
                txt_file.name = filename
                try:
                    await bot_instance.send_document(
                        chat_id=req.user_id,
                        document=InputFile(txt_file, filename=filename),
                        caption=f"📄 Data akun pesanan `{order['order_code']}`",
                        parse_mode="MarkdownV2"
                    )
                except Exception as e:
                    log.error("Failed sending txt file: %s", e)
                
                # 2) Send receipt
                receipt_text = msg.order_completed_msg(order, result_data, "balance")
                try:
                    await bot_instance.send_message(chat_id=req.user_id, text=receipt_text, parse_mode="MarkdownV2")
                except Exception as e:
                    log.error("Failed sending receipt: %s", e)
            else:
                try:
                    await bot_instance.send_message(
                        chat_id=req.user_id,
                        text=f"❌ Stok {msg._e(p['name'])} habis di server\\. Hubungi admin\\.",
                        parse_mode="MarkdownV2"
                    )
                except Exception as e:
                    log.error("Failed sending out-of-stock msg: %s", e)
                    
        # 3) Send CS contact (once at the end)
        cs_wa_link = f"https://wa.me/{ADMIN_WA}" if ADMIN_WA else ""
        cs_tg_link = f"https://t.me/{BOT_USERNAME}"
        contact_text = f"Telegram\n{STORE_NAME} CS\n\nHubungi admin jika ada masalah:\n"
        if cs_wa_link:
            contact_text += f"📱 WA: {cs_wa_link}\n"
        contact_text += f"💬 Telegram: {cs_tg_link}"
        try:
            await bot_instance.send_message(chat_id=req.user_id, text=contact_text, disable_web_page_preview=False)
        except Exception as e:
            log.error("Failed sending CS contact: %s", e)
            
        return {"status": "ok_balance"}

class ActionRequest(BaseModel):
    user_id: int
    action: str

@app.post("/api/action")
async def trigger_action(req: ActionRequest):
    if req.action == "topup" and bot_instance:
        try:
            await bot_instance.send_message(
                chat_id=req.user_id,
                text="Untuk melakukan pengisian saldo, silakan ketik /start lalu pilih menu *💰 Saldo*.",
                parse_mode="MarkdownV2"
            )
        except Exception:
            pass
    return {"status": "ok"}

# Mount static files for the webapp frontend
webapp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webapp")
if os.path.exists(webapp_dir):
    app.mount("/", StaticFiles(directory=webapp_dir, html=True), name="webapp")
