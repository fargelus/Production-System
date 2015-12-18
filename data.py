__author__ = 'dima'

import json
# from tkinter.messagebox import showerror

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
    size = len(ENTITY)
    matrix = [[_] * size for i in range(size)]

    for i in range(size):
        for j in range(size):
            if i == j:
                matrix[i][j] = 0

    matrix = parse_rels(matrix)

    return matrix


def parse_rels(matrix):
    size = len(matrix)

    for key in sorted(RELS):
        for val in RELS[key]:
            if val['type'] == 'is are':
                to = int(val['to']) - 1
                from_ = int(key) - 1
                matrix[from_][to] = 1
            elif val['type'] == 'part of':
                to = int(val['to']) - 1
                from_ = int(key) - 1
                matrix[from_][to] = 2
            else:
                to = int(val['to']) - 1
                from_ = int(key) - 1
                matrix[from_][to] = 3

    return matrix


def add_rules(matrix):
    """ функция по очереди добавляет правила => формирует новые связи """
    matrix_size = len(matrix)
    matrix = add_transitivity(matrix.copy(), matrix_size)
    matrix = add_links_partof_cont(matrix.copy(), matrix_size)
    matrix = add_similarity(matrix.copy(), matrix_size)
    matrix = add_distributivus(matrix.copy(), matrix_size)

    return matrix


def add_transitivity(matrix, size):
    """ добавляем правило вида x->y->z => x->z """
    verts = make_vertex_list(matrix.copy(), size, 1)

    # формируем различные сочетания вершин
    for vertices_list in verts:
        verts_size = len(vertices_list)
        for i in range(verts_size):
            for j in range(i + 1, verts_size):
                from_ = vertices_list[i]
                to = vertices_list[j]
                if matrix[from_][to] != 1:
                    matrix[from_][to] = 1
                if matrix[to][from_] != 1:
                    matrix[to][from_] = 1

    # формируем список доп.связей
    repeat_vertex = []
    verts_size = len(verts)
    for i in range(verts_size):
        if i > 0:
            copy_list = verts[:i]
            new_size = len(copy_list)
            for each_item in verts[i]:
                for j in range(new_size):
                    if each_item in copy_list[j]:
                        repeat_vertex.append(each_item)

    # созд. доп_связи
    for item in repeat_vertex:
        for i in range(size):
            if matrix[i][item] == 1:
                for j in range(size):
                    if matrix[item][j] == 1:
                        matrix[i][j] = 1
                        matrix[j][i] = 1

    return matrix


def make_vertex_list(matrix, size, type):
    # создадим списки всех изменяющихся вершин
    verts = []
    if type == 1:
        for i in range(size):
            vertices_list = []
            for j in range(size):
                if matrix[i][j] == 1:
                    if i not in vertices_list:
                        vertices_list.append(i)
                    vertices_list.append(j)

            if vertices_list:
                verts.append(vertices_list)
    elif type == 2:
        for i in range(size):
            part_of_list = []
            for j in range(size):
                if matrix[i][j] == 2:
                    if i not in part_of_list:
                        part_of_list.append(i)
                    part_of_list.append(j)

            if part_of_list:
                verts.append(part_of_list)

    else:
        for i in range(size):
            contains_of_list = []
            for j in range(size):
                if matrix[i][j] == 3:
                    if i not in contains_of_list:
                        contains_of_list.append(i)
                    contains_of_list.append(j)

            if contains_of_list:
                verts.append(contains_of_list)
    return verts


