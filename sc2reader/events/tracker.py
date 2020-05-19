from __future__ import absolute_import, print_function, unicode_literals, division
import functools
from sc2reader.events.base import Event
from sc2reader.utils import Length
clamp = functools.partial(max, 0)
class TrackerEvent(Event):
	"""
    Parent class for all tracker events.
    """
	def __init__(self, frames):
		self.frame = frames % 2 ** 32
		self.second = self.frame >> 4
		self.name = self.__class__.__name__
	def load_context(self, replay):
		pass
	def _str_prefix(self):
		return "{0}\t ".format(Length(seconds=int(self.frame / 16)))
	def __str__(self):
		return self._str_prefix() + self.name
class PlayerSetupEvent(TrackerEvent):
	""" Sent during game setup to help us organize players better """
	def __init__(self, frames, data, build):
		super(PlayerSetupEvent, self).__init__(frames)
		self.pid = data[0]
		self.type = data[1]
		self.uid = data[2]
		self.sid = data[3]
class PlayerStatsEvent(TrackerEvent):
	"""
    Player Stats events are generated for all players that were in the game even if they've since
    left every 10 seconds. An additional set of stats events are generated at the end of the game.
    When a player leaves the game, a single PlayerStatsEvent is generated for that player and no
    one else. That player continues to generate PlayerStatsEvents at 10 second intervals until the
    end of the game.
    In 1v1 games, the above behavior can cause the losing player to have 2 events generated at the
    end of the game. One for leaving and one for the  end of the game.
    """
	def __init__(self, frames, data, build):
		super(PlayerStatsEvent, self).__init__(frames)
		self.pid = data[0]
		self.player = None
		self.stats = data[1]
		self.minerals_current = clamp(self.stats[0])
		self.vespene_current = clamp(self.stats[1])
		self.minerals_collection_rate = clamp(self.stats[2])
		self.vespene_collection_rate = clamp(self.stats[3])
		self.workers_active_count = clamp(self.stats[4])
		self.minerals_used_in_progress_army = clamp(self.stats[5])
		self.minerals_used_in_progress_economy = clamp(self.stats[6])
		self.minerals_used_in_progress_technology = clamp(self.stats[7])
		self.minerals_used_in_progress = self.minerals_used_in_progress_army + self.minerals_used_in_progress_economy + self.minerals_used_in_progress_technology
		self.vespene_used_in_progress_army = clamp(self.stats[8])
		self.vespene_used_in_progress_economy = clamp(self.stats[9])
		self.vespene_used_in_progress_technology = clamp(self.stats[10])
		self.vespene_used_in_progress = self.vespene_used_in_progress_army + self.vespene_used_in_progress_economy + self.vespene_used_in_progress_technology
		self.resources_used_in_progress = self.minerals_used_in_progress + self.vespene_used_in_progress
		self.minerals_used_current_army = clamp(self.stats[11])
		self.minerals_used_current_economy = clamp(self.stats[12])
		self.minerals_used_current_technology = clamp(self.stats[13])
		self.minerals_used_current = self.minerals_used_current_army + self.minerals_used_current_economy + self.minerals_used_current_technology
		self.vespene_used_current_army = clamp(self.stats[14])
		self.vespene_used_current_economy = clamp(self.stats[15])
		self.vespene_used_current_technology = clamp(self.stats[16])
		self.vespene_used_current = self.vespene_used_current_army + self.vespene_used_current_economy + self.vespene_used_current_technology
		self.resources_used_current = self.minerals_used_current + self.vespene_used_current
		self.minerals_lost_army = clamp(self.stats[17])
		self.minerals_lost_economy = clamp(self.stats[18])
		self.minerals_lost_technology = clamp(self.stats[19])
		self.minerals_lost = self.minerals_lost_army + self.minerals_lost_economy + self.minerals_lost_technology
		self.vespene_lost_army = clamp(self.stats[20])
		self.vespene_lost_economy = clamp(self.stats[21])
		self.vespene_lost_technology = clamp(self.stats[22])
		self.vespene_lost = self.vespene_lost_army + self.vespene_lost_economy + self.vespene_lost_technology
		self.resources_lost = self.minerals_lost + self.vespene_lost
		self.minerals_killed_army = clamp(self.stats[23])
		self.minerals_killed_economy = clamp(self.stats[24])
		self.minerals_killed_technology = clamp(self.stats[25])
		self.minerals_killed = self.minerals_killed_army + self.minerals_killed_economy + self.minerals_killed_technology
		self.vespene_killed_army = clamp(self.stats[26])
		self.vespene_killed_economy = clamp(self.stats[27])
		self.vespene_killed_technology = clamp(self.stats[28])
		self.vespene_killed = self.vespene_killed_army + self.vespene_killed_economy + self.vespene_killed_technology
		self.resources_killed = self.minerals_killed + self.vespene_killed
		self.food_used = clamp(self.stats[29]) / 4096.0
		self.food_made = clamp(self.stats[30]) / 4096.0
		self.minerals_used_active_forces = clamp(self.stats[31])
		self.vespene_used_active_forces = clamp(self.stats[32])
		self.ff_minerals_lost_army = clamp(self.stats[33]) if build >= 26490 else None
		self.ff_minerals_lost_economy = clamp(self.stats[34]) if build >= 26490 else None
		self.ff_minerals_lost_technology = clamp(self.stats[35]) if build >= 26490 else None
		self.ff_vespene_lost_army = clamp(self.stats[36]) if build >= 26490 else None
		self.ff_vespene_lost_economy = clamp(self.stats[37]) if build >= 26490 else None
		self.ff_vespene_lost_technology = clamp(self.stats[38]) if build >= 26490 else None
	def __str__(self):
		return self._str_prefix() + "{0: >15} - Stats Update".format(str(self.player))
