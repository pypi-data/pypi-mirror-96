import json
import logging
from typing import Mapping, Optional, Tuple, Union

from pkg_resources import get_distribution
import requests
from requests.auth import HTTPBasicAuth

from kpler.sdk.enums import Platform


class Configuration:
    def __init__(
        self,
        platform: Platform,
        email: str,
        password: str,
        proxies: Optional[Mapping[str, str]] = None,
        certificates: Optional[Union[Tuple[str, str], str]] = None,
        verify: Optional[bool] = True,
        log_level=None,
    ):

        self.proxies = proxies
        self.certificates = certificates
        self.verify = verify

        self.platform = platform

        self.email = email
        self.password = password
        self.auth_validated = False

        logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s")
        self.logger = logging.getLogger("kpler")
        self.logger.setLevel(log_level or logging.ERROR)

        self._check_new_version()
        self._authenticate()

    @property
    def base_url(self) -> str:
        return str(self.platform.value)

    def _authenticate(self) -> None:
        if self.auth_validated:
            return

        response = requests.get(
            f"{self.base_url}/trades/columns",
            auth=HTTPBasicAuth(self.email, self.password),
            proxies=self.proxies,
            cert=self.certificates,
            verify=self.verify,
        )
        email_platform_str = f"'{self.email}' on '{self.platform}'"
        if response.status_code == 200:
            self.auth_validated = True
            self.logger.info(f"Credentials validated for {email_platform_str}")
        else:
            self.auth_validated = False
            self.logger.error(
                f"Unable to validate your credentials for {email_platform_str}: {response.content}"  # type: ignore
            )

    def _change_platform(self, platform: Platform) -> None:
        self.platform = platform
        self._authenticate()

    def _check_new_version(self) -> None:
        version = self.get_clean_version(get_distribution("kpler.sdk").version)
        response = requests.get(
            f"{self.base_url}/clients/python_sdk/versions?afterVersion={version}&size=1",
            auth=HTTPBasicAuth(self.email, self.password),
            proxies=self.proxies,
            cert=self.certificates,
            verify=self.verify,
        )
        json_data = json.loads(response.text)
        if isinstance(json_data, list) and len(json_data) > 0:
            self.logger.info(
                f"A new versions {json_data[0]['clientVersion']} is available, please upgrade the Kpler SDK."
            )

    def get_clean_version(self, version) -> str:
        return ".".join(version.split(".")[:3])
