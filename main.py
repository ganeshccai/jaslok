from flask import Flask, request, jsonify
from data import doctor_data, get_doctor_by_name, get_doctor_by_name_city, clean_name
from copy import deepcopy
import firebase_admin
from firebase_admin import credentials, firestore
import pprint
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)


def send_email(to_email, subject, body):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    from_email = "anaraseg@gmail.com"  # Sender email
    from_name = "Jaslok Hospital"  # Sender display name
    from_addr = f"{from_name} <{from_email}>"
    password = "gbbm sfks jbje nqxo"  # Your app password (use env var in real projects)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(from_email, password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()


firebase_admin.initialize_app()
db = firestore.client()

doctors_db = deepcopy(doctor_data)


def cx_response(text, params=None, suggestions=None):
    messages = [{"text": {"text": [text]}}]
    if suggestions:
        chips = {"type": "chips", "options": [{"text": s} for s in suggestions]}
        messages.append({"payload": {"richContent": [[chips]]}})
    res = {"fulfillment_response": {"messages": messages}}
    if params:
        res["session_info"] = {"parameters": params}
    return jsonify(res)


def normalize_date(date_str):
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return date_str.strip()


def format_12hr(time_str):
    # Assumes time_str is "HH:MM"
    return datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    pprint.pprint(data)

    tag = data.get("fulfillmentInfo", {}).get("tag", "")
    user_email = data.get("sessionInfo", {}).get("parameters", {}).get("user_email")
    params = data.get("sessionInfo", {}).get("parameters", {})

    doctorname_param = params.get("doctorname", "")
    if isinstance(doctorname_param, dict):
        doctorname = doctorname_param.get("doctorname", "")
    else:
        doctorname = str(doctorname_param).strip()
    city = params.get("city", "").strip()
    specialty = params.get("specialty", "").strip()
    date_param = params.get("date", "")
    if not date_param:
        date_param = params.get("text", "")
    if isinstance(date_param, dict):
        # Dialogflow sometimes sends date as {'day': 12.0, 'month': 8.0, 'year': 2025.0}
        if all(k in date_param for k in ("day", "month", "year")):
            day = int(date_param["day"])
            month = int(date_param["month"])
            year = int(date_param["year"])
            date = f"{year:04d}-{month:02d}-{day:02d}"
        else:
            date = date_param.get("date", "")
    else:
        date = str(date_param).strip()
    time_param = params.get("time", "")
    if isinstance(time_param, dict):
        # Convert to HH:MM format
        hours = int(time_param.get("hours", 0))
        minutes = int(time_param.get("minutes", 0))
        time = f"{hours:02d}:{minutes:02d}"
    else:
        time = str(time_param).strip()

    print("--- TAG:", tag)
    print("doctorname:", doctorname)
    print("city:", city)
    print("specialty:", specialty)
    print("date:", date)
    print("time:", time)

    print(f"[DEBUG] tag: {tag}, doctorname: '{doctorname}', date: '{date}'")

    if tag == "get_doctors":
        # return cx_response("Test doctors:", suggestions=["Dr. A", "Dr. B"])
        print(f"[DEBUG] city: '{city}', specialty: '{specialty}'")
        matched = []
        for doc in doctors_db:
            doc_city = doc["city"].strip().lower()
            doc_specialty = doc["specialty"].strip().lower()
            city_match = city and doc_city == city.lower()
            specialty_match = specialty and doc_specialty == specialty.lower()
            if city and specialty:
                if city_match and specialty_match:
                    matched.append(doc["doctorname"])
            elif city:
                if city_match:
                    matched.append(doc["doctorname"])
            elif specialty:
                if specialty_match:
                    matched.append(doc["doctorname"])
            else:
                matched.append(doc["doctorname"])
        print(f"[DEBUG] Matched doctors: {matched}")
        if matched:
            return cx_response(
                f"👇 Available **{specialty}** in **{city}**:",
                suggestions=matched,
            )
        if city and specialty:
            return cx_response(f"No doctors found for {specialty} in {city}.")
        elif city:
            return cx_response(f"No doctors found in {city}.")
        elif specialty:
            return cx_response(f"No doctors found for {specialty}.")
        else:
            return cx_response("No doctors found.")

    elif tag == "send_booked_email":
        patientname = params.get("patientname", "") or "User"
        doctorname = str(params.get("doctorname", "")).strip()
        specialization = params.get("specialty", "")
        city_val = params.get("city", "")
        time_12hr = format_12hr(time)
        if not user_email:
            return cx_response("User email not provided.")
        send_email(
            user_email,
            "Your appointment is confirmed.",
            f"Dear {patientname},\n\nYour appointment with {doctorname} ({specialization}) has been successfully booked for {date} at {time_12hr} in {city_val}.\n\nThank you.\n\n---\nThis is just a test email, please ignore.",
        )
        fulfillment_text = "A confirmation email has been sent to your address."
        return jsonify(
            {
                "fulfillment_response": {
                    "messages": [{"text": {"text": [fulfillment_text]}}]
                }
            }
        )

    elif tag == "send_cancelled_email":
        patientname = params.get("patientname", "") or "User"
        doctorname = str(params.get("doctorname", "")).strip()
        specialization = params.get("specialty", "")
        city_val = params.get("city", "")
        time_12hr = format_12hr(time)
        if not user_email:
            return cx_response("User email not provided.")
        send_email(
            user_email,
            "Your appointment is cancelled.",
            f"Dear {patientname},\n\nYour appointment with {doctorname} ({specialization}) scheduled for {date} at {time_12hr} in {city_val} has been cancelled.\n\nThank you.\n\n---\nThis is just a test email, please ignore.",
        )
        fulfillment_text = ""
        return jsonify(
            {
                "fulfillment_response": {
                    "messages": [{"text": {"text": [fulfillment_text]}}]
                }
            }
        )

    elif tag == "get_doctor_details_by_name":
        if doctorname and not date.strip():
            from data import slot_dates

            print("Available slot_dates:", slot_dates)
            return cx_response(
                f"📅 Please select a date for {doctorname}:",
                suggestions=slot_dates[:5],  # Show next 5 dates as chips
            )
        print(f"[DEBUG] city: '{city}', specialty: '{specialty}'")
        doc = (
            get_doctor_by_name_city(doctorname, city)
            if city
            else get_doctor_by_name(doctorname)
        )
        if doc:
            return cx_response(
                f"Doctor found: {doc['doctorname']} - {doc['specialty']} in {doc['city']}",
                {
                    "doctorname": doc["doctorname"],
                    "city": doc["city"],
                    "specialty": doc["specialty"],
                    "slot_type": doc["slot_type"],
                },
                suggestions=["Show Available Slots"],  # Change button text
            )
        return cx_response("Doctor not found.")

    elif tag == "get_dates":
        # Show date chips after doctor selection
        if doctorname:
            from data import slot_dates

            print("Available slot_dates:", slot_dates)
            return cx_response(
                f"Please select a date for {doctorname}:", suggestions=slot_dates[:5]
            )
        return cx_response("Please select a doctor first.")

    elif tag == "get_slots":
        # Show time slots after date selection
        doctorname_str = str(doctorname).strip() if doctorname else ""
        date_str = str(date).strip() if date else ""
        if doctorname_str and date_str:
            date_norm = normalize_date(date_str)
            for doc in doctors_db:
                if clean_name(doc["doctorname"]) == clean_name(doctorname_str):
                    # Get all slots for the doctor and date
                    all_slots = doc["slots"].get(date_norm, [])
                    # Fetch booked slots from Firestore
                    booked_slots = []
                    bookings_ref = db.collection("Jaslok Hospitals")
                    query = (
                        bookings_ref.where("doctorname", "==", doctorname_str)
                        .where("date", "==", date_norm)
                        .where("status", "==", "booked")
                    )
                    results = query.get()
                    for booking in results:
                        booked_slots.append(booking.get("slot"))
                    # Filter out booked slots
                    available_slots = [s for s in all_slots if s not in booked_slots]
                    slots_12hr = [format_12hr(s) for s in available_slots]
                    print(f"[DEBUG] Slots found: {slots_12hr}")
                    if slots_12hr:
                        return cx_response(
                            f"Available slots for {doctorname_str} on **{date_norm}**:\n 🕑Please select a time slot:",
                            suggestions=slots_12hr,
                        )
                    else:
                        return cx_response(
                            f"No slots available for {doctorname_str} on **{date_norm}**."
                        )
            return cx_response("Doctor not found.")
        return cx_response("Please select a doctor and date first.")

    elif tag == "book_slot":
        for doc in doctors_db:
            if clean_name(doc["doctorname"]) == clean_name(doctorname):
                if date in doc["slots"] and time in doc["slots"][date]:
                    doc_info = (
                        get_doctor_by_name_city(doctorname, city)
                        if city
                        else get_doctor_by_name(doctorname)
                    )
                    if not doc_info:
                        return cx_response("Doctor details not found.")
                    doc["slots"][date].remove(time)
                    db.collection("Jaslok Hospitals").add(
                        {
                            "doctorname": doctorname,
                            "city": doc_info["city"],
                            "specialty": doc_info["specialty"],
                            "slot_type": doc_info["slot_type"],
                            "date": date,
                            "slot": time,
                            "status": "booked",
                        }
                    )
                    time_12hr = format_12hr(time)
                    patientname = params.get("patientname", "") or "User"
                    specialization = doc_info.get("specialty", "")
                    city_val = doc_info.get("city", "")
                    return cx_response(
                        f"**Hi {patientname}, Appointment with {doctorname} ({specialization}) has been successfully booked ✅ for {date} at {time_12hr} in {city_val}.**",
                        params={"retry": None},
                    )
                else:
                    # Step-by-step selection: show only dates or only times
                    available_dates = list(doc["slots"].keys())
                    # Always clear both date and time, and set retry to True for failed booking
                    return cx_response(
                        "Slot already booked or invalid.",
                        params={"date": "", "time": "", "retry": True},
                    )
        return cx_response("Doctor not found.")

    elif tag == "cancel_slot":
        bookings_ref = db.collection("Jaslok Hospitals")
        query = (
            bookings_ref.where("doctorname", "==", doctorname)
            .where("date", "==", date)
            .where("slot", "==", time)
            .where("status", "==", "booked")
            .limit(1)
        )
        results = query.get()
        if results:
            booking_doc = results[0]
            booking_doc.reference.update({"status": "cancelled"})
            for doc in doctors_db:
                if clean_name(doc["doctorname"]) == clean_name(doctorname):
                    if time not in doc["slots"].get(date, []):
                        doc["slots"].setdefault(date, []).append(time)
                        doc["slots"][date].sort()
                    break
            time_12hr = format_12hr(time)
            return cx_response(
                f"Booking cancelled for {doctorname} at {time_12hr} on {date}."
            )
        return cx_response("Booking not found or already cancelled.")

    return cx_response("Invalid tag or missing parameters.")


@app.errorhandler(Exception)
def handle_exception(e):
    import traceback

    print(traceback.format_exc())
    return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
