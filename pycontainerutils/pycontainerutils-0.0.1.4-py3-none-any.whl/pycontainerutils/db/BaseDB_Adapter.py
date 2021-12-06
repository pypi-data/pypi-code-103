import warnings
from logging import getLogger
from sqlalchemy.engine.create import create_engine
from sqlalchemy.orm.session import sessionmaker

logger = getLogger(__name__)


class BaseDBAdapter(object):
    name = "BaseDBAdapter"
    # 연결된 DB 정보
    default_db_name = None
    # 세부 설정 사항
    is_echo_sql = False
    databases = None

    def __init__(self):
        # db 연결 정보
        self.engine_info = None
        self.db_name = None
        # db 연결 객체
        self.engine = None
        self.session_maker = None

    @classmethod
    def init_settings(cls, databases, is_echo_sql, default_db_name):
        """
        초기 설정
        :param databases: databases 목록
        :param is_echo_sql: sql echo 여부
        :param default_db_name: 기본으로 사용할 db 이름
        :return:
        """
        cls.databases = databases
        cls.is_echo_sql = is_echo_sql
        if default_db_name in databases:
            cls.default_db_name = default_db_name
        else:
            print(f"잘못된 {default_db_name}(default_db_name) 입니다.")
            raise SyntaxError

    def create_db_connect(self):
        db_link = f'postgresql://{self.engine_info["user"]}:{self.engine_info["password"]}' \
                  f'@{self.engine_info["host"]}:{self.engine_info["port"]}/{self.engine_info["database"]}'
        print(f"{self.name} engine create: {self.db_name} - {self.engine_info}")

        # engine 생성
        # self.engine = create_engine(db_link)
        self.engine = create_engine(db_link, echo=self.is_echo_sql)
        # DB 연결 create
        self.session_maker = sessionmaker(bind=self.engine)

    def register_info(self, db_name, direct):
        # 둘다 입력한 경우
        if db_name and direct:
            logger.error(f"db 이름과 direct를 통해 이중으로 연결되었습니다.\n"
                         f"db_name: {db_name}"
                         f"direct: {direct}")
            raise SyntaxError(f"db_name: {db_name}\n"
                              f"direct: {direct}")
        # db name을 입력한 경우
        if db_name is not None:
            self.register_info_db_name(db_name=db_name)
        # 직접 ip를 입력한 경우
        if direct is not None:
            self.register_info_direct(direct=direct)
        # 아무것도 입력하지 않은 경우
        if not db_name and not direct:
            if self.default_db_name is None:
                warnings.warn(f"초기화를 하지 않고 사용하셨습니다.\n"
                              f"사용하기전 BaseDBAdapter.init_settings을 실행해 주시길 바랍니다.")
                raise SyntaxError(f"default_db_name : {self.default_db_name}")
            else:
                self.register_info_db_name(db_name=self.default_db_name)

        # 연결 생성
        self.create_db_connect()

    def register_info_db_name(self, db_name):
        if db_name in self.databases:
            self.engine_info = self.databases[db_name]
            self.db_name = db_name
        else:
            # 기본 입력된 정도 등록
            # database에서 조회해서 등록
            logger.warning(f"해당 DB 이름을 settings의 DATABASES에서 찾을 수 없습니다.")
            raise KeyError

    def register_info_direct(self, direct):
        # 직접 입력
        self.engine_info = {
            "database": direct['database'],
            "user": direct['user'],
            "password": direct['password'],
            "host": direct['host'],
            "port": direct['port'],
        }
        self.db_name = 'direct'
        logger.warn(f"직접 db 정보를 입력하셨습니다.\n"
                    f"{self.engine_info}")
