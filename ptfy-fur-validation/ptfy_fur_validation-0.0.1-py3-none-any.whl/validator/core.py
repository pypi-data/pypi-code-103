import uuid

from ..logger.core import logger


class Validator:
    @staticmethod
    def validate_uuid(value, version=4):
        try:
            uuid.UUID(value, version=version)

            return value
        except:
            logger.critical(
                f"Value must be of type uuidv4, got {value} with type {type(value)}"
            )
            raise

    @staticmethod
    def validate_str(value):
        if type(value) is not str:
            logger.critical(
                f"Value must be of type str, got {value} with type {type(value)}"
            )
            raise TypeError

        return value

    @staticmethod
    def validate_int(value):
        if type(value) is not int:
            logger.critical(
                f"Value must be of type int, got {value} with type {type(value)}"
            )
            raise TypeError

        return value

    @staticmethod
    def validate_dict(value):
        if type(value) is not dict:
            logger.critical(
                f"Value must be of type dict, got {value} with type {type(value)}"
            )
            raise TypeError

    @staticmethod
    def validate_bool(value):
        if type(value) is not bool:
            logger.critical(
                f"Value must be of type bool, got {value} with type {type(value)}"
            )
            raise TypeError
