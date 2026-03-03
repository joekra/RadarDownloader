import os
import PySimpleGUI as sg
import requests
import boto3
import botocore
from datetime import datetime, timedelta

# Radar sites dictionary (full list of WSR-88D radar sites)
RADAR_SITES = {
    "KABR": "Aberdeen, SD",
    "KABX": "Albuquerque, NM",
    "KACX": "Jacksonville, FL",
    "KAKQ": "Wakefield, VA",
    "KAMA": "Amarillo, TX",
    "KAMX": "Miami, FL",
    "KAPX": "Gaylord, MI",
    "KARX": "La Crosse, WI",
    "KATX": "Seattle, WA",
    "KBBX": "Beale AFB, CA",
    "KBGM": "Binghamton, NY",
    "KBHX": "Eureka, CA",
    "KBIS": "Bismarck, ND",
    "KBLX": "Billings, MT",
    "KBMX": "Birmingham, AL",
    "KBOX": "Boston, MA",
    "KBRO": "Brownsville, TX",
    "KBUF": "Buffalo, NY",
    "KBYX": "Key West, FL",
    "KCAE": "Columbia, SC",
    "KCBW": "Caribou, ME",
    "KCBX": "Boise, ID",
    "KCCX": "State College, PA",
    "KCLE": "Cleveland, OH",
    "KCLX": "Charleston, SC",
    "KCRP": "Corpus Christi, TX",
    "KCXX": "Burlington, VT",
    "KCYS": "Cheyenne, WY",
    "KDAX": "Sacramento, CA",
    "KDDC": "Dodge City, KS",
    "KDFX": "Laughlin AFB, TX",
    "KDIX": "Philadelphia, PA",
    "KDLH": "Duluth, MN",
    "KDMX": "Des Moines, IA",
    "KDOX": "Dover AFB, DE",
    "KDTX": "Detroit, MI",
    "KDVN": "Davenport, IA",
    "KDYX": "Dyess AFB, TX",
    "KEAX": "Kansas City, MO",
    "KEMX": "Tucson, AZ",
    "KENX": "Albany, NY",
    "KEOX": "Fort Rucker, AL",
    "KEPZ": "El Paso, TX",
    "KESX": "Las Vegas, NV",
    "KEVX": "Eglin AFB, FL",
    "KEWX": "Austin/San Antonio, TX",
    "KEYX": "Edwards AFB, CA",
    "KFCX": "Roanoke, VA",
    "KFDR": "Frederick, OK",
    "KFDX": "Cannon AFB, NM",
    "KFFC": "Atlanta, GA",
    "KFSD": "Sioux Falls, SD",
    "KFSX": "Flagstaff, AZ",
    "KFWS": "Dallas/Fort Worth, TX",
    "KGGW": "Glasgow, MT",
    "KGJX": "Grand Junction, CO",
    "KGLD": "Goodland, KS",
    "KGRB": "Green Bay, WI",
    "KGRK": "Fort Hood, TX",
    "KGRR": "Grand Rapids, MI",
    "KGSP": "Greer, SC",
    "KGWX": "Columbus AFB, MS",
    "KGYX": "Portland, ME",
    "KHDX": "Holloman AFB, NM",
    "KHGX": "Houston, TX",
    "KHNX": "San Joaquin Valley, CA",
    "KHPX": "Fort Campbell, KY",
    "KHTX": "Hytop, AL",
    "KICT": "Wichita, KS",
    "KICX": "Cedar City, UT",
    "KILN": "Wilmington, OH",
    "KILX": "Lincoln, IL",
    "KIND": "Indianapolis, IN",
    "KINX": "Tulsa, OK",
    "KIWA": "Phoenix, AZ",
    "KIWX": "Northern Indiana, IN",
    "KJAX": "Jacksonville, FL",
    "KJGX": "Robins AFB, GA",
    "KJKL": "Jackson, KY",
    "KLBB": "Lubbock, TX",
    "KLCH": "Lake Charles, LA",
    "KLGX": "Langley Hill, WA",
    "KLIX": "New Orleans, LA",
    "KLNX": "North Platte, NE",
    "KLOT": "Chicago, IL",
    "KLRX": "Elko, NV",
    "KLSX": "St. Louis, MO",
    "KLTX": "Wilmington, NC",
    "KLWX": "Sterling, VA",
    "KLZK": "Little Rock, AR",
    "KMAF": "Midland/Odessa, TX",
    "KMAX": "Medford, OR",
    "KMBX": "Minot AFB, ND",
    "KMHX": "Morehead City, NC",
    "KMKX": "Milwaukee, WI",
    "KMLB": "Melbourne, FL",
    "KMOB": "Mobile, AL",
    "KMPX": "Minneapolis, MN",
    "KMQT": "Marquette, MI",
    "KMRX": "Morristown, TN",
    "KMSX": "Missoula, MT",
    "KMTX": "Salt Lake City, UT",
    "KMUX": "San Francisco, CA",
    "KMVX": "Mayville, ND",
    "KMXX": "Maxwell AFB, AL",
    "KNKX": "San Diego, CA",
    "KNQA": "Memphis, TN",
    "KOAX": "Omaha, NE",
    "KOHX": "Nashville, TN",
    "KOKX": "New York City, NY",
    "KOTX": "Spokane, WA",
    "KPAH": "Paducah, KY",
    "KPBZ": "Pittsburgh, PA",
    "KPDT": "Pendleton, OR",
    "KPOE": "Fort Polk, LA",
    "KPUX": "Pueblo, CO",
    "KRAX": "Raleigh, NC",
    "KRGX": "Reno, NV",
    "KRIW": "Riverton, WY",
    "KRLX": "Charleston, WV",
    "KRTX": "Portland, OR",
    "KSFX": "Pocatello, ID",
    "KSGF": "Springfield, MO",
    "KSHV": "Shreveport, LA",
    "KSJT": "San Angelo, TX",
    "KSMX": "Santa Maria, CA",
    "KSPI": "Springfield, IL",
    "KSRX": "Santa Rosa, CA",
    "KSTX": "San Antonio, TX",
    "KSUX": "Sioux City, IA",
    "KTAE": "Tallahassee, FL",
    "KTBW": "Tampa, FL",
    "KTDX": "Dallas/Fort Worth, TX",
    "KTHX": "Reno, NV",
    "KTLX": "Norman, OK",
    "KTOP": "Topeka, KS",
    "KTWX": "Jackson, MS",
    "KTYX": "Cedar Rapids, IA",
    "KUAO": "Aurora, OR",
    "KUEX": "Key West, FL",
    "KUWX": "Fort Worth, TX",
    "KVAX": "Vicksburg, MS",
    "KVTX": "Vicksburg, MS",
    "KWAO": "Anchorage, AK",
    "KWBC": "National Weather Service",
    "KWBG": "Fayetteville, AR",
    "KWES": "Fort Sill, OK",
    "KXWX": "Northern Virginia",
    "KYSI": "Northern Illinois",
    "KZFP": "Northern New Jersey"
}

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    config=botocore.config.Config(signature_version=botocore.UNSIGNED)
)
BUCKET_NAME = "unidata-nexrad-level2"

