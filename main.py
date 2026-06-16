import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

kivy.require('2.1.0')

def analizar(texto):
    return f"✅ Análisis completado\n\nDatos recibidos:\n{texto[:200]}..."

class AuditorApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        titulo = Label(text="AUDITOR DE APUESTAS", font_size='20sp', size_hint_y=0.08)
        layout.add_widget(titulo)
        self.entrada = TextInput(text='', multiline=True, size_hint_y=0.35, font_size='12sp',
                                 hint_text='Pega aquí las cuotas...')
        layout.add_widget(self.entrada)
        btn = Button(text="ANALIZAR", size_hint_y=0.08, background_color=(0.2, 0.6, 0.2, 1))
        btn.bind(on_press=self.analizar)
        layout.add_widget(btn)
        scroll = ScrollView(size_hint_y=0.45)
        self.resultado = Label(text="Esperando datos...", size_hint_y=None, font_size='12sp',
                               halign='left', valign='top')
        self.resultado.bind(size=self.resultado.setter('text_size'))
        scroll.add_widget(self.resultado)
        layout.add_widget(scroll)
        return layout
    def analizar(self, instance):
        texto = self.entrada.text
        if not texto.strip():
            self.resultado.text = "❌ No ingresaste datos"
            return
        self.resultado.text = analizar(texto)

if __name__ == "__main__":
    AuditorApp().run()
