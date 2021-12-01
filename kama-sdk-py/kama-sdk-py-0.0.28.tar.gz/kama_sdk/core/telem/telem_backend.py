from typing import Optional, Dict, List

from abc import ABC, abstractmethod

class TelemBackend(ABC):

  @abstractmethod
  def create_record(self, coll_id: str, record: Dict):
    raise NotImplementedError

  @abstractmethod
  def update_record(self, coll_id: str, record: Dict):
    raise NotImplementedError

  @abstractmethod
  def find_record_by_id(self, coll_id: str, record_id) -> Optional[Dict]:
    raise NotImplementedError

  @abstractmethod
  def query_collection(self, coll_id: str, query: Dict) -> List[Dict]:
    raise NotImplementedError

  @abstractmethod
  def collection_names(self) -> List[str]:
    raise NotImplementedError

  @abstractmethod
  def drop_collection(self, coll_id: str):
    raise NotImplementedError

  @abstractmethod
  def is_enabled(self) -> bool:
    raise NotImplementedError

  @abstractmethod
  def is_online(self) -> bool:
    raise NotImplementedError
