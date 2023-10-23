import json
from enum import Enum
from typing import List

from p0_backend.lib.redis import database

TaskId = str


class TaskCacheKey(Enum):
    NOTIFICATION = "p0.notification_tasks"
    REVOKED_TASKS = "p0.revoked_tasks"


class TaskCache:
    def __init__(self):
        self._cache = database

    def get_tasks(self, task_type: TaskCacheKey) -> List[TaskId]:
        return self._get_list(task_type)

    def revoked_tasks(self) -> List[TaskId]:
        return self._get_list(TaskCacheKey.REVOKED_TASKS)

    def add_revoked_task(self, task_id: TaskId) -> None:
        tasks = self.revoked_tasks()
        tasks.append(task_id)
        self._cache.set(TaskCacheKey.REVOKED_TASKS.value, json.dumps(tasks))

    def remove_revoked_task(self, task_id: TaskId) -> None:
        revoked_tasks = self.revoked_tasks()
        if task_id in revoked_tasks:
            revoked_tasks.remove(task_id)
            self._set_list(TaskCacheKey.REVOKED_TASKS, revoked_tasks)

    def _get_list(self, key: TaskCacheKey) -> List[str]:
        cache_item = self._cache.get(key.value)

        if cache_item:
            task_ids = json.loads(cache_item)
            assert isinstance(task_ids, List)
            return task_ids
        else:
            return []

    def _set_list(self, key: TaskCacheKey, values: List) -> None:
        self._cache.set(key.value, json.dumps(values))

    def clear_tasks(self, task_type: TaskCacheKey) -> None:
        self._cache.set(task_type.value, json.dumps([]))

    def add_task(self, task_type: TaskCacheKey, task_id: TaskId) -> None:
        tasks = self.get_tasks(task_type)
        tasks.append(task_id)
        self._cache.set(task_type.value, json.dumps(tasks))
