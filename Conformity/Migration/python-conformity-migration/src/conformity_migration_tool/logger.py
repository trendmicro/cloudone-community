import logging


class Logger:
    def info(self, msg: object, *args, file_only=False, **kwargs) -> None:
        ...

    def warn(self, msg: object, *args, file_only=False, **kwargs) -> None:
        ...

    def debug(self, msg: object, *args, file_only=False, **kwargs) -> None:
        ...

    def error(self, msg: object, *args, file_only=False, **kwargs) -> None:
        ...

    def exception(self, msg: object, *args, file_only=False, **kwargs) -> None:
        ...


class AppLogger(Logger):
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def _prepare_for_log(self, kwargs: dict, file_only=False):
        # remove these params from converted print statements
        kwargs.pop("end", None)
        kwargs.pop("flush", None)

        extra: dict = kwargs.setdefault("extra", dict())
        extra["file_only"] = file_only

    def info(self, msg: object, *args, file_only=False, **kwargs) -> None:
        self._prepare_for_log(kwargs, file_only=file_only)
        return self.logger.info(msg, *args, **kwargs)

    def warn(self, msg: object, *args, file_only=False, **kwargs) -> None:
        self._prepare_for_log(kwargs, file_only=file_only)
        return self.logger.warning(msg, *args, **kwargs)

    def debug(self, msg: object, *args, file_only=False, **kwargs) -> None:
        self._prepare_for_log(kwargs, file_only=file_only)
        return self.logger.debug(msg, *args, **kwargs)

    def error(self, msg: object, *args, file_only=False, **kwargs) -> None:
        self._prepare_for_log(kwargs, file_only=file_only)
        return self.logger.error(msg, *args, **kwargs)

    def exception(self, msg: object, *args, file_only=False, **kwargs) -> None:
        self._prepare_for_log(kwargs, file_only=file_only)
        return self.logger.exception(msg, *args, **kwargs)


class NoStrackTraceExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info) -> str:
        return str(exc_info[1])

    def format(self, record: logging.LogRecord):
        # clears cached exc_text formatted by other Formatter.formatException(record.exc_info)
        record.exc_text = ""
        return super().format(record=record)


class WithStrackTraceExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info) -> str:
        return super().formatException(exc_info)

    def format(self, record: logging.LogRecord):
        # clears cached exc_text formatted by other Formatter.formatException(record.exc_info)
        record.exc_text = ""
        return super().format(record=record)
