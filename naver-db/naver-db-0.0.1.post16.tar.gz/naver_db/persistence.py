from sqlalchemy import exc
import json


class Persistence:
    """Clase para el manejo de los datos de la base de datos"""

    def __init__(self, config, myApp, myDb):
        """Constructor de la clase

        Args:
            config (NaverConfig): Objeto de configuracion
            myApp (Flask): Objeto de la aplicacion
            myDb (FlaskAlchemy): Objeto de la base de datos
        """
        self.myApp = myApp
        self.myApp.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.myDb = myDb
        self.config = config
        self.mySession = [1, 1]

    # TESTED

    def _sql(self, rawSql):
        """Método para ejecutar una consulta SQL

        Args:
            rawSql (str): Consulta SQL

        Returns:
            res: Resultado de la consulta
        """
        try:
            assert type(rawSql) == str
            # assert type(sqlVars) == dict
            res = self._sqltran(rawSql)
            if res is not None:
                self.myDb.session.commit()
            return res
        except exc.SQLAlchemyError as e:
            self.myDb.session.rollback()
            print(e)
            raise e

    # TESTED

    def _sqltran(self, rawSql):
        """Método Raw para ejecutar una consulta SQL

        Args:
            rawSql (str): Consulta SQL

        Returns:
            dict: Diccionario que contiene el cursor y la sesión de la consulta
        """
        try:
            assert type(rawSql) == str
            # assert type(sqlVars) == dict
            cursor = self.myDb.session.execute(rawSql)
            session = self.myDb.session
            return {"cursor": cursor, "session": session}
        except exc.SQLAlchemyError as e: 
            print(e)
            raise e

    # TESTED

    def setWrite(
        self, stm, table, register=False, logtable="log", loglevel=1, logtype=1
    ):
        """Método de escritura a la base de datos

        Args:
            stm (str): Consulta SQL
            table (str): Tabla de la base de datos
            register (bool, optional): [description]. Defaults to False.
            logtable (str, optional): [description]. Defaults to "log".
            loglevel (int, optional): [description]. Defaults to 1.
            logtype (int, optional): [description]. Defaults to 1.

        Returns:
            res: Resultado de la consulta
        """
        self.config.core.getEnvCnx(table)
        res = self._sqltran(stm)
        if res is not None and register:
            self.setWriteLog(stm, logtable, loglevel, logtype)
        return res

    # TESTED

    def setWriteLog(self, stm, logtable="log", loglevel=1, logtype=1):
        """Método de escritura de LOG a la base de datos

        Args:
            stm (str): Consulta SQL
            logtable (str, optional): [description]. Defaults to "log".
            loglevel (int, optional): [description]. Defaults to 1.
            logtype (int, optional): [description]. Defaults to 1.

        Returns:
            res: Resultado de la consulta
        """
        insert = (
            "INSERT INTO "
            + logtable
            + """(description,log_level_id_fk,log_type_id_fk,user_id_fk)
             VALUES ('"""
            + str(stm)
            + "#"
            + str(self.mySession)
            + "',"
            + str(loglevel)
            + ","
            + str(logtype)
            + ","
            + str(self.mySession[0])
            + ")"
        )
        self.config.core.getEnvCnx(logtable)
        res = self._sqltran(insert)
        return res

    def spExec(self, sp, args):
        """Método para ejecutar un SP en SQL

        Args:
            sp (str): Nombre del SP
            args (list): Lista con los parametros del SP

        Returns:
            res: Resultado de la consulta
        """
        stm = "CALL " + sp + "(" + args + ")"
        return self._sql(stm)

    def setProp(self, table, key, value, condition):
        """Método para actualizar una propiedad de una tabla

        Args:
            table (str): Tabla de la base de datos
            key (str): Clave de la propiedad
            value (any): Valor de la propiedad
            condition (lambda): Condicion para la actualizacion

        Returns:
            res: Resultado de la consulta
        """
        if condition:
            stm = (
                "UPDATE "
                + table
                + " SET props = jsonb_set(props, "
                + key
                + ", '"
                + value
                + "' ,false) \
                FROM "
                + table
                + " \
                WHERE "
                + condition
                + ""
            )
            return self._sql(stm)

    """
       GETTERS
    """

    def getPaginatedQuery(self, stm, table, field, since, top):
        """Método para obtener una consulta paginada

        Args:
            stm (str): Consulta SQL
            table (str): Tabla de la base de datos
            field (str): Campo de la consulta
            since (int): Valor desde el que se obtendrán los registros
            top (int): Cantidad de registros a obtener

        Returns:
            res: Resultado de la consulta
        """
        condition = (
            lambda x: "AND" if (str(x).upper().contains("WHERE")) else "WHERE"
        )(stm)
        pStm = stm + " " + condition + " " + field + " > " + since + " LIMIT " + top
        res = self.getQuery(pStm, table)
        return res

    # TESTED

    def getProps(self, table, condition="1=1", schema="public"):
        """Método para obtener las propiedades de una tabla

        Args:
            table (str): Tabla de la base de datos
            condition (str, optional): Condición. Defaults to "1=1".

        Returns:
            props: Propiedades de la tabla
        """
        stm = 'SELECT props from {}."'.format(schema) + table + '" Where ' + condition
        print(stm)
        res = self.getQuery(stm, table)
        return res[0]["props"]

    # TESTED

    def getNextVal(self, field, table):
        """Método para obtener el siguiente valor de un campo

        Args:
            field (str): Campo de la tabla
            table (str): Tabla de la base de datos

        Returns:
            int: Siguiente valor
        """
        stm = "SELECT MAX(" + field + ") FROM " + table + ""
        res = self.getQuery(stm, table)
        return res[0]

    # TESTED

    def getUserPermission(self, userid, table="permission", schema="public"):
        """Método para obtener los permisos de un usuario

        Args:
            userid (int): ID del usuario
            table (str, optional): Tabla. Defaults to 'permission'.

        Returns:
            res: Resultado de la consulta
        """
        stm = (
            """ SELECT prm.* FROM {}.\"""".format(schema)
            + table
            + """\" prm 
                JOIN {}.\"profile\" prf 
                ON prm.profile_id_fk = prf.id 
                JOIN {}.\"profile_user\" prfUsr
                ON prfUsr.profile_id_fk = prf.id
                JOIN {}.\"user\" usr 
                ON  prfUsr.user_id_fk =usr.id
                WHERE  usr.id = """.format(schema)
            + userid
        )
        res = self.getQuery(stm, table)
        return res

    # TESTED

    def getParam(
        self,
        session,
        table="param",
        key=None,
        schema="public",
    ):
        """Método para obtener un parámetro de la tabla param

        Args:
            session (list): Lista de datos de sesión
            table (str, optional): Tabla. Defaults to 'param'.
            key (str, optional): Clave. Defaults to None.

        Returns:
            res: Resultado de la consulta
        """
        stm = (
            """SELECT prm.* FROM
               {}.\"""".format(schema)
            + table
            + """\" prm 
                JOIN {}.\"param_institution\" prmInst 
                ON prmInst.param_id_fk=prm.id
                JOIN {}.\"institution\" ins 
                ON ins.id = prmInst.institution_id_fk
                WHERE ins.id = """.format(schema)
            + session[0]
            + (lambda x: " AND prm.key=" + key if (x is not None) else "")(key)
        )
        res = self.getQuery(stm, table)
        return res

    # TESTED
    def existValue(value, replacement):
        """Método para sabe si un valor existe

        Args:
            value (str): Valor a buscar
            replacement (str): Valor a reemplazar

        Returns:
            str: Valor reemplazado
        """
        if value != "" and value != None:
            return "'" + value + "'"
        return replacement

    def getQuery(self, stm, table):
        """Método para obtener una consulta

        Args:
            stm (str): Consulta SQL
            table (str): Tabla de la base de datos

        Returns:
            json: Resultado de la consulta
        """
        self.config.core.getEnvCnx(table)
        res = self._sql(stm)
        return self.convert(res["cursor"].fetchall())

    def getStm(self, stm, table):
        """Método para obtener una consulta

        Args:
            stm (str): Consulta SQL
            table (str): Tabla de la base de datos

        Returns:
            json: Resultado de la consulta
        """
        self.config.core.getEnvCnx(table)
        res = self._sql(stm)
        return res

    def convert(self, res):
        """Método para convertir una consulta a una lista de diccionarios

        Args:
            res (res): Resultado de la consulta

        Returns:
            json: Resultado de la consulta
        """
        data = ""
        if isinstance(res, list):
            l = []
            for i in res:
                d = dict(i)
                l.append(d)
            data = l
        return json.loads(json.dumps(data, indent=4, sort_keys=True, default=str))

    # INSERT DTO
    def insertDto(self, dto, table):
        """Método para insertar un dto

        Args:
            dto (dto): DTO
            table (str): Tabla de la base de datos

        Returns:
            res: Resultado de la consulta
        """
        columns = ""
        values = ""

        for key, value in dto.__dict__().items():
            columns += "{},".format(str(key))
            values += "{},".format("\'"+str(value)+"\'" if value is not None else "NULL")
        stm = "INSERT INTO " + table + \
            " (" + columns[:-1] + ")" + " VALUES (" + values[:-1] + ") "
        stm += "RETURNING *"
        res = self.setWrite(stm, table)
        return res

    # PREPARE DTO LIST
    def prepareListDtoToInsert(self, dto_list, table):
        """Método para preparar una lista de dtos a insertar

        Args:
            dto_list (list): Lista de dtos
            table (str): Tabla de la base de datos

        Returns:
            res: Resultado de la consulta
        """

        stm = ""
        for dto in dto_list:
            columns = ""
            values = ""
            dto_items = dto.__dict__().items()
            for key, value in dto_items:
                columns += "{},".format(str(key))
                values += "{},".format("\'"+str(value)+"\'" if value is not None else "NULL")
            stm += "INSERT INTO " + table + " (" + columns[:-1] + ")" + " VALUES (" + values[:-1] + "); \n "
        return stm


    # UPDATE DTO
    def updateDto(self, dto, table, pk):
        """Método para actualizar un dto

        Args:
            dto (dto): DTO
            table (str): Tabla de la base de datos

        Returns:
            res: Resultado de la consulta
        """
        stm = "UPDATE " + table + " SET "
        for key, value in dto.__dict__().items():
            stm += " {}={} ,".format(key, "\'"+str(value)+"\'" if value is not None else "NULL")
        stm = stm[:-1]
        id = dto.__dict__()[pk]
        where = " WHERE {}=\'{}\'".format(pk, id)
        stm += where
        res = self.setWrite(stm, table)
        return res
