import wx
from .PyDraw import WolfMapViewer

if not '_' in globals()['__builtins__']: #Test de la présence de la fonction de traduction i18n "gettext" et définition le cas échéant pour ne pas créer d'erreur d'exécution
    import gettext
    _=gettext.gettext

class GuiHydrology(WolfMapViewer):

    def __init__(self, parent, title,w=500,h=500):
        super(GuiHydrology, self).__init__(parent, title = title,w=w,h=h)

        parametersmenu = wx.Menu()
        paramgen = parametersmenu.Append(1000,_('Main model'),_('General parameters'))
        paramgen = parametersmenu.Append(1001,_('Basin'),_('Basin parameters'))
        self.menubar.Append(parametersmenu,_('&Parameters'))

        toolsmenu = wx.Menu()
        newtool = toolsmenu.Append(wx.ID_EXECUTE,_('New tool'),_('My new tool...'))
        self.menubar.Append(toolsmenu,_('&Tools'))

    
    def OnMenubar(self,event):

        super().OnMenubar(event)

        id = event.GetId()
        item = self.menubar.FindItemById(id)

        if id==wx.ID_EXECUTE :
            print(_('Do anything !!'))
        if id==1000 :
            self.Parent.mainparams.Show()
        if id==1001 :
            self.Parent.basinparams.Show()


