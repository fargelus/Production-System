__author__ = 'dima'

""" тестируем gui по продукционнке """

from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *
import data


class Entrance(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack()
        self.master.title('Выберите путь')

        self.open_btn = Button(self, text='Выбрать', font=('times', 12), command=self.read_file)
        self.overview_btn = Button(self, text='Обзор', font=('times', 12), command=self.overview_click)

        self.entry = Entry(self, width=30)
        self.entry.focus_set()
        self.entry.bind('<Return>', lambda event: self.read_file())
        self.place_widgets()

    def place_widgets(self):
        self.entry.pack(side=TOP, fill=X, expand=YES)
        self.open_btn.pack(side=LEFT, fill=X, expand=YES)
        self.overview_btn.pack(side=RIGHT, fill=X, expand=YES)

    def overview_click(self):
        path = self.entry.get()
        if path:
            answ = askyesno('Внимание', 'Файл по указанному пути готов для открытия.\n'
                            'Вы хотите выбрать другой файл?')
            if answ:
                self.entry.delete(0, END)
                open_file = askopenfilename(defaultextension='.db', filetypes=[('Database', '.db'),
                                                                               ('SQLite3', '.sqlite3'),
                                                                               ('SQLite', '.sqlite')])
                self.entry.insert(0, open_file)
        else:
            open_file = askopenfilename(defaultextension='.db', filetypes=[('Database', '.db'),
                                                                           ('SQLite3', '.sqlite3'),
                                                                           ('SQLite', '.sqlite')])
            self.entry.insert(0, open_file)

    def read_file(self):
        filename = self.entry.get()

        if '.json' not in filename:
            if '.JSON' not in filename:
                showinfo('Формат базы знаний', 'База знаний представляет файл в формате JSON =>\n'
                                               'необходимо чтобы расширение файла было '
                                               'в этом формате')
                return

        showinfo('Бинго', 'База знаний успешно считана')
        self.destroy()
        file_handler = open(filename, 'r')
        base = file_handler.readlines()
        MainWindow(text_=base).mainloop()


class MainWindow(Frame):
    def __init__(self, text_, parent=None):
        Frame.__init__(self, parent)
        self.master.title('Продукционная система')
        self.pack()
        self.focus_set()

        self.text = text_

        self.src_label = Label(self, text='Исходные сущности и связи', font=('times', 12, 'italic bold'))
        self.dest_label = Label(self, text='Вывод', font=('times', 12, 'italic bold'))

        self.source_txt = Text(self)
        for item in text_:
            self.source_txt.insert(END, item)

        self.process_btn = Button(self, text='=>', font='16', command=self.get_result)

        self.sys_txt = Text(self)

        self.buffer_btn = Button(self, text='Показать буфер', font=('Times', 12, 'italic bold'),
                                 command=self.show_buffer, width=67, pady=5)

        self.bind('<Return>', lambda event: self.get_result())

        self.place_widgets()

    def place_widgets(self):
        self.src_label.grid(row=0, column=0)
        self.source_txt.grid(row=1, column=0)
        self.process_btn.grid(row=1, column=1)
        self.dest_label.grid(row=0, column=2)
        self.sys_txt.grid(row=1, column=2)
        self.buffer_btn.grid(row=2, column=2)

    def get_result(self):
        data.main(self.text)

        for item in open('output.txt'):
            self.sys_txt.insert(END, item)

    def show_buffer(self):
        pass

if __name__ == '__main__':
    Entrance().mainloop()


