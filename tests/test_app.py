"""HTTP-level regression tests using isolated, fictional SQLite records."""

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.sqlite3"),
                       "SECRET_KEY": "test-only-secret", "APP_ENV": "development"})


@pytest.fixture
def client(app):
    return app.test_client()


def write(client, method, path, payload=None):
    token = client.get("/api/csrf").get_json()["csrf_token"]
    return client.open(path, method=method, json=payload,
                       headers={"X-CSRF-Token": token})


def create(client, table, payload):
    response = write(client, "POST", f"/api/{table}", payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()


@pytest.fixture
def setup(client):
    student = create(client, "students", {"name": "Casey Example", "year": 8,
                                         "contact": "parent@example.invalid"})
    tutor = create(client, "tutors", {"name": "Jordan Demo", "subjects": "Math, English"})
    # Deterministically choose a future Monday, independent of execution date.
    day = date.today() + timedelta(days=14)
    day += timedelta(days=(-day.weekday()) % 7)
    window = create(client, "availability", {"tutor_id": tutor["id"], "weekday": 0,
                                            "start_time": "09:00", "end_time": "12:00"})
    booking = {"student_id": student["id"], "tutor_id": tutor["id"], "subject": "Math",
               "session_date": day.isoformat(), "start_time": "09:00", "duration": 60}
    return {"student": student, "tutor": tutor, "window": window, "booking": booking}


def test_create_read_update_and_delete_semantics(client, setup):
    student = setup["student"]
    assert client.get(f"/api/students/{student['id']}").get_json()["year"] == 8
    updated = write(client, "PATCH", f"/api/students/{student['id']}", {"year": 9})
    assert updated.status_code == 200
    assert updated.get_json()["name"] == "Casey Example"
    assert updated.get_json()["year"] == 9
    assert len(client.get("/api/students").get_json()) == 1
    assert write(client, "DELETE", f"/api/students/{student['id']}").get_json()["active"] == 0
    extra = create(client, "availability", {"tutor_id": setup["tutor"]["id"], "weekday": 1,
                                           "start_time": "09:00", "end_time": "10:00"})
    assert write(client, "DELETE", f"/api/availability/{extra['id']}").status_code == 204
    assert client.get(f"/api/availability/{extra['id']}").status_code == 404


@pytest.mark.parametrize("start,duration,expected", [
    ("09:00", 90, 201), ("11:00", 60, 201), ("08:59", 60, 400), ("11:01", 60, 400),
])
def test_whole_session_must_fit_window_boundaries(client, setup, start, duration, expected):
    response = write(client, "POST", "/api/sessions",
                     {**setup["booking"], "start_time": start, "duration": duration})
    assert response.status_code == expected
    assert len(client.get("/api/sessions").get_json()) == (1 if expected == 201 else 0)


def test_new_session_must_start_booked(client, setup):
    response = write(client, "POST", "/api/sessions", {**setup["booking"], "status": "attended"})
    assert response.status_code == 400
    assert client.get("/api/sessions").get_json() == []


def test_session_cannot_bridge_separate_availability_windows(client, setup):
    assert write(client, "PATCH", f"/api/availability/{setup['window']['id']}",
                 {"end_time": "10:00"}).status_code == 200
    create(client, "availability", {"tutor_id": setup["tutor"]["id"], "weekday": 0,
                                    "start_time": "10:00", "end_time": "12:00"})
    response = write(client, "POST", "/api/sessions",
                     {**setup["booking"], "start_time": "09:30", "duration": 60})
    assert response.status_code == 400
    assert client.get("/api/sessions").get_json() == []


def test_availability_uses_session_weekday(client, setup):
    tuesday = date.fromisoformat(setup["booking"]["session_date"]) + timedelta(days=1)
    rejected = write(client, "POST", "/api/sessions",
                     {**setup["booking"], "session_date": tuesday.isoformat()})
    assert rejected.status_code == 400
    create(client, "availability", {"tutor_id": setup["tutor"]["id"], "weekday": 1,
                                    "start_time": "09:00", "end_time": "12:00"})
    assert write(client, "POST", "/api/sessions",
                 {**setup["booking"], "session_date": tuesday.isoformat()}).status_code == 201


def test_invalid_move_is_rejected_without_losing_original(client, setup):
    session = create(client, "sessions", setup["booking"])
    response = write(client, "PATCH", f"/api/sessions/{session['id']}",
                     {"start_time": "11:30", "notes": "must not persist"})
    assert response.status_code == 400
    assert client.get(f"/api/sessions/{session['id']}").get_json() == session
    moved = write(client, "PATCH", f"/api/sessions/{session['id']}", {"start_time": "10:00"})
    assert moved.status_code == 200
    assert moved.get_json()["start_time"] == "10:00"
    assert moved.get_json()["id"] == session["id"]


@pytest.mark.parametrize("change", ["date", "tutor", "duration"])
def test_every_scheduling_move_obeys_same_window_rule(client, setup, change):
    session = create(client, "sessions", {**setup["booking"], "start_time": "11:00"})
    if change == "date":
        next_day = date.fromisoformat(session["session_date"]) + timedelta(days=1)
        values = {"session_date": next_day.isoformat()}
    elif change == "tutor":
        other = create(client, "tutors", {"name": "Riley Sample", "subjects": "Math"})
        values = {"tutor_id": other["id"]}
    else:
        values = {"duration": 90}
    path = f"/api/sessions/{session['id']}"
    assert write(client, "PATCH", path, values).status_code == 400
    assert client.get(path).get_json() == session


def test_removing_one_window_is_allowed_when_another_still_covers_booking(client, setup):
    session = create(client, "sessions", setup["booking"])
    create(client, "availability", {"tutor_id": setup["tutor"]["id"], "weekday": 0,
                                    "start_time": "08:00", "end_time": "13:00"})
    assert write(client, "DELETE", f"/api/availability/{setup['window']['id']}").status_code == 204
    assert client.get(f"/api/sessions/{session['id']}").get_json() == session


@pytest.mark.parametrize("method,payload", [("PATCH", {"end_time": "09:30"}), ("DELETE", None)])
def test_availability_change_cannot_invalidate_existing_session(client, setup, method, payload):
    session = create(client, "sessions", setup["booking"])
    path = f"/api/availability/{setup['window']['id']}"
    original = client.get(path).get_json()
    response = write(client, method, path, payload)
    assert response.status_code == 400
    assert client.get(path).get_json() == original
    assert client.get(f"/api/sessions/{session['id']}").get_json() == session


@pytest.mark.parametrize("table", ["students", "tutors"])
def test_deactivation_preserves_history_and_blocks_new_booking(client, setup, table):
    session = create(client, "sessions", setup["booking"])
    record = setup["student" if table == "students" else "tutor"]
    path = f"/api/{table}/{record['id']}"
    assert write(client, "DELETE", path).get_json()["active"] == 0
    assert client.get(path).status_code == 200
    assert client.get(f"/api/sessions/{session['id']}").get_json() == session
    assert write(client, "POST", "/api/sessions",
                 {**setup["booking"], "start_time": "10:00"}).status_code == 400
    # Recording an outcome for an existing booking must remain possible.
    assert write(client, "PATCH", f"/api/sessions/{session['id']}",
                 {"status": "attended"}).status_code == 200


def test_cancellation_retains_record_and_frees_time(client, setup):
    session = create(client, "sessions", setup["booking"])
    path = f"/api/sessions/{session['id']}"
    cancelled = write(client, "DELETE", path)
    assert cancelled.status_code == 200
    assert cancelled.get_json()["status"] == "cancelled"
    assert client.get(path).get_json()["student_id"] == setup["student"]["id"]
    assert client.get(f"/api/tutors/{setup['tutor']['id']}/upcoming").get_json() == []
    assert write(client, "POST", "/api/sessions", setup["booking"]).status_code == 201
    assert len(client.get("/api/sessions").get_json()) == 2


def test_tutor_view_empty_state_and_filter(client, setup):
    tutor_id = setup["tutor"]["id"]
    assert client.get(f"/api/tutors/{tutor_id}/upcoming").get_json() == []
    response = client.get(f"/my-schedule?tutor_id={tutor_id}")
    assert response.status_code == 200
    # This page is a JavaScript application shell; the API establishes its empty data state.
    assert b"Redgum Tutoring Schedule" in response.data
    session = create(client, "sessions", setup["booking"])
    other = create(client, "tutors", {"name": "Riley Sample", "subjects": "Math"})
    assert client.get(f"/api/tutors/{other['id']}/upcoming").get_json() == []
    mine = client.get(f"/api/tutors/{tutor_id}/upcoming").get_json()
    assert [row["id"] for row in mine] == [session["id"]]


def test_data_survives_app_recreation(app, client, setup):
    session = create(client, "sessions", setup["booking"])
    restarted = create_app({"TESTING": True, "DATABASE": app.config["DATABASE"],
                            "SECRET_KEY": "test-only-secret", "APP_ENV": "development"})
    assert restarted.test_client().get(f"/api/sessions/{session['id']}").get_json() == session


def test_csrf_missing_wrong_and_valid_tokens(client):
    payload = {"name": "Casey Example", "year": 8, "contact": "parent@example.invalid"}
    assert client.post("/api/students", json=payload).status_code == 400
    token = client.get("/api/csrf").get_json()["csrf_token"]
    assert client.post("/api/students", json=payload,
                       headers={"X-CSRF-Token": "wrong"}).status_code == 400
    assert client.get("/api/students").get_json() == []
    assert client.post("/api/students", json=payload,
                       headers={"X-CSRF-Token": token}).status_code == 201
    stranger = client.application.test_client()
    assert stranger.post("/api/students", json=payload,
                          headers={"X-CSRF-Token": token}).status_code == 400


@pytest.mark.parametrize("secret", [None, "", "local-development-only"])
def test_production_requires_non_default_secret(tmp_path, secret):
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app({"APP_ENV": "production", "SECRET_KEY": secret,
                    "DATABASE": str(tmp_path / "prod.sqlite3")})


@pytest.mark.parametrize("changes", [{"subject": "Chemistry"}, {"duration": 0},
                                      {"start_time": "9:00"}, {"session_date": "invalid"}])
def test_invalid_session_input_does_not_create_records(client, setup, changes):
    assert write(client, "POST", "/api/sessions", {**setup["booking"], **changes}).status_code == 400
    assert client.get("/api/sessions").get_json() == []


@pytest.mark.parametrize("duration", [30, 59, 61, 120])
def test_session_duration_is_sixty_or_ninety_minutes(client, setup, duration):
    assert write(client, "POST", "/api/sessions",
                 {**setup["booking"], "duration": duration}).status_code == 400


@pytest.mark.parametrize("status", ["attended", "missed", "cancelled"])
def test_non_booked_history_does_not_block_availability_removal(client, setup, status):
    session = create(client, "sessions", setup["booking"])
    assert write(client, "PATCH", f"/api/sessions/{session['id']}", {"status": status}).status_code == 200
    assert write(client, "DELETE", f"/api/availability/{setup['window']['id']}").status_code == 204
    historical = client.get(f"/api/sessions/{session['id']}").get_json()
    assert historical["status"] == status
    assert historical["session_date"] == session["session_date"]


def test_student_subjects_can_be_recorded_and_updated(client, setup):
    path = f"/api/students/{setup['student']['id']}"
    response = write(client, "PATCH", path, {"subjects": "Math, English"})
    assert response.status_code == 200
    assert response.get_json()["subjects"] == "Math, English"


@pytest.mark.parametrize("changes", [{"year": 4}, {"year": 13}, {"contact": ""}, {"contact": "   "}])
def test_student_requires_year_five_to_twelve_and_family_contact(client, changes):
    payload = {"name": "Casey Example", "year": 8, "contact": "parent@example.invalid"}
    assert write(client, "POST", "/api/students", {**payload, **changes}).status_code == 400
    assert client.get("/api/students").get_json() == []


def test_html_form_route_saves_subjects_and_rejects_incomplete_student(client):
    token = client.get("/api/csrf").get_json()["csrf_token"]
    payload = {"name": "Casey Example", "year": "8", "contact": "parent@example.invalid",
               "subjects": "Math, English", "csrf_token": token}
    response = client.post("/students", data=payload)
    assert response.status_code == 302
    records = client.get("/api/students").get_json()
    assert len(records) == 1
    assert records[0]["subjects"] == "Math, English"
    client.post("/students", data={**payload, "contact": ""})
    assert len(client.get("/api/students").get_json()) == 1
