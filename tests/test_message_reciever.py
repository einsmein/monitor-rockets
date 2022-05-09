import os
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.responses import Response
from fastapi.testclient import TestClient

from src import app, schemas
from src.backend import store


@pytest.fixture(scope="session")
def test_client():

    return TestClient(app.APP)


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
    assert store.is_processed("rocket-foo", 1)


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

    r = test_client.get("/state/rocket-foo")
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

    r = test_client.get("/state/rocket-foo")
    rocket = r.json()
    assert rocket.get("speed") == 1050


def test_message_processing_is_atomic(test_client, monkeypatch):
    class MockSet(set):
        def add(self, *args):
            raise Exception("mocking some exception")

    monkeypatch.setattr(
        "src.app.store._processed_message_num",
        {"rocket-to-fail": MockSet()},
    )

    with pytest.raises(Exception):
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

    r = test_client.get("/state/rocket-to-fail")
    assert not r.ok
    assert r.status_code == 404


def test_message_exploded(test_client):
    r = test_client.post(
        "/messages",
        json={
            "metadata": {
                "channel": "rocket-foo",
                "messageNumber": 5,
                "messageTime": str(datetime.now()),
                "messageType": "RocketExploded",
            },
            "message": {"reason": "not_enough_nutrient"},
        },
    )
    assert r.status_code == 200

    r = test_client.get("/state/rocket-foo")
    rocket = r.json()
    assert rocket.get("exploded_reason") == "not_enough_nutrient"


def test_message_mission_changed(test_client):
    r = test_client.post(
        "/messages",
        json={
            "metadata": {
                "channel": "rocket-foo",
                "messageNumber": 4,
                "messageTime": str(datetime.now()),
                "messageType": "RocketMissionChanged",
            },
            "message": {"newMission": "find_eagle"},
        },
    )
    assert r.status_code == 200

    r = test_client.get("/state/rocket-foo")
    rocket = r.json()
    assert rocket.get("mission") == "find_eagle"


def test_get_channels_sort_by_latest_update(test_client):
    test_client.post(
        "/messages",
        json={
            "metadata": {
                "channel": "rocket-1",
                "messageNumber": 1,
                "messageTime": "2021-05-09T20:39:51.756997",
                "messageType": "RocketMissionChanged",
            },
            "message": {"newMission": "some_mission"},
        },
    )
    test_client.post(
        "/messages",
        json={
            "metadata": {
                "channel": "rocket-2",
                "messageNumber": 1,
                "messageTime": "2021-04-09T20:39:51.756997",
                "messageType": "RocketMissionChanged",
            },
            "message": {"newMission": "some_mission"},
        },
    )
    test_client.post(
        "/messages",
        json={
            "metadata": {
                "channel": "rocket-3",
                "messageNumber": 1,
                "messageTime": "2021-03-09T20:39:51.756997",
                "messageType": "RocketMissionChanged",
            },
            "message": {"newMission": "some_mission"},
        },
    )
    r = test_client.get("/list")
    rockets = r.json()
    assert rockets[:3] == ["rocket-3", "rocket-2", "rocket-1"]
