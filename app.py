"""Redgum Tutoring: fictional teaching prototype with persistent scheduling rules."""

import os
import secrets
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import click
from flask import Flask, abort, flash, g, jsonify, redirect, render_template, request, session, url_for


STATUSES = ("booked", "attended", "cancelled", "missed")
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
BUSINESS_TIMEZONE = timezone(timedelta(hours=10), "Australia/Brisbane")
SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL CHECK(length(trim(name)) > 0),
 year INTEGER NOT NULL CHECK(year BETWEEN 5 AND 12), contact TEXT NOT NULL DEFAULT '',
 subjects TEXT NOT NULL DEFAULT '',
 active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
);
CREATE TABLE IF NOT EXISTS tutors (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL CHECK(length(trim(name)) > 0),
 subjects TEXT NOT NULL CHECK(length(trim(subjects)) > 0),
 active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
);
CREATE TABLE IF NOT EXISTS availability (
 id INTEGER PRIMARY KEY, tutor_id INTEGER NOT NULL REFERENCES tutors(id) ON DELETE RESTRICT,
 weekday INTEGER NOT NULL CHECK(weekday BETWEEN 0 AND 6),
 start_time TEXT NOT NULL, end_time TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
 id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE RESTRICT,
 tutor_id INTEGER NOT NULL REFERENCES tutors(id) ON DELETE RESTRICT,
 subject TEXT NOT NULL CHECK(length(trim(subject)) > 0), session_date TEXT NOT NULL,
 start_time TEXT NOT NULL, duration INTEGER NOT NULL CHECK(duration IN (60,90)),
 status TEXT NOT NULL DEFAULT 'booked' CHECK(status IN ('booked','attended','cancelled','missed')),
 notes TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_session_tutor_day ON sessions(tutor_id, session_date);
CREATE INDEX IF NOT EXISTS idx_session_student_day ON sessions(student_id, session_date);
CREATE INDEX IF NOT EXISTS idx_availability_tutor ON availability(tutor_id, weekday);
"""


class RuleError(ValueError):
    """A user-facing input or scheduling error."""


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(
        DATABASE=os.environ.get("APP_DATABASE", str(Path(app.instance_path) / "redgum.sqlite3")),
        APP_ENV=os.environ.get("APP_ENV", "development"),
        BUSINESS_TIMEZONE="Australia/Brisbane",
        SECRET_KEY=os.environ.get("SECRET_KEY", "local-development-only"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if test_config:
        app.config.update(test_config)
        if "APP_DATABASE" in test_config:
            app.config["DATABASE"] = test_config["APP_DATABASE"]
    if app.config["APP_ENV"] == "production" and app.config["SECRET_KEY"] in (None, "", "local-development-only"):
        raise RuntimeError("Set a non-default SECRET_KEY before running in production")
    if app.config["DATABASE"] != ":memory:":
        Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys=ON")
        return g.db

    @app.teardown_appcontext
    def close_db(error):
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()

    with app.app_context():
        db().executescript(SCHEMA)
        db().commit()

    def business_now():
        # Ipswich, Queensland uses UTC+10 throughout the year.
        return datetime.now(BUSINESS_TIMEZONE)

    def csrf_token():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(32)
        return session["csrf_token"]

    @app.before_request
    def protect_writes():
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            given = request.headers.get("X-CSRF-Token", request.form.get("csrf_token", ""))
            expected = session.get("csrf_token", "")
            if not expected or not secrets.compare_digest(str(given), str(expected)):
                abort(400, "Form expired. Refresh the page and try again.")

    @app.context_processor
    def globals_for_templates():
        return {"csrf_token": csrf_token(), "weekdays": WEEKDAYS, "statuses": STATUSES}

    @app.errorhandler(400)
    @app.errorhandler(404)
    def http_error(error):
        if request.path.startswith("/api/"):
            return jsonify(error=error.description), error.code
        return error

    def get_row(table, row_id):
        # Table names originate exclusively from the internal route registry.
        row = db().execute(f"SELECT * FROM {table} WHERE id=?", (row_id,)).fetchone()
        if row is None:
            abort(404, "Record not found")
        return row

    def data():
        if request.is_json:
            values = request.get_json(silent=True)
            if not isinstance(values, dict):
                abort(400, "A JSON object is required.")
            return values
        return request.form

    def text_value(values, key, label, default="", required=False):
        value = values.get(key, default)
        if not isinstance(value, str):
            raise RuleError(f"{label} must be text.")
        value = value.strip()
        if required and not value:
            raise RuleError(f"{label} is required.")
        if len(value) > 1000:
            raise RuleError(f"{label} is too long (maximum 1000 characters).")
        return value

    def integer(value, label, low=None, high=None):
        try:
            if isinstance(value, bool) or str(value).strip() != str(int(value)):
                raise ValueError
            result = int(value)
        except (TypeError, ValueError):
            raise RuleError(f"{label} must be a whole number.") from None
        if (low is not None and result < low) or (high is not None and result > high):
            raise RuleError(f"{label} must be between {low} and {high}.")
        return result

    def flag(value):
        if value in (True, 1, "1", "true", "on"):
            return 1
        if value in (False, 0, "0", "false", "off"):
            return 0
        raise RuleError("Active must be true or false.")

    def valid_time(value):
        if not isinstance(value, str):
            raise RuleError("Time must use HH:MM.")
        try:
            parsed = datetime.strptime(value, "%H:%M")
            if parsed.strftime("%H:%M") != value:
                raise ValueError
        except ValueError:
            raise RuleError("Time must use HH:MM in the 24-hour clock.") from None
        return value

    def minutes(value):
        hours, mins = value.split(":")
        return int(hours) * 60 + int(mins)

    def valid_date(value):
        try:
            parsed = date.fromisoformat(value)
            if parsed.isoformat() != value:
                raise ValueError
            return value
        except (TypeError, ValueError):
            raise RuleError("Date must use YYYY-MM-DD.") from None

    def subject_list(raw):
        if isinstance(raw, list):
            if not all(isinstance(value, str) for value in raw):
                raise RuleError("Subjects must contain text values.")
            raw = ",".join(raw)
        if not isinstance(raw, str):
            raise RuleError("Subjects must be comma-separated text or a list.")
        result = []
        for value in raw.replace("\n", ",").split(","):
            value = value.strip()
            if value and value.casefold() not in {s.casefold() for s in result}:
                result.append(value)
        if not result:
            raise RuleError("At least one subject is required.")
        if len(raw) > 1000:
            raise RuleError("Subjects are too long.")
        return ", ".join(result)

    def validate_student(values, old=None):
        previous = dict(old) if old else {}
        merged = {**previous, **dict(values)}
        return dict(name=text_value(merged, "name", "Student name", required=True),
                    year=integer(merged.get("year"), "School year", 5, 12),
                    contact=text_value(merged, "contact", "Contact", required=True),
                    subjects=text_value(merged, "subjects", "Student subjects"),
                    active=flag(merged.get("active", 1)))

    def validate_tutor(values, old=None):
        merged = {**(dict(old) if old else {}), **dict(values)}
        return dict(name=text_value(merged, "name", "Tutor name", required=True),
                    subjects=subject_list(merged.get("subjects", "")), active=flag(merged.get("active", 1)))

    def validate_availability(values, old=None):
        merged = {**(dict(old) if old else {}), **dict(values)}
        tutor_id = integer(merged.get("tutor_id"), "Tutor ID", 1)
        get_row("tutors", tutor_id)
        start = valid_time(merged.get("start_time", merged.get("start", "")))
        end = valid_time(merged.get("end_time", merged.get("end", "")))
        if minutes(end) <= minutes(start):
            raise RuleError("Availability end must be later than start on the same day.")
        return dict(tutor_id=tutor_id, weekday=integer(merged.get("weekday"), "Weekday", 0, 6),
                    start_time=start, end_time=end)

    def covered(item):
        weekday = date.fromisoformat(item["session_date"]).weekday()
        start = minutes(item["start_time"])
        finish = start + item["duration"]
        windows = db().execute("SELECT * FROM availability WHERE tutor_id=? AND weekday=?",
                               (item["tutor_id"], weekday)).fetchall()
        return any(minutes(w["start_time"]) <= start and finish <= minutes(w["end_time"]) for w in windows)

    def ensure_existing_sessions_covered(tutor_ids):
        now = business_now()
        for tutor_id in set(tutor_ids):
            sessions_for_tutor = db().execute(
                "SELECT * FROM sessions WHERE tutor_id=? AND status='booked' AND (session_date>? OR (session_date=? AND start_time>=?))",
                (tutor_id, now.date().isoformat(), now.date().isoformat(), now.strftime("%H:%M"))).fetchall()
            for item in sessions_for_tutor:
                if not covered(item):
                    raise RuleError(f"Availability change would leave session #{item['id']} outside the tutor's available hours. Move or cancel that session first.")

    def validate_session(values, old=None):
        merged = {**(dict(old) if old else {}), **dict(values)}
        student_id = integer(merged.get("student_id"), "Student ID", 1)
        tutor_id = integer(merged.get("tutor_id"), "Tutor ID", 1)
        student = get_row("students", student_id)
        tutor = get_row("tutors", tutor_id)
        item = dict(student_id=student_id, tutor_id=tutor_id,
                    subject=text_value(merged, "subject", "Subject", required=True),
                    session_date=valid_date(merged.get("session_date", merged.get("date", ""))),
                    start_time=valid_time(merged.get("start_time", merged.get("start", ""))),
                    duration=integer(merged.get("duration"), "Duration (minutes)", 60, 90),
                    status=merged.get("status", "booked"), notes=text_value(merged, "notes", "Notes"))
        if item["status"] not in STATUSES:
            raise RuleError("Choose booked, attended, cancelled or missed.")
        if old is None and item["status"] != "booked":
            raise RuleError("A new session must start in the booked state.")
        if item["duration"] not in (60, 90):
            raise RuleError("Session duration must be 60 or 90 minutes.")
        if minutes(item["start_time"]) + item["duration"] > 1440:
            raise RuleError("A session must end on the same calendar day.")
        scheduling_keys = ("student_id", "tutor_id", "subject", "session_date", "start_time", "duration")
        changed_schedule = old is None or any(item[key] != old[key] for key in scheduling_keys)
        reactivated = old is not None and old["status"] == "cancelled" and item["status"] != "cancelled"
        if changed_schedule or reactivated:
            if not tutor["active"] or not student["active"]:
                raise RuleError("New or moved sessions require an active student and an active tutor.")
            taught = {value.strip().casefold() for value in tutor["subjects"].split(",")}
            if item["subject"].casefold() not in taught:
                raise RuleError("The selected tutor does not teach this subject.")
            # Even a newly-created cancelled record must describe an originally valid booking.
            if not covered(item):
                raise RuleError("The whole session must fit inside one tutor availability window on the correct weekday.")
        return item

    validators = {"students": validate_student, "tutors": validate_tutor,
                  "availability": validate_availability, "sessions": validate_session}

    def save_record(table, values, row_id=None):
        old = get_row(table, row_id) if row_id else None
        cleaned = validators[table](values, old)
        try:
            # BEGIN IMMEDIATE makes validation and persistence a single transaction.
            db().execute("BEGIN IMMEDIATE")
            if table == "sessions":
                cleaned = validate_session(values, old)
            keys = list(cleaned)
            if old:
                assignment = ", ".join(f"{key}=?" for key in keys)
                db().execute(f"UPDATE {table} SET {assignment} WHERE id=?", (*cleaned.values(), row_id))
            else:
                columns = ", ".join(keys)
                placeholders = ", ".join("?" for _ in keys)
                row_id = db().execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", tuple(cleaned.values())).lastrowid
            if table == "availability":
                ensure_existing_sessions_covered([cleaned["tutor_id"]] + ([old["tutor_id"]] if old else []))
            db().commit()
        except Exception:
            db().rollback()
            raise
        return row_id

    def remove_record(table, row_id):
        old = get_row(table, row_id)
        try:
            db().execute("BEGIN IMMEDIATE")
            if table == "sessions":
                db().execute("UPDATE sessions SET status='cancelled' WHERE id=?", (row_id,))
            elif table in ("students", "tutors"):
                # Retire people instead of erasing identities from past bookings.
                db().execute(f"UPDATE {table} SET active=0 WHERE id=?", (row_id,))
            else:
                db().execute("DELETE FROM availability WHERE id=?", (row_id,))
                ensure_existing_sessions_covered([old["tutor_id"]])
            db().commit()
        except Exception:
            db().rollback()
            raise

    def sessions_query(where="", params=()):
        return db().execute(
            "SELECT s.*, st.name AS student_name, t.name AS tutor_name FROM sessions s "
            "JOIN students st ON st.id=s.student_id JOIN tutors t ON t.id=s.tutor_id "
            + where + " ORDER BY s.session_date,s.start_time,s.id", params).fetchall()

    def records(table):
        if table == "sessions":
            return sessions_query()
        if table == "availability":
            return db().execute("SELECT a.*,t.name AS tutor_name FROM availability a JOIN tutors t ON t.id=a.tutor_id ORDER BY t.name,a.weekday,a.start_time").fetchall()
        return db().execute(f"SELECT * FROM {table} ORDER BY active DESC,name,id").fetchall()

    def page(table, row_id=None):
        item = get_row(table, row_id) if row_id else None
        if request.method == "POST":
            try:
                action = request.form.get("action", "save")
                if action in ("delete", "cancel", "deactivate"):
                    if not row_id:
                        raise RuleError("Choose a record first.")
                    remove_record(table, row_id)
                else:
                    save_record(table, request.form, row_id)
                flash("Changes saved.", "success")
                return redirect(url_for(table))
            except (RuleError, sqlite3.IntegrityError) as error:
                flash(str(error) if isinstance(error, RuleError) else "The change would break a data relationship.", "error")
        context = dict(items=records(table), item=item,
                       students=records("students"), tutors=records("tutors"),
                       availability=records("availability"))
        context[table] = context["items"]
        return render_template(f"{table}.html", **context)

    def api_collection(table):
        if request.method == "GET":
            return jsonify([dict(row) for row in records(table)])
        try:
            row_id = save_record(table, data())
            return jsonify(dict(get_row(table, row_id))), 201
        except (RuleError, sqlite3.IntegrityError) as error:
            return jsonify(error=str(error)), 400

    def api_item(table, row_id):
        if request.method == "GET":
            return jsonify(dict(get_row(table, row_id)))
        try:
            if request.method == "DELETE":
                remove_record(table, row_id)
            else:
                save_record(table, data(), row_id)
            return jsonify(dict(get_row(table, row_id))) if table != "availability" or request.method != "DELETE" else ("", 204)
        except (RuleError, sqlite3.IntegrityError) as error:
            return jsonify(error=str(error)), 400

    for table in validators:
        app.add_url_rule(f"/{table}", endpoint=table,
                         view_func=lambda table=table: page(table), methods=["GET", "POST"])
        app.add_url_rule(f"/{table}/<int:row_id>/edit", endpoint=f"edit_{table}",
                         view_func=lambda row_id, table=table: page(table, row_id), methods=["GET", "POST"])
        app.add_url_rule(f"/api/{table}", endpoint=f"api_{table}",
                         view_func=lambda table=table: api_collection(table), methods=["GET", "POST"])
        app.add_url_rule(f"/api/{table}/<int:row_id>", endpoint=f"api_{table}_item",
                         view_func=lambda row_id, table=table: api_item(table, row_id), methods=["GET", "PATCH", "PUT", "DELETE"])

    @app.get("/api/csrf")
    def api_csrf():
        return jsonify(csrf_token=csrf_token())

    @app.get("/health")
    def health():
        db().execute("SELECT 1")
        return {"status": "ok"}

    @app.get("/")
    def index():
        counts = {table: db().execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                  for table in ("students", "tutors", "sessions")}
        now = business_now()
        upcoming = sessions_query(
            "WHERE s.status='booked' AND (s.session_date>? OR (s.session_date=? AND s.start_time>=?))",
            (now.date().isoformat(), now.date().isoformat(), now.strftime("%H:%M")))
        return render_template("index.html", counts=counts, sessions=upcoming, upcoming=upcoming)

    def filtered_schedule():
        conditions, params = [], []
        for key in ("tutor_id", "student_id"):
            if request.args.get(key):
                conditions.append(f"s.{key}=?")
                params.append(integer(request.args[key], key, 1))
        day = request.args.get("date", "")
        if day:
            conditions.append("s.session_date=?")
            params.append(valid_date(day))
        return sessions_query("WHERE " + " AND ".join(conditions) if conditions else "", params)

    @app.get("/schedule")
    @app.get("/api/schedule")
    def schedule():
        try:
            items = filtered_schedule()
        except RuleError as error:
            abort(400, str(error))
        if request.path.startswith("/api/"):
            return jsonify([dict(row) for row in items])
        return render_template("schedule.html", sessions=items, items=items,
                               tutors=records("tutors"), students=records("students"))

    def upcoming_for_tutor(tutor_id):
        get_row("tutors", tutor_id)
        now = business_now()
        return sessions_query(
            "WHERE s.tutor_id=? AND s.status='booked' AND (s.session_date>? OR (s.session_date=? AND s.start_time>=?))",
            (tutor_id, now.date().isoformat(), now.date().isoformat(), now.strftime("%H:%M")))

    @app.get("/api/tutors/<int:tutor_id>/upcoming")
    def api_tutor_upcoming(tutor_id):
        return jsonify([dict(row) for row in upcoming_for_tutor(tutor_id)])

    @app.get("/my-schedule")
    def my_schedule():
        tutor_id = request.args.get("tutor_id", type=int)
        selected = get_row("tutors", tutor_id) if tutor_id else None
        items = upcoming_for_tutor(tutor_id) if tutor_id else []
        return render_template("my_schedule.html", tutors=records("tutors"), selected=selected,
                               sessions=items, items=items)

    @app.cli.command("seed-demo")
    def seed_demo():
        """Create a clearly fictional teaching sample in an empty database."""
        if any(db().execute(f"SELECT 1 FROM {table} LIMIT 1").fetchone() for table in validators):
            raise click.ClickException("Demo seeding requires an empty database.")
        try:
            db().execute("BEGIN IMMEDIATE")
            student_id = db().execute("INSERT INTO students(name,year,contact) VALUES (?,?,?)",
                                      ("Casey Example", 8, "parent@example.invalid")).lastrowid
            tutor_id = db().execute("INSERT INTO tutors(name,subjects) VALUES (?,?)",
                                    ("Jordan Demo", "Mathematics, English")).lastrowid
            for weekday in range(5):
                db().execute("INSERT INTO availability(tutor_id,weekday,start_time,end_time) VALUES (?,?,?,?)",
                             (tutor_id, weekday, "15:00", "19:00"))
            db().commit()
            click.echo(f"Fictional student #{student_id} and tutor #{tutor_id} created; no sessions booked.")
        except Exception:
            db().rollback()
            raise

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8000")), debug=False)
