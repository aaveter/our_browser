import wx
import cairo

class ListviewControl:

    def __init__(self, listview) -> None:
        print('-----!!!!!!!!!! ListviewControl:', listview.tag)
        self.listview = listview
        self.template = None
        self.scroll_pos = 0
        self.scroll_started = False
        listview.attrs['data_model'] = self

    def getItemsCount(self):
        return 10000

    def format_template(self, text, i):
        return text.replace('{{ counter }}', str(i))

    def on_wheel(self, event):
        d = event.GetWheelRotation()/4
        self.append_scroll(d)

    def append_scroll(self, d):
        self.scroll_pos -= d
        if self.scroll_pos < 0:
            self.scroll_pos = 0

    def propagateEvent(self, pos, event_name):
        if event_name == 'onclick':
            self.scroll_started = False
        elif event_name == 'ondown':
            if self.isIntoScroll(pos):
                self.scroll_started = pos
        elif event_name == 'onmoving':
            if self.scroll_started:
                d = (self.scroll_started[1] - pos[1]) #* 3
                self.scroll_started = pos
                print('EVENT lv:', pos, event_name, self.isIntoScroll(pos), d)
                self.append_scroll(d)
                return True

    def isIntoScroll(self, pos):
        drawer = self.listview.drawer
        scroll_width = 20
        scroll_right = drawer.pos[0] + drawer.size_calced[0]
        scroll_left = scroll_right - scroll_width
        scroll_top = drawer.pos[1] + scroll_width
        scroll_bottom = drawer.pos[1] + drawer.size_calced[1] - scroll_width
        return scroll_left <= pos[0] < scroll_right and scroll_top <= pos[1] < scroll_bottom
        


def connect_listview(node, listview_cls=ListviewControl):
    if not node:
        return
    for n in node.children:
        if n.tag:
            if n.tag.text == 'listview':
                listview_cls(n)
            elif n.tag.text == 'template':
                if node.tag and node.tag.text =='listview':
                    print('-----!!!!!!!!!! template:', n.tag)
                    node.attrs['data_model'].template = n

        connect_listview(n)


def draw_listview(drawer, listview, cr):
    _items_count = listview.getItemsCount()
    
    template = listview.template.children[0]
    t_drawer = template.drawer
    scroll_pos = listview.scroll_pos

    _ps = lv_pos = getattr(drawer, 'pos', (0, 0))
    _sz = getattr(drawer, 'size_calced', (0, 0))

    _sz = lv_size = drawer.draw_scroll(cr, _ps, _sz)

    lv_top = lv_pos[1]
    lv_bottom = lv_pos[1] + lv_size[1]
    
    if not hasattr(t_drawer, 'text'):
        t_drawer.text = template.text

    _ps = (_ps[0], _ps[1]-scroll_pos)

    #t_drawer.calc_size(_sz, [_ps[0], _ps[1]]) - works into calc_size tree

    w, h = int(lv_pos[0] + lv_size[0] + 10), int(lv_pos[1] + lv_size[1] + 10)
    temp_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    temp_cr = cairo.Context(temp_surface)
    
    for i in range(_items_count):
        bottom = _ps[1] + _sz[1]
        if bottom < lv_top:
            _ps, _sz = t_drawer.add_subnode_pos_size(template, _ps, _sz, margin=t_drawer.calced.margin)
            continue
        
        template.text = listview.format_template(t_drawer.text, i)
        
        _sz = t_drawer.calc_size(_sz, (_ps[0], _ps[1]))

        _ps, _sz = t_drawer.add_subnode_pos_size(template, _ps, _sz, margin=t_drawer.calced.margin)

        t_drawer.draw(temp_cr)

        if _ps[1] > lv_bottom:
            break

    cr.set_source_surface(temp_surface, 0, 0) #, lv_pos[0], lv_pos[1])
    cr.rectangle(lv_pos[0], lv_pos[1], lv_size[0], lv_size[1])
    cr.fill()

    scroll_size = _ps[1] - lv_pos[1]

    drawer.draw_scroll_pos(cr, lv_pos, lv_size, scroll_pos, scroll_size)
