import hashlib
import hmac
SECRET_KEY = b"894d37da41fb91344a4d1e87412986ad1db183a677a20be2076a7623c24a32a7"
if __name__ == "__main__":
    hmac_obj = hmac.new(SECRET_KEY, "Blabla".encode("UTF-8"), hashlib.sha256)
    hmac_obj2 = hmac.new(SECRET_KEY, "Blabla".encode("UTF-8"), hashlib.sha256)
    print(type(hmac_obj.digest()))
    print(hmac.compare_digest(hmac_obj.digest(), hmac_obj2.digest()))
