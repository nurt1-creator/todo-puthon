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
)

from logic import TodoManager


load_dotenv()
BOT_TOKEN = os.environ.get("TOKEN")


class AddTaskState(StatesGroup):
    waiting_for_title = State()
    waiting_for_desc = State()


class DeleteTaskState(StatesGroup):
    waiting_for_title = State()


class ToggleTaskState(StatesGroup):
    waiting_for_title = State()


class Keyboards:
    START = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Show menu", callback_data="showmenu_button")]
    ])

    MENU = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Show tasks", callback_data="task_list_button")],
        [InlineKeyboardButton(text="Add task", callback_data="add_button")],
        [InlineKeyboardButton(text="Delete task", callback_data="delete_button")],
        [InlineKeyboardButton(text="Change status", callback_data="toggle_button")],
    ])

    BACK = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back", callback_data="back_button")]
    ])


class TodoBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.tm = TodoManager()
        self._register_handlers()

    def _register_handlers(self):
        self.dp.message.register(self.cmd_start, CommandStart())
        self.dp.message.register(self.cmd_help, Command("help"))
        self.dp.message.register(self.cmd_list, Command("list"))
        self.dp.message.register(self.cmd_add, Command("add"))
        self.dp.message.register(self.cmd_del, Command("del"))
        self.dp.message.register(self.cmd_toggle, Command("toggle"))

        self.dp.callback_query.register(
            self.cb_show_menu, lambda c: c.data == "showmenu_button"
        )
        self.dp.callback_query.register(
            self.cb_task_list, lambda c: c.data == "task_list_button"
        )
        self.dp.callback_query.register(
            self.cb_back, lambda c: c.data == "back_button"
        )
        self.dp.callback_query.register(
            self.cb_add, lambda c: c.data == "add_button"
        )
        self.dp.callback_query.register(
            self.cb_delete, lambda c: c.data == "delete_button"
        )
        self.dp.callback_query.register(
            self.cb_toggle, lambda c: c.data == "toggle_button"
        )

        self.dp.message.register(self.fsm_add_title, AddTaskState.waiting_for_title)
        self.dp.message.register(self.fsm_add_desc, AddTaskState.waiting_for_desc)
        self.dp.message.register(self.fsm_delete_title, DeleteTaskState.waiting_for_title)
        self.dp.message.register(self.fsm_toggle_title, ToggleTaskState.waiting_for_title)

    def _format_task_list(self) -> str | None:
        data = self.tm.get_all()
        if not data:
            return None
        return "\n".join(
            f"{k}: {v['title']} — {'✅' if v['completed'] else '❌'}"
            for k, v in data.items()
        )

    # --- Commands ---

    async def cmd_start(self, message: Message):
        await message.answer("Welcome to Todo Bot", reply_markup=Keyboards.START)

    async def cmd_help(self, message: Message):
        await message.answer(
            "Available commands:\n"
            "/help - help message\n"
            "/list - show all todo tasks\n"
            "/add - add todo task\n"
            "/del - delete todo task\n"
            "/toggle - change task status"
        )

    async def cmd_list(self, message: Message):
        text = self._format_task_list()
        await message.answer(text or "No tasks")

    async def cmd_add(self, message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Usage: /add Title | Description")
            return
        args = parts[1].split("|")
        title = args[0].strip()
        desc = args[1].strip() if len(args) > 1 else ""
        self.tm.add(title, desc)
        self.tm.save()
        await message.answer(f"Task '{title}' added ✅")

    async def cmd_del(self, message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Usage: /del Title")
            return
        title = parts[1].strip()
        if self.tm.delete(title):
            self.tm.save()
            await message.answer(f"Task '{title}' deleted")
        else:
            await message.answer(f"Task '{title}' not found")

    async def cmd_toggle(self, message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Usage: /toggle Title")
            return
        title = parts[1].strip()
        if self.tm.toggle(title):
            self.tm.save()
            await message.answer(f"Task '{title}' status changed")
        else:
            await message.answer(f"Task '{title}' not found")

    # --- Callbacks ---

    async def cb_show_menu(self, callback: CallbackQuery):
        await callback.answer()
        await callback.message.edit_text("Menu", reply_markup=Keyboards.MENU)

    async def cb_task_list(self, callback: CallbackQuery):
        await callback.answer()
        text = self._format_task_list()
        await callback.message.edit_text(
            text or "No tasks", reply_markup=Keyboards.BACK
        )

    async def cb_back(self, callback: CallbackQuery):
        await callback.answer()
        await callback.message.edit_text("Menu", reply_markup=Keyboards.MENU)

    async def cb_add(self, callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        await callback.message.answer("Enter task title:")
        await state.set_state(AddTaskState.waiting_for_title)

    async def cb_delete(self, callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        await callback.message.answer("Enter task title to delete:")
        await state.set_state(DeleteTaskState.waiting_for_title)

    async def cb_toggle(self, callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        await callback.message.answer("Enter task title to toggle:")
        await state.set_state(ToggleTaskState.waiting_for_title)

    # --- FSM handlers ---

    async def fsm_add_title(self, message: Message, state: FSMContext):
        await state.update_data(title=message.text.strip())
        await message.answer("Enter task description (or send '-' to skip):")
        await state.set_state(AddTaskState.waiting_for_desc)

    async def fsm_add_desc(self, message: Message, state: FSMContext):
        data = await state.get_data()
        title = data["title"]
        desc = "" if message.text.strip() == "-" else message.text.strip()
        self.tm.add(title, desc)
        self.tm.save()
        await state.clear()
        await message.answer(f"Task '{title}' added ✅")

    async def fsm_delete_title(self, message: Message, state: FSMContext):
        title = message.text.strip()
        await state.clear()
        if self.tm.delete(title):
            self.tm.save()
            await message.answer(f"Task '{title}' deleted")
        else:
            await message.answer(f"Task '{title}' not found")

    async def fsm_toggle_title(self, message: Message, state: FSMContext):
        title = message.text.strip()
        await state.clear()
        if self.tm.toggle(title):
            self.tm.save()
            await message.answer(f"Task '{title}' status changed")
        else:
            await message.answer(f"Task '{title}' not found")

    async def run(self):
        await self.dp.start_polling(self.bot)


if __name__ == "__main__":
    todo_bot = TodoBot(token=BOT_TOKEN)
    asyncio.run(todo_bot.run())
