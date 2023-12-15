import datetime
import json
import logging
import os
import time
from typing import Any, Optional

import requests
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Enhanced logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger("biolm_util")


def get_api_token() -> dict[str, str]:
    """Get a BioLM API token to use with future API requests.

    Copied from https://api.biolm.ai/
    """
    url = "https://biolm.ai/api/auth/token/"
    payload = json.dumps(
        {
            "username": get_environment_variable("BIOLM_USER"),
            "password": get_environment_variable("BIOLM_PASSWORD"),
        }
    )
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code != 200:
        raise ValueError("Failed to get API token")
    response_json = response.json()
    os.environ["BIOLM_ACCESS"] = response_json["access"]
    os.environ["BIOLM_REFRESH"] = response_json["refresh"]
    return response_json


def requests_retry_session(
    retries: int = 3,
    backoff_factor: float = 0.3,
    status_forcelist: Optional[list[int]] = None,
    session: Optional[requests.Session] = None,
) -> requests.Session:
    if status_forcelist is None:
        status_forcelist = list(range(400, 599))
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def retry_minutes(
    sess: requests.Session,
    method: str,
    url: str,
    headers: dict[str, str],
    data: Any,
    timeout: urllib3.util.Timeout,
    mins: int,
) -> requests.Response:
    try_until = datetime.datetime.now() + datetime.timedelta(minutes=mins)
    while datetime.datetime.now() < try_until:
        try:
            response = sess.request(
                method, url, headers=headers, data=data, timeout=timeout
            )
            response.raise_for_status()
            if "error" in response.json():
                raise ValueError(json.dumps(response.json()))
            return response
        except (
            requests.RequestException,
            Exception,
        ) as e:  # Broadened exception handling
            log.warning(f"Request failed: {e}, retrying in 5 seconds...")
            time.sleep(5)  # Wait for a constant 5 seconds before retrying
    raise ValueError("Failed to get a valid response within the specified time")


def get_environment_variable(key: str) -> str:
    value = os.environ.get(key)
    if value is None:
        raise ValueError(f"Environment variable {key} not set")
    return value


def make_biolm_request(
    model_slug: str,
    model_action: str,
    seq: str,
    timeout_duration: int,
    retry_duration: int,
) -> Any:
    url = f"https://biolm.ai/api/v1/models/{model_slug}/{model_action}/"
    payload = json.dumps({"instances": [{"data": {"text": seq}}]})
    headers = {
        "Content-Type": "application/json",
        "Cookie": (
            f"access={get_environment_variable('BIOLM_ACCESS')}; "
            f"refresh={get_environment_variable('BIOLM_REFRESH')}"
        ),
    }
    session = requests_retry_session()
    tout = urllib3.util.Timeout(total=timeout_duration, read=timeout_duration // 2)
    response = retry_minutes(
        session, "POST", url, headers, payload, tout, retry_duration
    )
    return response.json()


def esm2_transform(seq: str) -> Any:
    """Make a POST request to get the ESM2 transforms for a protein sequence."""
    model_slug = "esm2_t33_650M_UR50D"
    model_action = "transform"

    # Normally would POST multiple sequences at once for greater efficiency,
    # but for simplicity sake will do one at at time right now
    response = make_biolm_request(model_slug, model_action, seq, 720, 12)
    if "embeddings" in response:
        return response["embeddings"]
    else:
        raise ValueError("Response does not contain 'embeddings'")


def esmfold_pdb(seq: str) -> Any:
    """Make a POST request to predict a PDB file using ESMFold (i.e. ESM2)."""
    model_slug = "esmfold-singlechain"
    model_action = "predict"

    # Normally would POST multiple sequences at once for greater efficiency,
    # but for simplicity sake will do one at at time right now
    response = make_biolm_request(model_slug, model_action, seq, 180, 12)
    if "predictions" in response and response["predictions"]:
        return response["predictions"][0]
    else:
        raise ValueError("Response does not contain valid 'predictions'")
