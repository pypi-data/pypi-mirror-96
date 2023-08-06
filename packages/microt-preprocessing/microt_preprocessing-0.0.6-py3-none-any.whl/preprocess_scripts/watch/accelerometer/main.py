# import os
from os import path, makedirs
# import mhealthlab_client.mhlab as mhlab

from ...utils.validate_dates import *
from ...utils.validate_hours import validate_hours
from ...utils.get_time_zone import *
from .parse import *
# from .bafToCSV import *
# from .csvToMIMS import *
# from .baf_to_dataframe import *
from .dataframe_to_MIMS import *
from shutil import copyfile
import warnings

# from SWaN import classify

warnings.filterwarnings("ignore")

area = "data-watch"
device = "watch"
file_shortname = "accelerometer"

# since the accelerometer file name is mixed with irregular numbers, file name matching is needed.
name_pattern = "AndroidWearWatch"
TASK = "all"
SAMPLING_RATE = 50.0


def reg_exp_matching(hour_folder_path, name_pattern):
    file_list = listdir(hour_folder_path)
    matched_name = ""
    for file_str in file_list:
        if file_str.startswith(name_pattern):
            matched_name = file_str
            break
    return matched_name


def MIMSExist(hour_folder_path):
    # print(str(hour_folder_path))
    exist = False
    path_mims = None
    # in_path = sorted(glob(os.path.join(hour_folder_path, '020000000000-AccelerationCalibrated.*.sensor.csv')))[0]

    # If the MIMS-unit file already exists, import the csv file for concatenation of daily csv
    # tmpDir = os.path.dirname(in_path)
    path_mims_list = glob(os.path.join(hour_folder_path, "mims_*.csv"))
    # print('mims path list')
    # print(path_mims_list)

    if len(path_mims_list) > 0:
        path_mims = path_mims_list[0]
        # print(path_mims + " exists. Skipping csv to MIMS conversion for this file.")
        exist = True

    return exist, path_mims


def HARExist(hour_folder_path):
    # print(str(hour_folder_path))
    exist = False
    path_har = None
    path_har_list = glob(os.path.join(hour_folder_path, "har_*.csv"))
    # print('har path list')
    # print(path_har_list)

    if len(path_har_list) > 0:
        path_har = path_har_list[0]
        # print(path_har + " exists. Skipping csv to HAR conversion for this file.")
        exist = True
    return exist, path_har


