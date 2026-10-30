from datetime import date, datetime

import requests
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.clock import Clock

API = "http://127.0.0.1:8000"

BG          = (0.06, 0.08, 0.12, 1)
CARD        = (0.11, 0.14, 0.20, 1)
CARD_HOVER  = (0.17, 0.21, 0.30, 1)
INPUT_BG    = (0.16, 0.20, 0.28, 1)
ACCENT      = (0.20, 0.55, 1.00, 1)
DANGER      = (0.90, 0.30, 0.30, 1)
SUCCESS     = (0.30, 0.80, 0.40, 1)
WARNING     = (0.95, 0.75, 0.20, 1)
MUTED       = (0.55, 0.60, 0.70, 1)
TEXT        = (0.95, 0.97, 1.00, 1)
TEXT_DIM    = (0.65, 0.70, 0.80, 1)

STATUS_COLORS = {
    "draft":           WARNING,
    "pending_payment": ACCENT,
    "paid":            SUCCESS,
    "in_progress":     (0.95, 0.55, 0.20, 1),
    "done":            MUTED,
    "cancelled":       DANGER,
}
STATUS_LABELS = {
    "draft":           "Черновик",
    "pending_payment": "Ожидает оплаты",
    "paid":            "Оплачен",
    "in_progress":     "В работе",
    "done":            "Завершён",
    "cancelled":       "Отменён",
}


def digits_only(text, from_undo=False):
    if not text:
        return ""
    return "".join(ch for ch in text if ch.isdigit() or ch in ", ")


def phone_only(text, from_undo=False):
    if not text:
        return ""
    out = "".join(ch for ch in text if ch.isdigit() or ch == "+")
    if out.startswith("+"):
        out = "+" + out[1:].replace("+", "")
    else:
        out = out.replace("+", "")
    return out


def letters_only(text, from_undo=False):
    if not text:
        return ""
    allowed = set(" абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
                  "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
                  "abcdefghijklmnopqrstuvwxyz"
                  "ABCDEFGHIJKLMNOPQRSTUVWXYZ-")
    return "".join(ch for ch in text if ch in allowed)


def toast(msg, color=ACCENT):
    content = BoxLayout(orientation="vertical", padding=dp(12))
    lbl = Label(text=str(msg), halign="center", valign="middle",
                color=TEXT, font_size=dp(15))
    lbl.bind(size=lambda *_: setattr(lbl, "text_size", lbl.size))
    content.add_widget(lbl)
    popup = Popup(title="", content=content, size_hint=(0.8, 0.3),
                  separator_color=color)
    popup.background = ""
    popup.background_color = (0, 0, 0, 0)
    popup.open()
    Clock.schedule_once(lambda *_: popup.dismiss(), 2.2)


def confirm(title, text, on_yes):
    content = BoxLayout(orientation="vertical", padding=dp(16),
                        spacing=dp(10))
    lbl = Label(text=text, halign="center", valign="middle",
                color=TEXT, font_size=dp(15))
    lbl.bind(size=lambda *_: setattr(lbl, "text_size", lbl.size))
    content.add_widget(lbl)

    row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
    popup = Popup(title=title, content=content, size_hint=(0.8, 0.35),
                  separator_color=ACCENT)

    def _yes(*_):
        popup.dismiss()
        on_yes()

    def _no(*_):
        popup.dismiss()

    row.add_widget(DangerButton(text="Да", on_release=_yes))
    row.add_widget(GhostButton(text="Нет", on_release=_no))
    content.add_widget(row)
    popup.open()


