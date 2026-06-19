from flask import Flask, render_template, request, redirect, jsonify, Response, send_from_directory
import sqlite3
import json
import io
import csv
from datetime import date, datetime, timedelta

app = Flask(__name__)

DB_NAME = "database.db"


# =========================
# DATABASE CONNECTION
# =========================

def get_db_connection():

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    return conn


# =========================
# CREATE DATABASE
# =========================

def init_db():

    conn = get_db_connection()
    cursor = conn.cursor()

    # =====================
    # DAILY LOGS
    # =====================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS daily_logs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        date TEXT UNIQUE,
        day_name TEXT,

        status TEXT,
        full_day_outing INTEGER,

        wake_up_time TEXT,

        brush INTEGER,
        oil_pulling INTEGER,

        drink_type TEXT,

        almonds INTEGER,

        bath_type TEXT,

        breakfast TEXT,
        lunch TEXT,
        dinner TEXT,

        snack_type TEXT,
        snack_other TEXT,

        face_wash_morning INTEGER,
        ice_cube INTEGER,

        sunscreen_morning INTEGER,
        cc_cream INTEGER,

        sunscreen_afternoon INTEGER,

        face_wash_evening INTEGER,
        moisturizer INTEGER,

        hair_wash INTEGER,
        hair_care_type TEXT,

        kumkumadi_oil INTEGER,

        water_intake REAL,

        infused_water INTEGER,
        infused_water_amount REAL,

        screen_time REAL,
        laptop_time REAL,

        sleep_time TEXT,

        mood TEXT,

        journal TEXT

    )

    """)

    # =====================
    # STUDY LOGS
    # =====================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS study_logs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        date TEXT,

        session TEXT,

        subject TEXT,
        topic TEXT,

        start_time TEXT,
        end_time TEXT

    )

    """)

    # =====================
    # TOMORROW PREPARATION
    # =====================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS tomorrow_preparation (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        date TEXT UNIQUE,

        soak_almonds INTEGER,
        soak_badam_pisin INTEGER,

        soak_konda_kadalai INTEGER,
        soak_kadalaparuppu INTEGER,
        soak_pachapayir INTEGER,

        eggs_available INTEGER,
        paneer_available INTEGER,

        college_tomorrow INTEGER,

        bag_packed INTEGER,
        dress_ironed INTEGER

    )

    """)

    # =====================
    # PLANNER TASKS
    # =====================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS planner_tasks (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        task_name TEXT,

        task_type TEXT,

        submission_date TEXT,

        target_date TEXT,

        priority TEXT,

        status TEXT DEFAULT 'Pending'

    )

    """)

    # =====================
    # DRAFT AUTOSAVE
    # =====================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS drafts (

        date TEXT PRIMARY KEY,
        form_data TEXT,
        updated_at TEXT

    )

    """)

    conn.commit()
    conn.close()


# =========================
# INITIALIZE DATABASE
# =========================

init_db()
# =========================
# STREAK HELPERS
# =========================

def get_logged_dates():
    """Return a sorted set of date strings (YYYY-MM-DD) that have a daily_logs entry."""
    conn = get_db_connection()
    rows = conn.execute("SELECT date FROM daily_logs ORDER BY date ASC").fetchall()
    conn.close()
    return sorted({r["date"] for r in rows})


def calculate_streaks():
    """Return (current_streak, best_streak) based on consecutive calendar days logged."""
    logged = get_logged_dates()
    if not logged:
        return 0, 0

    logged_set = set(logged)
    date_objs = sorted(datetime.strptime(d, "%Y-%m-%d").date() for d in logged)

    # Best streak: longest run of consecutive calendar dates
    best = 1
    run = 1
    for i in range(1, len(date_objs)):
        if (date_objs[i] - date_objs[i - 1]).days == 1:
            run += 1
        else:
            run = 1
        best = max(best, run)

    # Current streak: walk backwards from today (or yesterday if today not logged yet)
    today = date.today()
    cursor_day = today if str(today) in logged_set else today - timedelta(days=1)
    current = 0
    while str(cursor_day) in logged_set:
        current += 1
        cursor_day -= timedelta(days=1)

    return current, best


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():

    return render_template("index.html")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    today_date = str(date.today())
    day_name = datetime.today().strftime("%A")

    conn = get_db_connection()

    row = conn.execute(
        "SELECT * FROM daily_logs WHERE date = ?",
        (today_date,)
    ).fetchone()

    draft_row = conn.execute(
        "SELECT form_data FROM drafts WHERE date = ?",
        (today_date,)
    ).fetchone()

    conn.close()

    current_streak, best_streak = calculate_streaks()

    draft_json = draft_row["form_data"] if draft_row else "null"

    return render_template(
        "dashboard.html",
        data=row,
        today=today_date,
        day_name=day_name,
        current_streak=current_streak,
        best_streak=best_streak,
        draft_json=draft_json
    )

# =========================
# PLANNER PAGE
# =========================

@app.route("/planner")
def planner():

    conn = get_db_connection()

    tasks = conn.execute("""

        SELECT *
        FROM planner_tasks

        ORDER BY submission_date ASC

    """).fetchall()

    conn.close()

    return render_template(
        "planner.html",
        tasks=tasks
    )


# =========================
# HEALTH CHECK
# =========================

@app.route("/ping")
def ping():

    return jsonify({
        "status": "running",
        "app": "RoutineX"
    })
# =========================
# SAVE DAILY LOG
# =========================

@app.route("/save", methods=["POST"])
def save_daily_log():

    today_date = str(date.today())

    conn = get_db_connection()
    cursor = conn.cursor()

    # ---------------------
    # BASIC FIELDS
    # ---------------------

    status = request.form.get("status")
    full_day_outing = 1 if request.form.get("full_day_outing") else 0

    wake_up_time = request.form.get("wake_up_time")

    brush = 1 if request.form.get("brush") else 0
    oil_pulling = 1 if request.form.get("oil_pulling") else 0

    drink_type = request.form.get("drink_type")

    almonds = 1 if request.form.get("almonds") else 0

    bath_type = request.form.get("bath_type")

    breakfast = request.form.get("breakfast")
    lunch = request.form.get("lunch")
    dinner = request.form.get("dinner")

    snack_type = request.form.get("snack_type")
    snack_other = request.form.get("snack_other")

    face_wash_morning = 1 if request.form.get("face_wash_morning") else 0
    ice_cube = 1 if request.form.get("ice_cube") else 0

    sunscreen_morning = 1 if request.form.get("sunscreen_morning") else 0
    cc_cream = 1 if request.form.get("cc_cream") else 0

    sunscreen_afternoon = 1 if request.form.get("sunscreen_afternoon") else 0

    face_wash_evening = 1 if request.form.get("face_wash_evening") else 0
    moisturizer = 1 if request.form.get("moisturizer") else 0

    hair_wash = 1 if request.form.get("hair_wash") else 0
    hair_care_type = request.form.get("hair_care_type")

    kumkumadi_oil = 1 if request.form.get("kumkumadi_oil") else 0

    water_intake = request.form.get("water_intake")

    infused_water = 1 if request.form.get("infused_water") else 0
    infused_water_amount = request.form.get("infused_water_amount")

    screen_time = request.form.get("screen_time")
    laptop_time = request.form.get("laptop_time")

    sleep_time = request.form.get("sleep_time")

    mood = request.form.get("mood")
    journal = request.form.get("journal")

    # ---------------------
    # CHECK EXISTING DATE
    # ---------------------

    existing = cursor.execute(
        """
        SELECT id
        FROM daily_logs
        WHERE date = ?
        """,
        (today_date,)
    ).fetchone()

    # ---------------------
    # UPDATE
    # ---------------------

    if existing:

        cursor.execute("""

        UPDATE daily_logs

        SET

        status = ?,
        full_day_outing = ?,

        wake_up_time = ?,

        brush = ?,
        oil_pulling = ?,

        drink_type = ?,

        almonds = ?,

        bath_type = ?,

        breakfast = ?,
        lunch = ?,
        dinner = ?,

        snack_type = ?,
        snack_other = ?,

        face_wash_morning = ?,
        ice_cube = ?,

        sunscreen_morning = ?,
        cc_cream = ?,

        sunscreen_afternoon = ?,

        face_wash_evening = ?,
        moisturizer = ?,

        hair_wash = ?,
        hair_care_type = ?,

        kumkumadi_oil = ?,

        water_intake = ?,

        infused_water = ?,
        infused_water_amount = ?,

        screen_time = ?,
        laptop_time = ?,

        sleep_time = ?,

        mood = ?,
        journal = ?

        WHERE date = ?

        """, (

            status,
            full_day_outing,

            wake_up_time,

            brush,
            oil_pulling,

            drink_type,

            almonds,

            bath_type,

            breakfast,
            lunch,
            dinner,

            snack_type,
            snack_other,

            face_wash_morning,
            ice_cube,

            sunscreen_morning,
            cc_cream,

            sunscreen_afternoon,

            face_wash_evening,
            moisturizer,

            hair_wash,
            hair_care_type,

            kumkumadi_oil,

            water_intake,

            infused_water,
            infused_water_amount,

            screen_time,
            laptop_time,

            sleep_time,

            mood,
            journal,

            today_date

        ))

    # ---------------------
    # INSERT
    # ---------------------

    else:

        day_name = datetime.today().strftime("%A")

        cursor.execute("""

        INSERT INTO daily_logs (

            date,
            day_name,

            status,
            full_day_outing,

            wake_up_time,

            brush,
            oil_pulling,

            drink_type,

            almonds,

            bath_type,

            breakfast,
            lunch,
            dinner,

            snack_type,
            snack_other,

            face_wash_morning,
            ice_cube,

            sunscreen_morning,
            cc_cream,

            sunscreen_afternoon,

            face_wash_evening,
            moisturizer,

            hair_wash,
            hair_care_type,

            kumkumadi_oil,

            water_intake,

            infused_water,
            infused_water_amount,

            screen_time,
            laptop_time,

            sleep_time,

            mood,
            journal

        )

        VALUES (

            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?

        )

        """, (

            today_date,
            day_name,

            status,
            full_day_outing,

            wake_up_time,

            brush,
            oil_pulling,

            drink_type,

            almonds,

            bath_type,

            breakfast,
            lunch,
            dinner,

            snack_type,
            snack_other,

            face_wash_morning,
            ice_cube,

            sunscreen_morning,
            cc_cream,

            sunscreen_afternoon,

            face_wash_evening,
            moisturizer,

            hair_wash,
            hair_care_type,

            kumkumadi_oil,

            water_intake,

            infused_water,
            infused_water_amount,

            screen_time,
            laptop_time,

            sleep_time,

            mood,
            journal

        ))

    cursor.execute("DELETE FROM drafts WHERE date = ?", (today_date,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")
# =========================
# SAVE STUDY LOGS
# =========================

@app.route("/save-study", methods=["POST"])
def save_study():

    study_date = str(date.today())

    conn = get_db_connection()
    cursor = conn.cursor()

    subjects = request.form.getlist("subject[]")
    topics = request.form.getlist("topic[]")
    starts = request.form.getlist("start_time[]")
    ends = request.form.getlist("end_time[]")
    sessions = request.form.getlist("session[]")

    cursor.execute(
        """
        DELETE FROM study_logs
        WHERE date = ?
        """,
        (study_date,)
    )

    for i in range(len(subjects)):

        if subjects[i].strip() == "":
            continue

        cursor.execute("""

        INSERT INTO study_logs (

            date,
            session,
            subject,
            topic,
            start_time,
            end_time

        )

        VALUES (?, ?, ?, ?, ?, ?)

        """, (

            study_date,
            sessions[i],
            subjects[i],
            topics[i],
            starts[i],
            ends[i]

        ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# =========================
# SAVE TOMORROW PREPARATION
# =========================

@app.route("/save-preparation", methods=["POST"])
def save_preparation():

    prep_date = str(date.today())

    conn = get_db_connection()
    cursor = conn.cursor()

    soak_almonds = 1 if request.form.get("soak_almonds") else 0
    soak_badam_pisin = 1 if request.form.get("soak_badam_pisin") else 0

    soak_konda_kadalai = 1 if request.form.get("soak_konda_kadalai") else 0
    soak_kadalaparuppu = 1 if request.form.get("soak_kadalaparuppu") else 0
    soak_pachapayir = 1 if request.form.get("soak_pachapayir") else 0

    eggs_available = 1 if request.form.get("eggs_available") else 0
    paneer_available = 1 if request.form.get("paneer_available") else 0

    college_tomorrow = 1 if request.form.get("college_tomorrow") else 0

    bag_packed = 1 if request.form.get("bag_packed") else 0
    dress_ironed = 1 if request.form.get("dress_ironed") else 0

    existing = cursor.execute(
        """
        SELECT id
        FROM tomorrow_preparation
        WHERE date = ?
        """,
        (prep_date,)
    ).fetchone()

    if existing:

        cursor.execute("""

        UPDATE tomorrow_preparation

        SET

        soak_almonds = ?,
        soak_badam_pisin = ?,

        soak_konda_kadalai = ?,
        soak_kadalaparuppu = ?,
        soak_pachapayir = ?,

        eggs_available = ?,
        paneer_available = ?,

        college_tomorrow = ?,

        bag_packed = ?,
        dress_ironed = ?

        WHERE date = ?

        """, (

            soak_almonds,
            soak_badam_pisin,

            soak_konda_kadalai,
            soak_kadalaparuppu,
            soak_pachapayir,

            eggs_available,
            paneer_available,

            college_tomorrow,

            bag_packed,
            dress_ironed,

            prep_date

        ))

    else:

        cursor.execute("""

        INSERT INTO tomorrow_preparation (

            date,

            soak_almonds,
            soak_badam_pisin,

            soak_konda_kadalai,
            soak_kadalaparuppu,
            soak_pachapayir,

            eggs_available,
            paneer_available,

            college_tomorrow,

            bag_packed,
            dress_ironed

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            prep_date,

            soak_almonds,
            soak_badam_pisin,

            soak_konda_kadalai,
            soak_kadalaparuppu,
            soak_pachapayir,

            eggs_available,
            paneer_available,

            college_tomorrow,

            bag_packed,
            dress_ironed

        ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# =========================
# ADD PLANNER TASK
# =========================

@app.route("/add-task", methods=["POST"])
def add_task():

    conn = get_db_connection()
    cursor = conn.cursor()

    task_name = request.form.get("task_name")
    task_type = request.form.get("task_type")

    submission_date = request.form.get("submission_date")
    target_date = request.form.get("target_date")

    priority = request.form.get("priority")

    cursor.execute("""

    INSERT INTO planner_tasks (

        task_name,
        task_type,

        submission_date,
        target_date,

        priority

    )

    VALUES (?, ?, ?, ?, ?)

    """, (

        task_name,
        task_type,

        submission_date,
        target_date,

        priority

    ))

    conn.commit()
    conn.close()

    return redirect("/planner")


# =========================
# UPCOMING TASKS
# =========================

@app.route("/upcoming-tasks")
def upcoming_tasks():

    conn = get_db_connection()

    tasks = conn.execute("""

    SELECT *
    FROM planner_tasks

    WHERE
    julianday(submission_date)
    - julianday('now')

    BETWEEN 0 AND 10

    ORDER BY submission_date ASC

    """).fetchall()

    conn.close()

    result = []

    for task in tasks:

        result.append({

            "task_name": task["task_name"],
            "task_type": task["task_type"],
            "submission_date": task["submission_date"],
            "priority": task["priority"]

        })

    return jsonify(result)


# =========================
# ANALYTICS PAGE
# =========================

@app.route("/analytics")
def analytics_page():
    current_streak, best_streak = calculate_streaks()
    return render_template(
        "analytics.html",
        current_streak=current_streak,
        best_streak=best_streak
    )


# =========================
# API: STREAK
# =========================

@app.route("/api/streak")
def api_streak():
    current_streak, best_streak = calculate_streaks()
    return jsonify({
        "current_streak": current_streak,
        "best_streak": best_streak
    })


# =========================
# API: WEEKLY SUMMARY (last 7 days)
# =========================

@app.route("/api/weekly-summary")
def api_weekly_summary():
    conn = get_db_connection()

    today = date.today()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    day_strs = [str(d) for d in days]

    rows = conn.execute(
        f"SELECT * FROM daily_logs WHERE date IN ({','.join('?' for _ in day_strs)})",
        day_strs
    ).fetchall()
    conn.close()

    rows_by_date = {r["date"]: r for r in rows}

    daily_breakdown = []
    completed_days = 0
    water_values = []

    for d in day_strs:
        row = rows_by_date.get(d)
        logged = row is not None
        if logged:
            completed_days += 1
            try:
                if row["water_intake"]:
                    water_values.append(float(row["water_intake"]))
            except (TypeError, ValueError):
                pass

        daily_breakdown.append({
            "date": d,
            "day_name": datetime.strptime(d, "%Y-%m-%d").strftime("%A"),
            "logged": logged,
            "status": row["status"] if logged else None
        })

    completion_rate = round((completed_days / 7) * 100, 1)
    avg_water = round(sum(water_values) / len(water_values), 2) if water_values else 0

    return jsonify({
        "range": {"start": day_strs[0], "end": day_strs[-1]},
        "completed_days": completed_days,
        "total_days": 7,
        "completion_rate": completion_rate,
        "average_water_intake": avg_water,
        "daily_breakdown": daily_breakdown
    })


# =========================
# API: MONTHLY SUMMARY (last 30 days)
# =========================

@app.route("/api/monthly-summary")
def api_monthly_summary():
    conn = get_db_connection()

    today = date.today()
    days = [today - timedelta(days=i) for i in range(29, -1, -1)]
    day_strs = [str(d) for d in days]

    rows = conn.execute(
        f"SELECT * FROM daily_logs WHERE date IN ({','.join('?' for _ in day_strs)})",
        day_strs
    ).fetchall()

    total_study = conn.execute(
        "SELECT COUNT(*) FROM study_logs WHERE date >= ?",
        (day_strs[0],)
    ).fetchone()[0]

    conn.close()

    rows_by_date = {r["date"]: r for r in rows}

    chart_data = []
    completed_days = 0
    water_values = []
    sleep_count = {}
    mood_count = {}

    for d in day_strs:
        row = rows_by_date.get(d)
        logged = row is not None
        if logged:
            completed_days += 1
            try:
                if row["water_intake"]:
                    water_values.append(float(row["water_intake"]))
            except (TypeError, ValueError):
                pass
            if row["mood"]:
                mood_count[row["mood"]] = mood_count.get(row["mood"], 0) + 1

        chart_data.append({"date": d, "completed": 1 if logged else 0})

    completion_rate = round((completed_days / 30) * 100, 1)
    avg_water = round(sum(water_values) / len(water_values), 2) if water_values else 0
    top_mood = max(mood_count, key=mood_count.get) if mood_count else None

    current_streak, best_streak = calculate_streaks()

    return jsonify({
        "range": {"start": day_strs[0], "end": day_strs[-1]},
        "tracked_days": completed_days,
        "total_days": 30,
        "completion_rate": completion_rate,
        "study_entries": total_study,
        "average_water_intake": avg_water,
        "top_mood": top_mood,
        "current_streak": current_streak,
        "best_streak": best_streak,
        "chart_data": chart_data
    })


# =========================
# DRAFT AUTOSAVE API
# =========================

@app.route("/api/draft", methods=["GET"])
def get_draft():
    today_date = str(date.today())
    conn = get_db_connection()
    row = conn.execute(
        "SELECT form_data, updated_at FROM drafts WHERE date = ?",
        (today_date,)
    ).fetchone()
    conn.close()

    if not row:
        return jsonify({"draft": None})

    try:
        data = json.loads(row["form_data"])
    except (TypeError, ValueError):
        data = None

    return jsonify({"draft": data, "updated_at": row["updated_at"]})


@app.route("/api/draft", methods=["POST"])
def save_draft():
    today_date = str(date.today())
    payload = request.get_json(silent=True) or {}
    form_data = json.dumps(payload)
    updated_at = datetime.now().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO drafts (date, form_data, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            form_data = excluded.form_data,
            updated_at = excluded.updated_at
        """,
        (today_date, form_data, updated_at)
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "saved", "updated_at": updated_at})


@app.route("/api/draft", methods=["DELETE"])
def delete_draft():
    today_date = str(date.today())
    conn = get_db_connection()
    conn.execute("DELETE FROM drafts WHERE date = ?", (today_date,))
    conn.commit()
    conn.close()
    return jsonify({"status": "cleared"})


# =========================
# EXPORT BACKUP (JSON + CSV)
# =========================

@app.route("/export/json")
def export_json():
    conn = get_db_connection()

    data = {
        "exported_at": datetime.now().isoformat(),
        "daily_logs": [dict(r) for r in conn.execute("SELECT * FROM daily_logs ORDER BY date ASC").fetchall()],
        "study_logs": [dict(r) for r in conn.execute("SELECT * FROM study_logs ORDER BY date ASC").fetchall()],
        "tomorrow_preparation": [dict(r) for r in conn.execute("SELECT * FROM tomorrow_preparation ORDER BY date ASC").fetchall()],
        "planner_tasks": [dict(r) for r in conn.execute("SELECT * FROM planner_tasks ORDER BY submission_date ASC").fetchall()]
    }

    conn.close()

    buffer = io.BytesIO(json.dumps(data, indent=2).encode("utf-8"))
    filename = f"routinex-backup-{date.today()}.json"

    return Response(
        buffer.getvalue(),
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/export/csv")
def export_csv():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM daily_logs ORDER BY date ASC").fetchall()
    conn.close()

    output = io.StringIO()

    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(r))
    else:
        output.write("No daily log data available\n")

    filename = f"routinex-daily-logs-{date.today()}.csv"

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# =========================
# PWA: MANIFEST + SERVICE WORKER
# =========================

@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json", mimetype="application/manifest+json")


@app.route("/sw.js")
def service_worker():
    return send_from_directory("static/js", "sw.js", mimetype="application/javascript")


@app.route("/offline")
def offline():
    return render_template("offline.html")
    
# =========================
# RUN APP
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )