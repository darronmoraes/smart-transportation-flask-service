import base64

# pip install pip
import pyotp

# validity of code in seconds
INTERVAL = 30
VALID_WINDOW = 10

def generate_otp(email, phone_country_code, phone_number):
    # every ${INTERVAL}s a new otp would be generated if asked
    secret = "%s|%s%s" % (email, phone_country_code, phone_number)
    secret_base64_encoded = base64.b32encode(secret.encode("utf-8"))
    totp = pyotp.TOTP(secret_base64_encoded, interval=INTERVAL)
    otp = totp.now()
    return otp


def verify_otp(email, phone_country_code, phone_number, otp):
    secret = "%s|%s%s" % (email, phone_country_code, phone_number)
    secret_base64_encoded = base64.b32encode(secret.encode("utf-8"))
    totp = pyotp.TOTP(secret_base64_encoded, interval=INTERVAL)
    otp_verified = totp.verify(otp, valid_window=VALID_WINDOW)
    return otp_verified