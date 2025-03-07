import traceback
from typing import Dict, Optional

import requests
import streamlit as st
from huggingface_hub import HfFolder
from loguru import logger

from autotrain import config
from autotrain.tasks import TASKS


FORMAT_TAG = "\033[{code}m"
RESET_TAG = FORMAT_TAG.format(code=0)
BOLD_TAG = FORMAT_TAG.format(code=1)
RED_TAG = FORMAT_TAG.format(code=91)
GREEN_TAG = FORMAT_TAG.format(code=92)
YELLOW_TAG = FORMAT_TAG.format(code=93)
PURPLE_TAG = FORMAT_TAG.format(code=95)
CYAN_TAG = FORMAT_TAG.format(code=96)


class UnauthenticatedError(Exception):
    pass


class UnreachableAPIError(Exception):
    pass


def get_auth_headers(token: str, prefix: str = "Bearer"):
    return {"Authorization": f"{prefix} {token}"}


def http_get(
    path: str,
    token: str,
    domain: str = config.AUTOTRAIN_BACKEND_API,
    token_prefix: str = "Bearer",
    suppress_logs: bool = False,
    **kwargs,
) -> requests.Response:
    """HTTP GET request to the AutoNLP API, raises UnreachableAPIError if the API cannot be reached"""
    logger.info(f"Sending GET request to {domain + path}")
    try:
        response = requests.get(
            url=domain + path, headers=get_auth_headers(token=token, prefix=token_prefix), **kwargs
        )
    except requests.exceptions.ConnectionError:
        raise UnreachableAPIError("❌ Failed to reach AutoNLP API, check your internet connection")
    response.raise_for_status()
    return response


def http_post(
    path: str,
    token: str,
    payload: Optional[Dict] = None,
    domain: str = config.AUTOTRAIN_BACKEND_API,
    suppress_logs: bool = False,
    **kwargs,
) -> requests.Response:
    """HTTP POST request to the AutoNLP API, raises UnreachableAPIError if the API cannot be reached"""
    logger.info(f"Sending POST request to {domain + path}")
    try:
        response = requests.post(
            url=domain + path, json=payload, headers=get_auth_headers(token=token), allow_redirects=True, **kwargs
        )
    except requests.exceptions.ConnectionError:
        raise UnreachableAPIError("❌ Failed to reach AutoNLP API, check your internet connection")
    response.raise_for_status()
    return response


def get_task(task_id: int) -> str:
    for key, value in TASKS.items():
        if value == task_id:
            return key
    return "❌ Unsupported task! Please update autonlp"


def get_user_token():
    return HfFolder.get_token()


def user_authentication(token):
    logger.info("Authenticating user...")
    headers = {}
    cookies = {}
    if token.startswith("hf_"):
        headers["Authorization"] = f"Bearer {token}"
    else:
        cookies = {"token": token}
    try:
        response = requests.get(
            config.HF_API + "/api/whoami-v2",
            headers=headers,
            cookies=cookies,
            timeout=3,
        )
    except (requests.Timeout, ConnectionError) as err:
        logger.error(f"Failed to request whoami-v2 - {repr(err)}")
        raise Exception("Hugging Face Hub is unreachable, please try again later.")
    return response.json()


def get_project_cost(username, token, task, num_samples, num_models):
    logger.info("Getting project cost...")
    task_id = TASKS[task]
    pricing = http_get(
        path=f"/pricing/compute?username={username}&task_id={task_id}&num_samples={num_samples}&num_models={num_models}",
        token=token,
    )
    return pricing.json()["price"]


def app_error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            logger.error(f"{func.__name__} has failed due to an exception:")
            logger.error(traceback.format_exc())
            if "param_choice" in str(err):
                st.warning("Unable to estimate costs. Job params not chosen yet.")
            elif "Failed to reach AutoNLP API" in str(err):
                st.warning("Unable to reach AutoTrain API. Please check your internet connection.")
            elif "An error has occurred: 'NoneType' object has no attribute 'type'" in str(err):
                st.warning("Unable to estimate costs. Data not uploaded yet.")
            else:
                st.error(f"An error has occurred: {err}")

    return wrapper
