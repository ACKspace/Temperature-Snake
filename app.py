import pickle
from datetime import datetime, timedelta
from collections import OrderedDict
import urllib.request
import re
import time

# Build our list for this data
STARTDATE = datetime.strptime("2023-12-25", '%Y-%m-%d')
LATITUDE = "50.8449365"
LONGITUDE = "6.0064879"

def tempToColor(temp):   
    if temp < 0:
        return "light grey"
    elif temp < 5:
        return "dark grey"
    elif temp < 10:
        return "blue"
    elif temp < 15:
        return "green"
    elif temp < 20:
        return "light green"
    elif temp < 25:
        return "yellow"
    elif temp < 30:
        return "orange"
    elif temp < 35:
        return "orange-red"
    else:
        return "red"
    
def average(l):
    return round(sum(l) / len(l))

try:
    days = pickle.load(open("days.p", "rb"))
except FileNotFoundError:
    days = OrderedDict()

# Determine from which date onwards we should start getting temperature data
try:
    # Get the date after the last one we have data on
    startDate = datetime.strptime(next(reversed(days)), '%Y-%m-%d') + timedelta(days=1)
except StopIteration:
    # We didn't find any days, so start from the beginning
    startDate = STARTDATE

# weerlive.nl only gives data for two days prior
endDate = datetime.today() - timedelta(days=2)

# Stolen from stackoverflow, yields dates between start and end date
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def getTemps(stringDate, latitude, longitude):
    url = f"https://weerlive.nl/items/php/historiegrafieken_ophalen.php?lat={latitude}&lon={longitude}&dag={stringDate}"
    javascript = str(urllib.request.urlopen(url).read())
    cleaned = re.sub(r"[\n\t\s]*", "", javascript).replace(r"\n","").replace("\\","")
    temperatures = re.search(r".*datasets:\[{label:'temperatuur',data:\[((-?\d+(\.\d+)?,?)*)\].*", cleaned)
    return [float(x) for x in temperatures.group(1).split(",")]

for single_date in daterange(startDate, endDate):
    stringDate = single_date.strftime("%Y-%m-%d")
    temps = getTemps(stringDate, LATITUDE, LONGITUDE)
    print(f"{stringDate}: {temps}")
    days[stringDate] = temps
    time.sleep(4)

pickle.dump( days, open( "days.p", "wb" ) )

print("{| class=\"wikitable sortable\"")
print("|-")
print("! Date !! Avg. Temp !! Color")
print("|-")

for i, key in enumerate(days):
    avgTemp = average(days[key])
    print(f"| {key} || {avgTemp} || {tempToColor(avgTemp)}")
    if i < len(days) - 1:
        print("|-")

print("|}")
input()