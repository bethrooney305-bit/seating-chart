import streamlit as st
import random

# --- Core Algorithm ---
def build_seating_chart(students, conflicts, layout_type, rows=None, cols=None, num_tables=None, table_size=None):
    if layout_type == "Grid (Rows x Columns)":
        total_seats = rows * cols
        seats = [(r, c) for r in range(rows) for c in range(cols)]
    else:
        total_seats = num_tables * table_size
        seats = [(t, s) for t in range(num_tables) for s in range(table_size)]

    if len(students) > total_seats:
        return "Error: More students than available seats!", None

    all_positions = list(students) + ["(Empty)"] * (total_seats - len(students))
    random.shuffle(all_positions)
    chart = {}

    def is_valid(student, seat):
        if student == "(Empty)": return True
        for other_seat, other_student in chart.items():
            if other_student == "(Empty)": continue
            
            # Check conflicts
            if (student in conflicts.get(other_student, [])) or (other_student in conflicts.get(student, [])):
                if layout_type == "Grid (Rows x Columns)":
                    r1, c1 = seat
                    r2, c2 = other_seat
                    if abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1: return False
                else:
                    t1, _ = seat
                    t2, _ = other_seat
                    if t1 == t2: return False
        return True

    def backtrack(seat_index):
        if seat_index == len(seats): return True
        current_seat = seats[seat_index]
        for i in range(len(all_positions)):
            student = all_positions[i]
            if is_valid(student, current_seat):
                chart[current_seat] = student
                all_positions.pop(i)
                if backtrack(seat_index + 1): return True
                all_positions.insert(i, student)
                del chart[current_seat]
        return False

    if backtrack(0): return chart, seats
    return None, None

# --- Web Interface ---
st.title("🍎 Teacher's Smart Seating Chart Generator")
st.write("Create conflict-free seating charts instantly.")

# Inputs
students_input = st.text_area("1. Enter Student Names (one per line):", 
                              "Alex\nBen\nCharlie\nDaniel\nEmma\nFinley\nGrace\nHarper")

conflicts_input = st.text_area("2. Enter Conflicts (Format: Student Name: Conflict1, Conflict2 - one per line):", 
                               "Alex: Ben, Charlie\nEmma: Finley")

layout = st.radio("3. Choose Classroom Layout:", ["Grid (Rows x Columns)", "Tables"])

if layout == "Grid (Rows x Columns)":
    col1, col2 = st.columns(2)
    r = col1.number_input("Number of Rows", min_value=1, value=5)
    c = col2.number_input("Columns per Row", min_value=1, value=6)
else:
    col1, col2 = st.columns(2)
    t_num = col1.number_input("Number of Tables", min_value=1, value=6)
    t_size = col2.number_input("Students per Table", min_value=1, value=5)

if st.button("Generate Seating Chart 🎯"):
    # Process inputs
    student_list = [s.strip() for s in students_input.split("\n") if s.strip()]
    
    conflict_dict = {}
    for line in conflicts_input.split("\n"):
        if ":" in line:
            key, values = line.split(":")
            conflict_dict[key.strip()] = [v.strip() for v in values.split(",") if v.strip()]

    # Run generator
    if layout == "Grid (Rows x Columns)":
        chart, seats = build_seating_chart(student_list, conflict_dict, layout, rows=r, cols=c)
        if isinstance(chart, str): st.error(chart)
        elif chart:
            for row in range(r):
                cols_list = st.columns(c)
                for col in range(c):
                    cols_list[col].metric(f"Row {row+1}-Col {col+1}", chart[(row, col)])
        else:
            st.error("Could not find a valid arrangement. Try adding more empty seats or reducing conflicts.")
    else:
        chart, seats = build_seating_chart(student_list, conflict_dict, layout, num_tables=t_num, table_size=t_size)
        if isinstance(chart, str): st.error(chart)
        elif chart:
            for table in range(t_num):
                st.subheader(f"🪑 Table {table + 1}")
                t_students = [chart[(table, s)] for s in range(t_size)]
                st.write(", ".join(t_students))
