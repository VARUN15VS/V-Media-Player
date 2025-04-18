import random
import mysql.connector
import smtplib
from email.message import EmailMessage

from_mail = 'vdevelopmentandtesting@gmail.com'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="pass123",
    database="v_player"
)
cursor = db.cursor()

def otp_verification(to_email):
    otp_str = ""
    for i in range(6):
        otp_str += str(random.randint(0, 9))  # Generate OTP

    # Send the OTP via email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_mail, 'qekb yyrb sfgi myan')

        msg = EmailMessage()
        msg['Subject'] = 'OTP Verification Mail'
        msg['From'] = from_mail
        msg['To'] = to_email
        msg.set_content(f"Please do not share your OTP with anyone. If you share your OTP with anyone then we are not responsible for it. Thank you for using V-Media-Player. Your OTP is: {otp_str}")

        server.send_message(msg)
        server.quit()
        print(f"OTP sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
        return "2"  # Email sending failed

    # Check if email already exists in the database
    cursor.execute("SELECT COUNT(*) FROM verification WHERE email=%s", (to_email,))
    result = cursor.fetchone()
    
    if result and result[0] == 0:
        # Insert new email and OTP into the verification table
        cursor.execute("INSERT INTO verification (email, otp) VALUES (%s, %s)", (to_email, otp_str))
        print(f"Inserted OTP for {to_email}")
    else:
        # Update OTP for the existing email
        cursor.execute("UPDATE verification SET otp = %s WHERE email = %s", (otp_str, to_email))
        print(f"Updated OTP for {to_email}")

    try:
        db.commit()  # Commit the transaction
        print("Database commit successful")
        return "0"  # OTP generation and storing successful
    except Exception as e:
        print(f"Error committing transaction: {e}")
        return "1"  # Failed to commit changes to database

def otp_verification_check(to_email, otp_str):
    print("starting")
    cursor.execute("SELECT otp FROM verification WHERE email = %s", (to_email,))
    result = cursor.fetchone()
    print("Middle")

    if result is not None:
        if result[0] == otp_str:
            return "0"  # OTP matches
        else:
            return "1"  # OTP doesn't match
    else:
        return "-1"  # Email not found in the database
    
def check_existing_email(to_email):
    cursor.execute("SELECT COUNT(*) from login WHERE email=%s", (to_email,))
    if cursor.fetchone()[0] == 1:
        return "-1"
    else:
        return otp_verification(to_email)
    
def thank_you_mail(to_email, username):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_mail, 'qekb yyrb sfgi myan')

        msg = EmailMessage()
        msg['Subject'] = 'Thank You'
        msg['From'] = from_mail
        msg['To'] = to_email
        msg.set_content(f"Thank You! for choosing V-MEDIA-PLAYER.\nYOUR USER NAME IS: " +username)

        server.send_message(msg)
        server.quit()
        return "0"
    except Exception as e:
        print(f"Error sending email: {e}")
        return "2"  # Email sending failed
    
def extract_media_name(uname, mname):
    cursor.execute("Select file_name from movie where user_name=%s and movie_name=%s", (uname, mname,))
    result = cursor.fetchone()[0]
    print("result=> " , result)
    return result

def delete_otp_verification(to_email):
    otp_str = ""
    for i in range(6):
        otp_str += str(random.randint(0, 9))  # Generate OTP

    # Send the OTP via email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_mail, 'qekb yyrb sfgi myan')

        msg = EmailMessage()
        msg['Subject'] = 'OTP Verification Mail'
        msg['From'] = from_mail
        msg['To'] = to_email
        msg.set_content(f"We are sad to see you go! Thank you for being a part of V-Media Player and for trusting us with your entertainment needs. We truly appreciate your time with us and hope you had a great experience.If you ever decide to return, we will be here to welcome you back with open arms!Wishing you the best,The V-Media Player Team Your OTP is: {otp_str}")

        server.send_message(msg)
        server.quit()
        print(f"OTP sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
        return "2"  # Email sending failed

    # Check if email already exists in the database
    cursor.execute("SELECT COUNT(*) FROM verification WHERE email=%s", (to_email,))
    result = cursor.fetchone()
    
    if result and result[0] == 0:
        # Insert new email and OTP into the verification table
        cursor.execute("INSERT INTO verification (email, otp) VALUES (%s, %s)", (to_email, otp_str))
        print(f"Inserted OTP for {to_email}")
    else:
        # Update OTP for the existing email
        cursor.execute("UPDATE verification SET otp = %s WHERE email = %s", (otp_str, to_email))
        print(f"Updated OTP for {to_email}")

    try:
        db.commit()  # Commit the transaction
        print("Database commit successful")
        return "0"  # OTP generation and storing successful
    except Exception as e:
        print(f"Error committing transaction: {e}")
        return "1"  # Failed to commit changes to database