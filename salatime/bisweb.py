from datetime import datetime
import requests
import requests_cache as rc
from bs4 import BeautifulSoup as bs
import re

BASE_URL = "https://aleemstudio.com/SalatTimings/SalatTimings4MonthExternal/"
month = datetime.now().month
day = datetime.now().day
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
  return timelist[day-1] # 0-index -- unnecessary if you keep <th>

def displayTimes(today):
  print("")
  print(months[month],today[0],"|","Ramadan",getRamadanDay())
  print("=================")
  print("   Fajr: ",today[1],"AM")
  print("Sunrise: ",today[2],"AM")
  print("   Duhr:",today[3],"PM")
  print("    Asr: ",today[4],"PM")
  print("Maghrib: ",today[5],"PM")
  print("   Isha: ",today[6],"PM")
  print("")

def getRamadanDay(): # only works for 2019
  if month == 5:
    return day - 5
  elif month == 6:
    return day + 26

def displayCurrentPrayer(today): # impure function, also ugly -- TODO: refactor
  # convert PM into 24h
  for i in range(3,7):
    hm = re.split(':',today[i])
    hour = hm[0]
    minute = hm[1]
    if int(hour) < 12:
      hour = str(int(hour) + 12)
    today[i] = f"{hour}:{minute}"
  current_hour = datetime.now().hour
  current_minute = datetime.now().minute
  
  # actually calculate current / remaining
  for prayer in today[1:]:
    hm = re.split(':',prayer)
    prayer_hour = int(hm[0])
    prayer_minute = int(hm[1])
    for i in range(1,7):
      if f"{prayer_hour}:{prayer_minute}" == today[i]:
        if i in range(2,7):
          current_prayer = i-1 # before next prayer
        else:
          current_prayer = 0 # pre-fajr interval
      rem_hour = prayer_hour - current_hour
      rem_min = prayer_minute - current_minute
      if rem_min < 0:
        rem_min += 60
        rem_hour -= 1
        
    # determine format and print
    if prayer_hour < current_hour:
      continue
    if prayer_hour == current_hour:
      if prayer_minute <= current_minute:
        continue
      else:
        print(f"Time until next prayer is {prayer_minute-current_minute} minutes.")
        print("Current prayer:",prayers[current_prayer-1],today[current_prayer])
        break
    else:
      print(f"Time until next prayer is {rem_hour} hours and {rem_min} minutes.")
      print("Current prayer:",prayers[current_prayer-1],today[current_prayer])
      break


if __name__ == '__main__':
  page = getCurrentMonthPage(month)
  table = getTimesTable(page)
  timelist = getListOfTimes(table)
  today = getCurrentDayTimes(timelist)
  displayTimes(today)

  displayCurrentPrayer(today)
  print("")
