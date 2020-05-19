import datetime
from appscript import *
calendarname = "Home"
start = datetime.time(19, 0, 0)
end = datetime.time(21, 0, 0)
summary = "Watch dinner & eat teevee"
app("iCal").calendars[calendarname].events.end.make(new=k.event, with_properties={k.start_date: start, k.end_date: end, k.summary: summary})