def add_links_partof_cont(matrix, size):
    """ добавим правила вида =2 => 3 и наоборот(если что-то part of то наоборот
        contains_of и в обратную сторону) """
    part_of_list = make_vertex_list(matrix, size, 2)
    cont_of_list = make_vertex_list(matrix, size, 3)
    for item in part_of_list:
        from_vertex_list = item[1:]
        to_vertex = item[0]
        for vertex in from_vertex_list:
            matrix[vertex][to_vertex] = 3

    for item in cont_of_list:
        from_vertex_list = item[1:]
        to_vertex = item[0]
        for vertex in from_vertex_list:
            matrix[vertex][to_vertex] = 2

    # доп.связи
    triangles = get_triangle_list()
    vals = list(filter((lambda key: key if (ENTITY[key] == "∠AHC" or ENTITY[key] == "∠BHC") else None),
                       ENTITY.keys()))
    vals = sorted([int(val) - 1 for val in vals])
    for i in range(triangles[0], triangles[-1] + 1):
        for j in range(size):
            if matrix[i][j] == 3:
                if ENTITY[str(j + 1)] == "α":
                    matrix[i][vals[0]] = 3
                    matrix[vals[0]][i] = 2
                if ENTITY[str(j + 1)] == "β":
                    matrix[i][vals[-1]] = 3
                    matrix[vals[-1]][i] = 2

    matrix = add_another_partof_cont_links(part_of_list[:], cont_of_list[:],
                                           matrix.copy(), size)

    side_keys = ["AB", "AC", "BC", "CH", "AH", "BH"]
    side = {ENTITY[key]: key for key in ENTITY.keys() if ENTITY[key] in side_keys}

    for i in range(triangles[0], triangles[-1] + 1):
        tmp_list = [i]
        for j in range(size):
            if matrix[i][j] == 3:
                tmp_list.append(ENTITY[str(j + 1)])

        if "∠AHC" in tmp_list and ENTITY[str(i+1)] != "ΔACB":
            matrix[i][int(side["AH"]) - 1] = 3
            matrix[int(side["AH"]) - 1][i] = 2
            matrix[i][int(side["AC"]) - 1] = 3
            matrix[int(side["AC"]) - 1][i] = 2
            matrix[i][int(side["CH"]) - 1] = 3
            matrix[int(side["CH"]) - 1][i] = 2
        if "∠BHC" in tmp_list and ENTITY[str(i+1)] != "ΔACB":
            matrix[i][int(side["BH"]) - 1] = 3
            matrix[int(side["BH"]) - 1][i] = 2
            matrix[i][int(side["BC"]) - 1] = 3
            matrix[int(side["BC"]) - 1][i] = 2
            matrix[i][int(side["CH"]) - 1] = 3
            matrix[int(side["CH"]) - 1][i] = 2

    return matrix


def add_another_partof_cont_links(part_of_list, cont_of_list, matrix, size):
    for item in part_of_list:
        from_vertex_list = item[1:]
        to_vertex = item[0]
        for j in range(size):
            if matrix[to_vertex][j] == 1:
                for each_item in from_vertex_list:
                    matrix[j][each_item] = 2
                    matrix[each_item][j] = 3

    new_links = []
    for item in cont_of_list:
        to_vertex_list = item[1:]
        from_vertex = item[0]
        for vertex in to_vertex_list:
            for j in range(size):
                if matrix[vertex][j] == 1:
                    matrix[from_vertex][j] = 3
                    matrix[j][from_vertex] = 2
                    new_links.append([from_vertex, j])

    # если что-то часть чего-то большого, то все
    # объекты из которых состоит это что-то являются
    # частью этого супер объекта
    for each_link in new_links:
        to = each_link[-1]
        from_ = each_link[0]
        for i in range(size):
            if matrix[to][i] == 3:
                matrix[from_][i] = 3
                matrix[i][from_] = 2

    return matrix


def add_similarity(matrix, size):
    multiple_objs = make_vertex_list(matrix, size, 3)

    angles_in_obj = []
    for obj in multiple_objs:
        first_one = [obj[0]]
        possible_variants = obj[1:]
        temp_list = list(filter((lambda x: x in range(4, 17)), possible_variants))

        if temp_list:
            first_one.extend(temp_list)
            angles_in_obj.append(first_one)

    matrix = make_similarity(matrix.copy(), angles_in_obj[:])
    matrix = make_ratio(matrix.copy(), size)
    return matrix


def get_simil_triangle_list():
    return [int(keys) - 1 for keys in ENTITY if '~' in ENTITY[keys]]


def make_similarity(matrix, angles_in_obj):
    """ добавляем условие подобия """

    # удаляем прямые углы из последовательности
    right_angles = [4, 5, 10]
    for item in angles_in_obj:
        for r_angle in right_angles:
            if r_angle in item:
                item.remove(r_angle)

    # находим утверждения про подобие
    simil_triangle_list = get_simil_triangle_list()

    angles_size = len(angles_in_obj)
    similarity_list = list()
    for i in range(angles_size):
        for j in range(angles_size-1, -1, -1):
            if i == j:
                continue

            x = str(angles_in_obj[i][0] + 1)
            y = str(angles_in_obj[j][0] + 1)
            if [x, y] in similarity_list or [y, x] in similarity_list:
                break

            operated_list = [(row, col) for row in angles_in_obj[i][1:] for col
                             in angles_in_obj[j][1:]]

            units = list(filter((lambda args, matrix=matrix: matrix[args[0]][args[1]] == 1
                                 and args[0] != args[1]),
                              operated_list))

            if units:
                simil_triangle = [x, y]
                similarity_list.append(simil_triangle)

                # сделать связь подобие и тд
                # узнаём в какой узел вести связь

                link_number = None
                for item in simil_triangle_list:
                    if ENTITY[x] in ENTITY[str(item + 1)] and ENTITY[y] in ENTITY[str(item + 1)]:
                        link_number = item
                        break

                real_x = int(x) - 1
                real_y = int(y) - 1
                matrix[real_x][link_number] = 2
                matrix[link_number][real_x] = 3
                matrix[real_y][link_number] = 2
                matrix[link_number][real_y] = 3
    return matrix


