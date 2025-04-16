import streamlit as st

# ------------------ Timetable Generator Class ------------------

class TimeTableGenerator:
    def __init__(self, subjects, teachers, rooms, periods_per_day, teacher_availability):
        self.subjects = subjects
        self.teachers = teachers
        self.rooms = rooms
        self.periods_per_day = periods_per_day
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.timetable = {}
        self.teacher_schedule = {}
        self.room_schedule = {}
        self.teacher_availability = teacher_availability

    def generate(self):
        for class_id in self.subjects:
            self.timetable[class_id] = [["" for _ in range(self.periods_per_day)] for _ in range(len(self.days))]
            for subject in self.subjects[class_id]:
                self.assign_subject(class_id, subject)
        return self.timetable

    def assign_subject(self, class_id, subject):
        teacher = self.teachers[subject]
        for day in range(len(self.days)):
            for period in range(self.periods_per_day):
                if not self.is_teacher_available(teacher, day, period):
                    continue
                if self.timetable[class_id][day][period] == "" and not self.is_teacher_busy(teacher, day, period):
                    room = self.find_available_room(day, period)
                    if room:
                        self.timetable[class_id][day][period] = f"{subject} ({room})"
                        self.mark_teacher_busy(teacher, day, period)
                        self.mark_room_busy(room, day, period)
                        return

    def is_teacher_available(self, teacher, day, period):
        return (day, period) in self.teacher_availability.get(teacher, set())

    def is_teacher_busy(self, teacher, day, period):
        return self.teacher_schedule.get((teacher, day, period), False)

    def mark_teacher_busy(self, teacher, day, period):
        self.teacher_schedule[(teacher, day, period)] = True

    def find_available_room(self, day, period):
        for room in self.rooms:
            if not self.room_schedule.get((room, day, period), False):
                return room
        return None

    def mark_room_busy(self, room, day, period):
        self.room_schedule[(room, day, period)] = True


# ------------------ Streamlit UI ------------------

st.set_page_config(page_title="Timetable Generator", layout="wide")
st.title("📅 Custom Timetable Generator")

# Get basic input
num_classes = st.number_input("Number of Classes", min_value=1, max_value=10, value=2)
periods_per_day = st.slider("Periods per Day", 1, 10, 6)
rooms = st.multiselect("Select Available Rooms", ["R1", "R2", "R3", "R4"], default=["R1", "R2"])
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
time_slots = [(d, p) for d in range(len(days)) for p in range(periods_per_day)]

# Collect class-wise subjects
subjects = {}
st.header("📚 Subjects per Class")
for i in range(num_classes):
    class_id = f"Class_{chr(65 + i)}"
    subj_list = st.text_input(f"Enter subjects for {class_id} (comma separated)", key=f"subj_{i}")
    if subj_list:
        subjects[class_id] = [s.strip() for s in subj_list.split(",")]

# Collect teacher assignments
teachers = {}
st.header("👩‍🏫 Teacher Assignments")
all_subjects = sorted(set(s for sl in subjects.values() for s in sl))
for subject in all_subjects:
    teacher = st.text_input(f"Enter teacher for subject '{subject}'", key=f"teach_{subject}")
    if teacher:
        teachers[subject] = teacher

# Collect teacher availability
teacher_availability = {}
st.header("🕐 Teacher Availability")
for teacher in set(teachers.values()):
    available_slots = st.multiselect(
        f"Available slots for {teacher} (Day-Period)",
        options=[f"{days[d]}-P{p+1}" for d, p in time_slots],
        default=[],
        key=f"avail_{teacher}"
    )
    teacher_availability[teacher] = {
        (days.index(s.split("-")[0]), int(s.split("-")[1][1:]) - 1)
        for s in available_slots
    }

# Generate timetable
if st.button("Generate Timetable"):
    if not subjects or not teachers or not teacher_availability:
        st.error("Please fill in all required inputs: subjects, teachers, and availability.")
    else:
        generator = TimeTableGenerator(subjects, teachers, rooms, periods_per_day, teacher_availability)
        timetable = generator.generate()

        for class_id, schedule in timetable.items():
            st.subheader(f"📘 Timetable for {class_id}")
            data = []
            for day_index, day in enumerate(generator.days):
                row = {"Day": day}
                for period in range(periods_per_day):
                    row[f"P{period + 1}"] = schedule[day_index][period] if schedule[day_index][period] else "Free"
                data.append(row)
            st.table(data)
