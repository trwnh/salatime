#%% Imports

from datetime import datetime
import requests
import requests_cache
from bs4 import BeautifulSoup as bs
import re

#%% Invariants
requests_cache.install_cache()

BASE_URL = "https://aleemstudio.com/SalatTimings/SalatTimings4MonthExternal/"
current_month = datetime.now().month
current_day = datetime.now().day
current_hour = datetime.now().hour
current_minute = datetime.now().minute

months = [
  "Unknown",
  "January",
  "Febuary",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December"
]
prayers = [
  "Qiyam",
  "Fajr",
  "Shurooq",
  "Duhr",
  "Asr",
  "Maghrib",
  "Isha"
]

#%% Downloading and parsing

def getCurrentMonthPage(month):
  """Scrapes the webpage of the current month's prayer times from BISWeb.
  Input: Current month (int)
  Output: HTML response text (str)
  """
  return requests.get(BASE_URL + str(month)).text

def getTimesTable(page):
  """Uses BeautifulSoup to extract just the times table from HTML.
  Input: HTML response text (str)
  Output: HTML <table> element (str)
  """
  return bs(page, 'html.parser').find(id="#times").table

def parse(table):
  """Parse <table> for rows and data-elements.
  Input: HTML <table> element (str)
  Output: Header and data (list[list[str]])
  """
  trs = table.find_all('tr')
  month = []
  for tr in trs:
    cells = tr.find_all('td')
    if not cells:
      cells = tr.find_all('th')
    row = [cell.text.strip() for cell in cells]
    month.append(row)
  return month

#%% Utility functions

def irange(start,end):
  """Wrapper for range() built-in, but includes upper bound."""
  return range(start,end+1)

def split(time):
  """Splits a time into hours and minutes (at colon).
  Input: Time in the form HH:MM (str)
  Output: Hours, minutes (int, int)
  """
  hour, minute = re.split(':',time)
  return int(hour), int(minute)

def PMto24(prayer_time):
  """Converts PM prayer time to 24-hour format.
  Input: Time in HH:MM (str)
  Output: Time in HH:MM (str)
  Note: 
  """
  hour, minute = split(prayer_time)
  if hour < 12: 
    hour += 12
  if hour > 22: # prayer after 9:30pm is unrealistic
    hour -= 12 # ... so this is probably duhr at 11am (winter)
  return f"{hour}:{minute}"

def time_until(time):
  """Calculates difference between current time and target time.
  Input: Target time
  Output: Remaining hours/minutes (int, int)
  """
  hour, minute = split(time)
  remaining_hours = hour - current_hour
  remaining_minutes = minute - current_minute
  if remaining_minutes < 0:
    remaining_minutes += 60
    remaining_hours -= 1
  return remaining_hours, remaining_minutes

#%% Helper functions

def currentPrayer(day):
  """Determine which prayer is currently active.
  Input: A day and its prayer times (list[str])
  Output: Index of current prayer (int)
  (PM logic is very naive due to lack of actual AM/PM in source data.)
  """
  for i, time in enumerate(day):
    if i == 0: # day[0] is the date,
      continue # so skip it bc it's not a prayer time.
    if i == 6: # if you reach isha,
      return i # then it is current bc all others are not current.
    if i > 2: # if it's not fajr or shurooq,
      time = PMto24(time) # then it's most likely a PM time.
    hours_until, minutes_until = time_until(time)
    time_in_future = (hours_until > 0) or (hours_until == 0 and minutes_until > 0)
    if time_in_future:
      return i-1

def getRamadanDay():
  """Returns today's date in Ramadan (only for 2019)"""
  # TODO: make it more generic by parsing GET response of 13th month
  if current_month == 5:
    return current_day - 5
  elif current_month == 6:
    return current_day + 26

#%% Display and output

def display(day):
  """Print out the times table for a day.
  Input: A day and its prayer times (list[str])
  Output: (print to console)
  """
# TODO: use multiple assignment? date,fajr,...,isha = day
#   - on second thought, nah, it's less readable.
#   - may want to consider auxiliary function to set global vars on runtime?
# TODO: support months other than current_month
  print(months[current_month],day[0],"| Ramadan",getRamadanDay())
  print("=================")
  print("   Fajr: ",day[1],"AM")
  print("Shurooq: ",day[2],"AM")
  print("   Duhr:",day[3],"PM")
  print("    Asr: ",day[4],"PM")
  print("Maghrib: ",day[5],"PM")
  print("   Isha: ",day[6],"PM")

def displayActive(day):
  """Print metrics about the current/next prayers. Input implied to be today.
  Input: A day and its prayer times (list[str])
  Output: (print to console)
  """

  current = currentPrayer(day)

  if not current: # 0 = qiyam (pre-fajr), no real current prayer
    print("Current prayer is Qiyam.")
  else:
    current_prayer = day[current]
    if current in irange(3,6): # current in [duhr, asr, maghrib, isha]
      current_prayer = PMto24(current_prayer)
    print(f"Current prayer is {prayers[current]} since {current_prayer}.")
  
  print(f"The time is currently {current_hour}:{str(current_minute).zfill(2)}.")

  if current in irange(0,5): # isha has no next prayer
    next_prayer = day[current+1]
    if current+1 in irange(3,6): # next in [duhr, asr, maghrib, isha]
      next_prayer = PMto24(next_prayer)
    print(f"Next prayer is {prayers[current+1]} at {next_prayer}.")
    h,m = time_until(next_prayer)
    if h:
      print(f"Time until next prayer is {h} hours and {m} minutes.")
    else:
      print(f"Time until next prayer is {m} minutes.")

#%% Default output

if __name__ == '__main__':
  #start_time = datetime.now()
  page = getCurrentMonthPage(current_month)
  table = getTimesTable(page)
  month = parse(table)
  today = month[current_day]
  print("")
  display(today)
  print("")
  displayActive(today)
  print("")
  #end_time = datetime.now()
  #print("Time taken:",end_time-start_time)
