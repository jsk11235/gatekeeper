import schemdraw
import schemdraw.elements as elm


def compute_size(statement, length):
    if statement == '':
        return {"left": 0, "right": 0, "down": 0}
    total_paren = 0
    split_idx = 0
    operator = ''
    is_enclosed = statement[0] == '('
    left_size = 1
    right_size = 1
    vert_size = 1
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
    s1_size = compute_size(s1,length)
    s2_size = compute_size(s2,length)

    if operator == '&':
        vert_size = s1_size["down"] + s2_size["down"] + 5 * length
        if s1_size["left"] > s2_size["left"]:
            left_size = s1_size["left"]
        else:
            left_size = s2_size["left"]

        if s1_size["right"] > s2_size["right"]:
            right_size = s1_size["right"]
        else:
            right_size = s2_size["right"]

    elif operator == '|':
        if s1_size["down"] > s2_size["down"]:
            vert_size = s1_size["down"] + 2 * length
        else:
            vert_size = s2_size["down"] + 2 * length
        left_size = s1_size["left"]
        right_size = s1_size["right"] + s2_size["left"] + s2_size["right"] + 8*length

    elif operator == '!':
        left_size = s2_size["left"] + s2_size["right"]
        vert_size = s2_size["down"] + 0.5 * length
        right_size = 0
    return {"left": left_size, "right": right_size, "down": vert_size}


def build_circut(drawing: schemdraw.Drawing, collector, statement, length):
    total_paren = 0
    split_idx = 0
    operator = ''
    print(statement)
    is_enclosed = statement[0] == '('
    print(is_enclosed)
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
    size_s1 = compute_size(s1, length)
    size_s2 = compute_size(s2, length)
    if operator == '&':
        l1 = drawing.add(elm.Line().down(length).at(collector))
        em1 = build_circut(drawing, l1.end, s1, length)
        l2 = drawing.add(elm.Line().down(size_s1["down"]+4*length).at(em1))
        em2 = build_circut(drawing, l2.end, s2, length)
        l3 = drawing.add(elm.Line().down(size_s2["down"]+length).at(em2))
        emitter = l3.end
    elif operator == '|':
        l1 = drawing.add(elm.Line().down(length).at(collector))
        l2 = drawing.add(elm.Line().right(length+size_s1["right"]+size_s2["left"]).at(l1.end))
        l3a = drawing.add(elm.Line().down(size_s1["down"]).at(l2.end))
        l3b = drawing.add(elm.Line().down(size_s2["down"]).at(l1.end))
        em1 = build_circut(drawing, l3a.end, s1, length)
        em2 = build_circut(drawing, l3b.end, s2, length)
        l4 = drawing.add(elm.Line().at(em2).to(em1))
        emitter = l4.end
    elif operator == '!':
        t = drawing.add(elm.BjtNpn(circle=True).right().anchor('collector').at(collector))
        emitter = t.emitter
        drawing.add(elm.Resistor().left(length).at(t.base))
        l2 = drawing.add(elm.Line().up(length))
        drawing.add(elm.Resistor().up(length).at(l2.end))
        drawing.add(elm.Label().label('+'))
        l3 = drawing.add(elm.Line().down(length / 2).at(l2.start))
        em = build_circut(drawing, l3.end, s2, length / 2)
        drawing.add(elm.Line().down(length / 2).at(em))
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
        em = build_circut(draw, line.end, "(" + logic + ")", draw.unit * 0.1)
        draw.add(elm.LED().down().at(em))
        draw.add(elm.Line().down(0.0001 * draw.unit).label('-'))


full_build("(A&B)|(!A&!B)")
