import json
import os
import datetime
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Configuration
BOT_TOKEN = "8622209396:AAFJs_YjJEcj0Ai8GhR1v7KUp6NicfqF-jY"
ADMIN_ID = 6627943855
WEB_APP_URL = "doitienban.duckdns.org"

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Ensure data directory exists
if not os.path.exists("data"):
    os.makedirs("data", exist_ok=True)


# Helper Functions to Handle JSON Files
def load_json(filepath, default):
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def save_user_info(user):
    users = load_json("data/users.json", {})
    user_id = str(user.id)

    if user_id not in users:
        date_joined = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        date_joined = users[user_id].get(
            "date_joined", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    users[user_id] = {
        "id": user.id,
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "username": user.username or "",
        "date_joined": date_joined,
    }
    save_json("data/users.json", users)


# Middleware Check for Blocked Users
async def is_blocked(update: Update) -> bool:
    user = update.effective_user
    if not user:
        return False

    blocked_list = load_json("data/blocked.json", [])
    if user.id in blocked_list and user.id != ADMIN_ID:
        await update.effective_message.reply_text(
            "🚫 *Bạn đã bị chặn sử dụng bot này!*", parse_mode="Markdown"
        )
        return True
    return False


# Handlers
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_blocked(update):
        return

    user = update.effective_user
    save_user_info(user)

    # ADMIN MENU
    if user.id == ADMIN_ID:
        admin_menu = (
            "👑 *BẢNG ĐIỀU KHIỂN QUẢN TRỊ VIÊN*\n"
            "───────────────────\n"
            "📊 *Thống kê hệ thống:*\n"
            "👉 `/stats` - Xem tổng quan người dùng & đơn hàng\n\n"
            "📢 *Gửi thông báo & Phản hồi:*\n"
            "👉 `/all <Nội dung>` - Bắn thông báo toàn bộ\n"
            "👉 `/send <ID> <Nội dung>` - Gửi riêng cho 1 khách\n"
            "👉 `/reply <ID> <Nội dung>` - Trả lời nhanh cho khách\n\n"
            "🛒 *Quản lý Đơn hàng:*\n"
            "👉 `/orders` - Xem 10 đơn hàng mới nhất\n"
            "👉 `/update <Mã_Đơn> <Trạng_Thái>` - Đổi trạng thái đơn (VD: `/update ORD123 Completed`)\n\n"
            "👥 *Quản lý Người dùng:*\n"
            "👉 `/users` - Danh sách khách hàng\n"
            "👉 `/block <ID>` | `/unblock <ID>` | `/blocked` - Quản lý chặn"
        )
        await update.message.reply_text(admin_menu, parse_mode="Markdown")
        return

    # USER MENU
    reply_text = (
        f"👋 *Xin chào {user.first_name}!*\n"
        "Chào mừng bạn đến với Ứng dụng Mua Bán Dịch Vụ Tự Động.\n\n"
        "🚀 Bấm nút bên dưới để mở Mini App chọn dịch vụ và thanh toán!"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🛍️ MỞ MINI APP MUA GÓI", web_app={"url": WEB_APP_URL}
            )
        ],
        [
            InlineKeyboardButton(
                "📋 TRA CỨU ĐƠN HÀNG", callback_data="check_order_guide"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        reply_text, reply_markup=reply_markup, parse_mode="Markdown"
    )


# ADMIN COMMANDS
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    users = load_json("data/users.json", {})
    orders = load_json("data/orders.json", {})

    total_users = len(users)
    total_orders = len(orders)
    total_revenue = 0

    for ord_info in orders.values():
        status = str(ord_info.get("status", "")).lower()
        if status in ["completed", "thành công"]:
            total_revenue += int(ord_info.get("price", 0))

    msg = (
        "📈 *BÁO CÁO THỐNG KÊ HỆ THỐNG*\n"
        "───────────────────\n"
        f"👥 Tổng khách hàng: *{total_users}*\n"
        f"📦 Tổng số đơn hàng: *{total_orders}*\n"
        f"💰 Doanh thu (Đơn completed): *{total_revenue:,}đ*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    orders = load_json("data/orders.json", {})
    recent_keys = list(orders.keys())[-10:]

    msg = "🛒 *10 ĐƠN HÀNG MỚI NHẤT*\n───────────────────\n"

    if not recent_keys:
        msg += "Chưa có đơn hàng nào."
    else:
        for ord_id in reversed(recent_keys):
            ord_info = orders[ord_id]
            price = int(ord_info.get("price", 0))
            msg += (
                f"📦 Mã: `{ord_id}` | Khách: `{ord_info.get('user_id')}`\n"
                f"💵 Gói: *{ord_info.get('package_name')}* ({price:,}đ)\n"
                f"🚦 Trạng thái: *{ord_info.get('status')}*\n"
                "───────────\n"
            )

    await update.message.reply_text(msg, parse_mode="Markdown")


async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "❌ *Cú pháp sai!* Dùng: `/update <Mã_Đơn> <Trạng_thái>`\nVí dụ: `/update ORD101 Completed`",
            parse_mode="Markdown",
        )
        return

    order_id = args[0].upper()
    new_status = " ".join(args[1:])

    orders = load_json("data/orders.json", {})

    if order_id in orders:
        orders[order_id]["status"] = new_status
        save_json("data/orders.json", orders)

        await update.message.reply_text(
            f"✅ Đã cập nhật đơn hàng `{order_id}` sang trạng thái: *{new_status}*",
            parse_mode="Markdown",
        )

        customer_id = orders[order_id].get("user_id")
        if customer_id:
            customer_msg = (
                "🔔 *CẬP NHẬT TRẠNG THÁI ĐƠN HÀNG*\n"
                "───────────────────\n"
                f"📦 Mã đơn: `{order_id}`\n"
                f"🚦 Trạng thái mới: *{new_status}*"
            )
            try:
                await context.bot.send_message(
                    chat_id=customer_id, text=customer_msg, parse_mode="Markdown"
                )
            except Exception:
                pass
    else:
        await update.message.reply_text(
            f"❌ Không tìm thấy mã đơn `{order_id}`.", parse_mode="Markdown"
        )


async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    users = load_json("data/users.json", {})
    total = len(users)

    msg = f"👥 *DANH SÁCH NGƯỜI DÙNG ({total})*\n───────────────────\n"
    if total == 0:
        msg += "Chưa có dữ liệu."
    else:
        for idx, (uid, u) in enumerate(users.items(), 1):
            name = f"{u.get('first_name', '')} {u.get('last_name', '')}".strip()
            username = f"@{u['username']}" if u.get("username") else "N/A"
            msg += f"{idx}. ID: `{uid}` | {name} | {username}\n"
            if idx >= 50:
                msg += "...\n_(Chỉ hiển thị tối đa 50 người dùng gần nhất)_"
                break

    await update.message.reply_text(msg, parse_mode="Markdown")


async def blocked_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    blocked = load_json("data/blocked.json", [])
    msg = f"🚫 *DANH SÁCH ID BỊ CHẶN ({len(blocked)})*\n───────────────────\n"
    if not blocked:
        msg += "Không có ai bị chặn."
    else:
        for idx, b_id in enumerate(blocked, 1):
            msg += f"{idx}. ID: `{b_id}`\n"

    await update.message.reply_text(msg, parse_mode="Markdown")


async def send_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    message_content = " ".join(context.args).strip()
    if not message_content:
        await update.message.reply_text(
            "❌ Thiếu nội dung! Cú pháp: `/all <Nội dung>`", parse_mode="Markdown"
        )
        return

    users = load_json("data/users.json", {})
    ok, fail = 0, 0
    notice = (
        "📢 *THÔNG BÁO CHUNG TỪ HỆ THỐNG*\n───────────────────\n" + message_content
    )

    for u_id in users.keys():
        if int(u_id) == ADMIN_ID:
            continue
        try:
            await context.bot.send_message(
                chat_id=int(u_id), text=notice, parse_mode="Markdown"
            )
            ok += 1
        except Exception:
            fail += 1

    await update.message.reply_text(
        f"📊 *KẾT QUẢ GỬI THÔNG BÁO*\n\n✅ Thành công: *{ok}*\n❌ Thất bại: *{fail}*",
        parse_mode="Markdown",
    )


async def reply_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Cú pháp sai! Dùng: `/send <ID_Khách> <Nội dung>`", parse_mode="Markdown"
        )
        return

    target_id = args[0]
    msg_text = " ".join(args[1:])

    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=f"💬 *PHẢN HỒI TỪ ADMIN*\n───────────────────\n{msg_text}",
            parse_mode="Markdown",
        )
        await update.message.reply_text(
            f"✅ Đã gửi tin tới ID: `{target_id}`", parse_mode="Markdown"
        )
    except Exception:
        await update.message.reply_text(
            f"❌ Gửi thất bại tới ID: `{target_id}`", parse_mode="Markdown"
        )


async def block_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        return

    target_id_str = context.args[0].strip()
    if target_id_str.isdigit():
        target_id = int(target_id_str)
        blocked_list = load_json("data/blocked.json", [])
        if target_id not in blocked_list:
            blocked_list.append(target_id)
            save_json("data/blocked.json", blocked_list)
            await update.message.reply_text(
                f"✅ Đã chặn ID: `{target_id}`", parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"⚠️ ID `{target_id}` đã có trong danh sách chặn.",
                parse_mode="Markdown",
            )


async def unblock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        return

    target_id_str = context.args[0].strip()
    if target_id_str.isdigit():
        target_id = int(target_id_str)
        blocked_list = load_json("data/blocked.json", [])
        if target_id in blocked_list:
            blocked_list.remove(target_id)
            save_json("data/blocked.json", blocked_list)
            await update.message.reply_text(
                f"✅ Đã mở chặn ID: `{target_id}`", parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"⚠️ ID `{target_id}` không có trong danh sách bị chặn.",
                parse_mode="Markdown",
            )


# USER COMMANDS & MESSAGES
async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_blocked(update):
        return

    save_user_info(update.effective_user)
    args = context.args

    if args:
        order_id = args[0].upper()
        orders = load_json("data/orders.json", {})

        if order_id in orders:
            ord_info = orders[order_id]
            price = int(ord_info.get("price", 0))
            reply_text = (
                "📋 *THÔNG TIN HÓA ĐƠN* 📋\n\n"
                f"📦 Mã đơn: `{ord_info.get('id', order_id)}`\n"
                f"💵 Dịch vụ: *{ord_info.get('package_name')}*\n"
                f"💰 Số tiền: {price:,}đ\n"
                f"🚦 Tình trạng: *{ord_info.get('status')}*"
            )
        else:
            reply_text = "❌ Không tìm thấy mã đơn hàng. Vui lòng kiểm tra lại syntax: `/check <Mã_Đơn>`"
    else:
        reply_text = "❌ Vui lòng nhập mã đơn. Ví dụ: `/check ORD12345`"

    await update.message.reply_text(reply_text, parse_mode="Markdown")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_blocked(update):
        return

    user = update.effective_user
    save_user_info(user)
    text = update.message.text

    # Forward non-command messages from users to Admin
    if user.id != ADMIN_ID:
        forward_msg = (
            "📩 *TIN NHẮN TỪ KHÁCH HÀNG*\n"
            f"👤 Khách: `{user.id}` ({user.first_name})\n"
            f"💬 Nội dung: {text}\n\n"
            f"👉 Dùng lệnh `/reply {user.id} <Nội_dung>` để trả lời."
        )
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID, text=forward_msg, parse_mode="Markdown"
            )
        except Exception:
            pass

    warning_text = (
        "⚠️ *CẢNH BÁO:* Bot tự động không hỗ trợ trò chuyện trực tiếp!\n\n"
        "👉 Nhấn /start để mở Mini App hoặc gõ `/check <Mã_Đơn>` để kiểm tra đơn hàng."
    )
    await update.message.reply_text(warning_text, parse_mode="Markdown")


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_order_guide":
        guide_text = (
            "💡 *HƯỚNG DẪN TRA CỨU ĐƠN HÀNG*\n\n"
            "Gõ theo cú pháp: `/check <Mã_Đơn>`\n"
            "Ví dụ: `/check ORD12345`"
        )
        await query.message.reply_text(guide_text, parse_mode="Markdown")


# Main Bot Initializer
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # User & General Handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("admin", start_handler))
    app.add_handler(CommandHandler("check", check_command))

    # Admin Handlers
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("orders", orders_command))
    app.add_handler(CommandHandler("update", update_command))
    app.add_handler(CommandHandler("users", users_command))
    app.add_handler(CommandHandler("blocked", blocked_command))
    app.add_handler(CommandHandler("all", send_all_command))
    app.add_handler(CommandHandler("send", reply_user_command))
    app.add_handler(CommandHandler("reply", reply_user_command))
    app.add_handler(CommandHandler("block", block_command))
    app.add_handler(CommandHandler("unblock", unblock_command))

    # Callback & Free text Handlers
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    print("Bot đang chạy...")
    app.run_polling()


if __name__ == "__main__":
    main()
