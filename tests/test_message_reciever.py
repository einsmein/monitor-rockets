from unittest.mock import MagicMock
from datetime import datetime

import pytest
from fastapi.responses import Response
from fastapi.testclient import TestClient

from src import app, schemas


@pytest.fixture(scope="function")
def test_client():

    return TestClient(app.create_app(), raise_server_exceptions=False)


def test_message_launched(test_client):
    r = test_client.post(
        "/messages",
        json={
            "metadata": {
                "channel": "rocket-foo",
                "messageNumber": 1,
                "messageTime": str(datetime.now()),
                "messageType": "RocketLaunched",
            },
            "message": {
                "type": "TEST-ROCKET",
                "launchSpeed": 100,
                "mission": "test_mission",
            },
        },
    )
    assert r.ok


def test_duplicate_message(test_client):
    r = test_client.post(
        "/messages",
        json={
            "metadata": {
                "channel": "rocket-foo",
                "messageNumber": 1,
                "messageTime": str(datetime.now()),
                "messageType": "RocketLaunched",
            },
            "message": {
                "type": "TEST-ROCKET",
                "launchSpeed": 200,
                "mission": "test_mission",
            },
        },
    )
    assert r.status_code == 204


def test_get_state(test_client):
    r = test_client.get("/state/rocket-foo")
    assert r.ok

    rocket = r.json()
    assert rocket["type"] == "TEST-ROCKET"
    assert rocket["speed"] == 100
    assert rocket["mission"] == "test_mission"
    assert 1 in rocket["processed_msg_num"]


def test_message_speed_increased(test_client):
    r = test_client.post(
        "/messages",
        json={
            "metadata": {
                "channel": "rocket-foo",
                "messageNumber": 2,
                "messageTime": str(datetime.now()),
                "messageType": "RocketSpeedIncreased",
            },
            "message": {
                "by": 1000,
            },
        },
    )
    assert r.status_code == 200

    rocket = r.json()
    assert rocket.get("speed") == 1100


def test_message_speed_decreased(test_client):
    r = test_client.post(
        "/messages",
        json={
            "metadata": {
                "channel": "rocket-foo",
                "messageNumber": 3,
                "messageTime": str(datetime.now()),
                "messageType": "RocketSpeedDecreased",
            },
            "message": {
                "by": 50,
            },
        },
    )
    assert r.status_code == 200

    rocket = r.json()
    assert rocket.get("speed") == 1050


def test_message_processing_is_atomic(test_client, monkeypatch):
    class MockSet(set):
        def add(self, *args):
            raise Exception("mocking some exception")

    monkeypatch.setattr("src.app.rockets", {"rocket-to-fail": schemas.Rocket(
        processed_msg_num=MockSet()
    )})

    r = test_client.post(
        "/messages",
        json={
            "metadata": {
                "channel": "rocket-to-fail",
                "messageNumber": 1,
                "messageTime": str(datetime.now()),
                "messageType": "RocketLaunched",
            },
            "message": {
                "type": "TEST-ROCKET",
                "launchSpeed": 100,
                "mission": "test_mission",
            },
        },
    )
    assert not r.ok
    assert r.status_code == 500
    assert "mocking some exception" in r.content.decode("utf-8")

    r = test_client.get("/state/rocket-to-fail")
    assert r.ok

    rocket = r.json()
    assert rocket["type"] is None
    assert rocket["speed"] == 0
    assert rocket["mission"] == None
    assert 1 not in rocket["processed_msg_num"]

