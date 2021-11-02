#
import wx
from wx.core import SB_VERTICAL
import wx.lib.wxcairo
import cairo
from os.path import abspath, join, dirname
import sys

from our_browser.ext_depends import noder_parse_file, noder_parse_text, DATA_PATH
from our_browser.drawing import make_drawable_tree
from our_browser.listview import ListviewControl, connect_listview


class DrawingArea(wx.Panel):
    
    def __init__ (self , *args , **kw):
        super(DrawingArea , self).__init__ (*args , **kw)

        self.scroll_pos = 0
        self.ROOT = None #= make_drawable_tree(ROOT_NODE)
        
        self.SetDoubleBuffered(True)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_UP, self.onClick)
    
    def OnSize(self, event):
        self.Refresh() # MUST have this, else the rectangle gets rendered corruptly when resizing the window!
        event.Skip() # seems to reduce the ammount of OnSize and OnPaint events generated when resizing the window
        
    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        cr = wx.lib.wxcairo.ContextFromDC(dc)
        self.DoDrawing(cr, dc)
        
    def DoDrawing(self, cr, dc):
        size = self.GetSize()

        cr.set_source_rgb (1.0, 1.0, 1.0)
        cr.rectangle(0, 0, size[0], size[1])
        cr.fill()

        self.ROOT.calc_size(size, (0, self.scroll_pos))
        self.ROOT.draw(cr)
    
    def onScrollWin1(self, event):
        print('SCROLL', event.Position)
        self.scroll_pos = -event.Position
        #self.Update()
        self.Refresh()

    def onClick(self, event):
        print('CLICK', event.Position)
        self.ROOT.propagateEvent(event.Position, 'onclick')
        print('~~~', self.ROOT.node)
        self.Refresh()


class Frame(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(Frame, self).__init__(*args, **kwargs) 
        
        self.InitUI()

    def InitUI(self):
        self.SetIcon(wx.Icon(join(DATA_PATH, "our_browser.ico")))

        panel = wx.Panel(self)        
        vbox = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(vbox)        

        self.mainPanel = mainPanel = DrawingArea(panel)
        vbox.Add(mainPanel, 1, wx.EXPAND | wx.ALL, 0)

        scroll = wx.ScrollBar(panel, style=SB_VERTICAL)
        scroll.SetScrollbar(position=0, thumbSize=16, range=1000, pageSize=100)
        vbox.Add(scroll, 0, wx.EXPAND | wx.ALL, 0)

        self.SetSize((800, 600))
        self.SetTitle('Our Browser')
        self.Centre()

        scroll.Bind(wx.EVT_SCROLL, mainPanel.onScrollWin1)


class BrowserApp:

    def __init__(self, html_path=None, html_text='', listview_cls=ListviewControl) -> None:

        self.ROOT_NODE = ROOT_NODE = noder_parse_file(html_path) if html_path else noder_parse_text(html_text)
        connect_listview(ROOT_NODE, listview_cls=listview_cls)

        self.app = wx.App()
        self.frame = Frame(None)

    def update_drawers(self):
        self.frame.mainPanel.ROOT = make_drawable_tree(self.ROOT_NODE)

    def run(self):
        self.update_drawers()
        self._connect_styles(self.ROOT_NODE)
        self.frame.Show(True)
        self.app.MainLoop()

    def _connect_styles(self, node):
        styler = self.ROOT_NODE.styler
        styler.connect_styles_to_node(node)
        for n in node.children:
            self._connect_styles(n)


def main(listview_cls=ListviewControl):
    html_path = sys.argv[1].replace('\\', '/')
    app = BrowserApp(listview_cls=listview_cls, html_path=html_path)
    app.run()


if __name__ == '__main__':
    main()