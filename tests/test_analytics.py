from utils import client, original_url, login_user

def test_analytics_endpoint():
    headers = login_user()
    shorten_response = client.post(
        url="/shorten",
        json={"original_url":original_url},
        headers=headers
    )
    short_code = shorten_response.json()["short_code"]

    for i in range(6):
        redirect_response = client.get(
            url=f"/{short_code}",
            follow_redirects=False
        )
        assert redirect_response.status_code == 307
        assert redirect_response.headers["location"] == original_url

    analytics_response = client.get(
        url=f"/analytics/{short_code}",
        headers=headers
    )

    assert analytics_response.status_code == 200
    assert analytics_response.json()["total_clicks"] >= 1