def print_matrix(matrix):
    size = len(matrix)
    for i in range(size):
        for j in range(size):
            print(matrix[i][j], end=' ')
        print()


def parse_matrix(matrix):
    output_filename = '/home/dima/Рабочий стол/Production System/output.txt'
    output = open(output_filename, 'w')

    euristic_filename = '/home/dima/Рабочий стол/Production System/euristic.txt'
    euristic = open(euristic_filename, 'w')
    is_are = ' является '
    part_of = ' часть '
    contains_of = ' состоит из '

    size = len(matrix)
    for i in range(size):
        for j in range(size):
            if matrix[i][j] == 1:
                from_ = ENTITY[str(i+1)]
                to = ENTITY[str(j+1)]
                output.write(from_ + is_are + to + '\n')
            elif matrix[i][j] == 2:
                from_ = ENTITY[str(i+1)]
                to = ENTITY[str(j+1)]
                output.write(from_ + part_of + to + '\n')
            elif matrix[i][j] == 3:
                from_ = ENTITY[str(i+1)]
                to = ENTITY[str(j+1)]
                output.write(from_ + contains_of + to + '\n')
            else:
                pass

    str_to_find = 'AB*AB'
    vals_keys = get_vals_keys()
    key = int(vals_keys[str_to_find]) - 1
    for j in range(size):
        if matrix[key][j] == 1:
            to = ENTITY[str(j+1)]
            euristic.write(str_to_find + is_are + to + '\n')


def make_ratio(matrix, size):
    simil_triangle = sorted(get_simil_triangle_list())

    number_simils = []
    for i in range(simil_triangle[0], simil_triangle[-1] + 1):
        for j in range(size):
            select_col = (lambda row=i, col=j: col if matrix[row][col] == 3 else None)(i, j)
            if select_col:
                number_simils.append(select_col)

    vals_keys = get_vals_keys()
    for item in number_simils:
        for j in range(size):
            if matrix[item][j] == 3:
                if ENTITY[str(j+1)] == "AC" and ENTITY[str(item+1)] != "ΔACB":
                    main_from_ = int(vals_keys["AC*AC"]) - 1
                    main_to = int(vals_keys["AB*AH"]) - 1
                    matrix[main_from_][main_to] = 1
                    matrix[main_to][main_from_] = 1
                if ENTITY[str(j+1)] == "BC" and ENTITY[str(item+1)] != "ΔACB":
                    main_from_ = int(vals_keys["BC*BC"]) - 1
                    main_to = int(vals_keys["AB*BH"]) - 1
                    matrix[main_from_][main_to] = 1
                    matrix[main_to][main_from_] = 1

    matrix = divide_multiple_objects(matrix.copy())

    new_part_of_list = make_vertex_list(matrix.copy(), size, 2)
    new_cont_of_list = make_vertex_list(matrix.copy(), size, 3)
    matrix = add_another_partof_cont_links(new_part_of_list, new_cont_of_list, matrix.copy(), size)

    # если что-то состоит из одинаковых элементов
    # с чем-то, то делаем между ними связь является
    new_cont_of_list = make_vertex_list(matrix.copy(), size, 3)
    out = []
    in_ = []
    for i in range(len(new_cont_of_list)):
        mult_obj = new_cont_of_list[i][0]
        parts = new_cont_of_list[i][1:]
        for j in range(len(new_cont_of_list) - 1, -1, -1):
            if i == j:
                continue
            compare_mult_obj = new_cont_of_list[j][0]
            compare_parts = new_cont_of_list[j][1:]
            if compare_parts == parts \
                    and mult_obj not in compare_parts and compare_mult_obj not in parts:
                out.append(mult_obj)
                in_.append(compare_mult_obj)

    for key_from, key_to in zip(out, in_):
        if matrix[key_from][key_to] != 1:
            matrix[key_from][key_to] = 1
        if matrix[key_to][key_from] != 1:
            matrix[key_to][key_from] = 1

    return matrix


