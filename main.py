import schemdraw
import schemdraw.elements as elm

def build_circut(drawing: schemdraw.Drawing, collector, statement, length):
    total_paren = 0
    split_idx = 0
    print(statement)
    for i in range(1, len(statement) - 1):
        if statement[i] == '(':
            total_paren += 1
        elif statement[i] == ')':
            total_paren -= 1
        elif total_paren == 0:
            operator = statement[i]
            split_idx = i
            break

    s1 = statement[1:split_idx]
    s2 = statement[split_idx + 1:-1]

    if operator == '&':
        l1 = drawing.add(elm.Line().down(length).at(collector))
        em1 = build_circut(drawing, l1.end, s1, length)
        l2 = drawing.add(elm.Line().down(length).at(em1))
        em2 = build_circut(drawing, l2.end, s2, length)
        l3 = drawing.add(elm.Line().down(length).at(em2))
        emitter = l3.end
    elif operator == '|':
        l1 = drawing.add(elm.Line().down(length).at(collector))
        l2 = drawing.add(elm.Line().left().at(l1.end))
        l3a = drawing.add(elm.Line().down(length).at(l2.end))
        l3b = drawing.add(elm.Line().down(length).at(l1.end))
        em1 = build_circut(drawing, l3a.end, s1, length)
        em2 = build_circut(drawing, l3b.end, s2, length)
        l4 = drawing.add(elm.Line().at(em2).to(em1))
        emitter = l4.end
    elif operator == '!':
        t = drawing.add(elm.BjtNpn(circle=True).right().anchor('collector').at(collector))
        emitter = t.emitter
        l1 = drawing.add(elm.Line().left(length).at(t.base))
        drawing.add(elm.Resistor().left().at(t.base))
        l2 = drawing.add(elm.Line().up(length))
        drawing.add(elm.Resistor().up().at(l2.end))
        drawing.add(elm.Label().label('+'))
        l3 = drawing.add(elm.Line().down(length / 2).at(l2.start))
        em = build_circut(drawing, l3.end, s2, length)
        drawing.add(elm.Line().down(length/2).at(em))
        drawing.add(elm.Label().label('-'))
    else:
        t = drawing.add(elm.BjtNpn(circle=True).right().anchor('collector').at(collector).label(operator))
        emitter = t.emitter
    return emitter


with schemdraw.Drawing() as draw:
    line = draw.add(elm.Line().down(0.0001 * draw.unit))
    draw.add(elm.Resistor().up().at(line.start))
    draw.add(elm.Label().label('+'))
    build_circut(draw, line.end, "(((A)|(B))&"
                                   "(!((B)&(A))))", draw.unit * 0.3)
    draw.add(elm.LED().down())
    draw.add(elm.Line().down(0.0001 * draw.unit).label('-'))