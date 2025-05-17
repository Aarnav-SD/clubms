import bcrypt
import uuid
from mysql.connector import Error

def create_user(db, user):
    member_id = f"M{str(uuid.uuid4())[:6]}"
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (memberId, tier, email, password, isAdmin) VALUES (%s, %s, %s, %s, %s)",
        (member_id, user.tier, user.email, hashed, user.isAdmin)
    )
    db.commit()
    cursor.close()
    return {**user.dict(), "memberId": member_id}

def authenticate_user(db, email, password):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
        return {"success": True, "user": user}
    raise Exception("Invalid credentials")

def create_event(db, event):
    event_id = f"e{uuid.uuid4().hex[:6]}"
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO events (id, title, date, maxSeats, seatsBooked, tier, description, imageUrl)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (event_id, event.title, event.date, event.maxSeats, 0, event.tier, event.description, event.imageUrl)
    )
    db.commit()
    cursor.close()
    return {**event.dict(), "id": event_id, "seatsBooked": 0}

def list_events(db):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    cursor.close()
    return events

def get_users(db):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    cursor.close()
    return data

def get_user_by_member_id(db, member_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE memberId = %s", (member_id,))
    user = cursor.fetchone()
    cursor.close()
    if not user:
        raise Exception("User not found")
    return user

def edit_user(db, member_id, user_data):
    cursor = db.cursor()
    updates = []
    values = []
    for field in user_data.dict(exclude_unset=True):
        updates.append(f"{field} = %s")
        value = user_data.dict()[field]
        if field == "password":
            value = bcrypt.hashpw(value.encode(), bcrypt.gensalt())
        values.append(value)
    query = f"UPDATE users SET {', '.join(updates)} WHERE memberId = %s"
    cursor.execute(query, values + [member_id])
    db.commit()
    cursor.close()
    return {"message": "User updated"}

def edit_event(db, event_id, event_data):
    cursor = db.cursor()
    updates = []
    values = []
    for field in event_data.dict(exclude_unset=True):
        updates.append(f"{field} = %s")
        values.append(event_data.dict()[field])
    query = f"UPDATE events SET {', '.join(updates)} WHERE id = %s"
    cursor.execute(query, values + [event_id])
    db.commit()
    cursor.close()
    return {"message": "Event updated"}

def book_seats(db, event_id, seats):
    cursor = db.cursor()
    cursor.execute("SELECT seatsBooked, maxSeats FROM events WHERE id = %s", (event_id,))
    row = cursor.fetchone()
    if not row or row[0] + seats > row[1]:
        raise Exception("Not enough seats available")
    cursor.execute(
        "UPDATE events SET seatsBooked = seatsBooked + %s WHERE id = %s", (seats, event_id)
    )
    db.commit()
    cursor.close()
    return {"message": f"Booked {seats} seats"} 