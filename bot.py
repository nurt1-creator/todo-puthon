import os
from dotenv import load_dotenv
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    FSInputFile,
)

from logic import TodoManager

load_dotenv()
BOT_TOKEN = os.environ.get("TOKEN")

# ───────────────────────────── FSM States ─────────────────────────────

class AddTaskState(StatesGroup):
    waiting_for_title = State()
    waiting_for_desc  = State()

class DeleteTaskState(StatesGroup):
    waiting_for_title = State()

class ToggleTaskState(StatesGroup):
    waiting_for_title = State()

# ───────────────────────────── Keyboards ──────────────────────────────

class Keyboards:
    START = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Open Menu", callback_data="showmenu_button")]
    ])

    MENU = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Show tasks",    callback_data="task_list_button")],
        [InlineKeyboardButton(text="➕ Add task",       callback_data="add_button")],
        [InlineKeyboardButton(text="🗑 Delete task",   callback_data="delete_button")],
        [InlineKeyboardButton(text="✅ Change status", callback_data="toggle_button")],
        [InlineKeyboardButton(text="💣 Delete all",    callback_data="delete_all_button")],
    ])

    ACCEPT = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes", callback_data="yes_button"),
            InlineKeyboardButton(text="❌ No",  callback_data="no_button"),
        ]
    ])

    BACK = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_button")]
    ])

    BACK_MENU = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to menu", callback_data="back_button")]
    ])

# ───────────────────────────── Bot ────────────────────────────────────

# Замени на свои file_id после первой отправки
PHOTO_MENU    = "AgACAgIAAxkDAAPDacbHXn8n2cW6MIr95d4GmbqvTj8AAsYaaxsv7ThKA8s7qWBVuqkBAAMCAAN5AAM6BA"
PHOTO_DELETED = "AgACAgIAAxkDAAIBBGnHhicrcxXhegVBTdtcB7IbLP_2AAL2EmsbL-1ASiK7GTMQA-qlAQADAgADeQADOgQ"


class TodoBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp  = Dispatcher()
        self.tm  = TodoManager()
        self._register_handlers()

    # ── Handler registration ──────────────────────────────────────────

    def _register_handlers(self):
        # Commands
        self.dp.message.register(self.cmd_start,  CommandStart())
        self.dp.message.register(self.cmd_help,   Command("help"))
        self.dp.message.register(self.cmd_list,   Command("list"))
        self.dp.message.register(self.cmd_add,    Command("add"))
        self.dp.message.register(self.cmd_del,    Command("del"))
        self.dp.message.register(self.cmd_toggle, Command("toggle"))

        # Callbacks
        cb = self.dp.callback_query
        cb.register(self.cb_show_menu,  lambda c: c.data == "showmenu_button")
        cb.register(self.cb_task_list,  lambda c: c.data == "task_list_button")
        cb.register(self.cb_back,       lambda c: c.data == "back_button")
        cb.register(self.cb_add,        lambda c: c.data == "add_button")
        cb.register(self.cb_delete,     lambda c: c.data == "delete_button")
        cb.register(self.cb_toggle,     lambda c: c.data == "toggle_button")
        cb.register(self.cb_delete_all, lambda c: c.data == "delete_all_button")
        cb.register(self.cb_accept_yes, lambda c: c.data == "yes_button")
        cb.register(self.cb_accept_no,  lambda c: c.data == "no_button")

        # FSM
        msg = self.dp.message
        msg.register(self.fsm_add_title,    AddTaskState.waiting_for_title)
        msg.register(self.fsm_add_desc,     AddTaskState.waiting_for_desc)
        msg.register(self.fsm_delete_title, DeleteTaskState.waiting_for_title)
        msg.register(self.fsm_toggle_title, ToggleTaskState.waiting_for_title)

    # ── Helpers ───────────────────────────────────────────────────────

    def _format_task_list(self) -> str:
        data = self.tm.get_all()
        if not data:
            return "📭 No tasks yet"
        lines = []
        for k, v in data.items():
            status = "✅" if v["completed"] else "🔲"
            lines.append(f"{status} <b>{v['title']}</b>  <i>#{k}</i>")
        return "\n".join(lines)

    async def _show_menu(self, message: Message):
        """Удаляет текущее сообщение и показывает меню с фото."""
        try:
            await message.delete()
        except Exception:
            pass
        await message.answer_photo(
            photo=PHOTO_MENU,
            caption="📋 <b>Todo Bot Menu</b>",
            reply_markup=Keyboards.MENU,
            parse_mode="HTML",
        )

    async def _safe_edit(self, message: Message, text: str, reply_markup=None) -> Message:
        """Редактирует сообщение или создаёт новое если не получается. Возвращает сообщение."""
        try:
            result = await message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
            # edit_text возвращает True или Message в зависимости от версии
            if result is True or result is None:
                raise ValueError("edit returned non-message")
            return result
        except Exception:
            try:
                await message.delete()
            except Exception:
                pass
            return await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")

    async def _save_bot_msg(self, state: FSMContext, message: Message):
        """Сохраняет id и chat_id сообщения бота в FSM state."""
        await state.update_data(bot_msg_id=message.message_id, chat_id=message.chat.id)

    async def _edit_bot_msg(self, state: FSMContext, text: str, reply_markup=None):
        """Редактирует сохранённое сообщение бота по данным из FSM state."""
        data = await state.get_data()
        bot_msg_id = data.get("bot_msg_id")
        chat_id    = data.get("chat_id")
        if bot_msg_id and chat_id:
            try:
                await self.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=bot_msg_id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                )
            except Exception:
                pass

    # ── Commands ──────────────────────────────────────────────────────

    async def cmd_start(self, message: Message):
        await message.answer(
            "👋 <b>Welcome to Todo Bot!</b>\nPress the button below to open the menu.",
            reply_markup=Keyboards.START,
            parse_mode="HTML",
        )

    async def cmd_help(self, message: Message):
        await message.answer(
            "📖 <b>Available commands:</b>\n\n"
            "/help   — this message\n"
            "/list   — show all tasks\n"
            "/add    — <code>/add Title | Description</code>\n"
            "/del    — <code>/del Title</code>\n"
            "/toggle — <code>/toggle Title</code>",
            parse_mode="HTML",
        )

    async def cmd_list(self, message: Message):
        await message.answer(self._format_task_list(), parse_mode="HTML")

    async def cmd_add(self, message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Usage: <code>/add Title | Description</code>", parse_mode="HTML")
            return
        args  = parts[1].split("|")
        title = args[0].strip()
        desc  = args[1].strip() if len(args) > 1 else ""
        self.tm.add(title, desc)
        self.tm.save()
        await message.answer(f"✅ Task <b>{title}</b> added!", parse_mode="HTML")

    async def cmd_del(self, message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Usage: <code>/del Title</code>", parse_mode="HTML")
            return
        title = parts[1].strip()
        if self.tm.delete(title):
            self.tm.save()
            await message.answer(f"🗑 Task <b>{title}</b> deleted.", parse_mode="HTML")
        else:
            await message.answer(f"❌ Task <b>{title}</b> not found.", parse_mode="HTML")

    async def cmd_toggle(self, message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Usage: <code>/toggle Title</code>", parse_mode="HTML")
            return
        title = parts[1].strip()
        if self.tm.toggle(title):
            self.tm.save()
            await message.answer(f"🔄 Task <b>{title}</b> status changed.", parse_mode="HTML")
        else:
            await message.answer(f"❌ Task <b>{title}</b> not found.", parse_mode="HTML")

    # ── Callbacks ─────────────────────────────────────────────────────

    async def cb_show_menu(self, callback: CallbackQuery):
        await callback.answer()
        await self._show_menu(callback.message)

    async def cb_task_list(self, callback: CallbackQuery):
        await callback.answer()
        text = self._format_task_list()
        await self._safe_edit(callback.message, text, Keyboards.BACK_MENU)

    async def cb_back(self, callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        await state.clear()
        await self._show_menu(callback.message)

    async def cb_add(self, callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        sent = await self._safe_edit(
            callback.message,
            "✏️ <b>Add task</b>\n\nEnter task title:",
            Keyboards.BACK,
        )
        await self._save_bot_msg(state, sent)
        await state.set_state(AddTaskState.waiting_for_title)

    async def cb_delete(self, callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        sent = await self._safe_edit(
            callback.message,
            "🗑 <b>Delete task</b>\n\nEnter task title to delete:",
            Keyboards.BACK,
        )
        await self._save_bot_msg(state, sent)
        await state.set_state(DeleteTaskState.waiting_for_title)

    async def cb_toggle(self, callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        sent = await self._safe_edit(
            callback.message,
            "🔄 <b>Change status</b>\n\nEnter task title to toggle:",
            Keyboards.BACK,
        )
        await self._save_bot_msg(state, sent)
        await state.set_state(ToggleTaskState.waiting_for_title)

    async def cb_delete_all(self, callback: CallbackQuery):
        await callback.answer()
        await self._safe_edit(
            callback.message,
            "⚠️ <b>Are you sure?</b>\n\nThis will delete <b>all</b> tasks!",
            Keyboards.ACCEPT,
        )

    async def cb_accept_yes(self, callback: CallbackQuery):
        await callback.answer("Deleted! 💣", show_alert=False)
        self.tm.clear()
        self.tm.save()
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer_photo(
            photo=PHOTO_DELETED,
            caption="💣 <b>All tasks deleted!</b>",
            reply_markup=Keyboards.BACK_MENU,
            parse_mode="HTML",
        )

    async def cb_accept_no(self, callback: CallbackQuery):
        await callback.answer()
        await self._show_menu(callback.message)

    # ── FSM handlers ──────────────────────────────────────────────────

    async def fsm_add_title(self, message: Message, state: FSMContext):
        title = message.text.strip()
        await message.delete()
        await state.update_data(title=title)
        await self._edit_bot_msg(
            state,
            f"✏️ <b>Add task</b>\n\nTitle: <code>{title}</code>\n\nNow enter description\n(or send <code>-</code> to skip):",
            Keyboards.BACK,
        )
        await state.set_state(AddTaskState.waiting_for_desc)

    async def fsm_add_desc(self, message: Message, state: FSMContext):
        data  = await state.get_data()
        title = data["title"]
        desc  = "" if message.text.strip() == "-" else message.text.strip()
        await message.delete()
        self.tm.add(title, desc)
        self.tm.save()
        await state.clear()
        await self._edit_bot_msg(
            state,
            f"✅ Task <b>{title}</b> added!\n\nReturn to menu:",
            Keyboards.BACK_MENU,
        )

    async def fsm_delete_title(self, message: Message, state: FSMContext):
        title = message.text.strip()
        await message.delete()
        if self.tm.delete(title):
            self.tm.save()
            text = f"🗑 Task <b>{title}</b> deleted."
        else:
            text = f"❌ Task <b>{title}</b> not found."
        await state.clear()
        await self._edit_bot_msg(state, text, Keyboards.BACK_MENU)

    async def fsm_toggle_title(self, message: Message, state: FSMContext):
        title = message.text.strip()
        await message.delete()
        if self.tm.toggle(title):
            self.tm.save()
            text = f"🔄 Task <b>{title}</b> status changed."
        else:
            text = f"❌ Task <b>{title}</b> not found."
        await state.clear()
        await self._edit_bot_msg(state, text, Keyboards.BACK_MENU)

    # ── Run ───────────────────────────────────────────────────────────

    async def run(self):
        await self.dp.start_polling(self.bot)


if __name__ == "__main__":
    todo_bot = TodoBot(token=BOT_TOKEN)
    asyncio.run(todo_bot.run())