class Card(BoxLayout):
    def __init__(self, bg=CARD, radius=14, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            self._color = Color(*bg)
            self._rect = RoundedRectangle(radius=[dp(radius)])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size


class PrimaryButton(Button):
    def __init__(self, bg=ACCENT, **kw):
        super().__init__(**kw)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = TEXT
        self.bold = True
        self.font_size = dp(14)
        self._bg = bg
        with self.canvas.before:
            self._btn_color = Color(*bg)
            self._btn_rect = RoundedRectangle(radius=[dp(12)])
        self.bind(pos=self._upd, size=self._upd, state=self._on_state)

    def _upd(self, *_):
        self._btn_rect.pos = self.pos
        self._btn_rect.size = self.size

    def _on_state(self, *_):
        if self.state == "down":
            r, g, b, a = self._bg
            self._btn_color.rgba = (r * 0.7, g * 0.7, b * 0.7, a)
        else:
            self._btn_color.rgba = self._bg


class GhostButton(PrimaryButton):
    def __init__(self, **kw):
        super().__init__(bg=CARD_HOVER, **kw)


class DangerButton(PrimaryButton):
    def __init__(self, **kw):
        super().__init__(bg=DANGER, **kw)


class SuccessButton(PrimaryButton):
    def __init__(self, **kw):
        super().__init__(bg=SUCCESS, **kw)


def make_input(hint="", password=False, input_filter=None):
    ti = TextInput(hint_text=hint,
                   password=password,
                   multiline=False,
                   size_hint_y=None,
                   height=dp(50),
                   font_size=dp(15),
                   halign="center",
                   foreground_color=TEXT,
                   hint_text_color=MUTED,
                   cursor_color=ACCENT,
                   background_color=INPUT_BG,
                   background_normal="",
                   background_active="",
                   padding=[dp(12), dp(14), dp(12), dp(14)])
    if input_filter:
        ti.input_filter = input_filter
    return ti


class StatusPill(BoxLayout):
    def __init__(self, status, **kw):
        super().__init__(size_hint=(None, None),
                         size=(dp(150), dp(30)), **kw)
        color = STATUS_COLORS.get(status, MUTED)
        text = STATUS_LABELS.get(status, status)
        with self.canvas.before:
            self._c = Color(*color)
            self._r = RoundedRectangle(radius=[dp(15)])
        self.bind(pos=self._upd, size=self._upd)
        lbl = Label(text=text, color=(0, 0, 0, 1), bold=True,
                    font_size=dp(12))
        self.add_widget(lbl)

    def _upd(self, *_):
        self._r.pos = self.pos
        self._r.size = self.size


class Api:
    def __init__(self):
        self.base = API
        self.token = None

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def post(self, path, payload):
        r = requests.post(self.base + path, json=payload,
                          headers=self._headers(), timeout=10)
        r.encoding = "utf-8"
        return r

    def get(self, path):
        r = requests.get(self.base + path, headers=self._headers(),
                         timeout=10)
        r.encoding = "utf-8"
        return r

    def patch(self, path, payload):
        r = requests.patch(self.base + path, json=payload,
                           headers=self._headers(), timeout=10)
        r.encoding = "utf-8"
        return r

    def delete(self, path):
        r = requests.delete(self.base + path,
                            headers=self._headers(), timeout=10)
        r.encoding = "utf-8"
        return r


class Root(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=dp(14),
                         spacing=dp(10), **kw)
        Window.clearcolor = BG
        self.api = Api()
        self.user = None
        self._orders_cache = []
        self._filter_text = ""
        self._build_login()

    def clear(self):
        self.clear_widgets()

    def _header(self, title, subtitle=None, right_button=None):
        head = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(8))
        left = BoxLayout(orientation="vertical")
        left.add_widget(Label(text=title, color=TEXT, bold=True,
                              font_size=dp(19), halign="center",
                              valign="middle",
                              size_hint_y=None, height=dp(32)))
        if subtitle:
            left.add_widget(Label(text=subtitle, color=TEXT_DIM,
                                  font_size=dp(12), halign="center",
                                  valign="middle",
                                  size_hint_y=None, height=dp(22)))
        head.add_widget(left)
        if right_button:
            head.add_widget(right_button)
        return head

    def _build_login(self):
        self.clear()
        self.add_widget(Widget(size_hint_y=0.12))
        card = Card(orientation="vertical", padding=dp(20), spacing=dp(12),
                    size_hint_y=None, height=dp(380))
        card.add_widget(Label(text="АВТОМОЙКА", color=TEXT, bold=True,
                              font_size=dp(24), halign="center",
                              size_hint_y=None, height=dp(36)))
        card.add_widget(Label(text="Войдите, чтобы продолжить",
                              color=TEXT_DIM, font_size=dp(12),
                              halign="center",
                              size_hint_y=None, height=dp(18)))
        card.add_widget(Widget(size_hint_y=None, height=dp(8)))

        self.phone_in = make_input("Телефон", input_filter=phone_only)
        self.pass_in = make_input("Пароль", password=True)
        card.add_widget(self.phone_in)
        card.add_widget(self.pass_in)

        card.add_widget(PrimaryButton(text="Войти",
                                      size_hint_y=None, height=dp(48),
                                      on_release=self.do_login))
        card.add_widget(GhostButton(
            text="Регистрация",
            size_hint_y=None, height=dp(44),
            on_release=lambda *_: self._build_register()))

        self.add_widget(card)
        self.add_widget(Widget(size_hint_y=0.4))

    def _build_register(self):
        self.clear()
        self.add_widget(Widget(size_hint_y=0.08))
        card = Card(orientation="vertical", padding=dp(20), spacing=dp(12),
                    size_hint_y=None, height=dp(430))
        card.add_widget(Label(text="Регистрация", color=TEXT, bold=True,
                              font_size=dp(22), halign="center",
                              size_hint_y=None, height=dp(34)))
        card.add_widget(Label(text="Создайте аккаунт клиента",
                              color=TEXT_DIM, font_size=dp(12),
                              halign="center",
                              size_hint_y=None, height=dp(18)))
        card.add_widget(Widget(size_hint_y=None, height=dp(4)))

        self.reg_name = make_input("Имя", input_filter=letters_only)
        self.reg_phone = make_input("Телефон", input_filter=phone_only)
        self.reg_pass = make_input("Пароль", password=True)
        card.add_widget(self.reg_name)
        card.add_widget(self.reg_phone)
        card.add_widget(self.reg_pass)

        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        row.add_widget(PrimaryButton(text="Создать",
                                     on_release=self.do_register))
        row.add_widget(GhostButton(text="Назад",
                                   on_release=lambda *_: self._build_login()))
        card.add_widget(row)

        self.add_widget(card)
        self.add_widget(Widget(size_hint_y=0.3))

    def _build_home(self):
        self.clear()
        role = self.user.get("role", "client")

        logout = DangerButton(text="Выйти",
                              size_hint=(None, None),
                              size=(dp(90), dp(38)),
                              on_release=self.do_logout)
        self.add_widget(self._header(
            f"Привет, {self.user['name']}",
            f"{self.user['phone']}  •  {role}",
            logout))

        if role == "washer":
            btns = [("Мои задачи", self.load_orders, SuccessButton)]
        elif role in ("admin", "manager"):
            btns = [("Обновить заказы", self.load_orders, PrimaryButton)]
        else:
            btns = [("Услуги", self.load_services, GhostButton),
                    ("Мои заказы", self.load_orders, PrimaryButton)]

        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        for text, cb, cls in btns:
            row.add_widget(cls(text=text, on_release=cb))
        self.add_widget(row)

        self.scroll = ScrollView()
        self.output = BoxLayout(orientation="vertical", spacing=dp(10),
                                padding=[0, dp(6)], size_hint_y=None)
        self.output.bind(minimum_height=self.output.setter("height"))
        self.scroll.add_widget(self.output)
        self.add_widget(self.scroll)

        if role == "washer":
            self.load_orders()
        elif role in ("admin", "manager"):
            self.load_orders()
        else:
            self.load_services()

    def _add_info(self, text):
        self.output.clear_widgets()
        lbl = Label(text=text, color=TEXT_DIM, markup=True,
                    size_hint_y=None, halign="center", valign="middle")
        lbl.bind(width=lambda *_: setattr(lbl, "text_size",
                                          (lbl.width, None)),
                 texture_size=lambda *_: setattr(lbl, "height",
                                                 lbl.texture_size[1]))
        self.output.add_widget(lbl)

    def do_login(self, *_):
        try:
            r = self.api.post("/api/auth/login", {
                "phone": self.phone_in.text.strip(),
                "password": self.pass_in.text
            })
            if r.status_code != 200:
                toast("Ошибка входа", DANGER)
                return
            self.api.token = r.json()["access_token"]
            self._load_me()
        except Exception as e:
            toast(f"Сервер недоступен: {e}", DANGER)

    def do_register(self, *_):
        try:
            r = self.api.post("/api/users", {
                "name": self.reg_name.text.strip(),
                "phone": self.reg_phone.text.strip(),
                "password": self.reg_pass.text
            })
            if r.status_code not in (200, 201):
                toast("Ошибка регистрации", DANGER)
                return
            toast("Регистрация успешна!", SUCCESS)
            self._build_login()
        except Exception as e:
            toast(f"Сервер недоступен: {e}", DANGER)

    def _load_me(self):
        r = self.api.get("/api/users/me")
        if r.status_code != 200:
            toast("Не удалось получить профиль", DANGER)
            return
        self.user = r.json()
        self._build_home()

    def do_logout(self, *_):
        self.api.token = None
        self.user = None
        self._orders_cache = []
        self._filter_text = ""
        self._build_login()

    # ---------- услуги ----------
    def load_services(self, *_):
        try:
            r = self.api.get("/api/services")
            if r.status_code != 200:
                toast(f"Ошибка: {r.text}", DANGER)
                return
            services = r.json()
            self.output.clear_widgets()
            for s in services:
                card = Card(orientation="horizontal", padding=dp(14),
                            spacing=dp(10),
                            size_hint_y=None, height=dp(72))
                info = BoxLayout(orientation="vertical", size_hint_x=0.72)

                name = Label(text=f"{s['name']}", color=TEXT, bold=True,
                             font_size=dp(15), halign="left", valign="middle")
                name.bind(size=lambda lbl, *_: setattr(lbl, "text_size",
                                                       lbl.size))
                info.add_widget(name)

                desc = Label(text=f"{s.get('description','')}",
                             color=TEXT_DIM, font_size=dp(12),
                             halign="left", valign="middle")
                desc.bind(size=lambda lbl, *_: setattr(lbl, "text_size",
                                                       lbl.size))
                info.add_widget(desc)
                card.add_widget(info)

                price = Label(text=f"{int(s['price'])} ₽",
                              color=ACCENT, bold=True, font_size=dp(16),
                              halign="right", valign="middle",
                              size_hint_x=0.28)
                price.bind(size=lambda lbl, *_: setattr(lbl, "text_size",
                                                        lbl.size))
                card.add_widget(price)
                self.output.add_widget(card)

            self.order_input = make_input("id услуг (например: 1,2)",
                                          input_filter=digits_only)
            self.output.add_widget(self.order_input)
            self.output.add_widget(
                PrimaryButton(text="Создать заказ",
                              size_hint_y=None, height=dp(48),
                              on_release=self.create_order))
        except Exception as e:
            toast(f"Сервер недоступен: {e}", DANGER)

    def create_order(self, *_):
        try:
            raw = self.order_input.text.strip()
            if not raw:
                toast("Укажите id услуг", DANGER)
                return
            parts = [p.strip() for p in raw.split(",") if p.strip()]
            if not all(p.isdigit() for p in parts):
                toast("Только цифры и запятые", DANGER)
                return
            ids = [int(p) for p in parts]
            r = self.api.post("/api/orders", {
                "date": date.today().isoformat(),
                "time": datetime.now().strftime("%H:%M:%S"),
                "service_ids": ids
            })
            if r.status_code not in (200, 201):
                toast(f"Ошибка: {r.text}", DANGER)
                return
            order = r.json()
            toast(f"Заказ #{order['id']} создан", SUCCESS)
            self.load_orders()
        except Exception as e:
            toast(f"Ошибка: {e}", DANGER)

    # ---------- заказы ----------
    def load_orders(self, *_):
        try:
            r = self.api.get("/api/orders")
            if r.status_code != 200:
                toast(f"Ошибка: {r.text}", DANGER)
                return
            self._orders_cache = r.json()
            self._render_orders()
        except Exception as e:
            toast(f"Сервер недоступен: {e}", DANGER)

    def _render_orders(self):
        orders = self._orders_cache
        role = self.user.get("role", "client")
        self.output.clear_widgets()

        # Поле поиска — показывается только здесь, на экране заказов
        search_row = BoxLayout(size_hint_y=None, height=dp(44),
                               spacing=dp(8))
        self.search_input = make_input("Поиск по id / статусу")
        self.search_input.text = self._filter_text
        self.search_input.bind(text=self._on_search_change)
        search_row.add_widget(self.search_input)
        search_row.add_widget(GhostButton(
            text="Очистить", size_hint=(None, 1), width=dp(100),
            on_release=self._clear_search))
        self.output.add_widget(search_row)

        if self._filter_text:
            filtered = []
            for o in orders:
                if (self._filter_text in str(o["id"]).lower()
                        or self._filter_text in o["status"].lower()):
                    filtered.append(o)
            orders = filtered

        if not orders:
            self._add_info("Заказов пока нет")
            return

        now = datetime.now()
        for o in orders:
            card = Card(orientation="vertical", padding=dp(14),
                        spacing=dp(4),
                        size_hint_y=None, height=dp(160))

            row1 = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(6))
            num = Label(text=f"Заказ #{o['id']}", color=TEXT, bold=True,
                        font_size=dp(15), halign="left", valign="middle")
            num.bind(size=lambda lbl, *_: setattr(lbl, "text_size",
                                                  lbl.size))
            row1.add_widget(num)

            total = int(o.get("total") or 0)
            price = Label(text=f"{total} ₽", color=ACCENT, bold=True,
                          font_size=dp(15), halign="right", valign="middle",
                          size_hint=(None, 1), width=dp(110))
            price.bind(size=lambda lbl, *_: setattr(lbl, "text_size",
                                                    lbl.size))
            row1.add_widget(price)
            card.add_widget(row1)

            client_text = "Клиент: —"
            if o.get("client_name"):
                client_text = f"Клиент: {o['client_name']}"
                if o.get("client_phone"):
                    client_text += f"  ({o['client_phone']})"
            cl = Label(text=client_text, color=TEXT_DIM, font_size=dp(13),
                       halign="center", valign="middle",
                       size_hint_y=None, height=dp(20))
            cl.bind(size=lambda lbl, *_: setattr(lbl, "text_size", lbl.size))
            card.add_widget(cl)

            info = Label(text=f"{o['date']}  •  {o['time']}",
                         color=TEXT_DIM, font_size=dp(13),
                         halign="center", valign="middle",
                         size_hint_y=None, height=dp(20))
            info.bind(size=lambda lbl, *_: setattr(lbl, "text_size",
                                                   lbl.size))
            card.add_widget(info)

            pill_row = BoxLayout(size_hint_y=None, height=dp(30))
            pill_row.add_widget(Widget())
            pill_row.add_widget(StatusPill(o["status"]))
            pill_row.add_widget(Widget())
            card.add_widget(pill_row)

            if o["status"] == "done" and o.get("finished_at"):
                try:
                    finished = datetime.fromisoformat(o["finished_at"])
                    left = max(0, 60 - int((now - finished).total_seconds()))
                    tl = Label(text=f"удалится через {left} с",
                               color=TEXT_DIM, font_size=dp(12),
                               halign="center", valign="middle",
                               size_hint_y=None, height=dp(18))
                    tl.bind(size=lambda lbl, *_: setattr(lbl, "text_size",
                                                         lbl.size))
                    card.add_widget(tl)
                except Exception:
                    pass

            self.output.add_widget(card)

            btn_row = BoxLayout(size_hint_y=None, height=dp(44),
                                spacing=dp(6))
            btn_row.add_widget(PrimaryButton(
                text="Подробнее",
                on_release=lambda *_, oid=o["id"]: self.open_order_view(oid)))

            if role == "client" and o["status"] in ("draft",
                                                    "pending_payment"):
                btn_row.add_widget(SuccessButton(
                    text="Оплатить",
                    on_release=lambda *_, oid=o["id"]: self.pay_order(oid)))
                btn_row.add_widget(GhostButton(
                    text="Изменить",
                    on_release=lambda *_, oid=o["id"]:
                        self.open_edit_order(oid)))
            elif role == "washer" and o["status"] == "paid":
                btn_row.add_widget(SuccessButton(
                    text="Начать",
                    on_release=lambda *_, oid=o["id"]:
                        self.start_order(oid)))
            elif role == "washer" and o["status"] == "in_progress":
                btn_row.add_widget(PrimaryButton(
                    text="Завершить",
                    on_release=lambda *_, oid=o["id"]:
                        self.finish_order(oid)))
            elif role in ("admin", "manager"):
                if role == "admin":
                    btn_row.add_widget(DangerButton(
                        text="Удалить",
                        on_release=lambda *_, oid=o["id"]:
                            self.confirm_delete(oid)))

            self.output.add_widget(btn_row)

    def _on_search_change(self, *_):
        self._filter_text = self.search_input.text.strip().lower()
        # перерисовываем список без пересоздания поля
        self._render_orders()

    def _clear_search(self, *_):
        self._filter_text = ""
        self._render_orders()

    # ---------- просмотр ----------
    def open_order_view(self, order_id):
        try:
            r = self.api.get(f"/api/orders/{order_id}")
            if r.status_code != 200:
                toast(f"Ошибка: {r.text}", DANGER)
                return
            o = r.json()
            self.clear()
            logout = DangerButton(text="Выйти",
                                  size_hint=(None, None),
                                  size=(dp(90), dp(38)),
                                  on_release=self.do_logout)
            self.add_widget(self._header(f"Заказ #{o['id']}",
                                         f"{o['date']}  •  {o['time']}",
                                         logout))
            self.add_widget(GhostButton(
                text="← Назад к списку",
                size_hint_y=None, height=dp(44),
                on_release=lambda *_: self._back_home()))

            scroll = ScrollView()
            info_box = BoxLayout(orientation="vertical", spacing=dp(10),
                                 padding=[0, dp(6)], size_hint_y=None)
            info_box.bind(minimum_height=info_box.setter("height"))

            def add_line(label, value):
                row = Card(orientation="horizontal", padding=dp(14),
                           spacing=dp(10),
                           size_hint_y=None, height=dp(52))
                lbl = Label(text=label, color=TEXT_DIM, font_size=dp(13),
                            halign="left", valign="middle",
                            size_hint_x=0.4)
                lbl.bind(size=lambda l, *_: setattr(l, "text_size", l.size))
                val = Label(text=str(value), color=TEXT, bold=True,
                            font_size=dp(14), halign="right",
                            valign="middle", size_hint_x=0.6)
                val.bind(size=lambda l, *_: setattr(l, "text_size", l.size))
                row.add_widget(lbl)
                row.add_widget(val)
                info_box.add_widget(row)

            add_line("ID", o["id"])
            add_line("Статус", STATUS_LABELS.get(o["status"], o["status"]))
            add_line("Клиент", o.get("client_name") or "—")
            add_line("Телефон", o.get("client_phone") or "—")
            add_line("Дата", o.get("date", "—"))
            add_line("Время", o.get("time", "—"))
            add_line("Сумма", f"{int(o.get('total') or 0)} ₽")
            if o.get("finished_at"):
                add_line("Завершён", o["finished_at"])

            scroll.add_widget(info_box)
            self.add_widget(scroll)
        except Exception as e:
            toast(f"Ошибка: {e}", DANGER)

    def _back_home(self):
        self._build_home()

    # ---------- редактирование ----------
    def open_edit_order(self, order_id):
        content = BoxLayout(orientation="vertical", padding=dp(16),
                            spacing=dp(12))
        content.add_widget(Label(
            text=f"Изменить состав заказа #{order_id}",
            color=TEXT, bold=True, font_size=dp(15),
            size_hint_y=None, height=dp(30)))
        content.add_widget(Label(
            text="Введите новые id услуг через запятую",
            color=TEXT_DIM, font_size=dp(12),
            size_hint_y=None, height=dp(20)))

        inp = make_input("например: 1,3", input_filter=digits_only)
        content.add_widget(inp)

        popup = Popup(title="Редактирование заказа",
                      content=content, size_hint=(0.85, 0.4),
                      separator_color=ACCENT)

        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))

        def _save(*_):
            raw = inp.text.strip()
            if not raw:
                toast("Введите id услуг", DANGER)
                return
            parts = [p.strip() for p in raw.split(",") if p.strip()]
            if not all(p.isdigit() for p in parts):
                toast("Только цифры и запятые", DANGER)
                return
            ids = [int(p) for p in parts]
            try:
                r = self.api.patch(f"/api/orders/{order_id}",
                                   {"service_ids": ids})
                if r.status_code != 200:
                    toast(f"Ошибка: {r.text}", DANGER)
                    return
                toast(f"Заказ #{order_id} обновлён", SUCCESS)
                popup.dismiss()
                self.load_orders()
            except Exception as e:
                toast(f"Ошибка: {e}", DANGER)

        row.add_widget(PrimaryButton(text="Сохранить", on_release=_save))
        row.add_widget(GhostButton(text="Отмена",
                                   on_release=lambda *_: popup.dismiss()))
        content.add_widget(row)
        popup.open()

    # ---------- удаление ----------
    def confirm_delete(self, order_id):
        def _do_delete():
            try:
                r = self.api.delete(f"/api/orders/{order_id}")
                if r.status_code != 200:
                    toast(f"Ошибка: {r.text}", DANGER)
                    return
                toast(f"Заказ #{order_id} удалён", SUCCESS)
                self.load_orders()
            except Exception as e:
                toast(f"Ошибка: {e}", DANGER)

        confirm("Удаление",
                f"Удалить заказ #{order_id}?\nЭто действие необратимо.",
                _do_delete)

    # ---------- действия ----------
    def pay_order(self, order_id):
        try:
            r = self.api.post(f"/api/orders/{order_id}/payment", {})
            if r.status_code not in (200, 201):
                toast(f"Ошибка: {r.text}", DANGER)
                return
            data = r.json()
            toast(f"Оплачено #{data['payment_id']}  •  {data['amount']} ₽",
                  SUCCESS)
            self.load_orders()
        except Exception as e:
            toast(f"Ошибка: {e}", DANGER)

    def start_order(self, order_id):
        try:
            r = self.api.patch(
                f"/api/orders/{order_id}/stages?stage=start", {})
            if r.status_code != 200:
                toast(f"Ошибка: {r.text}", DANGER)
                return
            toast(f"Заказ #{order_id} в работе", SUCCESS)
            self.load_orders()
        except Exception as e:
            toast(f"Ошибка: {e}", DANGER)

    def finish_order(self, order_id):
        try:
            r = self.api.patch(
                f"/api/orders/{order_id}/stages?stage=finish", {})
            if r.status_code != 200:
                toast(f"Ошибка: {r.text}", DANGER)
                return
            toast(f"Заказ #{order_id} завершён", SUCCESS)
            self.load_orders()
        except Exception as e:
            toast(f"Ошибка: {e}", DANGER)


class WashApp(App):
    def build(self):
        self.title = "Автомойка"
        Window.size = (360, 720)
        Window.minimum_width = 320
        Window.minimum_height = 600
        return Root()


if __name__ == "__main__":
    WashApp().run()