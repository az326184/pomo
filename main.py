import time
from pyratatui import (
    Terminal,
    Block,
    Gauge,
    Paragraph,
    Layout,
    Constraint,
    Direction,
    Style,
    Color,
)

# -------------------------
# SETTINGS
# -------------------------
WORK_TIME = 25 * 60      # 25 minutes
BREAK_TIME = 5 * 60      # 5 minutes

state = {
    "mode": "WORK",      # WORK / BREAK / PAUSED
    "time_left": WORK_TIME,
    "running": False,
}

last_tick = time.monotonic()


# -------------------------
# FORMAT TIME
# -------------------------
def format_time(seconds):
    m = seconds // 60
    s = seconds % 60
    return f"{m:02}:{s:02}"


# -------------------------
# UI
# -------------------------
def ui(frame):
    global state

    # Layout (top text + big gauge + footer)
    top, middle, bottom = (
        Layout()
        .direction(Direction.Vertical)
        .constraints([
            Constraint.length(3),
            Constraint.fill(1),
            Constraint.length(2),
        ])
        .split(frame.area)
    )

    # Title
    frame.render_widget(
        Paragraph.from_string("Pomodoro Timer 🍅")
        .block(Block().bordered().title("PyRatatui Pomodoro"))
        .style(Style().fg(Color.cyan()).bold()),
        top,
    )

    # Calculate percent for gauge
    if state["mode"] == "WORK":
        total = WORK_TIME
        color = Color.green()
    else:
        total = BREAK_TIME
        color = Color.magenta()

    percent = int((1 - state["time_left"] / total) * 100)
    percent = max(0, min(percent, 100))

    # Big progress bar
    frame.render_widget(
        Gauge()
        .percent(percent)
        .label(f"{format_time(state['time_left'])}")
        .style(Style().fg(color))
        .block(Block().bordered().title(state["mode"])),
        middle,
    )

    # Controls
    frame.render_widget(
        Paragraph.from_string(
            "SPACE = start/pause   |   r = reset   |   q = quit"
        ),
        bottom,
    )


# -------------------------
# MAIN LOOP
# -------------------------
with Terminal() as term:
    while True:
        now = time.monotonic()
        elapsed = now - last_tick

        # Countdown logic
        if state["running"] and elapsed >= 1:
            state["time_left"] -= 1
            last_tick = now

            # Switch modes automatically
            if state["time_left"] <= 0:
                if state["mode"] == "WORK":
                    state["mode"] = "BREAK"
                    state["time_left"] = BREAK_TIME
                else:
                    state["mode"] = "WORK"
                    state["time_left"] = WORK_TIME

        # Draw UI
        term.draw(ui)

        # Handle keys
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "q":
                break

            if ev.code == " ":
                state["running"] = not state["running"]

            if ev.code == "r":
                state["mode"] = "WORK"
                state["time_left"] = WORK_TIME
                state["running"] = False
                