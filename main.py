import asyncio
import os

from aiogram import types, Dispatcher, Bot
from pygelf import GelfTcpHandler
from loguru import logger

if os.getenv("KUBERNETES_NAMESPACE") and os.getenv("GELF_HOST") and os.getenv("GELF_PORT"):
    handler = GelfTcpHandler(
        host=os.getenv("GELF_HOST"),
        port=os.getenv("GELF_PORT"),
        _kubernetes_namespace_name=os.getenv("KUBERNETES_NAMESPACE"),
        _kubernetes_labels_app=os.getenv("KUBERNETES_APP"),
        _kubernetes_container_name=os.getenv("KUBERNETES_CONTAINER"),
        _kubernetes_pod_name=os.getenv("HOSTNAME"),
    )
    logger.add(handler)


bot = Bot(token=os.getenv("TG_TOKEN"), parse_mode='HTML')
dp = Dispatcher()


user_requests = {}


@dp.chat_join_request()
async def join(request: types.ChatJoinRequest):
    welcome_text_path = os.path.join(os.getenv('MESSAGES_FOLDER'), f"{request.chat.id}.txt")

    if not os.path.exists(welcome_text_path):
        logger.error(f'Can\'t load welcome message in path: {welcome_text_path}')
        return

    with open(welcome_text_path, '+r') as reader:
        welcome_text = reader.read()

    message = await bot.send_message(
        chat_id=request.user_chat_id,
        text=welcome_text,
        parse_mode="HTML",
    )

    # wait a few second before submitting the approval
    await asyncio.sleep(int(os.getenv("WAIT_BEFORE_APPROVE", 10)))

    await bot.edit_message_reply_markup(
        chat_id=request.user_chat_id,
        message_id=message.message_id,
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(text='Все понятно!', callback_data="approve_user"),
                ],
            ],
            resize_keyboard=True,
        ),
    )
    user_requests[request.user_chat_id] = request


@dp.callback_query(lambda c: c.data == 'approve_user')
async def approve_request(callback_query: types.CallbackQuery):
    if (request := user_requests.get(callback_query.from_user.id)) is not None:
        await request.approve()
        del user_requests[callback_query.from_user.id]

        # hide approve button
        await bot.edit_message_reply_markup(
            chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, reply_markup=None
        )


async def start():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start())
