from datetime import datetime, timedelta
from copy import deepcopy


# Define slot types
def generate_time_slots(start_time: str, end_time: str) -> list:
    fmt = "%H:%M"
    start = datetime.strptime(start_time, fmt)
    end = datetime.strptime(end_time, fmt)
    slots = []
    while start < end:
        slots.append(start.strftime(fmt))
        start += timedelta(minutes=30)
    return slots


# Generate next 30 weekdays (Mon–Fri only)
def generate_weekday_dates(days=365):
    dates = []
    current = datetime.today()
    while len(dates) < days:
        if current.weekday() < 5:  # 0 = Monday, ..., 4 = Friday
            dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return dates


# Slot templates
type_a_slots = generate_time_slots("10:00", "16:00")
type_b_slots = generate_time_slots("11:00", "14:00")
slot_dates = generate_weekday_dates(30)

# Doctor list (10 doctors)
doctor_data = [
    # Mumbai
    {
        "doctorname": "Dr Mehta",
        "city": "Mumbai",
        "specialty": "Cardiologist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Deshmukh",
        "city": "Mumbai",
        "specialty": "Cardiologist",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Thakur",
        "city": "Mumbai",
        "specialty": "Dentist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Joshi",
        "city": "Mumbai",
        "specialty": "Dentist",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Sawant",
        "city": "Mumbai",
        "specialty": "Neurologist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Gokhale",
        "city": "Mumbai",
        "specialty": "Neurologist",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Pawar",
        "city": "Mumbai",
        "specialty": "Pediatrician",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Kamat",
        "city": "Mumbai",
        "specialty": "Pediatrician",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Iyer",
        "city": "Mumbai",
        "specialty": "Dermatologist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Nair",
        "city": "Mumbai",
        "specialty": "Dermatologist",
        "slot_type": "B",
    },
    # Delhi
    {
        "doctorname": "Dr Sharma",
        "city": "Delhi",
        "specialty": "Cardiologist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Bansal",
        "city": "Delhi",
        "specialty": "Cardiologist",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Verma",
        "city": "Delhi",
        "specialty": "Dentist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Jain",
        "city": "Delhi",
        "specialty": "Dentist",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Sinha",
        "city": "Delhi",
        "specialty": "Neurologist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Chandra",
        "city": "Delhi",
        "specialty": "Neurologist",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Tripathi",
        "city": "Delhi",
        "specialty": "Pediatrician",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Agarwal",
        "city": "Delhi",
        "specialty": "Pediatrician",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Kaushik",
        "city": "Delhi",
        "specialty": "Dermatologist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Mittal",
        "city": "Delhi",
        "specialty": "Dermatologist",
        "slot_type": "B",
    },
    # Pune
    {
        "doctorname": "Dr Patil",
        "city": "Pune",
        "specialty": "Cardiologist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Jadhav",
        "city": "Pune",
        "specialty": "Cardiologist",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Desai",
        "city": "Pune",
        "specialty": "Dentist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Kulkarni",
        "city": "Pune",
        "specialty": "Dentist",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Shinde",
        "city": "Pune",
        "specialty": "Neurologist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Bhosale",
        "city": "Pune",
        "specialty": "Neurologist",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr More",
        "city": "Pune",
        "specialty": "Pediatrician",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Gade",
        "city": "Pune",
        "specialty": "Pediatrician",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Kapse",
        "city": "Pune",
        "specialty": "Dermatologist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Zende",
        "city": "Pune",
        "specialty": "Dermatologist",
        "slot_type": "B",
    },
    # Bangalore
    {
        "doctorname": "Dr Rao",
        "city": "Bangalore",
        "specialty": "Cardiologist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Reddy",
        "city": "Bangalore",
        "specialty": "Cardiologist",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Shetty",
        "city": "Bangalore",
        "specialty": "Dentist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Nayak",
        "city": "Bangalore",
        "specialty": "Dentist",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Gowda",
        "city": "Bangalore",
        "specialty": "Neurologist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Murthy",
        "city": "Bangalore",
        "specialty": "Neurologist",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Acharya",
        "city": "Bangalore",
        "specialty": "Pediatrician",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Kamath",
        "city": "Bangalore",
        "specialty": "Pediatrician",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Prasad",
        "city": "Bangalore",
        "specialty": "Dermatologist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Nandini",
        "city": "Bangalore",
        "specialty": "Dermatologist",
        "slot_type": "B",
    },
    # Hyderabad
    {
        "doctorname": "Dr Iyer",
        "city": "Hyderabad",
        "specialty": "Cardiologist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Nair",
        "city": "Hyderabad",
        "specialty": "Cardiologist",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Raju",
        "city": "Hyderabad",
        "specialty": "Dentist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Lakshmi",
        "city": "Hyderabad",
        "specialty": "Dentist",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Srinivas",
        "city": "Hyderabad",
        "specialty": "Neurologist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Rekha",
        "city": "Hyderabad",
        "specialty": "Neurologist",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Harsha",
        "city": "Hyderabad",
        "specialty": "Pediatrician",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Swati",
        "city": "Hyderabad",
        "specialty": "Pediatrician",
        "slot_type": "B",
    },
    {
        "doctorname": "Dr Anand",
        "city": "Hyderabad",
        "specialty": "Dermatologist",
        "slot_type": "A",
    },
    {
        "doctorname": "Dr Revathi",
        "city": "Hyderabad",
        "specialty": "Dermatologist",
        "slot_type": "B",
    },
]


def clean_name(doctorname):
    return doctorname.replace(".", "").replace(" ", "").strip().lower()


# Attach slots to each doctor
for doctor in doctor_data:
    doctor["slots"] = {}
    slot_template = type_a_slots if doctor["slot_type"] == "A" else type_b_slots
    for date in slot_dates:
        doctor["slots"][date] = slot_template.copy()


def get_doctor_by_name_city(doctorname, city):
    for doc in doctor_data:
        if (
            clean_name(doc["doctorname"]) == clean_name(doctorname)
            and doc["city"].lower() == city.lower()
        ):
            return doc
    return None


def get_doctor_by_name(doctorname):
    for doc in doctor_data:
        if clean_name(doc["doctorname"]) == clean_name(doctorname):
            return doc
    return None
