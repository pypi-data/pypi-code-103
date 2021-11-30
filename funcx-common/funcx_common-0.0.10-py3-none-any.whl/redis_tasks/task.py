import typing as t

from ..redis import (
    INT_SERDE,
    JSON_SERDE,
    FuncxRedisEnumSerde,
    HasRedisFieldsMeta,
    RedisField,
)
from .constants import InternalTaskState, TaskState
from .protocol import TaskProtocol

try:
    import redis

    has_redis = True
except ImportError:
    has_redis = False


class RedisTask(TaskProtocol, metaclass=HasRedisFieldsMeta):
    """
    ORM-esque class to wrap access to properties of tasks.

    Creation:
      Create a new task by instantiating this class, e.g.
      >>> RedisTask(reids_client, "foo_id")

    Loading:
      Read a task from storage using the `load()` classmethod, e.g.
      >>> RedisTask.load(redis_client, "foo_id")

    This class provides various task fields as descriptors via RedisField, and is
    responsible for de/serializing various data from/to hstore in Redis.

    There are several elements of this pattern of use which need to be fixed. It is
    important to be aware of the following:
    - there is currently no use of Redis transactions, so nothing is atomic
    - Each time a field descriptor is accessed, it is read, returned, and discarded.
      Reading a field multiple times, even in a single python statement, is vulnerable
      to data races
    - no field requirements or validity are enforced -- reading a field can raise an
      error if bad data were written to Redis
    - each field is read individually, which can be inefficient and inconsistent (vs
      getall or setall semantics)
    """

    # 2 weeks in seconds ( datetime.timedelta(weeks=2).total_seconds() )
    TASK_TTL = 1209600

    status = t.cast(TaskState, RedisField(serde=FuncxRedisEnumSerde(TaskState)))
    internal_status = t.cast(
        InternalTaskState, RedisField(serde=FuncxRedisEnumSerde(InternalTaskState))
    )
    user_id = RedisField(serde=INT_SERDE)
    function_id = RedisField()
    endpoint = t.cast(str, RedisField())
    container = RedisField()
    payload = RedisField(serde=JSON_SERDE)
    result = RedisField()
    result_reference = t.cast(
        t.Optional[t.Dict[str, t.Any]], RedisField(serde=JSON_SERDE)
    )
    exception = RedisField()
    completion_time = RedisField()
    task_group_id = RedisField()

    def __init__(
        self,
        redis_client: "redis.Redis",
        task_id: str,
        *,
        user_id: t.Optional[int] = None,
        function_id: t.Optional[str] = None,
        container: t.Optional[str] = None,
        payload: t.Any = None,
        task_group_id: t.Optional[str] = None,
    ):
        """
        If optional values are passed, then they will be written.

        Otherwise, they will fetched from any existing task entry.
        :param redis_client: Redis client for properties to get/set
        :param task_id: UUID of the task, as str
        :param user_id: ID of user to whom this task belongs
        :param function_id: UUID of the function for this task, as str
        :param container: UUID of container in which to run, as str
        :param payload: serialized function + input data
        :param task_group_id: UUID of task group that this task belongs to
        """
        self.redis_client = redis_client
        self.task_id = task_id
        self.hname = f"task_{task_id}"

        # if required attributes are not yet set, initialize them to their defaults
        if self.status is None:
            self.status = TaskState.WAITING_FOR_EP
        if self.internal_status is None:
            self.internal_status = InternalTaskState.INCOMPLETE

        if user_id is not None:
            self.user_id = user_id
        if function_id is not None:
            self.function_id = function_id
        if container is not None:
            self.container = container
        if payload is not None:
            self.payload = payload
        if task_group_id is not None:
            self.task_group_id = task_group_id

        # Used to pass bits of information to EP
        self.header = f"{self.task_id};{self.container};None"
        self._set_expire()

    def _set_expire(self):
        """Expires task after TASK_TTL, if not already set."""
        ttl = self.redis_client.ttl(self.hname)
        if ttl < 0:
            # expire was not already set
            self.redis_client.expire(self.hname, self.TASK_TTL)

    def delete(self):
        """Removes this task from Redis, to be used after the result is gotten"""
        self.redis_client.delete(self.hname)

    @classmethod
    def exists(cls, redis_client: "redis.Redis", task_id: str) -> bool:
        """Check if a given task_id exists in Redis"""
        return bool(redis_client.exists(f"task_{task_id}"))

    @classmethod
    def load(cls, redis_client: "redis.Redis", task_id: str) -> "RedisTask":
        """
        Load a task from storage. Raises a ValueError if the task is not found.
        """
        # TODO: This has a race condition. Encapsulate it in a transaction.
        if not cls.exists(redis_client, task_id):
            raise ValueError(f"Cannot load task {task_id}: does not exist")
        return cls(redis_client, task_id)
