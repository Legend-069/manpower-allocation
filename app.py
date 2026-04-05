import streamlit as st
from ortools.sat.python import cp_model

# -----------------------------
# LOGIN SYSTEM
# -----------------------------
USERNAME = "admin"
PASSWORD = "hvac123"

def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state["logged_in"] = True
        else:
            st.error("❌ Wrong username or password")

# Session check
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# -----------------------------
# DATA (You can edit later)
# -----------------------------
stations = [
    "Evaporator Fitment",
    "Blower Assembly",
    "Wiring",
    "Leak Test",
    "Gas Charging",
    "Final Inspection",
    "Packing"
]

employees = {
    "Rahul": {"type": "multi", "skills": {"Evaporator Fitment": 3, "Wiring": 2}},
    "Amit": {"type": "single", "skills": {"Gas Charging": 3}},
    "Neha": {"type": "multi", "skills": {"Leak Test": 3, "Final Inspection": 2}},
    "Ravi": {"type": "multi", "skills": {"Blower Assembly": 2, "Packing": 3}},
    "Pooja": {"type": "multi", "skills": {"Final Inspection": 3, "Packing": 2}}
}

# -----------------------------
# UI
# -----------------------------
st.title("🔧 Manpower Allocation System")

present = st.multiselect(
    "Select Present Employees",
    list(employees.keys())
)

# -----------------------------
# ASSIGN BUTTON
# -----------------------------
if st.button("Auto Assign"):

    model = cp_model.CpModel()

    x = {}
    for e in present:
        for s in stations:
            if s in employees[e]["skills"]:
                x[(e, s)] = model.NewBoolVar(f"x_{e}_{s}")

    # Constraint: 1 person per station (or empty)
    for s in stations:
        model.Add(sum(x[(e, s)] for e in present if (e, s) in x) <= 1)

    # Constraint: 1 station per employee
    for e in present:
        model.Add(sum(x[(e, s)] for s in stations if (e, s) in x) <= 1)

    # Objective: maximize skill + prioritize single-skilled
    model.Maximize(
        sum(
            x[(e, s)] * (
                employees[e]["skills"][s] +
                (2 if employees[e]["type"] == "single" else 0)
            )
            for (e, s) in x
        )
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    st.subheader("📊 Allocation Result")

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for s in stations:
            assigned = False
            for e in present:
                if (e, s) in x and solver.Value(x[(e, s)]) == 1:
                    st.write(f"✅ {s} → {e}")
                    assigned = True
            if not assigned:
                st.write(f"❌ {s} → Not Filled")
    else:
        st.error("No feasible solution")