import email
import os
import time

import requests

MAIL_HOG = os.environ.get("MAIL_HOG", "http://127.0.0.1:8025")


def wait_email(
    kind,
    query,
    expected_total=1,
    timeout=15,
    timeout_message="email (kind: {kind}, {query}) wasn't found in the given time {timeout}s",
):
    """
    - mailhog **kind**: Kind of search: enum: [ from, to, containing ]
    - mailhog **query**: Search parameter: string
    - **expected_total**: assert expected number of document for given query
    - **timeout**: time in second to wait email
    - **timout_message**: raised TimeoutError message
    """
    start_time = time.perf_counter()
    while True:
        time.sleep(0.5)
        response = requests.get(MAIL_HOG + f"/api/v2/search?kind={kind}&query={query}")
        assert response.status_code == 200, "Fake SMTP service wasn't ready"
        data = response.json()
        if data["total"] == expected_total:
            return data
        if (time.perf_counter() - start_time) > timeout:
            raise TimeoutError(
                timeout_message.format(kind=kind, query=query, timeout=timeout)
            )


def pdfs_from_email(email_content):
    msg = email.message_from_bytes(email_content.get("Raw", {}).get("Data").encode())
    pdfs = {}
    for payload in msg.get_payload():
        if payload.get_content_type() == "application/pdf":
            pdfs[payload.get_filename()] = payload.get_payload()
    return pdfs
