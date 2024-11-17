import datetime
def datetime_to_str(date: datetime.datetime):
  return None if date is None else date.strftime("%Y-%m-%d %H:%M:%S")

def datetime_from_str(date_str: str):
  return None if date_str is None else datetime.datetime.strptime(date_str,"%Y-%m-%d %H:%M:%S")

import re
def decode_unicode_string(encoded_str):
    # Use a regular expression to find all occurrences of 'uXXXX'
    decoded_str = re.sub(r'u([0-9A-Fa-f]{4})', lambda match: chr(int(match.group(1), 16)), encoded_str)
    return decoded_str
