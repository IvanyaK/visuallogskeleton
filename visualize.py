from graphviz import Digraph
from collections import defaultdict

# Часть программы, отвечающая за визуализацию лога событий в модели logskeleton
def find_pair(element, tuples): # Функция, которая находит второй элемент в паре
    for tuple_item in tuples:
        if tuple_item[0] == element:
            return tuple_item[1]
        elif tuple_item[1] == element:
            return tuple_item[0]
    return None
def find_first(element, tuples): # Функция, которая проверяет, стоит ли элемент в паре первым
    for t in tuples:
        if element == t[0]:
            return True


def find_max_in_tuples(dictionary, tuple_list): # Находит максимальное значение в парах (используется для специальных словарей)
    max_value = -float('inf')
    max_key = None

    for pair in tuple_list:
        for element in pair:
            if element in dictionary:
                if dictionary[element] > max_value:
                    max_value = dictionary[element]
                    max_key = element
    return max_value


def group_connected_tuples(tuple_list): # Функция, которая находит и составляет группы связанных элементов по эквивалентности (требует доработки)
    groups = defaultdict(list)
    element_to_group = {}
    group_counter = 0

    for tuple_item in tuple_list:
        a, b = tuple_item
        a_group = element_to_group.get(a)
        b_group = element_to_group.get(b)

        if a_group is None and b_group is None:
            current_group = group_counter
            group_counter += 1
            groups[current_group].append(tuple_item)
            element_to_group[a] = current_group
            element_to_group[b] = current_group
        elif a_group is not None and b_group is None:
            groups[a_group].append(tuple_item)
            element_to_group[b] = a_group
        elif b_group is not None and a_group is None:
            groups[b_group].append(tuple_item)
            element_to_group[a] = b_group
        elif a_group == b_group:
            groups[a_group].append(tuple_item)
        else:
            if len(groups[a_group]) < len(groups[b_group]):
                small_group, large_group = a_group, b_group
            else:
                small_group, large_group = b_group, a_group

            for item in groups[small_group]:
                groups[large_group].append(item)
                for element in item:
                    element_to_group[element] = large_group

            groups[large_group].append(tuple_item)
            element_to_group[a] = large_group
            element_to_group[b] = large_group

            del groups[small_group]

    result = {}
    element_to_value = {}

    for group in groups.values():
        key = str(group)
        value = len(group)
        result[key] = value
        for tuple_item in group:
            for element in tuple_item:
                element_to_value[element] = value

    return result, element_to_value
def visualize_model(model): # Основная функция визуализации
    always_after = model.get("always_after", [])
    always_before = model.get("always_before", [])
    directly_follows = model.get("directly_follows", [])
    equivalence = model.get("equivalence", [])
    never_together = model.get("never_together", [])
    activ_freq = model["activ_freq"].items()
    list_activ_freq = model.get("activ_freq", [])

    dot = Digraph("LogSkeleton", format="png", engine="dot")
    dot.attr(rankdir="TB", splines="polyline", bgcolor="white")
    dot.attr("node",
             shape="Mrecord",
             style="filled",
             fontname="Sans",
             fontsize="14")

    # - Строим диоды (рёбра, направленные в одну сторону)
    df = []
    for a, b in directly_follows:
        if (b,a) in df:
            continue
        df.append((a,b))
        dot.edge(a, b, color="sienna", penwidth="2")

    # - Исключаем повторяющиеся рёбра
    setdf = set(df)

    inp_a = []
    inp_b = []
    for a, b in always_after:
        if a == '▶' and (a,b) not in never_together and (b,a) not in never_together:
            inp_a.append((a,b))
            continue
        if b == '■' and (a,b) not in never_together and (b,a) not in never_together:
            inp_b.append((a,b))
            continue

    filtered_inp_a = [i for i in inp_a if i not in setdf]
    filtered_inp_b = [i for i in inp_b if i not in setdf]
    r = []

    # - Строим рёбра с отношением ответа (response)
    for a,b in always_after:
        if a == '▶':
            if b == '■':
                continue
            elif any(a in s for s in df) and (a, b) not in filtered_inp_a:
                continue
        if b == '■' and any(b in s for s in df) and (a, b) not in filtered_inp_b:
            continue
        if (b,a) in r:
            continue
        if (a,b) in equivalence and (a,b) not in directly_follows:
            r.append((a,b))
            dot.edge(a, b, color="#0000CD", penwidth="2")

    groups, counts = group_connected_tuples(r) # - Объединяем вершины в группы
    dict_counts = dict.fromkeys(list_activ_freq, 0) # - Создаем словарь с счетчиком того, сколько раз вершина встречалась в диодах
    for a, b in df:
        if a in dict_counts:
            dict_counts[a] += 1
        if b == '■' and b in dict_counts:
            dict_counts[b] += 1

    # - Строим вершины графа
    for act, cnt in activ_freq:
        if act not in counts:
            counts[act] = dict_counts[act]
        eq_elem = find_pair(act, r)
        if eq_elem == None:
            eq_elem = find_pair(act, equivalence)
        ord_elem = list(list_activ_freq.keys())
        if ((ord_elem.index(act) < ord_elem.index(eq_elem)) and act != '▶') or eq_elem == '▶':
            eq_elem = act

        lo, hi = min(cnt), max(cnt)
        if lo != hi:
            interval = f"{lo}..{hi}"
        elif lo == 0 and hi == 0:
            interval = f"{lo}..1"
        else:
            interval = str(hi)

        label = f"{{ {act} | {{ {eq_elem} | {counts[act]} | {interval} }} }}"
        dot.node(act, label=label, fillcolor='antiquewhite')

    # - Строим рёбра с отношением не существования (not co-existence)
    for a, b in never_together:
        if (find_first(a, r) and find_first(b, r)) and (a,b) not in equivalence and (b,a) not in equivalence:
            dot.edge(a, b, color="black", dir="both", arrowhead="tee", arrowtail="tee")
            break

    dot.render('log_skeleton_graph', view=True, cleanup=True)
