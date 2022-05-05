import logging
import os
import random
import sys
from functools import lru_cache
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict

import yaml
from requests import Response, Session
from requests.adapters import BaseAdapter, HTTPAdapter
from urllib3 import Retry
from vcr import VCR

from conformity_migration.conformity_api import (
    CloudOneConformityAPI,
    DefaultConformityAPI,
    LegacyConformityAPI,
    WorkaroundFixConformityAPI,
)

from .logger import (
    AppLogger,
    Logger,
    NoStrackTraceExceptionFormatter,
    WithStrackTraceExceptionFormatter,
)
from .utils import str2bool

script_dirpath = Path(__file__).parent

USER_CONF_FILENAME = "user_config.yml"
APP_CONF_FILENAME = "config.yml"


def _load_yaml_config(yaml_path: Path):
    with open(yaml_path, mode="r") as fh:
        return yaml.load(fh, Loader=yaml.SafeLoader)


def app_config_path() -> Path:
    return script_dirpath.joinpath(APP_CONF_FILENAME)


@lru_cache(maxsize=1)
def app_config() -> Dict[str, Any]:
    return _load_yaml_config(app_config_path())


def ask_user_to_run_configure():
    print(
        "Please configure migration tool by running this command: conformity-migration configure"
    )
    sys.exit(1)


def user_config_path() -> Path:
    return Path(USER_CONF_FILENAME)


@lru_cache(maxsize=1)
def user_config() -> Dict[str, Any]:
    path = user_config_path()
    if not path.exists():
        ask_user_to_run_configure()
    return _load_yaml_config(path)


class LoggerHTTPAdapter(BaseAdapter):
    def __init__(self, adapter: BaseAdapter, logger=Logger):
        self._adapter = adapter
        self._log = logger

    def _build_req_resp_txt(self, resp: Response):
        req = resp.request
        req_body = str(req.body) if req.body else ""
        return f"""[Request]
{req.method} {req.url}

{req_body}
[Response]
{resp.status_code} {resp.reason}
Content-Type: {resp.headers['Content-Type']}

{resp.text}"""

    def send(self, *args, **kwargs) -> Response:
        resp = self._adapter.send(*args, **kwargs)
        if not resp.ok:
            req_resp = self._build_req_resp_txt(resp)
            self._log.error(req_resp, file_only=True)
        return resp

    def close(self) -> None:
        return self._adapter.close()


class FakeErrorHTTPAdapter(BaseAdapter):
    def __init__(self, adapter: BaseAdapter):
        self._adapter = adapter

    def _fake_error(self, resp: Response):
        req = resp.request
        if req.method == "GET":
            return
        is_error = random.choice((True, False))
        if is_error:
            resp.status_code = 499
            resp.reason = "Fake Error :-)"

    def send(self, *args, **kwargs) -> Response:
        resp = self._adapter.send(*args, **kwargs)
        self._fake_error(resp)
        return resp

    def close(self) -> None:
        return self._adapter.close()


class TimeoutHTTPAdapter(BaseAdapter):
    def __init__(self, adapter: BaseAdapter, conn_timeout: float, read_timeout: float):
        self._adapter = adapter
        self._conn_timeout = conn_timeout
        self._read_timeout = read_timeout

    def send(self, *args, **kwargs) -> Response:
        timeout = (self._conn_timeout, self._read_timeout)
        kwargs["timeout"] = timeout
        return self._adapter.send(*args, **kwargs)

    def close(self) -> None:
        return self._adapter.close()


class VcrHTTPAdapter(BaseAdapter):
    def __init__(self, adapter: BaseAdapter, vcr: VCR, vcr_file: str):
        self._adapter = adapter
        self._vcr = vcr
        self._vcr_file = vcr_file

    def send(self, *args, **kwargs) -> Response:
        with self._vcr.use_cassette(path=self._vcr_file):
            return self._adapter.send(*args, **kwargs)

    def close(self) -> None:
        return self._adapter.close()


