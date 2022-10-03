import schemdraw
import schemdraw.elements as elm

sizes = {}


def compute_size(statement, drawing):
    global sizes
    if statement in sizes.keys():
        return sizes[statement]
    if statement == '':
        return {"left": 0.1 * drawing.unit,
                "right": 0.1 * drawing.unit,
                "vert": 0.1 * drawing.unit,
                "hang": 0,
                "no_hang":False}
    total_paren = 0
    split_idx = 0
    operator = ''
    is_enclosed = statement[0] == '('
    left_size = 0.5 * drawing.unit
    right_size = 0.5 * drawing.unit
    vert_size = 0.5 * drawing.unit
    hang_size = 0
    no_hang = False
    if is_enclosed:
        start = 1
        end = len(statement) - 1
    else:
        start = 0
        end = len(statement)
    for i in range(start, end):
        c = statement[i]
        if c == '(':
            total_paren += 1
        elif c == ')':
            total_paren -= 1
        elif total_paren == 0 and (c == '&' or c == '!' or c == '|'):
            operator = statement[i]
            split_idx = i
            break
    if len(operator) == 0:
        operator = statement

    s1 = statement[start:split_idx]
    s2 = statement[split_idx + 1:end]
    s1_size = compute_size(s1, drawing)
    s2_size = compute_size(s2, drawing)

    if operator == '&':
        vert_size = s1_size["vert"] + s2_size["vert"] + drawing.unit
        hang_size = vert_size
        if s1_size["left"] > s2_size["left"]:
            left_size = s1_size["left"]
        else:
            left_size = s2_size["left"]

        if s1_size["right"] > s2_size["right"]:
            right_size = s1_size["right"]
        else:
            right_size = s2_size["right"]
        no_hang = True
    elif operator == '|':
        hang_size = vert_size
        if s1_size["vert"] > s2_size["vert"]:
            vert_size = s1_size["vert"] + 1.5 * drawing.unit
        else:
            vert_size = s2_size["vert"] + 1.5 * drawing.unit
        left_size = s2_size["left"]
        right_size = s1_size["right"] + s1_size["left"] + s2_size["right"] + 0.5 * drawing.unit
        no_hang = True
    elif operator == '!':
        hang_size = 0.2 * drawing.unit + s2_size["hang"]
        left_size = s2_size["left"] + s2_size["right"] + 0.4 * drawing.unit
        vert_size = s2_size["vert"] + 0.5 * drawing.unit
        right_size = 0
    sizes[statement] = {"left": left_size, "right": right_size, "vert": vert_size, "hang": hang_size,
                        "no_hang": no_hang}
    return {"left": left_size, "right": right_size, "vert": vert_size, "hang": hang_size,
            "no_hang": no_hang}


def build_circut(drawing: schemdraw.Drawing, collector, statement):
    total_paren = 0
    split_idx = 0
    operator = ''
    is_enclosed = statement[0] == '('
    if statement == '':
        return collector
    if is_enclosed:
        start = 1
        end = len(statement) - 1
    else:
        start = 0
        end = len(statement)
    for i in range(start, end):
        c = statement[i]
        if c == '(':
            total_paren += 1
        elif c == ')':
            total_paren -= 1
        elif total_paren == 0 and (c == '&' or c == '!' or c == '|'):
            operator = statement[i]
            split_idx = i
            break
    if len(operator) == 0:
        operator = statement

    s1 = statement[start:split_idx]
    s2 = statement[split_idx + 1:end]
    size_s1 = compute_size(s1, drawing)
    size_s2 = compute_size(s2, drawing)
    if size_s1['no_hang']:
        size_s1['hang'] = 0
    if size_s2['no_hang']:
        size_s2['hang'] = 0
    if operator == '&':
        l1 = drawing.add(elm.Line().down(0.1 * drawing.unit).at(collector))
        em1 = build_circut(drawing, l1.end, s1)
        l2 = drawing.add(elm.Line().down(size_s1["hang"] + 0.1 * drawing.unit).at(em1))
        em2 = build_circut(drawing, l2.end, s2)
        l3 = drawing.add(elm.Line().down(size_s2["hang"] + 0.1 * drawing.unit).at(em2))
        emitter = l3.end
    elif operator == '|':
        max_down = max(size_s1['hang'], size_s2['hang'])
        l1 = drawing.add(elm.Line().down(0.5 * drawing.unit).at(collector))
        l2 = drawing.add(elm.Line().right(0.5 * drawing.unit + size_s1['left'] + size_s2['right']).at(l1.end))
        l5a = drawing.add(elm.Line().down(0.5 * drawing.unit).at(l2.end))
        l5b = drawing.add(elm.Line().down(0.5 * drawing.unit).at(l1.end))
        em1 = build_circut(drawing, l5a.end, s1)
        em2 = build_circut(drawing, l5b.end, s2)
        l3a = drawing.add(elm.Line().down(max_down).at(em1))
        l3b = drawing.add(elm.Line().down(max_down).at(em2))
        l4 = drawing.add(elm.Line().at(l3b.end).to(l3a.end))
        emitter = l4.end
    elif operator == '!':
        t = drawing.add(elm.BjtNpn(circle=True).right().anchor('collector').at(collector))
        emitter = t.emitter
        drawing.add(elm.Resistor().left(size_s2["right"] + 0.2 * drawing.unit).at(t.base))
        l2 = drawing.add(elm.Line().up(0.1 * drawing.unit))
        drawing.add(elm.Resistor().up(0.1 * drawing.unit).at(l2.end))
        drawing.add(elm.Label().label('+'))
        l3 = drawing.add(elm.Line().down(0.1 * drawing.unit).at(l2.start))
        em = build_circut(drawing, l3.end, s2)
        drawing.add(elm.Line().down(0.1 * drawing.unit).at(em))
        drawing.add(elm.Label().label('-'))
    else:
        t = drawing.add(elm.BjtNpn(circle=True).right().anchor('collector').at(collector).label(operator))
        emitter = t.emitter
    return emitter


def full_build(logic):
    with schemdraw.Drawing() as draw:
        line = draw.add(elm.Line().down(0.0001 * draw.unit))
        draw.add(elm.Resistor().up().at(line.start))
        draw.add(elm.Label().label('+'))
        draw.add(elm.LED().down().at(line.end))
        l2 = draw.add(elm.Line().down(0.0001 * draw.unit))
        em = build_circut(draw, l2.end, '(' + logic + ')')
        draw.add(elm.Line().down(draw.unit).label('-').at(em))


p = "!(A&B)"
q = "!(C|!D)"
full_build(f'({q})|({p})')