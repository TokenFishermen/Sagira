from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
import subprocess
import time

# Set window size and background color
Window.size = (900, 600)
Window.clearcolor = (0.1, 0.1, 0.2, 1)  # Dark gothic background

class SagiraGUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)

        # Chat history scroll view
        self.scroll_view = ScrollView(size_hint=(1, 0.8))
        self.chat_history = BoxLayout(orientation='vertical', size_hint_y=None)
        self.chat_history.bind(minimum_height=self.chat_history.setter('height'))
        self.scroll_view.add_widget(self.chat_history)
        self.add_widget(self.scroll_view)

        # Input layout
        input_layout = BoxLayout(size_hint=(1, 0.2), spacing=dp(10))
        self.text_input = TextInput(hint_text='Type your message...', multiline=False, size_hint=(0.8, 1))
        self.text_input.bind(on_text_validate=self.send_message)
        input_layout.add_widget(self.text_input)

        send_button = Button(text='Send', size_hint=(0.2, 1), background_color=(0.3, 0.3, 0.5, 1))
        send_button.bind(on_press=self.send_message)
        input_layout.add_widget(send_button)

        self.add_widget(input_layout)

        # Mock CLI integration placeholder
        self.add_message("Sagira: I am here. What do you need?", "sagira")

    def add_message(self, text, sender):
        label = Label(text=text, size_hint_y=None, height=dp(40), color=(1, 1, 1, 1) if sender == "user" else (0.8, 0.8, 1, 1))
        label.bind(size=lambda *args: setattr(label, 'text_size', (self.width - dp(20), None)))
        self.chat_history.add_widget(label)
        self.scroll_view.scroll_to(label)

    def send_message(self, instance):
        user_text = self.text_input.text.strip()
        if user_text:
            self.add_message(f"You: {user_text}", "user")
            self.text_input.text = ''
            # Simulate response (placeholder for actual CLI integration)
            Clock.schedule_once(lambda dt: self.simulate_response(user_text), 1)

    def simulate_response(self, user_text):
        response = f"Sagira: …consider your next step carefully."  # Placeholder response
        self.add_message(response, "sagira")

class SagiraApp(App):
    def build(self):
        return SagiraGUI()

if __name__ == '__main__':
    SagiraApp().run()
