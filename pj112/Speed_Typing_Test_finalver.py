import tkinter as tk
import time
import threading
import random
import os
import matplotlib.pyplot as plt

class TypeSpeedGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Typing Speed Application')
        self.root.geometry('1280x960')
        current_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_directory, 'texts.txt')

        self.texts = open(file_path, 'r').read().split('\n')

        self.frame = tk.Frame(self.root)

        self.sample_label = tk.Label(self.frame, text=random.choice(self.texts), font=('helvetica', 18), fg='black')
        self.sample_label.grid(row=0, column=0, columnspan=2, padx=5, pady=10)
        self.update_sample_text()

        self.input_entry = tk.Entry(self.frame, width=40, font=('helvetica', 24))
        self.input_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        self.input_entry.bind('<KeyRelease>', self.start)

        self.speed_label = tk.Label(self.frame, text='Speed: \n0.00 CPS\n0.00 CPM\n0.00 WPS\n0.00 WPM', font=('helvetica', 18))
        self.speed_label.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

        self.accuracy_label = tk.Label(self.frame, text='Accuracy: 100.00%', font=('helvetica', 18))
        self.accuracy_label.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        self.incorrect_label = tk.Label(self.frame, text='Incorrect: 0', font=('helvetica', 18))
        self.incorrect_label.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

        self.history_text = tk.Text(self.frame, height=5, width=40, font=('helvetica', 14))
        self.history_text.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

        self.reset_button = tk.Button(self.frame, text='Reset', command=self.reset, font=('helvetica', 24))
        self.reset_button.grid(row=6, column=0, columnspan=2, padx=5, pady=10)

        # เพิ่มการสร้างปุ่มแสดงกราฟ
        self.create_graph_button()

        self.frame.pack(expand=True)

        self.counter = 0 
        self.running = False
        self.history = []  # เพิ่มรายการเพื่อเก็บประวัติการพิมพ์
        self.incorrect_count = 0  # ตัวนับจำนวนการพิมพ์ผิด

        self.root.mainloop()

    def start(self, event):
        if not self.running:
            self.running = True
            t = threading.Thread(target=self.time_thread)
            t.start()

        if not self.sample_label.cget('text').startswith(self.input_entry.get()):
            self.input_entry.config(fg='red')
            self.incorrect_count += 1
            self.update_incorrect_label()
        else:
            self.input_entry.config(fg='black')

        if self.input_entry.get() == self.sample_label.cget('text'):
            self.running = False
            self.input_entry.config(fg='green')
            self.update_sample_text()
            self.save_to_history()
 
    def time_thread(self):
        while self.running:
            time.sleep(0.1)
            self.counter += 0.1
            input_text = self.input_entry.get()
            cps = len(input_text) / self.counter
            cpm = cps * 60
            words = input_text.split()
            wps = len(words) / self.counter
            wpm = wps * 60
            self.speed_label.config(text=f'Speed: \n{cps:.2f} CPS\n{cpm:.2f} CPM\n{wps:.2f} WPS\n{wpm:.2f} WPM')
            self.check_typos()
    
    def update_incorrect_label(self):
        self.incorrect_label.config(text=f'Incorrect: {self.incorrect_count}')

    def check_typos(self):
        sample_text = self.sample_label.cget('text')
        input_text = self.input_entry.get()

        if len(sample_text) == 0:  
            accuracy = 0.0
        else:
            min_len = min(len(sample_text), len(input_text))
            correct_chars = sum(1 for s, i in zip(sample_text[:min_len], input_text[:min_len]) if s == i)
            accuracy = (correct_chars / len(sample_text)) * 100
 
        self.accuracy_label.config(text=f'Accuracy: {accuracy:.2f}%')

    def reset(self):
        self.running = False
        self.counter = 0
        self.speed_label.config(text='Speed: \n0.00 CPS\n0.00 CPM\n0.00 WPS\n0.00 WPM')
        self.accuracy_label.config(text='Accuracy: 100.00%')
        self.incorrect_count = 0
        self.incorrect_label.config(text=f'Incorrect: {self.incorrect_count}')
        self.sample_label.config(text=random.choice(self.texts))
        self.input_entry.delete(0, tk.END)

    def update_sample_text(self):
        self.sample_label.config(text=random.choice(self.texts), fg='black')

    def save_to_history(self):
        input_text = self.input_entry.get()
        cps = len(input_text) / self.counter
        cpm = cps * 60
        words = input_text.split()
        wps = len(words) / self.counter
        wpm = wps * 60
        accuracy = float(self.accuracy_label.cget('text').split(':')[1][:-1])
        entry = f'Text: {input_text}\nSpeed: CPS={cps:.2f}, CPM={cpm:.2f}, WPS={wps:.2f}, WPM={wpm:.2f}\nAccuracy: {accuracy:.2f}%\nIncorrect: {self.incorrect_count}\n\n'
        self.history.append((entry, wpm, self.incorrect_count))  # บันทึกข้อมูลการพิมพ์, WPM และ Incorrect ไว้พร้อมกัน
        self.update_history_text()# อัปเดตข้อความประวัติการพิมพ์

    def update_history_text(self):
        self.history_text.delete(1.0, tk.END)
        for entry in self.history:
            self.history_text.insert(tk.END, entry[0])

    # เมธอดสร้างปุ่มแสดงกราฟ
    def create_graph_button(self):
        self.show_graph_button = tk.Button(self.frame, text='Show Typing Speed Graph', command=self.plot_typing_speed)
        self.show_graph_button.grid(row=7, column=0, columnspan=2, padx=5, pady=10)

    # เมธอดสำหรับแสดงกราฟ
    def plot_typing_speed(self):
        wpm_data = [item[1] for item in self.history]
        accuracy_data = [self.calculate_accuracy(item[0]) for item in self.history]
        incorrect_data = [item[2] for item in self.history]

        num_entries = len(wpm_data)  
        bar_width = 0.35
        index = range(num_entries)

        plt.figure(figsize=(10, 6))

        plt.bar(index, wpm_data, bar_width, color='blue', label='WPM')
        plt.xlabel('Entries')
        plt.ylabel('Words per Minute (WPM)')
        plt.title('Typing Speed Summary')

        plt.bar([i + bar_width for i in index], accuracy_data, bar_width, color='green', label='Accuracy')
        plt.xlabel('Entries')
        plt.ylabel('Accuracy (%)')
        plt.title('Typing Accuracy Summary')

        plt.bar([i + 2 * bar_width for i in index], incorrect_data, bar_width, color='red', label='Incorrect')
        plt.xlabel('Entries')
        plt.ylabel('Incorrect Count')
        plt.title('Typing Incorrect Summary')

        plt.xticks([i + bar_width for i in index], [str(i) for i in range(1, num_entries + 1)])
        plt.legend()
        plt.tight_layout()
        plt.show()

    def calculate_accuracy(self, entry):
        lines = entry.split('\n')
        for line in lines:
           if line.startswith('Accuracy'):
            accuracy_str = line.split(':')[-1].strip()
            return float(accuracy_str[:-1])


app = TypeSpeedGUI()

           
             


    

    


   





        

      
    
  
   






