import asynctest
import asyncio
from neo.Network.syncmanager import SyncManager
class SyncManagerTestCase(asynctest.TestCase):
	async def test_start(self):
		syncmgr = SyncManager(asynctest.MagicMock)
		syncmgr.reset()
		syncmgr.nodemgr.running = True
		syncmgr.run_service = asynctest.CoroutineMock()
		syncmgr.block_health = asynctest.CoroutineMock()
		await syncmgr.start()
		self.assertNotEqual(syncmgr.service_task, None)
		self.assertNotEqual(syncmgr.health_task, None)
class ShutdownSyncManagerTests(asynctest.TestCase):
	def setUp(self) -> None:
		self.syncmgr = SyncManager(asynctest.MagicMock)
		self.syncmgr.reset()
		self.syncmgr.nodemgr.running = True
		self.syncmgr.block_health = asynctest.CoroutineMock()
	async def test_normal_shutdown(self):
		self.syncmgr.block_health.side_effect = asyncio.CancelledError()
		await self.syncmgr.start()
		await self.syncmgr.shutdown()
		self.assertTrue(self.syncmgr.health_task.cancelled())
	async def test_shutdown_with_service_exception(self):
		self.syncmgr.raise_exception = False
		self.syncmgr.block_health.side_effect = asyncio.CancelledError()
		self.syncmgr.check_timeout = asynctest.CoroutineMock()
		self.syncmgr.sync = asynctest.CoroutineMock()
		await self.syncmgr.start()
		await asyncio.sleep(0.5)
		self.syncmgr.sync.side_effect = Exception()
		self.syncmgr.raise_exception = True
		await asyncio.sleep(0.5)
		await self.syncmgr.shutdown()
		self.assertTrue(self.syncmgr.health_task.cancelled())