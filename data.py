__author__ = 'dima'


list_of_entitys = list()

relations = list()      # списки смежности
_ = float('inf')


def read_entitys(data, src, dest):
    """
    :param data: данные в файле
    :param src: позиция для считывания сущности
    :param dest: позиция останова
    :return: None
    """
    while src < dest:
        line = data[src]
        line = line.strip()
        key = int(line[0])
        val = line[2:]
        entity = dict()
        entity[key] = val
        list_of_entitys.append(entity)
        src += 1

    for item in list_of_entitys:
        print(item)


def make_relations(data, src, dest):
    """
    :param data: данные в файле
    :param src: позиция для считывания отн-я
    :param dest: позиция останова
    :return:
    """
    relation_val_list = []
    while src < dest:
        line = data[src]
        line = line.strip()
        digit_list = [int(line[i]) - 1 for i in range(len(line)) if line[i].isdigit()]
        print(digit_list)
        relation_val_list.append(digit_list)
        src += 1

    fill_relations_matrix(relation_val_list)


def fill_relations_matrix(relation_val_list):
    """  заполняем нашу матрицу списком отношений -> создаём граф """
    global relations
    n = len(list_of_entitys)
    relations = [[_] * n for i in range(n)]

    for i in range(len(relation_val_list)):
        for j in range(len(relation_val_list) - 1):
            x = relation_val_list[i][j]
            y = relation_val_list[i][j+1]
            relations[x][y] = 1

    for i in range(n):
        for j in range(n):
            if i == j:
                relations[i][j] = 0


def parse_rules(data, src, dest):
    """ парсим правила, если что-то x то y """
    global relations
    rules_dict = dict()
    while src < dest:
        line = data[src]
        line = line.strip()
        pos_then = line.find('->')
        condition = line[:pos_then]
        conclusion = line[pos_then + 1:]
        condition_entity = [int(condition[i]) - 1 for i in range(len(condition)) if condition[i].isdigit()]
        print(condition_entity)
        conclusion_entity = [int(conclusion[i]) - 1 for i in range(len(conclusion)) if conclusion[i].isdigit()]
        print(conclusion_entity)
        src += 1
        rules_dict[condition_entity[0]] = conclusion_entity[0]

    size = len(relations)
    for key in rules_dict:
        for i in range(size):
            if relations[i][key] == 1:
                relations[i][rules_dict[key]] = 1


def get_new_entitys():
    """ обходим граф, и выводим в файл,
        новые сущности """
    file_to_write = open('output.txt', 'w')
    file_to_write.write('New Entitys:\n')

    n = len(relations)
    for i in range(n):
        for j in range(n):
            if relations[i][j] == 1:
                src = i + 1
                dest = j + 1
                copy_entitys = list_of_entitys[:]
                flag = False
                while len(copy_entitys) > 0:
                    entity = copy_entitys.pop(0)
                    if src in entity.keys():
                        flag = True
                        print(entity[src], '->', end=' ', file=file_to_write)
                    if dest in entity.keys() and flag:
                        flag = False
                        print(entity[dest], file=file_to_write)

    file_to_write.close()