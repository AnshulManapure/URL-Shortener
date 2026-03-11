from utils import client, original_url, login_user

def test_shorten():
    headers = login_user()
    response = client.post(
        url="/shorten",
        json={
            "original_url":original_url
        },
        headers=headers
    )
    assert response.status_code == 200


def test_redirect():
    headers = login_user()
    shorten_response = client.post(
        url="/shorten",
        json={
            "original_url":original_url
        },
        headers=headers
    )
    short_code = shorten_response.json()["short_code"]

    assert shorten_response.status_code == 200

    response = client.get(
        url=f"/{short_code}",
        follow_redirects=False
    )
    
    assert response.status_code == 307
    assert response.headers["location"] == original_url