class UnitBornEvent(TrackerEvent):
	"""
    Generated when a unit is created in a finished state in the game. Examples include the Marine,
    Zergling, and Zealot (when trained from a gateway). Units that enter the game unfinished (all
    buildings, warped in units) generate a :class:`UnitInitEvent` instead.
    Unfortunately, units that are born do not have events marking their beginnings like
    :class:`UnitInitEvent` and :class:`UnitDoneEvent` do. The closest thing to it are the
    :class:`~sc2reader.event.game.CommandEvent` game events where the command is a train unit
    command.
    """
	def __init__(self, frames, data, build):
		super(UnitBornEvent, self).__init__(frames)
		self.unit_id_index = data[0]
		self.unit_id_recycle = data[1]
		self.unit_id = self.unit_id_index << 18 | self.unit_id_recycle
		self.unit = None
		self.unit_type_name = data[2].decode("utf8")
		self.control_pid = data[3]
		self.upkeep_pid = data[4]
		self.unit_upkeeper = None
		self.unit_controller = None
		self.x = data[5]
		self.y = data[6]
		self.location = (self.x, self.y)
		if build < 27950:
			self.x = self.x * 4
			self.y = self.y * 4
			self.location = (self.x, self.y)
	def __str__(self):
		return self._str_prefix() + "{0: >15} - Unit born {1}".format(str(self.unit_upkeeper), self.unit)
class UnitDiedEvent(TrackerEvent):
	"""
    Generated when a unit dies or is removed from the game for any reason. Reasons include
    morphing, merging, and getting killed.
    """
	def __init__(self, frames, data, build):
		super(UnitDiedEvent, self).__init__(frames)
		self.unit_id_index = data[0]
		self.unit_id_recycle = data[1]
		self.unit_id = self.unit_id_index << 18 | self.unit_id_recycle
		self.unit = None
		self.killer_pid = data[2]
		self.killer = None
		self.killing_player_id = data[2]
		self.killing_player = None
		self.x = data[3]
		self.y = data[4]
		self.location = (self.x, self.y)
		self.killing_unit_index = None
		self.killing_unit_recycle = None
		self.killing_unit_id = None
		self.killing_unit = None
		if build < 27950:
			self.x = self.x * 4
			self.y = self.y * 4
			self.location = (self.x, self.y)
		else:
			self.killing_unit_index = data[5]
			self.killing_unit_recycle = data[6]
			if self.killing_unit_index:
				self.killing_unit_id = self.killing_unit_index << 18 | self.killing_unit_recycle
	def __str__(self):
		return self._str_prefix() + "{0: >15} - Unit died {1}.".format(str(self.unit.owner), self.unit)
