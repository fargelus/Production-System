__author__ = 'dima'

import json
from tkinter.messagebox import showerror

ENTITY = dict()
RELS = dict()
_ = float('inf')


def parse_base(records):
    global ENTITY, RELS, RULES

    json_str = str()
    for line in records:
        json_str += line

    parse_data = json.loads(json_str)
    ENTITY = parse_data["Entity"]
    RELS = parse_data["Rels"]


def make_graph(records):
    parse_base(records)

    size = len(ENTITY)
    matrix = [[_] * size for i in range(size)]

    for i in range(size):
        for j in range(size):
            if i == j:
                matrix[i][j] = 0

    for key, value in sorted(RELS.items()):
        matrix[int(key)-1][int(value)-1] = 1

    return matrix


def add_rules(matrix):
    """ добавляем правило вида x->y->z => x->z """
    new_rels = dict()
    for key in sorted(RELS):
        for reverse_key in sorted(RELS, reverse=True):
            if key == reverse_key:
                break
            if RELS[key] == reverse_key:
                new_rels[key] = RELS[reverse_key]

    for key, value in new_rels.items():
        matrix[int(key)-1][int(value)-1] = 1

    print(matrix)


def parse_matrix(matrix):
    filename = '/home/dima/Рабочий стол/Production System/output.txt'
    try:
        f_write = open(filename, 'w')
        size = len(matrix)
        is_a = 'есть'
        space = ' '
        for i in range(size):
            for j in range(size):
                if matrix[i][j] != 0 and matrix[i][j] != _:
                    line = ENTITY[str(i+1)] + space + is_a + space + ENTITY[str(j+1)] + '\n'
                    f_write.write(line)

    except IOError:
        showerror('Ошибка', 'Невозможно открыть файл для записи')


def main(records):
    parse_base(records)
    matrix = make_graph(records)
    add_rules(matrix)
    parse_matrix(matrix)


