__author__ = 'dima'

""" тестируем gui по продукционнке """

from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *
from data import *


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
                open_file = askopenfilename()
                self.entry.insert(0, open_file)
        else:
            open_file = askopenfilename()
            self.entry.insert(0, open_file)

    def read_file(self):
        filename = self.entry.get()

        try:
            file_to_read = open(filename)
            data_in_file = file_to_read.readlines()


            p_ent = data_in_file.index('Entitys:\n')
            p_rel = data_in_file.index('Relations:\n')
            p_rule = data_in_file.index('Rules:\n')
            end = len(data_in_file)

            read_entitys(data_in_file, p_ent + 1, p_rel - 1)
            make_relations(data_in_file, p_rel + 1, p_rule - 1)
            parse_rules(data_in_file, p_rule + 1, end)

        except FileNotFoundError as err:
            showerror('Open error', str(err))

        except UnboundLocalError:  # ?
            pass

        finally:
            file_to_read.close()

        self.destroy()

        mw = MainWindow()

        for item in data_in_file:
            mw.source_txt.insert(END, item)

        mw.mainloop()


class MainWindow(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.master.title('Продукционная система')
        self.pack()
        self.focus_set()

        self.src_label = Label(self, text='Исходные сущности и связи', font=('times', 12, 'italic bold'))
        self.dest_label = Label(self, text='Вывод', font=('times', 12, 'italic bold'))

        self.source_txt = Text(self)
        self.process_btn = Button(self, text='=>', font='16', command=self.get_result)
        self.sys_txt = Text(self)

        self.bind('<Return>', lambda event: self.get_result())

        self.place_widgets()

    def place_widgets(self):
        self.src_label.grid(row=0, column=0)
        self.source_txt.grid(row=1, column=0)
        self.process_btn.grid(row=1, column=1)
        self.dest_label.grid(row=0, column=2)
        self.sys_txt.grid(row=1, column=2)

    def get_result(self):
        get_new_entitys()

        for item in open('output.txt'):
            self.sys_txt.insert(END, item)


if __name__ == '__main__':
    Entrance().mainloop()


