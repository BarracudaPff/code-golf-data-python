from appscript import *
finder = app("Finder")
finder.activate()
w = finder.Finder_windows[1].target.get()
w.files[its.name_extension.isin(["htm", "html"])].select()