class UnitOwnerChangeEvent(TrackerEvent):
	"""
    Generated when either ownership or control of a unit is changed. Neural Parasite is an example
    of an action that would generate this event.
    """
	def __init__(self, frames, data, build):
		super(UnitOwnerChangeEvent, self).__init__(frames)
		self.unit_id_index = data[0]
		self.unit_id_recycle = data[1]
		self.unit_id = self.unit_id_index << 18 | self.unit_id_recycle
		self.unit = None
		self.control_pid = data[2]
		self.upkeep_pid = data[3]
		self.unit_upkeeper = None
		self.unit_controller = None
	def __str__(self):
		return self._str_prefix() + "{0: >15} took {1}".format(str(self.unit_upkeeper), self.unit)
class UnitTypeChangeEvent(TrackerEvent):
	"""
    Generated when the unit's type changes. This generally tracks upgrades to buildings (Hatch,
    Lair, Hive) and mode switches (Sieging Tanks, Phasing prisms, Burrowing roaches). There may
    be some other situations where a unit transformation is a type change and not a new unit.
    """
	def __init__(self, frames, data, build):
		super(UnitTypeChangeEvent, self).__init__(frames)
		self.unit_id_index = data[0]
		self.unit_id_recycle = data[1]
		self.unit_id = self.unit_id_index << 18 | self.unit_id_recycle
		self.unit = None
		self.unit_type_name = data[2].decode("utf8")
	def __str__(self):
		return self._str_prefix() + "{0: >15} - Unit {1} type changed to {2}".format(str(self.unit.owner), self.unit, self.unit_type_name)
class UpgradeCompleteEvent(TrackerEvent):
	"""
    Generated when a player completes an upgrade.
    """
	def __init__(self, frames, data, build):
		super(UpgradeCompleteEvent, self).__init__(frames)
		self.pid = data[0]
		self.player = None
		self.upgrade_type_name = data[1].decode("utf8")
		self.count = data[2]
	def __str__(self):
		return self._str_prefix() + "{0: >15} - {1} upgrade completed".format(str(self.player), self.upgrade_type_name)
class UnitInitEvent(TrackerEvent):
	"""
    The counter part to :class:`UnitDoneEvent`, generated by the game engine when a unit is
    initiated. This applies only to units which are started in game before they are finished.
    Primary examples being buildings and warp-in units.
    """
	def __init__(self, frames, data, build):
		super(UnitInitEvent, self).__init__(frames)
		self.unit_id_index = data[0]
		self.unit_id_recycle = data[1]
		self.unit_id = self.unit_id_index << 18 | self.unit_id_recycle
		self.unit = None
		self.unit_type_name = data[2].decode("utf8")
		self.control_pid = data[3]
		self.upkeep_pid = data[4]
		self.unit_upkeeper = None
		self.unit_controller = None
		self.x = data[5]
		self.y = data[6]
		self.location = (self.x, self.y)
		if build < 27950:
			self.x = self.x * 4
			self.y = self.y * 4
			self.location = (self.x, self.y)
	def __str__(self):
		return self._str_prefix() + "{0: >15} - Unit initiated {1}".format(str(self.unit_upkeeper), self.unit)
class UnitDoneEvent(TrackerEvent):
	"""
    The counter part to the :class:`UnitInitEvent`, generated by the game engine when an initiated
    unit is completed. E.g. warp-in finished, building finished, morph complete.
    """
	def __init__(self, frames, data, build):
		super(UnitDoneEvent, self).__init__(frames)
		self.unit_id_index = data[0]
		self.unit_id_recycle = data[1]
		self.unit_id = self.unit_id_index << 18 | self.unit_id_recycle
		self.unit = None
	def __str__(self):
		return self._str_prefix() + "{0: >15} - Unit {1} done".format(str(self.unit.owner), self.unit)
class UnitPositionsEvent(TrackerEvent):
	"""
    Generated every 15 seconds. Marks the positions of the first 255 units that were damaged in
    the last interval. If more than 255 units were damaged, then the first 255 are reported and
    the remaining units are carried into the next interval.
    """
	def __init__(self, frames, data, build):
		super(UnitPositionsEvent, self).__init__(frames)
		self.first_unit_index = data[0]
		self.items = data[1]
		self.units = dict()
		self.positions = list()
		unit_index = self.first_unit_index
		for i in range(0, len(self.items), 3):
			unit_index += self.items[i]
			x = self.items[i + 1]
			y = self.items[i + 2]
			if build < 27950:
				x = x * 4
				y = y * 4
			self.positions.append((unit_index, (x, y)))
	def __str__(self):
		return self._str_prefix() + "Unit positions update"