import pytest
from app.worker.worker_manager import WorkerManager
import pytest_asyncio

@pytest_asyncio.fixture
async def worker_manager():
    manager = WorkerManager(max_workers=2, auto_start=False)
    manager._start_worker_task()
    yield manager
    await manager.shutdown()
