from typing import Optional

import requests


def get_session_token(redirect_uri: str, code: str) -> Optional[str]:
    try:
        with open("/opt/avava-hello/clientsecret") as f:
            secret = f.read().strip()
    except Exception:
        print("failed to load client secret")
        return None
    response = requests.post(
        "https://oauth2.googleapis.com/token",
        json={
            "code": code,
            "client_id": "597130784690-p6rm59ers16r68s6sm4p4lkar1p1ipgv.apps.googleusercontent.com",
            "client_secret": secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
    )
    if not response.ok:
        return None
    return response.json()["access_token"]


def get_email(session_token: str):
    response = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo?alt=json",
        headers={"Authorization": f"Bearer {session_token}"},
    )
    if not response.ok:
        return None
    return response.json().get("email")
