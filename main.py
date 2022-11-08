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
                "hang": 0.5 * drawing.unit}
    total_paren = 0
    split_idx = 0
    operator = ''
    left_size = 0.5 * drawing.unit
    right_size = 0.5 * drawing.unit
    hang_size = 0.5 * drawing.unit
    start = 0
    end = len(statement)
    min_paren = 0
    used_min_paren = 0
    for i in range(start, end):
        c = statement[i]
        if c == '(':
            if i == total_paren:
                min_paren += 1
            total_paren += 1
        elif c == ')':
            total_paren -= 1
            if total_paren < min_paren:
                min_paren -= 1
        elif total_paren == min_paren and (c == '&' or (c == '!' and operator == '') or c == '|'):
            operator = statement[i]
            used_min_paren = min_paren
            split_idx = i
    if len(operator) == 0:
        operator = statement

    s1 = statement[used_min_paren:split_idx]
    s2 = statement[split_idx + 1:end - used_min_paren]
    s1_size = compute_size(s1, drawing)
    s2_size = compute_size(s2, drawing)

    if operator == '&':
        vert_size = s1_size["hang"] + s2_size["hang"] + drawing.unit * 0.7
        hang_size = vert_size
        if s1_size["left"] > s2_size["left"]:
            left_size = s1_size["left"]
        else:
            left_size = s2_size["left"]

        if s1_size["right"] > s2_size["right"]:
            right_size = s1_size["right"]
        else:
            right_size = s2_size["right"]
    elif operator == '|':
        if s1_size['hang'] > s2_size['hang']:
            hang_size = 0.8 * drawing.unit + s1_size['hang']
        else:
            hang_size = 0.8 * drawing.unit + s2_size['hang']
        left_size = s2_size["left"]
        right_size = s1_size["right"] + s1_size["left"] + s2_size["right"] + 0.5 * drawing.unit
    elif operator == '!':
        hang_size = 0.5 * drawing.unit + s2_size["hang"]
        left_size = s2_size["left"] + s2_size["right"] + 0.4 * drawing.unit
        right_size = 0.5 * drawing.unit
    sizes[statement] = {"left": left_size, "right": right_size, "hang": hang_size}
    return {"left": left_size, "right": right_size, "hang": hang_size}


def build_circut(drawing: schemdraw.Drawing, collector, statement):
    total_paren = 0
    split_idx = 0
    operator = ''
    print(statement)
    if statement == '':
        return collector
    start = 0
    end = len(statement)
    min_paren = 0
    used_min_paren = 0
    allow_not = True
    for i in range(start, end):
        c = statement[i]
        if c == '(':
            if i == total_paren:
                min_paren += 1
            total_paren += 1
        elif c == ')':
            total_paren -= 1
            if total_paren < min_paren:
                min_paren -= 1
        elif total_paren == min_paren and (c == '&' or (c == '!' and operator == '') or c == '|'):
            operator = statement[i]
            used_min_paren = min_paren
            split_idx = i

    print(total_paren)
    if len(operator) == 0:
        operator = statement

    s1 = statement[used_min_paren:split_idx]
    s2 = statement[split_idx + 1:end - used_min_paren]
    size_s1 = compute_size(s1, drawing)
    size_s2 = compute_size(s2, drawing)
    if operator == '&':
        l1 = drawing.add(elm.Line().down(0.2 * drawing.unit).at(collector))
        em1 = build_circut(drawing, l1.end, s1)
        l2 = drawing.add(elm.Line().down(0.3 * drawing.unit).at(em1))
        em2 = build_circut(drawing, l2.end, s2)
        l3 = drawing.add(elm.Line().down(0.2 * drawing.unit).at(em2))
        emitter = l3.end
    elif operator == '|':
        l1 = drawing.add(elm.Line().down(0.5 * drawing.unit).at(collector))
        l2 = drawing.add(elm.Line().right(0.5 * drawing.unit + size_s1['left'] + size_s2['right']).at(l1.end))
        l5a = drawing.add(elm.Line().down(0.3 * drawing.unit).at(l2.end))
        l5b = drawing.add(elm.Line().down(0.3 * drawing.unit).at(l1.end))
        em1 = build_circut(drawing, l5a.end, s1)
        em2 = build_circut(drawing, l5b.end, s2)
        if size_s1['hang'] > size_s2['hang']:
            l3c = drawing.add(elm.Line().down(size_s1['hang'] - size_s2['hang']).at(em2))
            l4 = drawing.add(elm.Line().at(l3c.end).to(em1))
        elif size_s2['hang'] > size_s1['hang']:
            l3c = drawing.add(elm.Line().down(size_s2['hang'] - size_s1['hang']).at(em1))
            l4 = drawing.add(elm.Line().at(em2).to(l3c.end))
        else:
            l4 = drawing.add(elm.Line().at(em2).to(em1))
        emitter = l4.end
    elif operator == '!':
        t = drawing.add(elm.BjtNpn(circle=True).right().anchor('collector').at(collector))
        drawing.add(elm.Resistor().left(size_s2["right"] + 0.2 * drawing.unit).at(t.base))
        l2 = drawing.add(elm.Line().up(0.1 * drawing.unit))
        drawing.add(elm.Resistor().up(0.1 * drawing.unit).at(l2.end))
        drawing.add(elm.Label().label('+'))
        l3 = drawing.add(elm.Line().down(0.1 * drawing.unit).at(l2.start))
        em = build_circut(drawing, l3.end, s2)
        drawing.add(elm.Line().down(0.1 * drawing.unit).at(em))
        drawing.add(elm.Label().label('-'))
        l4 = drawing.add(elm.Line().down(size_s2['hang']).at(t.emitter))
        emitter = l4.end
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
# full_build(f'{q}')
full_build(f'({q}|((!(E|F))&{p}))|(!(G&H))')
