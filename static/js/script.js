// =========================
// PAGE LOAD
// =========================

document.addEventListener("DOMContentLoaded", function () {

    setupStatusLogic();

    setupSnackLogic();

    setupCollegeLogic();

    setupInfusedWaterLogic();

    setupStudyLogic();

    loadUpcomingTasks();

    setupDraftAutosave();

    registerServiceWorker();

});


// =========================
// PWA: SERVICE WORKER
// =========================

function registerServiceWorker() {

    if (!("serviceWorker" in navigator)) {
        return;
    }

    navigator.serviceWorker
        .register("/sw.js")
        .catch(function (error) {
            console.log("Service worker registration failed", error);
        });
}


// =========================
// DRAFT AUTOSAVE
// =========================

function setupDraftAutosave() {

    const form = document.getElementById("daily-log-form");

    if (!form) {
        return;
    }

    let saveTimeout = null;

    // ---- Restore existing draft ----
    let draft = null;

    try {
        const raw = document.body.getAttribute("data-draft-json");
        draft = raw && raw !== "null" ? JSON.parse(raw) : null;
    } catch (error) {
        draft = null;
    }

    if (draft) {

        Object.keys(draft).forEach(function (name) {

            const field = form.elements[name];

            if (!field) {
                return;
            }

            if (field.type === "checkbox") {
                field.checked = !!draft[name];
            } else if (field.length !== undefined && field.tagName !== "SELECT") {
                // radio-like or multiple inputs sharing a name
                Array.prototype.forEach.call(field, function (input) {
                    if (input.type === "checkbox" || input.type === "radio") {
                        input.checked = input.value === draft[name];
                    } else {
                        input.value = draft[name];
                    }
                });
            } else {
                field.value = draft[name];
            }
        });

        const banner = document.getElementById("draft-banner");

        if (banner) {
            banner.style.display = "block";
        }

        // Re-trigger dependent UI logic (status dropdown, snack box, etc.)
        const statusField = document.getElementById("status");

        if (statusField) {
            statusField.dispatchEvent(new Event("change"));
        }
    }

    // ---- Save draft on any change/input, debounced ----
    function queueSave() {

        clearTimeout(saveTimeout);

        saveTimeout = setTimeout(function () {

            const formData = new FormData(form);
            const payload = {};

            formData.forEach(function (value, key) {
                payload[key] = value;
            });

            // Capture checkbox states explicitly (unchecked boxes are
            // omitted from FormData entirely)
            Array.prototype.forEach.call(
                form.querySelectorAll('input[type="checkbox"]'),
                function (box) {
                    payload[box.name] = box.checked;
                }
            );

            fetch("/api/draft", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            }).catch(function (error) {
                console.log("Draft autosave failed", error);
            });

        }, 800);
    }

    form.addEventListener("input", queueSave);
    form.addEventListener("change", queueSave);

    // Clear the draft once the form is actually submitted/saved
    form.addEventListener("submit", function () {
        fetch("/api/draft", { method: "DELETE" }).catch(function () {});
    });
}


// =========================
// STATUS LOGIC
// =========================

function setupStatusLogic() {

    const status = document.getElementById("status");

    const outingBox =
        document.getElementById("outing-box");

    const outsideSkinBox =
        document.getElementById("outside-skin-box");

    const afternoonCard =
        document.getElementById("afternoon-sunscreen-card");

    const nightStudyCard =
        document.getElementById("night-study-card");

    status.addEventListener("change", function () {

        if (this.value === "Outing") {

            outingBox.style.display = "block";

            outsideSkinBox.style.display = "block";

            afternoonCard.style.display = "block";

        }

        else if (this.value === "College") {

            outingBox.style.display = "none";

            outsideSkinBox.style.display = "block";

            afternoonCard.style.display = "block";

        }

        else {

            outingBox.style.display = "none";

            outsideSkinBox.style.display = "none";

            afternoonCard.style.display = "none";

            nightStudyCard.style.display = "block";

        }

    });


    const fullDay =
        document.getElementById("full_day_outing");

    if (fullDay) {

        fullDay.addEventListener("change", function () {

            if (this.checked) {

                nightStudyCard.style.display = "none";

            }

            else {

                nightStudyCard.style.display = "block";

            }

        });

    }

}


// =========================
// SNACK LOGIC
// =========================

