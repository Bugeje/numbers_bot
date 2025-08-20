from handlers.states import State
from telegram.ext import (
    ApplicationBuilder,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from telegram.request import HTTPXRequest
from settings import settings

from utils import BTN
from handlers import (
    start,
    receive_birthdate_text,
    show_extended_only_profile,
    send_bridges_pdf,
    core_profile_ai_and_pdf,
    save_name_and_ask_birthdate,
    request_partner_name,
    save_partner_name_and_ask_birthdate,
    receive_partner_birthdate_text,
    show_cycles_profile,
    send_months_pdf,
    days_conversation_handler,
    State
)

import logging
import re


def main():
    request = HTTPXRequest(read_timeout=settings.HTTP_TIMEOUT, write_timeout=settings.HTTP_TIMEOUT, connect_timeout=settings.HTTP_TIMEOUT, pool_timeout=settings.HTTP_TIMEOUT)

    app = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).request(request).build()


    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex(f"^{re.escape(BTN.RESTART)}$"), start)
        ],
        states={
            State.ASK_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_name_and_ask_birthdate)
            ],
            State.ASK_BIRTHDATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_birthdate_text)
            ],
            State.EXTENDED_ANALYSIS: [
                MessageHandler(filters.Regex(f"^{re.escape(BTN.PARTNER)}$"), request_partner_name),
                MessageHandler(filters.Regex(f"^{re.escape(BTN.CORE)}$"), core_profile_ai_and_pdf),
                MessageHandler(filters.Regex(f"^{re.escape(BTN.EXTENDED)}$"), show_extended_only_profile),
                MessageHandler(filters.Regex(f"^{re.escape(BTN.BRIDGES)}$"), send_bridges_pdf),
                MessageHandler(filters.Regex(f"^{re.escape(BTN.CYCLES)}$"), show_cycles_profile),
                MessageHandler(filters.Regex(f"^{re.escape(BTN.MONTHS)}$"), send_months_pdf)
            ],
            State.ASK_PARTNER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_partner_name_and_ask_birthdate)
            ],
            State.ASK_PARTNER_BIRTHDATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_partner_birthdate_text)
            ]
        },
        fallbacks=[MessageHandler(filters.Regex(f"^{re.escape(BTN.RESTART)}$"), start)]
    )


    app.add_handler(conv_handler)

    app.add_handler(days_conversation_handler)

    app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.PARTNER)}$"), request_partner_name))
    app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.CORE)}$"), core_profile_ai_and_pdf))
    app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.EXTENDED)}$"), show_extended_only_profile))
    app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.BRIDGES)}$"), send_bridges_pdf))
    app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.CYCLES)}$"), show_cycles_profile))
    app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.MONTHS)}$"), send_months_pdf))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_partner_name_and_ask_birthdate))  
    app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.RESTART)}$"), start))

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Бот запущен...")

    app.run_polling()


if __name__ == "__main__":
    main()
