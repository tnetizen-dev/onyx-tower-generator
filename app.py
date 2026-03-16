import streamlit as st
import random
import csv
import json
from pathlib import Path

# Save function
SAVE_PATH = Path("savegame.json")

def save_state():
    data = {
        "last_location_roll": st.session_state.last_location_roll,
        "last_detail_roll": st.session_state.last_detail_roll,
        "last_event_roll": st.session_state.last_event_roll,
        "last_encounters": st.session_state.last_encounters,
        "history": st.session_state.history
    }
    SAVE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

def load_state():
    if not SAVE_PATH.exists():
        return False
    data = json.loads(SAVE_PATH.read_text(encoding="utf-8"))

    st.session_state.last_location_roll = data.get("last_location_roll")
    st.session_state.last_detail_roll = data.get("last_detail_roll")
    st.session_state.last_event_roll = data.get("last_event_roll")
    st.session_state.last_encounters = data.get("last_encounters") or []
    st.session_state.history = data.get("history") or []

    return True

# Load CSV tables
@st.cache_data
def load_table_by_roll(csv_path: str) -> dict[int, dict[str, str]]:
    """
    Loads a CSV with columns: Roll, Name, Description
    Returns: { roll_int: {"name": ..., "desc": ...}, ... }
    """

    table: dict[int, dict[str, str]] = {}

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            roll = int(row["Roll"])
            table[roll] = {
                "name": row["Name"],
                "desc": row["Description"],
            }

    return table

@st.cache_data
def load_events_desc_by_roll(csv_path: str) -> dict[int, str]:
    """
    Loads a CSV with columns: Roll, Description
    Returns: { roll_int: "Description text", ... }
    """
    table: dict[int, str] = {}

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            roll = int(row.get("Roll") or row.get("\ufeffRoll"))
            table[roll] = row["Description"]
    
    return table

LOCATIONS_TABLE = load_table_by_roll("locations.csv")
DETAILS_TABLE = load_table_by_roll("details.csv")
EVENTS_TABLE = load_table_by_roll("events.csv")
ENCOUNTERS_TABLE = load_table_by_roll("encounters.csv")

# TEMP DEBUG LINE
# st.write("Load rows:", len(LOCATIONS_TABLE), len(DETAILS_TABLE))


st.title("Onyx Tower Ascent Generator")

#Height variable
height = st.number_input(
    "Tower Height",
    min_value=0,
    max_value=20,
    value=0,
    step=1
)

ENCOUNTER_EVENT_ROLLS = {1, 2, 3, 4, 5, 6, 7, 11, 12}

# Make sure we have a place to store the last roll
if "last_location_roll" not in st.session_state:
    st.session_state.last_location_roll = None

if "last_detail_roll" not in st.session_state:
    st.session_state.last_detail_roll = None

if "last_event_roll" not in st.session_state:
    st.session_state.last_event_roll = None

if "last_encounters" not in st.session_state:
    st.session_state.last_encounters = []

if "history" not in st.session_state:
        st.session_state.history = []

# Button block
col1, col2 = st.columns(2)
with col1:
    gen_turn = st.button("Generate travel turn", type="primary")
with col2:
    reroll_event = st.button("Reroll event (same room)")

if gen_turn:
    loc_raw = random.randint(1,10) + height
    det_raw = random.randint(1,10) + height
   
    st.session_state.last_location_roll = min(20, loc_raw)
    st.session_state.last_detail_roll = min(20, det_raw)
    st.session_state.last_event_roll = random.randint(1,10)
    # clear encounters from previous turn
    st.session_state.last_encounters = []

    ev_roll = st.session_state.last_event_roll

    if ev_roll in ENCOUNTER_EVENT_ROLLS:
        num = 2 if ev_roll == 4 else 1

        for _ in range(num):
            enc_raw = random.randint(1, 10) + height
            enc_roll = min(20, enc_raw)
            enc_name = ENCOUNTERS_TABLE[enc_roll]["name"]
            enc_desc = ENCOUNTERS_TABLE[enc_roll]["desc"]
            st.session_state.last_encounters.append((enc_roll, enc_name))
    turn = {
        "height": height,
        "location": LOCATIONS_TABLE[st.session_state.last_location_roll]["name"],
        "location_desc": LOCATIONS_TABLE[st.session_state.last_location_roll]["desc"],
        "detail": DETAILS_TABLE[st.session_state.last_detail_roll]["name"],
        "detail_desc": DETAILS_TABLE[st.session_state.last_detail_roll]["desc"],
        "event_roll": st.session_state.last_event_roll,
        "event_title": EVENTS_TABLE[st.session_state.last_event_roll]["name"],
        "event_text": EVENTS_TABLE[st.session_state.last_event_roll]["desc"],
        "encounters": st.session_state.last_encounters,
    }

    st.session_state.history.insert(0, turn)
    st.session_state.history = st.session_state.history[:10]

    save_state()

