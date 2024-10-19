import datetime

def datetime_to_str(date: datetime.datetime):
  return None if date is None else date.strftime("%Y-%m-%d %H:%M:%S")

def datetime_from_str(date_str: str):
  return None if date_str is None else datetime.datetime.strptime(date_str,"%Y-%m-%d %H:%M:%S")