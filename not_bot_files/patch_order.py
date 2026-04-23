import re

with open("/Users/al-birra/Documents/cahyo/warungkampus/handlers/order.py", "r") as f:
    content = f.read()

# Replace states
content = content.replace("UPLOAD_PROOF = 3", "UPLOAD_PROOF = 3\nTYPING_QTY = 4")

# Redesign start_order
start_order_new = """async def start_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split("_")[2])  # order_start_<id>
    product = await db.get_product(product_id)

    if not product or product["stock"] <= 0:
        await query.answer("❌ Stok produk habis!", show_alert=True)
        return ConversationHandler.END

    ctx.user_data[CTX_PRODUCT_ID] = product_id
    ctx.user_data[CTX_PRICE] = product["price"]
    ctx.user_data[CTX_QTY] = 1

    user_data = await db.get_user(update.effective_user.id)
    if user_data and user_data.get("is_reseller") and product.get("reseller_price"):
        ctx.user_data[CTX_PRICE] = product["reseller_price"]

    max_qty = product["stock"]

    await query.message.reply_text(
        msg.order_summary_msg(product, 1, user_data or {}),
        parse_mode="MarkdownV2",
        reply_markup=kb.order_checkout_kb(1, max_qty)
    )
    return SELECTING_QTY
"""

# Redesign select_qty
select_qty_new = """async def select_qty(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "order_cancel":
        await query.edit_message_text("❌ Order dibatalkan\\.", parse_mode="MarkdownV2")
        ctx.user_data.clear()
        return ConversationHandler.END

    product_id = ctx.user_data.get(CTX_PRODUCT_ID)
    product = await db.get_product(product_id)
    if not product:
        return ConversationHandler.END
        
    user_data = await db.get_user(update.effective_user.id)
    max_qty = product["stock"]

    # Handle payments
    if data in ["pay_qris", "pay_balance"]:
        qty = ctx.user_data.get(CTX_QTY, 1)
        price = product["price"]
        if qty >= (product.get("wholesale_min_qty") or 999) and product.get("wholesale_price"):
            price = product["wholesale_price"]
        elif user_data and user_data.get("is_reseller") and product.get("reseller_price"):
            price = product["reseller_price"]
        
        total = price * qty
        
        if data == "pay_balance":
            if user_data.get("balance", 0) < total:
                await query.answer("Kouta saldo tidak mencukupi!", show_alert=True)
                return SELECTING_QTY
                
            # Process balance payment directly
            order = await db.create_order(
                user_id=update.effective_user.id, product_id=product_id,
                product_name=product["name"], qty=qty, unit_price=price
            )
            # deduct balance and approve
            await db.deduct_balance(update.effective_user.id, total)
            await db.update_order_status(order["id"], "paid", payment_proof="balance")
            # Complete order logic is same as admin_approve_order
            accounts = await db.take_accounts(order["product_id"], order["qty"])
            if not accounts:
                await query.edit_message_text("❌ Stok akun habis di server! Silakan hubungi admin.", parse_mode="MarkdownV2")
                return ConversationHandler.END
            result_data = "\\n".join(accounts)
            await db.complete_order(order["id"], result_data)
            await query.edit_message_text(msg.order_completed_msg(order, result_data), parse_mode="MarkdownV2")
            ctx.user_data.clear()
            return ConversationHandler.END
            
        else:
            # Pay using QRIS
            order = await db.create_order(
                user_id=update.effective_user.id, product_id=product_id,
                product_name=product["name"], qty=qty, unit_price=price
            )
            ctx.user_data[CTX_ORDER_ID] = order["id"]
            
            # Show QRIS (mimic confirm_payment)
            invoice_text = msg.invoice_msg(order)
            try:
                import os
                if os.path.exists(QRIS_PATH):
                    with open(QRIS_PATH, "rb") as qris_file:
                        await query.message.reply_photo(
                            photo=qris_file, caption=invoice_text, parse_mode="MarkdownV2",
                            reply_markup=kb.cancel_order_kb(order["id"])
                        )
                else:
                    raise FileNotFoundError
            except FileNotFoundError:
                await query.message.reply_text(
                    invoice_text + "\\n\\n📷 \\\\[Upload QRIS kamu di folder assets/qris\\\\.jpg\\\\]",
                    parse_mode="MarkdownV2", reply_markup=kb.cancel_order_kb(order["id"])
                )
            await query.message.reply_text("📸 *Kirim foto bukti transfer di sini* setelah membayar\\\\.", parse_mode="MarkdownV2")
            return UPLOAD_PROOF

    # Handle quantity modifications
    current_qty = ctx.user_data.get(CTX_QTY, 1)
    if data.startswith("qty_"):
        val = data.split("_")[1]
        if val == "custom":
            msg_sent = await query.message.reply_text("Silakan ketik angka jumlah pesanan:")
            ctx.user_data["prompt_msg_id"] = msg_sent.message_id
            return TYPING_QTY
        elif val == "all":
            current_qty = max_qty
        else:
            current_qty += int(val)
            
    # Clamp quantity
    if current_qty < 1:
        current_qty = 1
    if current_qty > max_qty:
        current_qty = max_qty
        
    ctx.user_data[CTX_QTY] = current_qty

    # Update message if modified
    try:
        await query.edit_message_text(
            msg.order_summary_msg(product, current_qty, user_data or {}),
            parse_mode="MarkdownV2",
            reply_markup=kb.order_checkout_kb(current_qty, max_qty)
        )
    except Exception:
        pass
        
    return SELECTING_QTY

async def typing_qty_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        qty = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Harap masukkan *angka*.", parse_mode="MarkdownV2")
        return TYPING_QTY
        
    product_id = ctx.user_data.get(CTX_PRODUCT_ID)
    product = await db.get_product(product_id)
    max_qty = product["stock"]
    
    if qty < 1:
        qty = 1
    if qty > max_qty:
        qty = max_qty
        
    ctx.user_data[CTX_QTY] = qty
    
    # Try to edit the older prompt
    user_data_db = await db.get_user(update.effective_user.id)
    prompt_id = ctx.user_data.get("prompt_msg_id")
    if prompt_id:
        try:
            await ctx.bot.delete_message(chat_id=update.effective_chat.id, message_id=prompt_id)
        except Exception:
            pass
            
    await update.message.reply_text(
        msg.order_summary_msg(product, qty, user_data_db or {}),
        parse_mode="MarkdownV2",
        reply_markup=kb.order_checkout_kb(qty, max_qty)
    )
    return SELECTING_QTY
"""

# Regex substitute the old functions
content = re.sub(
    r"async def start_order.*?return SELECTING_QTY\n",
    start_order_new,
    content,
    flags=re.DOTALL
)

content = re.sub(
    r"async def select_qty.*?return CONFIRM_ORDER\n",
    select_qty_new,
    content,
    flags=re.DOTALL
)

# And update get_conversation_handler 
handler_old = r"""        states={
            SELECTING_QTY: \[
                CallbackQueryHandler\(select_qty, pattern=r"\^\(qty_\\d\+\|order_cancel\)\$"\),
            \],
            CONFIRM_ORDER: \["""
handler_new = r"""        states={
            SELECTING_QTY: [
                CallbackQueryHandler(select_qty, pattern=r"^(qty_.*|pay_.*|order_cancel)$"),
            ],
            TYPING_QTY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, typing_qty_handler)
            ],
            CONFIRM_ORDER: ["""
content = re.sub(handler_old, handler_new, content, flags=re.DOTALL)

with open("/Users/al-birra/Documents/cahyo/warungkampus/handlers/order.py", "w") as f:
    f.write(content)
