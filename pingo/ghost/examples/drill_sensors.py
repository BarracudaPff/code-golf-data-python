import pingo
board = pingo.ghost.GhostBoard("foo.json")
s_on = board.pins[9]
s_down = board.pins[10]
s_up = board.pins[11]
s_on.mode = pingo.OUT
s_down.mode = pingo.OUT
s_up.mode = pingo.OUT
s_up.hi()