# Helpers
def list_files_in_s3(prefix):
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        if "Contents" in response:
            return [obj["Key"] for obj in response["Contents"]]
    except Exception as e:
        print("Error listing files:", e)
        return []
    return []

def download_files(start, end, radar, window=None, progress_key=None):
    download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    os.makedirs(download_folder, exist_ok=True)

    prefix = f"{start.strftime('%Y/%m/%d')}/{radar}/"
    file_list = list_files_in_s3(prefix)

    # Pre-filter files to only include those within start/end
    filtered_files = []
    for file_key in file_list:
        try:
            file_time_str = file_key.split("_")[1][:6]
            file_datetime = datetime.strptime(start.strftime('%Y%m%d') + file_time_str, '%Y%m%d%H%M%S')
            if start <= file_datetime <= end:
                filtered_files.append(file_key)
        except:
            continue

    count = 0
    total_files = len(filtered_files)

    if progress_key and window:
        window[progress_key].UpdateBar(0, max=total_files)
        window.refresh()

    for idx, file_key in enumerate(filtered_files):
        try:
            file_path = os.path.join(download_folder, os.path.basename(file_key))
            s3_client.download_file(BUCKET_NAME, file_key, file_path)
            count += 1
        except Exception as e:
            print(f"Error downloading {file_key}: {e}")
        if progress_key and window:
            window[progress_key].UpdateBar(idx + 1)
            window.refresh()

    # ✅ Update the status text after completion
    if window:
        if count == 0:
            window["-STATUS-"].update(f"No files found for radar site {radar}.")
        else:
            window["-STATUS-"].update(f"Download Complete! {count} files downloaded.")
    return count

def validate_date_parts(year, month, day):
    try:
        return datetime(int(year), int(month), int(day)).date()
    except:
        return None

