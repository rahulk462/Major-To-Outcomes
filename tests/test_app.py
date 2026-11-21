import json

import pytest

from app import as_number, create_app, parse_compare


@pytest.fixture(scope="module")
def client():
    return create_app().test_client()


def test_pages_render(client):
    for url in ["/", "/sources", "/compare", "/compare?c=11.01,14.19,52.08", "/major/11.01"]:
        assert client.get(url).status_code == 200, url


def test_every_major_page_renders(client):
    majors = json.loads(client.get("/api/majors").data)
    assert len(majors) > 50
    for m in majors:
        assert client.get(f"/major/{m['cip4']}").status_code == 200, m["cip4"]


def test_unknown_major_404(client):
    assert client.get("/major/99.99").status_code == 404


def test_api_search(client):
    rows = json.loads(client.get("/api/majors?q=computer").data)
    assert any(r["cip4"] == "11.01" for r in rows)


def test_parse_compare_limits_and_dedupes():
    index = {"11.01": {}, "14.19": {}, "52.08": {}, "27.01": {}}
    assert parse_compare("11.01,11.01,bogus,14.19,52.08,27.01", index) == ["11.01", "14.19", "52.08"]
    assert parse_compare(None, index) == []


def test_as_number():
    assert as_number(None) is None
    assert as_number("x") is None
    assert as_number(3) == 3.0


def test_caveats_present_on_major_page(client):
    html = client.get("/major/11.01").data.decode()
    for phrase in ["federal financial aid", "knowledge rate", "suppressed"]:
        assert phrase in html
