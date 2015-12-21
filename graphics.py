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
                open_file = askopenfilename(defaultextension='.json', filetypes=[('JSON', '.json')])
                self.entry.insert(0, open_file)
        else:
            open_file = askopenfilename(defaultextension='.json', filetypes=[('JSON', '.json')])
            self.entry.insert(0, open_file)

    def read_file(self):
        filename = self.entry.get()

        if '.json' not in filename:
            if '.JSON' not in filename:
                showinfo('Формат базы знаний', 'База знаний представляет файл в формате JSON =>\n'
                                               'необходимо чтобы расширение файла было '
                                               'в этом формате')
                return

        try:
            file_handler = open(filename, 'r')
        except FileNotFoundError as err:
            showerror('Ошибка открытия', str(err))
            self.entry.delete(0, END)
            return

        base = file_handler.readlines()
        if base:
            showinfo('Бинго', 'База знаний успешно считана')
            self.destroy()
            MainWindow(text_=base).mainloop()
        else:
            showwarning('Предупреждение', 'Возможно файл пуст. Я не могу его прочесть')


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

        self.src_bar = Scrollbar(self)
        self.src_bar.config(command=self.source_txt.yview)
        self.source_txt.config(yscrollcommand=self.src_bar.set)

        self.process_btn = Button(self, text='=>', font='16', command=self.get_result)

        self.sys_txt = Text(self)

        self.sys_bar = Scrollbar(self)
        self.sys_bar.config(command=self.sys_txt.yview)
        self.sys_txt.config(yscrollcommand=self.sys_bar.set)

        self.buffer_btn = Button(self, text='Показать буфер', font=('Times', 12, 'italic bold'),
                                 command=self.show_buffer, width=67, pady=5)
        self.buffer_btn['state'] = DISABLED

        self.bind('<Return>', lambda event: self.get_result())

        self.place_widgets()

    def place_widgets(self):
        self.src_label.grid(row=0, column=0)
        self.src_bar.grid(row=1, column=1, sticky=NS)
        self.source_txt.grid(row=1, column=0)
        self.process_btn.grid(row=1, column=2)
        self.dest_label.grid(row=0, column=3)
        self.sys_bar.grid(row=1, column=4, sticky=NS)
        self.sys_txt.grid(row=1, column=3)
        self.buffer_btn.grid(row=2, column=3)

    def get_result(self):
        data.main(self.text)

        if self.sys_txt.get('1.0', END+'-1c'):
            self.sys_txt.delete('1.0', END)

        for item in open('euristic.txt'):
            self.sys_txt.insert(END, item)

        if self.sys_txt.get('1.0', END+'-1c'):
            self.buffer_btn['state'] = NORMAL

    def show_buffer(self):
        if self.sys_txt.get('1.0', END+'-1c'):
            self.sys_txt.delete('1.0', END)
        for item in open('output.txt'):
            self.sys_txt.insert(END, item)


if __name__ == '__main__':
    Entrance().mainloop()
