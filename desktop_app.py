#!/usr/bin/env python3
"""
Personal Assistant - Desktop GUI Application
Tkinter + Claude AI
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import anthropic
import os
from dotenv import load_dotenv
from datetime import datetime
import threading

# .env dosyasını yükle
load_dotenv()

# API Key kontrolü
API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not API_KEY:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        'API Key Hatası',
        'HATA: ANTHROPIC_API_KEY bulunamadı!\n\n'
        '.env dosyasında ANTHROPIC_API_KEY=sk-... ayarlayın'
    )
    root.destroy()
    exit()

# Claude client
client = anthropic.Anthropic(api_key=API_KEY)

# Chat history
chat_history = []

class PersonalAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title('🤖 Personal Assistant - Claude AI')
        self.root.geometry('900x700')
        self.root.configure(bg='#f0f0f0')

        # Title
        title_frame = tk.Frame(root, bg='#2c3e50', height=60)
        title_frame.pack(fill=tk.X)

        title_label = tk.Label(
            title_frame,
            text='🤖 Kişisel Asistan - Claude AI',
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=10)

        # Chat display area
        chat_frame = tk.Frame(root)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(chat_frame, text='Sohbet Geçmişi:', font=('Arial', 10, 'bold')).pack(anchor='w')

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            height=20,
            width=90,
            font=('Courier', 10),
            bg='#1e1e1e',
            fg='#00ff00',
            state='disabled',
            wrap=tk.WORD
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=5)

        # Configure tags for styling
        self.chat_display.tag_config('user', foreground='#00ffff')
        self.chat_display.tag_config('assistant', foreground='#00ff00')
        self.chat_display.tag_config('time', foreground='#ffff00')
        self.chat_display.tag_config('error', foreground='#ff0000')

        # Input area
        input_frame = tk.Frame(root)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(input_frame, text='Sorunuz:', font=('Arial', 10, 'bold')).pack(anchor='w')

        self.input_text = tk.Entry(
            input_frame,
            font=('Arial', 11),
            width=80
        )
        self.input_text.pack(fill=tk.X, pady=5)
        self.input_text.bind('<Return>', lambda e: self.send_message())

        # Buttons frame
        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        send_btn = tk.Button(
            button_frame,
            text='📤 Gönder',
            command=self.send_message,
            width=15,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold')
        )
        send_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(
            button_frame,
            text='🗑️ Temizle',
            command=self.clear_chat,
            width=15,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 10, 'bold')
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        exit_btn = tk.Button(
            button_frame,
            text='❌ Çık',
            command=root.quit,
            width=15,
            bg='#34495e',
            fg='white',
            font=('Arial', 10, 'bold')
        )
        exit_btn.pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_var = tk.StringVar(value='✅ Hazır')
        status_bar = tk.Label(
            root,
            textvariable=self.status_var,
            font=('Arial', 9),
            bg='#ecf0f1',
            anchor='w',
            relief=tk.SUNKEN
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Initial message
        self.add_to_display('🤖 Kişisel Asistan başlatıldı. Bir soru sorun!', 'info')

    def add_to_display(self, text, tag='assistant'):
        """Chat display'e mesaj ekle"""
        self.chat_display.config(state='normal')

        if tag == 'user':
            time_str = datetime.now().strftime('%H:%M')
            self.chat_display.insert(tk.END, f'\n👤 SEN ', 'user')
            self.chat_display.insert(tk.END, f'({time_str}): ', 'time')
            self.chat_display.insert(tk.END, f'{text}\n', 'user')
        elif tag == 'assistant':
            time_str = datetime.now().strftime('%H:%M')
            self.chat_display.insert(tk.END, f'\n🤖 ASISTAN ', 'assistant')
            self.chat_display.insert(tk.END, f'({time_str}): ', 'time')
            self.chat_display.insert(tk.END, f'{text}\n', 'assistant')
        elif tag == 'error':
            self.chat_display.insert(tk.END, f'\n❌ {text}\n', 'error')
        else:
            self.chat_display.insert(tk.END, f'\n{text}\n')

        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')

    def get_claude_response(self, user_message):
        """Claude'dan yanıt al"""
        try:
            # Konuşma geçmişini hazırla
            messages = [
                {'role': msg['role'], 'content': msg['content']}
                for msg in chat_history
            ]
            messages.append({'role': 'user', 'content': user_message})

            # Claude API çağrısı
            response = client.messages.create(
                model='claude-3-5-sonnet-20241022',
                max_tokens=2000,
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            return f'Hata: {str(e)}'

    def send_message(self):
        """Mesaj gönder"""
        user_input = self.input_text.get().strip()

        if not user_input:
            self.status_var.set('⚠️ Lütfen bir soru yazın')
            return

        # Kullanıcı mesajını ekle
        self.add_to_display(user_input, 'user')
        chat_history.append({'role': 'user', 'content': user_input})

        # Input temizle
        self.input_text.delete(0, tk.END)

        # Durumu güncelle
        self.status_var.set('⏳ Claude yanıt veriyor...')
        self.root.update()

        # Yanıt al (ayrı thread'de)
        def get_response():
            response = self.get_claude_response(user_input)
            self.add_to_display(response, 'assistant')
            chat_history.append({'role': 'assistant', 'content': response})
            self.status_var.set('✅ Hazır')

        thread = threading.Thread(target=get_response, daemon=True)
        thread.start()

    def clear_chat(self):
        """Sohbeti temizle"""
        chat_history.clear()
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state='disabled')
        self.add_to_display('🤖 Sohbet temizlendi. Yeni soru sorun!', 'info')
        self.status_var.set('✅ Hazır')

def main():
    """Ana program"""
    root = tk.Tk()
    app = PersonalAssistantApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
