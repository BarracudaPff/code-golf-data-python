from osax import *
sa = OSAX()
sa.beep(2)
sa.activate()
print(sa.display_dialog("Hello World!"))
print(sa.path_to(k.scripts_folder, from_=k.local_domain))