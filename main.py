#!/usr/bin/env python3
"""
AUDITOR DE MERCADOS - APP PARA ANDROID
Interfaz táctil con Kivy
"""

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import re
import math

kivy.require('2.1.0')
Window.size = (360, 640)

# ==================== FUNCIONES DE ANÁLISIS ====================

def analizar(texto):
    """Analiza las cuotas y devuelve el resultado formateado."""
    lineas = [l.strip() for l in texto.split('\n') if ':' in l]
    raw = {}
    for l in lineas:
        k, v = l.split(':', 1)
        raw[k.strip().lower()] = float(v.strip())

    # Detectar equipos
    excluir = ['over', 'under', 'total', '3i', '5i', '-1.5', '+1.5']
    equipos = [k for k in raw if not any(p in k for p in excluir) and len(k) > 2]
    equipos = list(set(equipos))

    if len(equipos) < 2:
        return "❌ No se detectaron dos equipos.\n\nFormato correcto:\nEquipo1: 1.47\nEquipo2: 2.70\nEquipo1 over 0.5: 1.20"

    e1, e2 = equipos[0], equipos[1]
    resultado = f"══════════════════════════════════════════\n"
    resultado += f"👥 {e1.upper()} vs {e2.upper()}\n"
    resultado += f"══════════════════════════════════════════\n\n"

    # Moneyline
    if e1 in raw and e2 in raw:
        p1 = 1/raw[e1]
        p2 = 1/raw[e2]
        suma = p1 + p2
        p1n, p2n = p1/suma, p2/suma
        resultado += f"💰 MONEYLINE:\n"
        resultado += f"   {e1.upper()}: {raw[e1]:.2f} → {p1n:.1%}\n"
        resultado += f"   {e2.upper()}: {raw[e2]:.2f} → {p2n:.1%}\n"
        fav = e1 if raw[e1] < raw[e2] else e2
        resultado += f"   ⭐ FAVORITO: {fav.upper()}\n\n"

    # Over 0.5 (para calcular probabilidad real)
    ov1 = None
    ov2 = None
    for k in raw:
        if e1 in k and ('over 0.5' in k or 'mas de 0.5' in k):
            ov1 = raw[k]
        if e2 in k and ('over 0.5' in k or 'mas de 0.5' in k):
            ov2 = raw[k]

    if ov1 and ov2:
        p1 = 1/ov1
        p2 = 1/ov2
        suma = p1 + p2
        p1n, p2n = p1/suma, p2/suma
        resultado += f"⚾ MÁS DE 0.5 CARRERAS:\n"
        resultado += f"   {e1.upper()}: {ov1:.2f} → {p1n:.1%}\n"
        resultado += f"   {e2.upper()}: {ov2:.2f} → {p2n:.1%}\n\n"

        # Calcular λ (carreras esperadas)
        lambda1 = -math.log(1 - p1n) if p1n < 1 else 2.0
        lambda2 = -math.log(1 - p2n) if p2n < 1 else 2.0
        resultado += f"📊 λ (carreras esperadas):\n"
        resultado += f"   {e1.upper()} = {lambda1:.2f}\n"
        resultado += f"   {e2.upper()} = {lambda2:.2f}\n\n"

        # Probabilidad real por Poisson
        prob_local = 0
        for i in range(15):
            for j in range(15):
                pi = math.exp(-lambda1) * (lambda1**i) / math.factorial(i)
                pj = math.exp(-lambda2) * (lambda2**j) / math.factorial(j)
                if i > j:
                    prob_local += pi * pj
        resultado += f"🎯 PROBABILIDAD REAL:\n"
        resultado += f"   {e1.upper()}: {prob_local:.1%}\n"
        resultado += f"   {e2.upper()}: {1-prob_local:.1%}\n\n"

        # Valor esperado y Kelly
        if e1 in raw:
            ev1 = raw[e1] * prob_local - 1
            kelly1 = max(0, min((raw[e1] * prob_local - 1) / (raw[e1] - 1), 0.05))
            resultado += f"💎 VALOR:\n"
            resultado += f"   {e1.upper()}: EV {ev1:+.1%} | Kelly {kelly1:.1%}\n"
            ev2 = raw[e2] * (1-prob_local) - 1
            kelly2 = max(0, min((raw[e2] * (1-prob_local) - 1) / (raw[e2] - 1), 0.05))
            resultado += f"   {e2.upper()}: EV {ev2:+.1%} | Kelly {kelly2:.1%}\n\n"

    # Total del partido
    for k in raw:
        if 'total' in k and 'over' in k:
            nums = re.findall(r'[\d\.]+', k)
            linea = float(nums[0]) if nums else 0
            over = raw[k]
            under_key = None
            for uk in raw:
                if 'total' in uk and 'under' in uk:
                    unums = re.findall(r'[\d\.]+', uk)
                    if unums and float(unums[0]) == linea:
                        under_key = uk
                        break
            if under_key:
                under = raw[under_key]
                p_over = 1/over
                p_under = 1/under
                suma = p_over + p_under
                p_on, p_un = p_over/suma, p_under/suma
                hold = (p_over + p_under - 1) * 100
                resultado += f"⚾ TOTAL PARTIDO ({linea:.1f}):\n"
                resultado += f"   Over {linea:.1f}: {over:.2f} → {p_on:.1%}\n"
                resultado += f"   Under {linea:.1f}: {under:.2f} → {p_un:.1%}\n"
                resultado += f"   Margen (hold): {hold:.1f}%\n\n"
            break

    return resultado

# ==================== APLICACIÓN KIVY ====================

class AuditorApp(App):
    def build(self):
        self.title = "Auditor de Apuestas"
        layout_main = BoxLayout(orientation='vertical', padding=10, spacing=10)

        titulo = Label(text="🔍 AUDITOR DE MERCADOS", font_size='20sp', size_hint_y=0.08, bold=True)
        layout_main.add_widget(titulo)

        subtitulo = Label(text="⚾ Béisbol | ⚽ Fútbol", font_size='12sp', size_hint_y=0.05)
        layout_main.add_widget(subtitulo)

        self.texto_entrada = TextInput(
            text='', 
            multiline=True, 
            size_hint_y=0.35, 
            font_size='12sp',
            hint_text='Ejemplo:\nPhiladelphia Phillies: 1.47\nMiami Marlins: 2.70\nPhillies over 0.5: 1.20\nMarlins over 0.5: 1.55\ntotal over 8: 1.91\ntotal under 8: 1.89'
        )
        layout_main.add_widget(self.texto_entrada)

        btn = Button(text="📊 ANALIZAR", size_hint_y=0.08, background_color=(0.2, 0.6, 0.2, 1))
        btn.bind(on_press=self.analizar)
        layout_main.add_widget(btn)

        self.resultado_scroll = ScrollView(size_hint_y=0.42)
        self.resultado_label = Label(
            text="Esperando datos...", 
            size_hint_y=None, 
            font_size='12sp',
            halign='left', 
            valign='top'
        )
        self.resultado_label.bind(size=self.resultado_label.setter('text_size'))
        self.resultado_scroll.add_widget(self.resultado_label)
        layout_main.add_widget(self.resultado_scroll)

        return layout_main

    def analizar(self, instance):
        texto = self.texto_entrada.text
        if not texto.strip():
            self.resultado_label.text = "❌ No ingresaste datos"
            return
        resultado = analizar(texto)
        self.resultado_label.text = resultado

if __name__ == "__main__":
    AuditorApp().run()

