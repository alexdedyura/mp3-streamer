import http.server
import socketserver
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# Порт для HTTP сервера
PORT = 8000
selected_files = []
current_file_index = 0
server_thread = None

class MP3RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global selected_files, current_file_index
        
        if selected_files and self.path == "/stream":
            self.send_response(200)
            self.send_header('Content-type', 'audio/mpeg')
            self.send_header('Content-Disposition', 'inline')
            self.end_headers()
            
            with open(selected_files[current_file_index], 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    self.wfile.write(data)
        else:
            self.send_error(404, "File Not Found: %s" % self.path)

def start_server():
    global server_thread, selected_files
    
    if not selected_files:
        messagebox.showwarning("Выбор файла", "Пожалуйста, выберите MP3 файлы для стриминга.")
        return
    
    Handler = MP3RequestHandler
    httpd = socketserver.TCPServer(("", PORT), Handler)
    
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    messagebox.showinfo("Сервер запущен", f"Сервер запущен на порту {PORT}. Перейдите по адресу http://localhost:{PORT}/stream для прослушивания.")

def stop_server():
    global server_thread
    
    if server_thread:
        http.server.TCPServer.shutdown()
        server_thread.join()
        server_thread = None
        messagebox.showinfo("Сервер остановлен", "Сервер успешно остановлен.")

def select_files():
    global selected_files
    selected_files = filedialog.askopenfilenames(filetypes=[("MP3 files", "*.mp3")])
    if selected_files:
        file_list.delete(0, tk.END)  # Очищаем текущий список
        for file in selected_files:
            file_list.insert(tk.END, os.path.basename(file))

def switch_song():
    global current_file_index
    
    selected_index = file_list.curselection()
    if selected_index:
        current_file_index = selected_index[0]
        messagebox.showinfo("Переключение песни", f"Текущая песня: {os.path.basename(selected_files[current_file_index])}")
    else:
        messagebox.showwarning("Выбор песни", "Пожалуйста, выберите песню из списка.")

# Создание GUI с использованием tkinter
root = tk.Tk()
root.title("MP3 Стример")

file_label = tk.Label(root, text="Выберите MP3 файлы для стриминга:", width=50)
file_label.pack(pady=10)

select_button = tk.Button(root, text="Выбрать MP3 файлы", command=select_files)
select_button.pack(pady=5)

file_list = tk.Listbox(root, width=50, height=10)
file_list.pack(pady=10)

switch_button = tk.Button(root, text="Переключить песню", command=switch_song)
switch_button.pack(pady=5)

start_button = tk.Button(root, text="Запустить сервер", command=start_server)
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Остановить сервер", command=stop_server)
stop_button.pack(pady=5)

root.mainloop()
