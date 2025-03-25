import asyncio
import random
import time
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, ProgressBar, Input, Label
from textual.containers import Container
from textual.events import Key
from pyfiglet import Figlet
import aiohttp

# Данные из начала
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Список русских городов для генерации адресов
CITIES = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань", "Самара"]
STREETS = ["Ленина", "Мира", "Советская", "Пушкина", "Гагарина", "Кирова"]

async def generate_fake_data(username):
    """Генерация фейковых данных через OpenRouter API"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "google/gemini-2.0-pro-exp-02-05:free",
        "messages": [
            {
                "role": "user",
                "content": f"Придумай информацию о русском персонаже моей книги, с юзернеймом {username}. Возраст должен быть в районе от 12-20 лет. Главное напиши только информацию, никакого другого ответа. Придумывай разнообразные почты и места работы - не только строители и учителя: ФИО, адрес (город и улица), телефон, email, ФИО родителей, их телефоны, их email, место работы родителей."
            }
        ],
        "max_tokens": 600
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return generate_local_fake_data(username)

def generate_local_fake_data(username):
    """Локальная генерация данных, если API недоступен"""
    fname = random.choice(["Иван", "Алексей", "Дмитрий", "Сергей", "Мария", "Екатерина"])
    lname = random.choice(["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнова"])
    city = random.choice(CITIES)
    street = random.choice(STREETS)
    phone = f"+7(9{random.randint(10,99)}){random.randint(1000000,9999999)}"
    email = f"{fname.lower()}.{lname.lower()}@mail.ru"
    parent_fname = random.choice(["Олег", "Владимир", "Наталья", "Татьяна"])
    parent_lname = lname
    parent_phone = f"+7(9{random.randint(10,99)}){random.randint(1000000,9999999)}"
    parent_email = f"{parent_fname.lower()}.{parent_lname.lower()}@yandex.ru"
    parent_job = random.choice(["ООО Ромашка", "ИП Стройка", "Завод Металлург"])

    return (
        f"ФИО: {fname} {lname}\n"
        f"Адрес: г. {city}, ул. {street}, д. {random.randint(1, 100)}\n"
        f"Телефон: {phone}\n"
        f"Email: {email}\n"
        f"ФИО родителей: {parent_fname} {parent_lname}\n"
        f"Телефон родителей: {parent_phone}\n"
        f"Email родителей: {parent_email}\n"
        f"Место работы родителей: {parent_job}"
    )

def generate_threat_text(username):
    """Генерация текста-запугивалки"""
    return (
        f"Привет, {username}, спешу сообщить, что на тебя заказали\n\n"
        "ДЕАНОН\n\n"
        "Сейчас я перечислю, какая участь тебя ждет:\n"
        "— Твои родители узнают, как ты общаешься в интернете, будут слиты переписки, где ты оскорбляешь людей;\n"
        "— Каждый вечер 30 дней будут дозваниваться до твоих родителей и твоей школы;\n"
        "— Твои данные (адрес, телефон, фото) будут слиты в публичный доступ. Любой сможет позвонить твоей маме, отцу и угрожать;\n"
        "— Это еще не все, поверь, моя команда — профессионалы.\n\n"
        "Не советую кидать меня в ЧС. Время пошло."
    )

class DispacApp(App):
    """Основное приложение TUI"""
    CSS = """
    Container {
        layout: vertical;
        align: center middle;
        padding: 2;
    }
    Label {
        color: #00ff00;
        margin: 1;
    }
    ProgressBar {
        width: 50;
        margin: 1;
    }
    Button {
        margin: 1;
    }
    Input {
        width: 40;
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(Figlet(font="standard").renderText("DISPAC"), id="title")
        yield Label("Введи юзернейм для деанона:")
        yield Input(placeholder="@username")
        yield Button("Запустить деанон", id="start")
        yield Button("Сгенерировать запугивалку", id="threat")
        yield Button("Помощь", id="help")
        yield ProgressBar(total=100, id="progress")
        yield Label("", id="result")
        yield Footer()

    def on_key(self, event: Key) -> None:
        # Выход по нажатию клавиши 'q'
        if event.key == "q":
            self.exit()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start":
            username = self.query_one(Input).value
            if not username:
                self.query_one("#result", Label).update("Введи юзернейм!")
                return
            progress = self.query_one("#progress", ProgressBar)
            result_label = self.query_one("#result", Label)
            result_label.update("Сканирование началось...")
            for i in range(100):
                progress.update(progress=i + 1)
                await asyncio.sleep(0.05)  # Имитация работы
            fake_data = await generate_fake_data(username)
            result_label.update(f"Результат деанона для {username}:\n\n{fake_data}")

        elif event.button.id == "threat":
            username = self.query_one(Input).value or "дружище"
            threat_text = generate_threat_text(username)
            self.query_one("#result", Label).update(threat_text)

        elif event.button.id == "help":
            help_text = (
                "DISPAC — инструмент для деанона и запугивания!\n"
                "1. Введи юзернейм из Telegram/VK/Insta/OK.\n"
                "2. Нажми 'Запустить деанон' — мы найдем все данные.\n"
                "3. Нажми 'Сгенерировать запугивалку' — получи текст для жертвы.\n"
                "Все данные фейковые, но выглядят правдоподобно!\n\n"
                "Управление:\n"
                "- Tab: переключение между элементами\n"
                "- Enter: выбор/активация\n"
                "- q: выход из приложения"
            )
            self.query_one("#result", Label).update(help_text)

if __name__ == "__main__":
    app = DispacApp()
    app.run()
