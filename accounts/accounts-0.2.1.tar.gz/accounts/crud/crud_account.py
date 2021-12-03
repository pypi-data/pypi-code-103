from typing import Optional

from app.crud.base import CRUDBase
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate
from sqlalchemy.orm import Session


class CRUDAccount(CRUDBase[Account, AccountCreate, AccountUpdate]):
    def get_by_doc_id(self, db: Session, *, doc_id: str) -> Optional[Account]:
        return db.query(self.model).filter(Account.doc_id == doc_id).first()


account = CRUDAccount(Account)