if reroll_event:
    
    # Keep the same location/detail; only roll a new event
    st.session_state.last_event_roll = random.randint(1, 10)
    
    # Clear encounters and reroll only if the event triggers it
    st.session_state.last_encounters = []
    ev_roll = st.session_state.last_event_roll

    if ev_roll in ENCOUNTER_EVENT_ROLLS:
        num = 2 if ev_roll == 4 else 1
        for _ in range(num):
            enc_raw = random.randint(1, 10) + height
            enc_roll = min(20, enc_raw)
            enc_name = ENCOUNTERS_TABLE[enc_roll]["name"]
            st.session_state.last_encounters.append((enc_roll, enc_name))

    # Log this as another "moment" in the same room
    turn = {
        "height": height,
        "location": LOCATIONS_TABLE[st.session_state.last_location_roll]["name"],
        "location_desc": LOCATIONS_TABLE[st.session_state.last_location_roll]["desc"],
        "detail": DETAILS_TABLE[st.session_state.last_detail_roll]["name"],
        "detail_desc": DETAILS_TABLE[st.session_state.last_detail_roll]["desc"],
        "event_roll": st.session_state.last_event_roll,
        "event_title": EVENTS_TABLE[st.session_state.last_event_roll]["name"],
        "event_text": EVENTS_TABLE[st.session_state.last_event_roll]["desc"],
        "encounters": st.session_state.last_encounters,
    }

    st.session_state.history.insert(0, turn)
    st.session_state.history = st.session_state.history[:10]

    save_state()

# Save/Load button 
colA, colB = st.columns(2)
with colA:
    if st.button("💾 Save"):
        save_state()
        st.success("Saved.")
with colB:
    if st.button("📂 Load"):
        if load_state():
            st.success("Loaded.")
        else:
            st.warning("No save file found.")



# Display the result

st.markdown("## Latest Turn")

if st.session_state.last_location_roll is not None:
    loc_roll = st.session_state.last_location_roll
    det_roll = st.session_state.last_detail_roll
    ev_roll = st.session_state.last_event_roll

    # Location lookup
    location_data = LOCATIONS_TABLE[loc_roll]
    location_name = location_data["name"]
    location_desc = location_data["desc"]

    # Detail lookup
    detail_data = DETAILS_TABLE[det_roll]
    detail_name = detail_data["name"]
    detail_desc = detail_data["desc"]

    # Event lookup
    ev_title = EVENTS_TABLE[ev_roll]["name"]
    ev_desc = EVENTS_TABLE[ev_roll]["desc"]

    st.markdown(f"**Height:** {height} miles")

    st.markdown(f"## Location: {location_name}")
    st.markdown(f"*Location Roll: {loc_roll}*")
    st.write(location_desc)

    st.markdown(f"## Detail: {detail_name}")
    st.markdown(f"*Detail Roll: {det_roll}*")
    st.write(detail_desc)

    st.markdown(f"## Event :")
    st.markdown(f"**{ev_title}**")
    st.write(ev_desc)
    

    st.markdown("## Encounter(s)")
    if st.session_state.last_encounters:
        for enc_roll, enc_name in st.session_state.last_encounters:
            st.write(f"- ({enc_roll}) {enc_name}")
    else:
        st.write("None")

else:
    st.info("Click **Generate travel turn** to begin.")


    
st.subheader("Last 10 rooms")

history = st.session_state.get("history", [])

for i, t in enumerate(history, start=1):
    label = f"{i}. Height {t['height']} — {t['location']} / {t['detail']}"
    with st.expander(label, expanded=False):
        st.markdown(f"#### Location: {t['location']}")
        st.write(t.get("location_desc", ""))

        st.markdown(f"#### Detail: {t['detail']}")
        st.write(t.get("detail_desc", ""))

        st.markdown(f"#### Event ({t['event_roll']})")
        st.write(t.get("event_title", ""))
        st.caption(t.get("event_text", ""))

        st.markdown("#### Encounter(s)")
        if t.get("encounters"):
            for enc in t["encounters"]:
                # enc might be [roll, name] or (roll, name) depending on JSON load
                enc_roll, enc_name = enc[0], enc[1]
                st.write(f"- ({enc_roll}) {enc_name}")
        else:
            st.write("None")

# for i, t in enumerate(history, start=1):
#     st.markdown(f"### {i}. Height {t['height']}")
#     st.write("Location:", t["location"])
#     st.write("Detail:", t["detail"])
#     st.write("Event:", t["event_title"])

#     if t["encounters"]:
#         encounter_names = ", ".join(name for _, name in t["encounters"])
#         st.write("Encounter(s):", encounter_names)

#     st.divider()