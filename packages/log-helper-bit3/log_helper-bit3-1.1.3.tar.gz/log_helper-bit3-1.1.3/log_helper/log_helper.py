import logging
import uuid
from datetime import datetime
from inspect import getframeinfo, stack, Traceback
from logging.handlers import RotatingFileHandler
from typing import Optional

from log_helper.models import LogModel


class LogHelper:
    CRITICAL: int = 50
    ERROR: int = 40
    DEBUG: int = 10
    FATAL: int = CRITICAL
    INFO: int = 20
    NOTSET: int = 0
    WARNING: int = 30
    WARN: int = WARNING

    def __init__(self):
        self.logs: list[LogModel] = []
        self.__log_levels: list[int] = [
            self.CRITICAL
            , self.ERROR
            , self.DEBUG
            , self.FATAL
            , self.INFO
            , self.NOTSET
            , self.WARNING
            , self.WARN
        ]
        self.__logger: logging.Logger = None

    def debug(self, message: str) -> None:
        """
        Registra un mensaje tipo DEBUG en el log

        :param message: Mensaje que se desea registrar
        :type message: str
        :return:
        """

        self.__add_log(self.DEBUG, message)

    def info(self, message: str) -> None:
        """
        Registra un mensaje tipo INFO en el log

        :param message: Mensaje que se desea registrar
        :type message: str
        :return:
        """

        self.__add_log(self.INFO, message)

    def warning(self, message: str) -> None:
        """
        Registra un mensaje tipo WARNING en el log

        :param message: Mensaje que se desea registrar
        :type message: str
        :return:
        """

        self.__add_log(self.WARNING, message)

    def error(self, message: str) -> None:
        """
        Registra un mensaje tipo ERROR en el log

        :param message: Mensaje que se desea registrar
        :type message: str
        :return:
        """

        self.__add_log(self.ERROR, message)

    def fatal(self, message: str) -> None:
        """
        Registra un mensaje tipo FATAL en el log

        :param message: Mensaje que se desea registrar
        :type message: str
        :return:
        """

        self.__add_log(self.FATAL, message)

    def save_logs(self, log_name: str = "app.log", log_level=INFO, max_bytes_per_file: int = 1024 * 1024,
                  backup_count: int = 10) -> bool:
        """
        Guarda en un archivo determinado los logs ubicados en la pila de logs de la clase

        :param log_name: Path del log de la aplicación que usa la clase. En este se registrarán los logs de la clase
        :type log_name: str
        :param log_level: Nivel a partir del cual se van a registrar los logs
        :type log_level: int
        :param max_bytes_per_file: Tamaño máximo del log en bytes, por defecto es una mega (1024 Kb)
        :type max_bytes_per_file: int
        :param backup_count: Cantidad de backups que se desean dejar después que se los logs lleguen a su tamaño máximo
        :type backup_count: int
        :return: Verdadero si los logs fueron impresos correctamente
        :rtype: bool
        """

        if self.logs.__len__() == 0:
            return False

        if log_level not in self.__log_levels:
            log_level = self.NOTSET

        self.__config_log(log_name, log_level, max_bytes_per_file, backup_count)
        for log in self.logs:
            if log.log_level == LogHelper.DEBUG:
                self.__logger.debug(self.__build_message_to_print_in_log(log))
            elif log.log_level == LogHelper.INFO:
                self.__logger.info(self.__build_message_to_print_in_log(log))
            elif log.log_level == LogHelper.WARNING:
                self.__logger.warning(self.__build_message_to_print_in_log(log))
            elif log.log_level == LogHelper.ERROR:
                self.__logger.error(self.__build_message_to_print_in_log(log))
            elif log.log_level == LogHelper.FATAL:
                self.__logger.fatal(self.__build_message_to_print_in_log(log))

        self.__close_logger()
        return True

    @DeprecationWarning
    def add_log(self, logType: int, message: str) -> None:
        """
        Agrega a la pila de logs un nuevo mensaje

        :param logType: Tipo de mensaje
        CRITICAL: int = 50
        FATAL: int = CRITICAL
        ERROR: int = 40
        WARNING: int = 30
        WARN: int = WARNING
        INFO: int = 20
        DEBUG: int = 10
        NOTSET: int = 0
        :type logType: int
        :param message: Mensaje que se desea registrar en el log
        :type message: str
        """

        if logType not in self.__log_levels:
            logType = self.NOTSET

        self.__add_log(logType, message)

    def __add_log(self, logType: int, message: str) -> None:
        """
        Agrega a la pila de logs un nuevo mensaje

        :param logType: Tipo de mensaje
        CRITICAL: int = 50
        FATAL: int = CRITICAL
        ERROR: int = 40
        WARNING: int = 30
        WARN: int = WARNING
        INFO: int = 20
        DEBUG: int = 10
        NOTSET: int = 0
        :type logType: int
        :param message: Mensaje que se desea registrar en el log
        :type message: str
        """

        if isinstance(message, BaseException):
            ex: BaseException = message
            if hasattr(ex, 'message'):
                message = ex.message
            else:
                message = ex.__str__()

        if message is None or message.strip().__len__() == 0:
            return

        st = stack()
        caller: Traceback = getframeinfo(st[2][0])
        log = LogModel()
        log.log_level = logType
        log.filename = caller.filename
        log.function = caller.function
        log.line_number = caller.lineno
        log.message = message.strip()
        log.creation_date = datetime.now()

        self.logs.append(log)

    def __config_log(self, log_name: str = "app.log", log_level=INFO, max_bytes_per_file: int = 1024 * 1024,
                     backup_count: int = 10) -> None:
        """
        Establece las propiedades del logger

        :param log_name: Path del log de la aplicación que usa la clase. En este se registrarán los logs de la clase
        :type log_name: str
        :param log_level: Nivel a partir del cual se van a registrar los logs
        :type log_level: int
        :param max_bytes_per_file: Tamaño máximo del log en bytes, por defecto es una mega (1024 Kb)
        :type max_bytes_per_file: int
        :param backup_count: Cantidad de backups que se desean dejar después que se los logs lleguen a su tamaño máximo
        :type backup_count: int
        """

        self.__logger: logging.Logger = logging.getLogger(uuid.uuid1().__str__())
        self.__logger.setLevel(log_level)

        formatter = logging.Formatter('%(message)s')
        rf_handler: RotatingFileHandler = \
            logging.handlers.RotatingFileHandler(log_name, maxBytes=max_bytes_per_file, backupCount=backup_count)
        rf_handler.setFormatter(formatter)
        rf_handler.setLevel(log_level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)

        self.__logger.addHandler(rf_handler)
        self.__logger.addHandler(console_handler)

    def __close_logger(self) -> None:
        log_handlers = list(self.__logger.handlers)
        for handler in log_handlers:
            self.__logger.removeHandler(handler)
            handler.flush()
            handler.close()

    @staticmethod
    def __build_message_to_print_in_log(log: LogModel) -> Optional[str]:
        """
        Construye el mensaje que se va a registrar en el archivo de log con base a los datos de un log

        :param log: Datos del log
        :type log: LogModel
        :return: El mensaje que se debe registrar en el archivo de log
        :rtype: str
        """

        if log is None:
            return None

        log_level_name: str = LogHelper.get_log_level_name(log.log_level)
        message: str = \
            f'{log.creation_date} |->\t[{log_level_name}]\t{log.message}\t[Line: {log.line_number}]\t[{log.filename}]'

        return message

    @staticmethod
    def get_log_level_name(log_level: int) -> Optional[str]:
        """
        Obtiene el nombre de un nivel de log en específico

        :param log_level: Nivel del log al que se le desea obtener el log
        :type log_level: str
        :return: Nombre del nivel de log
        :rtype: Optional[str]
        """

        if log_level is None:
            return None

        if log_level == LogHelper.DEBUG:
            return 'DEBUG'
        elif log_level == LogHelper.INFO:
            return 'INFO'
        elif log_level == LogHelper.WARNING:
            return 'WARN'
        elif log_level == LogHelper.ERROR:
            return 'ERROR'
        elif log_level == LogHelper.FATAL:
            return 'FATAL'
        elif log_level == LogHelper.NOTSET:
            return 'NOTSET'
        else:
            return None