def pre_process(microT_root_path, intermediate_file_save_path, p_id, date):
    participant_folder_path = microT_root_path
    area_folder_path = participant_folder_path + sep + area
    hours_with_target_file_list = {}  # included in participant stats report
    if path.exists(area_folder_path):
        date_folder_path = area_folder_path + sep + date
        if path.exists(date_folder_path):
            file_save_date_path = intermediate_file_save_path + sep + "intermediate_file" + sep + p_id + sep + date
            if not path.exists(file_save_date_path):
                makedirs(file_save_date_path)
            day_file_name_mims = device + "_" + file_shortname + "_mims_clean_" + date + ".csv"
            day_file_name_har_intensity = device + "_" + file_shortname + "_har_clean_" + "_intensity_" + date + ".csv"
            day_file_name_har_activity = device + "_" + file_shortname + "_har_clean_" + "_activity_" + date + ".csv"
            day_file_name_har_posture = device + "_" + file_shortname + "_har_clean_" + "_posture_" + date + ".csv"
            day_file_save_path_mims = file_save_date_path + sep + day_file_name_mims
            day_file_save_path_har_intensity = file_save_date_path + sep + day_file_name_har_intensity
            day_file_save_path_har_activity = file_save_date_path + sep + day_file_name_har_activity
            day_file_save_path_har_posture = file_save_date_path + sep + day_file_name_har_posture
            date_swan_file = microT_root_path + sep + area + sep + date + sep + "SWaN_" + date + "_final.csv"
            p_id_no_domain = p_id.split("@")[0]
            swan_dest = file_save_date_path + sep + device + "_" + file_shortname + "_swan_clean_" + date + ".csv"
            if not path.exists(day_file_save_path_mims) and not path.exists(day_file_save_path_har_activity) and \
                    not path.exists(day_file_save_path_har_intensity) and not path.exists(
                day_file_save_path_har_posture) and not path.exists(swan_dest):
                # if not path.exists(date_swan_file):
                #     print("For date: " + date)
                #     classify.time_study_preprocessing_main(sampling_rate=SAMPLING_RATE, input_folder=microT_root_path,
                #                   file_path=p_id_no_domain, startdateStr=date)
                if path.exists(date_swan_file):
                    copyfile(date_swan_file, swan_dest)
                df_participant_mims = pd.DataFrame()
                df_participant_har_intensity = pd.DataFrame()
                df_participant_har_activity = pd.DataFrame()
                df_participant_har_posture = pd.DataFrame()
                date_folder_path = area_folder_path + sep + date
                # check hourly folder
                validated_hour_list, HAVE_ALL_HOURS = validate_hours(date_folder_path)
                if len(validated_hour_list) == 0:
                    print("Cannot find hour folder in {} data".format(date))
                # iterate through hour folders
                hours_with_target_file = len(validated_hour_list)  # included in participant stats report
                for hour in validated_hour_list:
                    hour_folder_path = date_folder_path + sep + hour
                    # time zone
                    time_zone = get_time_zone(hour_folder_path)
                    # step 2.1: read target hourly file, baf to csv, csv to mims
                    target_file_matched = reg_exp_matching(hour_folder_path, name_pattern)
                    # binary_df = None
                    if len(target_file_matched) > 0:
                        target_file_path = hour_folder_path + sep + target_file_matched
                        # compressed_csv_path = bafToCsv(target_file_path) ## Convert this to a data frame first
                        # binary_df = baf_to_dataframe(target_file_path)
                        mimsExist, mims_path = MIMSExist(hour_folder_path)
                        harExists, har_path = HARExist(hour_folder_path)
                        out_path_general = hour_folder_path + sep + "har_" + date + "_" + hour + ".csv"
                        out_path_intensity = hour_folder_path + sep + "har_" + date + "_" + hour + "_intensity" + ".csv"
                        out_path_posture = hour_folder_path + sep + "har_" + date + "_" + hour + "_posture" + ".csv"
                        out_path_activity = hour_folder_path + sep + "har_" + date + "_" + hour + "_activity" + ".csv"
                        # run_har = True
                        # if not harExists:
                        #     hr_dfs = mhlab.run_har_on_dataframe(TASK, binary_df, SAMPLING_RATE, out_path_general)
                        #     df_hour_activity = hr_dfs['activity']
                        #     df_hour_intensity = hr_dfs['intensity']
                        #     df_hour_posture = hr_dfs['posture']
                        # else:
                        if path.exists(out_path_activity):
                            df_hour_activity = pd.read_csv(out_path_activity)
                            df_participant_har_activity = pd.concat([df_participant_har_activity, df_hour_activity])
                        if path.exists(out_path_intensity):
                            df_hour_intensity = pd.read_csv(out_path_intensity)
                            df_participant_har_intensity = pd.concat([df_participant_har_intensity, df_hour_intensity])
                        if path.exists(out_path_posture):
                            df_hour_posture = pd.read_csv(out_path_posture)
                            df_participant_har_posture = pd.concat([df_participant_har_posture, df_hour_posture])

                        # if not mimsExist:
                        #     df_hour_mims = dataframe_to_MIMS(hour_folder_path, date,
                        #                                      hour,
                        #                                      binary_df)
                        # else:
                        if mims_path is not None and path.exists(mims_path):
                            df_hour_mims = pd.read_csv(mims_path)
                            df_hour_mims = parse_raw_df(df_hour_mims, time_zone)
                            df_participant_mims = pd.concat([df_participant_mims, df_hour_mims])
                        # except:
                        #     print("Empty mims csv file", mims_path)
                        #     continue
                    else:
                        hours_with_target_file -= 1
                        continue

                    # step 2.2: parse target hourly file
                    # if df_hour_mims.shape[0] != 0:
                    #     df_hour_mims = parse_raw_df(df_hour_mims, time_zone)
                    #     df_participant_mims = pd.concat([df_participant_mims, df_hour_mims])

                    # if df_hour_activity.shape[0] != 0:
                    #     df_participant_har_activity = pd.concat([df_participant_har_activity, df_hour_activity])

                    # if df_hour_intensity.shape[0] != 0:
                    #     df_participant_har_intensity = pd.concat([df_participant_har_intensity, df_hour_intensity])

                    # if df_hour_posture.shape[0] != 0:
                    #     df_participant_har_posture = pd.concat([df_participant_har_posture, df_hour_posture])

                hours_with_target_file_list[date] = hours_with_target_file
                if df_participant_mims.shape[0] != 0:
                    df_participant_mims.to_csv(day_file_save_path_mims, index=False)
                if df_participant_har_intensity.shape[0] != 0:
                    df_participant_har_intensity.to_csv(day_file_save_path_har_intensity, index=False)
                if df_participant_har_activity.shape[0] != 0:
                    df_participant_har_activity.to_csv(day_file_save_path_har_activity, index=False)
                if df_participant_har_posture.shape[0] != 0:
                    df_participant_har_posture.to_csv(day_file_save_path_har_posture, index=False)


if __name__ == "__main__":
    microT_root_path = r"E:\data\wocket\Wockets-win32-x64\resources\app\src\srv\MICROT"
    intermediate_file_save_path = r"C:\Users\jixin\Desktop\temp"
    p_id_list = ["aditya4_internal@timestudy_com"]
    date_start = "2020-01-01"
    date_end = "2020-07-01"

    pre_process(microT_root_path, intermediate_file_save_path, p_id_list, date_start)
