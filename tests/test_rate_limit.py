from utils import client, original_url, login_user

def test_user_rate_limit():
    headers = login_user()
    for i in range(10):
        response = client.post(
            url="/shorten",
            json={
                "original_url":original_url
            },
            headers=headers
        )
        assert response.status_code == 200

    response = client.post(
            url="/shorten",
            json={
                "original_url":original_url
            },
            headers=headers
        )
    assert response.status_code == 429