def validate_hour_minute(hour_str, minute_str):
    try:
        h, m = int(hour_str), int(minute_str)
        if not (0 <= h <= 23 and 0 <= m <= 59):
            return None
        m = (m // 10) * 10  # round minutes to nearest 10
        return f"{h:02d}:{m:02d}"
    except:
        return None

# GUI Layout
left_column = [
    [sg.Text("Radar Site", font=("Helvetica", 14, "bold"), justification="center")],
    [sg.Input("", key="-RADAR-", size=(12,1), justification="center")],
    [sg.Text("", pad=(0,0))],  # small vertical space

    [sg.Text("Select Date", font=("Helvetica", 14, "bold"), justification="center")],
    [sg.Text("Year"), sg.Input("", key="-YEAR-", size=(5,1)),
     sg.Text("Month"), sg.Input("", key="-MONTH-", size=(3,1)),
     sg.Text("Day"), sg.Input("", key="-DAY-", size=(3,1))],

    [sg.Button("Previous Day", size=(10,1)), sg.Button("Next Day", size=(10,1))],
    [sg.Text("", pad=(0,0))],  # small vertical space

    [sg.Text("Start Time", font=("Helvetica", 14, "bold"), justification="center")],
    [sg.Text("Hour"), sg.Input("", key="-START_HH-", size=(3,1)),
     sg.Text("Minute"), sg.Input("", key="-START_MM-", size=(3,1))],

    [sg.Text("End Time", font=("Helvetica", 14, "bold"), justification="center")],
    [sg.Text("Hour"), sg.Input("", key="-END_HH-", size=(3,1)),
     sg.Text("Minute"), sg.Input("", key="-END_MM-", size=(3,1))],

    # Download button centered under day buttons
    [sg.Column([[sg.Button("Download", size=(21,1))]], element_justification="center", pad=(0,10))],

    # Progress bar
    [sg.ProgressBar(max_value=100, orientation='h', size=(20, 20), key="-PROGRESS-", visible=False, bar_color=("green", "white"))],

    [sg.Text("", key="-STATUS-", size=(30,1), text_color="white", justification="center", expand_x=True)]
]


# Right column - map image
right_column = [
    [sg.Image(filename=r"C:\Users\offic\WSR-88DMap.png", key="-MAP-", size=(1367, 600))]
]

# Combine columns
layout = [
    [sg.Column(left_column, element_justification="center"), sg.Column(right_column)]
]

# Create window
window = sg.Window("Radar Downloader", layout, resizable=True, finalize=True)

# Event Loop
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break

    # Day change buttons
    if event in ["Next Day", "Previous Day"]:
        year, month, day = values["-YEAR-"], values["-MONTH-"], values["-DAY-"]
        current_date = validate_date_parts(year, month, day) or datetime.utcnow().date()
        new_date = current_date + timedelta(days=1) if event=="Next Day" else current_date - timedelta(days=1)
        window["-YEAR-"].update(new_date.strftime("%Y"))
        window["-MONTH-"].update(new_date.strftime("%m"))
        window["-DAY-"].update(new_date.strftime("%d"))
        window["-START_HH-"].update("00")
        window["-START_MM-"].update("00")

    # Download
    if event == "Download":
        radar = values["-RADAR-"].upper().strip()
        if not radar:
            sg.popup("Please enter a radar site code.")
            continue

        date_val = validate_date_parts(values["-YEAR-"], values["-MONTH-"], values["-DAY-"])
        if not date_val:
            sg.popup("Invalid date entered.")
            continue

        start_time_val = validate_hour_minute(values["-START_HH-"], values["-START_MM-"])
        end_time_val = validate_hour_minute(values["-END_HH-"], values["-END_MM-"])
        if not start_time_val or not end_time_val:
            sg.popup("Invalid start or end time.")
            continue

        start_dt = datetime.strptime(f"{date_val} {start_time_val}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{date_val} {end_time_val}", "%Y-%m-%d %H:%M")
        if start_dt >= end_dt:
            sg.popup("Start time must be before end time.")
            continue

        # Show progress bar
        window["-PROGRESS-"].update(0, max=100, visible=True)
        window.refresh()

        # Download files with progress
        count = download_files(start_dt, end_dt, radar, window=window, progress_key="-PROGRESS-")
        window["-PROGRESS-"].update(visible=False)

        if count == 0:
            sg.popup(f"No files found for radar site {radar}.")
        

window.close()