import os
import calendar
import os.path
import sys
from time import time
from datetime import datetime

from UploadFile_test import UploadFile
from StatisticalReport_test import CreateReportFile, CreateOpenAlarmsFile
import TerugkoppelingExcelFile_test
import OpenAlarmsExcelFile_test
from Merge_test import CreateHistory, Load, Save

def Terugkoppeling(IRIS_log,key,**kwargs):
    FolderName = "Logboek"
    DriveID = '1GiFD2nv6R8I12iZEuCOXlXv8f8rv4QdO'

    if 'Firsttime' in kwargs:
        csv_files = CreateReportFile(IRIS_log, Dag = None)
        path = kwargs['folder_path']
        Logs = CreateHistory(csv_files[2],path)
    else:
        csv_files = CreateReportFile(IRIS_log)

    print("Creating Excel file for the report")
    file = TerugkoppelingExcelFile_test.CreateExcelFile(csv_files)
    for f in csv_files:
        os.remove(f)

    if 'FileName' in kwargs:
        name = kwargs['FileName']
        feedback = UploadFile(file,FolderName,DriveID,key, FileName = name)
    else:
        feedback = UploadFile(file,FolderName,DriveID,key)
    if 'Month' in kwargs:
        if is_last_day_of_month():
            FolderName = "Archief"
            DriveID = '18wbKUIajcX4qauT463T116S6s7Linaav'
            UploadFile(file,FolderName,DriveID,'last_day', FileName = name)
    os.remove(file)

    if 'Firsttime' in kwargs:
        return feedback, Logs
    else:
        return feedback

def CreateLog(st,feedback):
    et = time()
    duration_seconds = (et - st)
    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)
    print(f"{minutes} minutes and {seconds} seconds")
    
    #Set working directory to data folder
    os.chdir(os.path.join(os.getcwd(),"data"))

    if os.path.exists("Log_test.txt"):
        f = open("Log_test.txt","a")
    else:
        f = open("Log_test.txt","x")
        f.writelines("Date                           Runtime (in s)                  Result\n")
    et = time()    
    f.writelines("{}     {} minutes and {} seconds         {}\n".format(datetime.now(),minutes,seconds,feedback))
    f.close()
    os.chdir(os.path.dirname(os.getcwd()))

def OpenAlarms(Log,key):
    FolderName = "test"
    DriveID = '0AIm6EsRAnC2mUk9PVA'

    csv_file =  CreateOpenAlarmsFile(Log)

    print("Creating Excel file for Actual Alarms")
    file = OpenAlarmsExcelFile_test.CreateExcelFile(csv_file)

    open_alarms_file_name = {'open_alarms': "Openstaande Alarmen"}
    Save(open_alarms_file_name, "dates_test.json")

    feedback = UploadFile(file, FolderName, DriveID,key , FileName = open_alarms_file_name['open_alarms'])
    os.remove(file)
    os.remove(csv_file)

    return feedback

def is_last_day_of_month():
    now = datetime.now()
    # Extract year and month from the current date
    year = now.year
    month = now.month
    
    # Get the number of days in the current month
    days_in_month = calendar.monthrange(year, month)[1]
    
    # Check if the current day is equal to the number of days in the month
    return now.day == days_in_month

def SetDates():
    json_path = "dates_test.json"
    dates = Load(json_path)

    change = {
        'old_week': dates['week'],
        'old_month': dates['month']
    }

    Save(change, json_path)

def RemoveOldFiles(folder_path):
    file_name_json='dates.json'

    files = Load(file_name_json)
    os.chdir(os.path.join(os.getcwd(),"data"))
    if os.path.exists(file_name_json):
        if files['old_week'] != files['week']:

            key = files['old_week']
            path = os.path.join(folder_path,key)
            if os.path.exists(path):
                os.remove(path)
        if files['old_month'] != files['month']:
            key = files['old_month']
            path = os.path.join(folder_path,key)
            if os.path.exists(path):
                 os.remove(path)
    os.chdir(os.path.dirname(os.getcwd()))

def main():
    paths_dic = Load("source_paths.json")
    start_time = time()
    Logbook = paths_dic["iris_log_test"]
    ActueelAlarms = paths_dic["open_alarms_log_test"]

    day = ""
    week = ""
    month = ""
    openalarms = ""
    
    if os.path.exists(Logbook):
        Feedback, Logs = Terugkoppeling(Logbook, 'day', Firsttime = None, folder_path = paths_dic["week_month_log_folder_test"])
        day = "day logbook"
    else:
        Feedback = "The day log path does not exist."

        print(Feedback)
    print("")
        
    if os.path.exists(Logs[0]):
        Feedback = Terugkoppeling(Logs[0], 'week', FileName = os.path.basename(Logs[0]))
        week = "week logbook"
    else:
        log_feedback = "The week log path does not exist."
        print(Feedback)
    print("")

    if os.path.exists(Logs[1]):
        Feedback = Terugkoppeling(Logs[1], 'month', FileName = os.path.basename(Logs[1]), Month = None)
        month = "month logbook"
    else:
        log_feedback = "The month log path does not exist."
        print(Feedback)
    print("")
    
    if os.path.exists(ActueelAlarms):
        Feedback = OpenAlarms(ActueelAlarms, 'open_alarms')
        openalarms = "open alarms log"
    else:
        log_feedback = "The Open Alarms path does not exist."
        print(Feedback)
    print("")
    
    all_files = list(filter(None,[day,week,month, openalarms]))

    if len(all_files) == 0:
        log_feedback = "No files were uploaded"
    else:
        log_feedback = "The files: " + ", ".join(all_files) + " have been uploaded."
    CreateLog(start_time,log_feedback)

    RemoveOldFiles(folder_path = paths_dic["week_month_log_folder"])

    SetDates()

    
if __name__ == '__main__':
    print("Starting")
    sys.exit(main())