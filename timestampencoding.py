# taken from https://www.guyrutenberg.com/2010/04/30/url-safe-timestamps-using-base64/
import base64
import struct
import time
 
def build_timestamp():
    """
    Return a 6 chars url-safe timestamp
    """
    return base64.urlsafe_b64encode(struct.pack("!L",int(time.time())))[:-2]
 
def read_timestamp(t):
    """
    Convert a 6 chars url-safe timestamp back to time
    """
    return struct.unpack("!L",base64.urlsafe_b64decode(t+"=="))[0]