def get_vals_keys():
    return {ENTITY[key]: key for key in ENTITY.keys()}


def divide_multiple_objects(matrix):
    """ сделать связи part of, contains of для составных
        объектов """
    vals_keys = get_vals_keys()
    mult_objects = get_multiple_obj()
    mult_objects = sorted([obj for obj in mult_objects if '~' not in ENTITY[str(obj+1)]])

    for item in mult_objects:
        object = ENTITY[str(item+1)]
        parsed_string = ''.join(c if (c.isalpha() or c == '*' or c == '~') else ' ' for c in object)
        if len(parsed_string) == 5:
            matrix = divide_simple(item, parsed_string, matrix.copy(),
                                       vals_keys.copy())
        else:
            simple_objs = parsed_string.split(' ')
            for obj in simple_objs:
                if obj:
                    obj = obj.strip()
                    val = int(vals_keys[obj]) - 1
                    matrix[item][val] = 3
                    matrix[val][item] = 2
                    if len(obj) == 5:
                        matrix = divide_simple(item, obj, matrix.copy(),
                                               vals_keys.copy())

    return matrix


def divide_simple(number, composite_obj, matrix, vals_keys):
    simple_objs = composite_obj.split('*')
    if simple_objs[0] == simple_objs[1]:
        val = int(vals_keys[simple_objs[0]]) - 1
        matrix[number][val] = 3
        matrix[val][number] = 2
    else:
        for obj in simple_objs:
            val = int(vals_keys[obj]) - 1
            matrix[number][val] = 3
            matrix[val][number] = 2
    return matrix


def get_multiple_obj():
    return [int(key) - 1 for key in ENTITY if len(ENTITY[key]) > 4]


def get_triangle_list():
    return sorted([int(key) - 1 for key in ENTITY if 'Δ' in ENTITY[key]
                     and len(ENTITY[key]) == 4])


def add_distributivus(matrix, size):
    composite_objs = get_multiple_obj()
    composite_objs = [obj for obj in composite_objs if '+' in ENTITY[str(obj+1)]]
    composite_objs.sort()

    for each_item in composite_objs:
        object = ENTITY[str(each_item + 1)]
        parsed_string = ''.join(c if c.isalpha() else ' ' for c in object)
        list_of_objects = parsed_string.split(' ')
        unique = []
        for i in range(len(list_of_objects)):
            for j in range(len(list_of_objects) - 1, -1, -1):
                if i == j:
                    continue
                if list_of_objects[i] == list_of_objects[j]:
                    if abs(i-j) >= 2:
                        if list_of_objects[i] not in unique:
                            unique.append(list_of_objects[i])
        if unique:
            matrix = make_new_obj(object, unique, matrix.copy(), size)

    return matrix


def make_new_obj(obj, unique, matrix, size):
    val = unique[0]
    new_str = ''
    location = -1
    indexes = []
    while True:
        location = obj.find(val, location + 1)
        if location == -1:
            break
        else:
            indexes.append(location + 3)

    new_str += val + '*('
    for i in indexes:
        j = i
        while True:
            if obj[j] == ' ':
                new_str += ' + '
                break
            if j == len(obj) - 1:
                new_str += obj[j] + ')'
                break
            new_str += obj[j]
            j += 1

    left_braces = new_str.find('(') + 1
    right_braces = new_str.find(')')
    find_object = new_str[left_braces:right_braces]

    val_keys = get_vals_keys()
    if find_object in val_keys.keys():
        number = int(val_keys[find_object]) - 1
        for j in range(size):
            if matrix[number][j] == 1:
                match_obj = ENTITY[str(j+1)]
                new_str = new_str[:left_braces - 1] + match_obj
                if new_str in val_keys.keys():
                    number_to_connect = int(val_keys[new_str]) - 1
                    number_from_connect = int(val_keys[obj]) - 1
                    matrix[number_from_connect][number_to_connect] = 1
                    matrix[number_to_connect][number_from_connect] = 1
                    for k in range(size):
                        if matrix[number_from_connect][k] == 1:
                            if ENTITY[str(k+1)] != new_str:
                                matrix[k][number_to_connect] = 1
                                matrix[number_to_connect][k] = 1

    return matrix


def main(records):
    parse_base(records)
    matrix = make_graph(records)
    matrix = add_rules(matrix.copy())
    parse_matrix(matrix)
