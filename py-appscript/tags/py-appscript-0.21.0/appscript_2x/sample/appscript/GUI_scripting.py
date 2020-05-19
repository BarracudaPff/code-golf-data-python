from appscript import *
texteditgui = app("System Events").processes["TextEdit"]
app("TextEdit").activate()
mref = texteditgui.menu_bars[1].menus
mref["File"].menu_items["New"].click()
mref["Edit"].menu_items["Paste"].click()
mref["Window"].menu_items["Zoom"].click()