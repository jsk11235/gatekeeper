import schemdraw
import schemdraw.elements as elm


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

    if operator == '&':
        l1 = drawing.add(elm.Line().down(length).at(collector))
        em1 = build_circut(drawing, l1.end, s1, length / 2)
        l2 = drawing.add(elm.Line().down(length).at(em1))
        em2 = build_circut(drawing, l2.end, s2, length / 2)
        l3 = drawing.add(elm.Line().down(length).at(em2))
        emitter = l3.end
    elif operator == '|':
        l1 = drawing.add(elm.Line().down(length).at(collector))
        l2 = drawing.add(elm.Line().right(4*length).at(l1.end))
        l3a = drawing.add(elm.Line().down(length).at(l2.end))
        l3b = drawing.add(elm.Line().down(length).at(l1.end))
        em1 = build_circut(drawing, l3a.end, s1, length / 2)
        em2 = build_circut(drawing, l3b.end, s2, length / 2)
        l4 = drawing.add(elm.Line().at(em2).to(em1))
        emitter = l4.end
    elif operator == '!':
        t = drawing.add(elm.BjtNpn(circle=True).right().anchor('collector').at(collector))
        emitter = t.emitter
        drawing.add(elm.Resistor().left().at(t.base))
        l2 = drawing.add(elm.Line().up(length))
        drawing.add(elm.Resistor().up().at(l2.end))
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
        em = build_circut(draw, line.end, "("+logic+")", draw.unit * 0.3)
        draw.add(elm.LED().down().at(em))
        draw.add(elm.Line().down(0.0001 * draw.unit).label('-'))


full_build("(A|B)&(!(A&B))")
