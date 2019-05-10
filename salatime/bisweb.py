from datetime import datetime
import requests
import requests_cache as rc
from bs4 import BeautifulSoup as bs
import re

BASE_URL = "https://aleemstudio.com/SalatTimings/SalatTimings4MonthExternal/"
current_month = datetime.now().month
current_day = datetime.now().day
current_hour = datetime.now().hour
current_minute = datetime.now().minute
rc.install_cache()

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
  "Fajr",
  "Sunrise",
  "Duhr",
  "Asr",
  "Maghrib",
  "Isha"
]

def getCurrentMonthPage(month):
  response = requests.get(BASE_URL + str(month))
  return response.text

def getTimesTable(page):
  return bs(page, 'html.parser').find(id="#times").table

def getListOfTimes(table):
  trs = table.find_all('tr')[1:] # cut off <th> headings
  timelist = []
  for tr in trs:
    td = tr.find_all('td')
    times = [i.text.strip() for i in td] # prayer times for one day
    timelist.append(times) #TODO: refactor this for more speed, maybe?
  return timelist

def getCurrentDayTimes(timelist):
  return timelist[current_day-1] # 0-index -- unnecessary if you keep <th>

def displayTimes(today):
  print("")
  print(months[current_month],today[0],"|","Ramadan",getRamadanDay())
  print("=================")
  print("   Fajr: ",today[1],"AM")
  print("Sunrise: ",today[2],"AM")
  print("   Duhr:",today[3],"PM")
  print("    Asr: ",today[4],"PM")
  print("Maghrib: ",today[5],"PM")
  print("   Isha: ",today[6],"PM")
  print("")

def getRamadanDay(): # only works for 2019
  if current_month == 5:
    return current_day - 5
  elif month == 6:
    return current_day + 26

def displayCurrentPrayer(today): # impure function, also ugly -- TODO: refactor
  today_times = today[1:] # chop off date
  # convert PM into 24h
  for i in range(2,6):
    prayer_hour, prayer_minute = splitHM(today_times[i])
    if prayer_hour < 12:
      prayer_hour += 12
    today_times[i] = f"{prayer_hour}:{prayer_minute}"
  
  # actually calculate current / remaining
  for prayer_time in today_times:
    prayer_hour, prayer_minute = splitHM(prayer_time)
    # wastefully calculate remaining time even when not determined to be current
    rem_hour = prayer_hour - current_hour
    rem_min = prayer_minute - current_minute
    if rem_min < 0:
      rem_min += 60
      rem_hour -= 1
    # determine current and print
    if prayer_hour < current_hour:
      continue
    if prayer_hour == current_hour:
      if prayer_minute <= current_minute:
        continue
      else:
        next_prayer = findNextPrayer(prayer_time, today_times)
        print(f"Current prayer is {prayers[next_prayer - 1]} since {today[next_prayer]}.",)
        print(f"Next prayer is {prayers[next_prayer]} at {prayer_time}.")
        print(f"Time until next prayer is {rem_hour} hours and {rem_min} minutes.")
      break
    else:
      next_prayer = findNextPrayer(prayer_time, today_times)
      print(f"Current prayer is {prayers[next_prayer - 1]} since {today[next_prayer]}.",)
      print(f"Next prayer is {prayers[next_prayer]} at {prayer_time}.")
      print(f"Time until next prayer is {rem_hour} hours and {rem_min} minutes.")
      break

def splitHM(time):
  hm = re.split(':',time)
  return int(hm[0]), int(hm[1])

def findNextPrayer(time, today_times):
  for i in range(len(today)):
    if time == today_times[i]:
      return i

if __name__ == '__main__':
  page = getCurrentMonthPage(current_month)
  table = getTimesTable(page)
  timelist = getListOfTimes(table)
  today = getCurrentDayTimes(timelist)
  displayTimes(today)

  displayCurrentPrayer(today)
  print("")
