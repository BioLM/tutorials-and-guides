import datetime
import json
import logging
import os
import time

import requests
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

log = logging.getLogger("biolm_util")


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=None,
    session=None,
):
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


def retry_minutes(sess, URL, HEADERS, dat, timeout, mins):
    """Retry for N minutes."""
    try:
        now = datetime.datetime.now()
        try_until = now + datetime.timedelta(minutes=mins)
        while datetime.datetime.now() < try_until:
            response = None
            try:
                log.info(f"Trying {datetime.datetime.now()}")
                response = sess.post(URL, headers=HEADERS, data=dat, timeout=timeout)
                response.raise_for_status()
                if "error" in response.json():
                    raise ValueError(response.json().dumps())
                else:
                    break
            except Exception as e:
                log.warning(e)
                if response:
                    log.warning(response.text)
                time.sleep(5)  # Wait 5 seconds between tries
        if response is None:
            err = "Got Nonetype response"
            raise ValueError(err)
        elif "Server Error" in response.text:
            err = "Got Server Error"
            raise ValueError(err)
        else:
            response.raise_for_status()
    except Exception:
        raise
    else:
        return response


def get_api_token():
    """Get a BioLM API token to use with future API requests.

    Copied from https://api.biolm.ai/#d7f87dfd-321f-45ae-99b6-eb203519ddeb.
    """
    url = "https://biolm.ai/api/auth/token/"

    payload = json.dumps(
        {
            "username": os.environ.get("BIOLM_USER"),
            "password": os.environ.get("BIOLM_PASS"),
        }
    )
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 200:
        raise ValueError("Failed to get API token")

    response_json = response.json()

    os.environ["BIOLM_ACCESS"] = response_json["access"]
    os.environ["BIOLM_REFRESH"] = response_json["refresh"]

    return response_json


def esm2_transform(seq):
    """Make a POST request to get the ESM2 transforms for a protein sequence."""
    url = "https://biolm.ai/api/v1/models/esm2_t33_650M_UR50D/transform/"

    # Normally would POST multiple sequences at once for greater efficiency,
    # but for simplicity sake will do one at at time right now
    payload = json.dumps({"instances": [{"data": {"text": seq}}]})

    access = os.environ.get("BIOLM_ACCESS")
    refresh = os.environ.get("BIOLM_REFRESH")
    if not access or not refresh:
        raise ValueError("BioLM access or refresh token not set")

    headers = {
        "Cookie": f"access={access};refresh={refresh}",
        "Content-Type": "application/json",
    }

    session = requests_retry_session()
    tout = urllib3.util.Timeout(total=720, read=360)
    response = session.post(url, headers=headers, data=payload, timeout=tout)

    resp_json = response.json()
    transformations = resp_json[
        "predictions"
    ]  # List, containing dicts for each sequence POSTed

    return transformations  # list of dict_keys(['name', 'mean_representations', 'contacts', 'logits', 'attentions'])


def esmfold_pdb(seq):
    """Make a POST request to predict a PDB file using ESMFold (i.e. ESM2)."""
    url = "https://biolm.ai/api/v1/models/esmfold-singlechain/predict/"

    # Normally would POST multiple sequences at once for greater efficiency,
    # but for simplicity sake will do one at at time right now
    payload = json.dumps({"instances": [{"data": {"text": seq}}]})

    access = os.environ.get("BIOLM_ACCESS")
    refresh = os.environ.get("BIOLM_REFRESH")
    if not access or not refresh:
        raise ValueError("BioLM access or refresh token not set")

    headers = {
        "Cookie": f"access={access};refresh={refresh}",
        "Content-Type": "application/json",
    }

    session = requests_retry_session()
    tout = urllib3.util.Timeout(total=180, read=180)
    response = retry_minutes(session, url, headers, payload, tout, mins=12)

    resp_json = response.json()
    # resp_json['predictions']  # List, one item for each sequence POSTed

    return resp_json["predictions"][0]
