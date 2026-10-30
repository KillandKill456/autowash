from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label


class TestApp(App):
    def build(self):
        root = BoxLayout(orientation="vertical", padding=40, spacing=20)
        root.add_widget(Label(text="Кликни в поле и напиши что-нибудь",
                              size_hint_y=None, height=40))
        root.add_widget(TextInput(hint_text="Обычное поле",
                                  size_hint_y=None, height=50))
        root.add_widget(TextInput(hint_text="Пароль", password=True,
                                  size_hint_y=None, height=50))
        return root


if __name__ == "__main__":
    TestApp().run()