function setupSnackLogic() {

    const snack =
        document.getElementById("snack_type");

    const otherBox =
        document.getElementById("other-snack-box");

    if (!snack) return;

    otherBox.style.display = "none";

    snack.addEventListener("change", function () {

        if (this.value === "Other") {

            otherBox.style.display = "block";

        }

        else {

            otherBox.style.display = "none";

        }

    });

}


// =========================
// COLLEGE TOMORROW
// =========================

function setupCollegeLogic() {

    const checkbox =
        document.getElementById("college_tomorrow");

    const box =
        document.getElementById(
            "college-preparation-box"
        );

    if (!checkbox) return;

    box.style.display = "none";

    checkbox.addEventListener("change", function () {

        if (this.checked) {

            box.style.display = "block";

        }

        else {

            box.style.display = "none";

        }

    });

}


// =========================
// INFUSED WATER
// =========================

function setupInfusedWaterLogic() {

    const checkbox =
        document.getElementById(
            "infused_water_toggle"
        );

    const box =
        document.getElementById(
            "infused-water-box"
        );

    if (!checkbox) return;

    box.style.display = "none";

    checkbox.addEventListener("change", function () {

        if (this.checked) {

            box.style.display = "block";

        }

        else {

            box.style.display = "none";

        }

    });

}


// =========================
// STUDY LOGIC
// =========================

function setupStudyLogic() {

    const morningToggle =
        document.getElementById(
            "morning_study_toggle"
        );

    const morningBox =
        document.getElementById(
            "morning-study-box"
        );

    if (morningBox)
        morningBox.style.display = "none";

    if (morningToggle) {

        morningToggle.addEventListener(
            "change",
            function () {

                morningBox.style.display =
                    this.checked
                        ? "block"
                        : "none";

            }
        );
    }


    const nightToggle =
        document.getElementById(
            "night_study_toggle"
        );

    const nightBox =
        document.getElementById(
            "night-study-box"
        );

    if (nightBox)
        nightBox.style.display = "none";

    if (nightToggle) {

        nightToggle.addEventListener(
            "change",
            function () {

                nightBox.style.display =
                    this.checked
                        ? "block"
                        : "none";

            }
        );
    }

}


// =========================
// ADD MORNING STUDY
// =========================

function addMorningStudy() {

    const container =
        document.getElementById(
            "morning-study-container"
        );

    const row = document.createElement("div");

    row.className = "study-row";

    row.innerHTML = `

        <input
        type="hidden"
        name="session[]"
        value="Morning">

        <input
        type="text"
        name="subject[]"
        placeholder="Subject">

        <input
        type="text"
        name="topic[]"
        placeholder="Topic">

        <input
        type="time"
        name="start_time[]">

        <input
        type="time"
        name="end_time[]">

    `;

    container.appendChild(row);

}


// =========================
// ADD NIGHT STUDY
// =========================

function addNightStudy() {

    const container =
        document.getElementById(
            "night-study-container"
        );

    const row = document.createElement("div");

    row.className = "study-row";

    row.innerHTML = `

        <input
        type="hidden"
        name="session[]"
        value="Evening">

        <input
        type="text"
        name="subject[]"
        placeholder="Subject">

        <input
        type="text"
        name="topic[]"
        placeholder="Topic">

        <input
        type="time"
        name="start_time[]">

        <input
        type="time"
        name="end_time[]">

    `;

    container.appendChild(row);

}


// =========================
// UPCOMING TASKS
// =========================

function loadUpcomingTasks() {

    fetch("/upcoming-tasks")

        .then(response => response.json())

        .then(data => {

            const container =
                document.getElementById(
                    "upcoming-tasks-container"
                );

            if (!container) return;

            container.innerHTML = "";

            if (data.length === 0) {

                container.innerHTML = `

                    <div class="empty-task">

                        No upcoming tasks.

                    </div>

                `;

                return;
            }

            data.forEach(task => {

                container.innerHTML += `

                    <div class="task-card">

                        <h4>
                            ${task.task_name}
                        </h4>

                        <p>
                            ${task.task_type}
                        </p>

                        <p>
                            Due:
                            ${task.submission_date}
                        </p>

                        <p>
                            Priority:
                            ${task.priority}
                        </p>

                    </div>

                `;

            });

        })

        .catch(error => {

            console.log(
                "Task loading error",
                error
            );

        });

}