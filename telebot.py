from telegram import (
    InlineKeyboardMarkup,
    Update,
    ReplyKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from pymongo import MongoClient
import datetime
import os
from telegram import InlineKeyboardButton

# Mongo Config
MONGO_URI = os.getenv("MONGO_URI") or "mongodb://localhost:27017"
DB_NAME = "deeper_systems_bot"
COLLECTION_NAME = "users"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users = db[COLLECTION_NAME]
# client.drop_database(DB_NAME)

# Conversations States
(MAINMENU_STATE, CKBALANCE, DEPOSIT, WITHDRAW, WITHDRAW_STATE, DEPOSIT_STATE, BACK, CANCEL, CONFIRM, CONFIRM_STATE) = range(10)

DEPOSIT_OP = 1
WITHDRAW_OP = 2

# Inline Keyboards
main_options_keyboard = [
    [
        InlineKeyboardButton("Check Balance", callback_data=str(CKBALANCE)),
    ],
    [
        InlineKeyboardButton("Deposit", callback_data=str(DEPOSIT)),
    ],
    [
        InlineKeyboardButton("Withdraw", callback_data=str(WITHDRAW)),
    ]
]

back_keyboard = [
    [
        InlineKeyboardButton("Back", callback_data=str(BACK)),
    ]
]

confirm_cancel_keyboard = [
    [
        InlineKeyboardButton("Confirm", callback_data=str(CONFIRM)),
        InlineKeyboardButton("Cancel", callback_data=str(CANCEL)),
    ]
]

# Messages
main_menu_msg = "Select an option:"

def new_user(user):
    user_data = {
        "_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "balance": 0,
        "deposits": [],
        "withdraws": [],
    }
    users.insert_one(user_data)

def add_deposit(user_id, amount):
    """Adiciona um depósito ao usuário e atualiza o saldo."""
    users.update_one(
        {"_id": user_id},
        {
            "$inc": {"balance": amount},
            "$push": {"deposits": {"amount": amount, "timestamp": datetime.datetime.utcnow()}}
        }
    )

def add_withdraw(user_id, amount):
    """Registra um saque se o saldo for suficiente."""
    user = users.find_one({"_id": user_id})
    
    if user and user["balance"] >= amount:
        users.update_one(
            {"_id": user_id},
            {
                "$inc": {"balance": -amount},
                "$push": {"withdraws": {"amount": amount, "timestamp": datetime.datetime.utcnow()}}
            }
        )
        return True
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    db_user = users.find_one({"_id": user.id})
    if not db_user:
        new_user(user)
    context.user_data["user_info"] = db_user
    reply_markup = InlineKeyboardMarkup(main_options_keyboard)
    await update.message.reply_text(
        main_menu_msg,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    return MAINMENU_STATE

async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    reply_markup = InlineKeyboardMarkup(main_options_keyboard)
    user_info = context.user_data["user_info"] = users.find_one({"_id": query.from_user.id})
    balance = user_info["balance"]
    last_deposit = user_info["deposits"][-1] if user_info["deposits"] else None
    last_withdraw = user_info["withdraws"][-1] if user_info["withdraws"] else None

    response = f"<b>Your balance</b>: {balance}\n"
    if last_deposit:
        response += f"<b>Last deposit</b>: {last_deposit['amount']} on {last_deposit['timestamp']}\n"
    if last_withdraw:
        response += f"<b>Last withdraw</b>: {last_withdraw['amount']} on {last_withdraw['timestamp']}\n"

    response += "\nSelect an option:"
    await query.edit_message_text(
        response,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    return MAINMENU_STATE

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    user_info = context.user_data["user_info"]
    if user_info["balance"] == 0:
        await query.edit_message_text(
            "You have no balance to withdraw.",
            reply_markup=InlineKeyboardMarkup(back_keyboard),
            parse_mode=ParseMode.HTML
        )
        return MAINMENU_STATE

    reply_markup = InlineKeyboardMarkup(back_keyboard)
    await query.edit_message_text(
        "Please enter the deposit amount:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    return WITHDRAW_STATE

async def make_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = int(update.message.text)
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        user_info = context.user_data["user_info"] = users.find_one({"_id": update.message.from_user.id})
        if user_info["balance"] < amount:
            await update.message.reply_text(
                "Insufficient balance.",
                parse_mode=ParseMode.HTML
            )
            return WITHDRAW_STATE
        context.user_data["operation"] = WITHDRAW_OP
        context.user_data["amount"] = amount
        reply_markup = InlineKeyboardMarkup(confirm_cancel_keyboard)
        await update.message.reply_text(
            f"Confirm withdraw of {amount}?",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        return CONFIRM_STATE
    except ValueError:
        await update.message.reply_text(
            "Invalid amount. Please enter a valid number.",
            parse_mode=ParseMode.HTML
        )
        return WITHDRAW_STATE

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    reply_markup = InlineKeyboardMarkup(back_keyboard)
    await query.edit_message_text(
        "Please enter the deposit amount:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    return DEPOSIT_STATE

async def make_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:    
    try:
        amount = int(update.message.text)
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        context.user_data["operation"] = DEPOSIT_OP
        context.user_data["amount"] = amount
        reply_markup = InlineKeyboardMarkup(confirm_cancel_keyboard)
        await update.message.reply_text(
            f"Confirm deposit of {amount}?",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        return CONFIRM_STATE
    except ValueError:
        await update.message.reply_text(
            "Invalid amount. Please enter a valid number.",
            parse_mode=ParseMode.HTML
        )
        return DEPOSIT_STATE

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_info = context.user_data["user_info"]
    amount = context.user_data["amount"]
    print(context.user_data)
    if context.user_data["operation"] == DEPOSIT_OP:
        add_deposit(user_info["_id"], amount)
        await query.edit_message_text(
            f"Deposit of {amount} confirmed.",
            reply_markup=InlineKeyboardMarkup(main_options_keyboard),
            parse_mode=ParseMode.HTML
        )
        return MAINMENU_STATE
    elif context.user_data["operation"] == WITHDRAW_OP:
        add_withdraw(user_info["_id"], amount)
        await query.edit_message_text(
            f"Withdrawal of {amount} confirmed.",
            reply_markup=InlineKeyboardMarkup(main_options_keyboard),
            parse_mode=ParseMode.HTML
        )
        return MAINMENU_STATE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Operation canceled.",
        reply_markup=InlineKeyboardMarkup(main_options_keyboard),
        parse_mode=ParseMode.HTML
    )
    return MAINMENU_STATE

async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    reply_markup = InlineKeyboardMarkup(main_options_keyboard)
    await query.edit_message_text(
        main_menu_msg,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    return MAINMENU_STATE

def main() -> None:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    application = Application.builder().token(bot_token).build()
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
        ],
        states={
            MAINMENU_STATE: [
                CallbackQueryHandler(check_balance, pattern=f"^{CKBALANCE}$"),
                CallbackQueryHandler(withdraw, pattern=f"^{WITHDRAW}$"),
                CallbackQueryHandler(deposit, pattern=f"^{DEPOSIT}$"),
            ],
            WITHDRAW_STATE:[
                CallbackQueryHandler(back_to_main_menu, pattern=f"^{BACK}$"),
                MessageHandler(filters.TEXT, make_withdraw),
            ],
            DEPOSIT_STATE: [
                CallbackQueryHandler(back_to_main_menu, pattern=f"^{BACK}$"),
                MessageHandler(filters.TEXT, make_deposit),
            ],
            CONFIRM_STATE: [
                CallbackQueryHandler(cancel, pattern=f"^{CANCEL}$"),
                CallbackQueryHandler(confirm, pattern=f"^{CONFIRM}$"),
            ],
            

        },
        fallbacks=[
            MessageHandler(filters.Regex("^Done$"), start),
        ],
    )
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