def _http_adapter() -> BaseAdapter:
    app_conf = app_config()

    adapter = HTTPAdapter(
        max_retries=Retry(
            total=None,
            connect=0,
            read=0,
            redirect=0,
            other=0,
            backoff_factor=app_conf["API_RETRY_BACKOFF_FACTOR"],
            status=app_conf["API_RETRY_COUNT"],  # max retries for any status_forcelist
            status_forcelist=app_conf["API_RETRY_HTTP_STATUSES"],
            allowed_methods=False,  # false means retry on all Methods
            respect_retry_after_header=True,
        )
    )

    adapter = TimeoutHTTPAdapter(
        adapter,
        conn_timeout=app_conf["API_CONNECTION_TIMEOUT"],
        read_timeout=app_conf["API_READ_TIMEOUT"],
    )

    adapter = LoggerHTTPAdapter(adapter=adapter, logger=logger())

    return adapter


def _vcr_adapter(
    adapter: BaseAdapter,
    vcr_file: str,
    vcr_mode: str,
    fake_api_key: str,
    decode_compressed_response=False,
) -> BaseAdapter:
    if vcr_file:
        vcr = VCR(
            record_mode=vcr_mode,
            match_on=("method", "scheme", "host", "port", "path", "query", "body"),
            filter_headers=[("Authorization", f"ApiKey {fake_api_key}")],
            decode_compressed_response=True,
        )
        adapter = VcrHTTPAdapter(adapter=adapter, vcr=vcr, vcr_file=vcr_file)
    return adapter


def _legacy_http() -> Session:
    sess = Session()
    adapter = _http_adapter()
    adapter = _vcr_adapter(
        adapter=adapter,
        vcr_file=os.getenv("LEG_VCR_FILE", ""),
        vcr_mode=os.getenv("LEG_VCR_MODE", "none"),
        fake_api_key="fake-api-key-for-legacy_conformity",
    )
    sess.mount("https://", adapter=adapter)
    return sess


def _c1_http() -> Session:
    sess = Session()
    adapter = _http_adapter()
    adapter = _vcr_adapter(
        adapter=adapter,
        vcr_file=os.getenv("C1_VCR_FILE", ""),
        vcr_mode=os.getenv("C1_VCR_MODE", "none"),
        fake_api_key="fake-api-key-for-c1_conformity",
    )
    if str2bool(os.getenv("FAKE_C1_HTTP_ERROR", "False")):
        adapter = FakeErrorHTTPAdapter(adapter=adapter)
    sess.mount("https://", adapter=adapter)
    return sess


def legacy_conformity_api() -> LegacyConformityAPI:
    user_conf = user_config()
    api_key = user_conf["LEGACY_CONFORMITY"]["API_KEY"]
    base_url = user_conf["LEGACY_CONFORMITY"]["API_BASE_URL"]

    api = DefaultConformityAPI(api_key=api_key, base_url=base_url, http=_legacy_http())
    api = WorkaroundFixConformityAPI(api)
    api = LegacyConformityAPI(api)
    return api


def c1_conformity_api() -> CloudOneConformityAPI:
    user_conf = user_config()
    api_key = user_conf["CLOUD_ONE_CONFORMITY"]["API_KEY"]
    base_url = user_conf["CLOUD_ONE_CONFORMITY"]["API_BASE_URL"]

    api = DefaultConformityAPI(api_key=api_key, base_url=base_url, http=_c1_http())
    api = WorkaroundFixConformityAPI(api)
    api = CloudOneConformityAPI(api)
    return api


@lru_cache(maxsize=1)
def logger() -> Logger:
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.INFO)
    ch_fmt = NoStrackTraceExceptionFormatter(fmt="%(message)s")
    ch.setFormatter(ch_fmt)
    ch.addFilter(lambda logrec: not logrec.file_only)  # type: ignore
    logger.addHandler(ch)

    fh_fmt = WithStrackTraceExceptionFormatter(
        fmt="[%(asctime)s] %(levelname)s %(message)s"
    )

    log_fh = RotatingFileHandler(
        filename="conformity-migration.log", maxBytes=1024**2, backupCount=4
    )
    log_fh.setLevel(logging.DEBUG)
    log_fh.setFormatter(fmt=fh_fmt)
    logger.addHandler(log_fh)

    err_fh = RotatingFileHandler(
        filename="conformity-migration-error.log", maxBytes=1024**2, backupCount=4
    )
    err_fh.setLevel(logging.ERROR)
    err_fh.setFormatter(fmt=fh_fmt)
    logger.addHandler(err_fh)

    log_backoff = app_config()["LOG_BACKOFF"]
    if log_backoff:
        backoff_logger = logging.getLogger("backoff")
        backoff_logger.addHandler(log_fh)
        backoff_logger.addHandler(err_fh)

    return AppLogger(logger=logger)
