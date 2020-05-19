class date(real_date):
	def strftime(self, fmt):
		return strftime(self, fmt)
class datetime(real_datetime):
	def strftime(self, fmt):
		return strftime(self, fmt)
	def combine(self, date, time):
		return datetime(date.year, date.month, date.day, time.hour, time.minute, time.microsecond, time.tzinfo)
	def date(self):
		return date(self.year, self.month, self.day)
def new_date(d):
	"""Generate a safe date from a datetime.date object."""
	return date(d.year, d.month, d.day)
def new_datetime(d):
	"""
    Generate a safe datetime from a datetime.date or datetime.datetime object.
    """
	kw = [d.year, d.month, d.day]
	if isinstance(d, real_datetime):
		kw.extend([d.hour, d.minute, d.second, d.microsecond, d.tzinfo])
	return datetime(*kw)
_illegal_formatting = re.compile(r"((^|[^%])(%%)*%[sy])")
def _findall(text, substr):
	sites = []
	i = 0
	while True:
		j = text.find(substr, i)
		if j == -1:
			break
		sites.append(j)
		i = j + 1
	return sites
def strftime(dt, fmt):
	if dt.year >= 1900:
		return super(type(dt), dt).strftime(fmt)
	illegal_formatting = _illegal_formatting.search(fmt)
	if illegal_formatting:
		msg = "strftime of dates before 1900 does not handle {0}"
		raise TypeError(msg.format(illegal_formatting.group(0)))
	year = dt.year
	delta = 2000 - year
	off = 6 * (delta // 100 + delta // 400)
	year += off
	year += ((2000 - year) // 28) * 28
	timetuple = dt.timetuple()
	s1 = time.strftime(fmt, (year,) + timetuple[1:])
	sites1 = _findall(s1, str(year))
	s2 = time.strftime(fmt, (year + 28,) + timetuple[1:])
	sites2 = _findall(s2, str(year + 28))
	sites = []
	for site in sites1:
		if site in sites2:
			sites.append(site)
	s = s1
	syear = "%04d" % (dt.year,)
	for site in sites:
		s = s[:site] + syear + s[site + 4 :]
	return s