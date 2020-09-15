#%%
import os
import numpy as np
import pandas as pd
# import re
from datetime import datetime
import concurrent.futures
# edit FOLDER_NAME to point to actual location of your files

FOLDER_NAME = 'C:\Projects\swimdata-sample'

def read_files(file):
    """
    actual parser of text in file if data in result in not accurate adjast columns mapping here
    :param :file name
    :return :list of records in file organazied my field name
    """

    file_data = []
    filepath = os.path.join(FOLDER_NAME, file)
    # print(filepath)

    with open(filepath, "rb") as r:
        for i,line in enumerate(r):
            if i > 3:
                file_record = {}
                if line[0:3] == b'D01':
                    line = line[0:142].decode('iso-8859-1')
                    # file_record['event_name'] = 'D01'
                    # file_record['column2'] = line[3:11].strip()
                    file_record['name'] = line[11:39].strip()
                    file_record['ussnum'] = line[39:55]
                    file_record['dob'] = line[55:63]
                    # parse lataer into age sex and comp type
                    age_p = line[63:67]
                    file_record['age'] = age_p[0:2]
                    file_record['sex_code'] = age_p[-2]
                    file_record['event_code'] = age_p[-1]


                    file_record['event_dist'] = line[67:71]
                    file_record['event_type'] = line[71:72]

                    file_record['event_number'] = line[73:75]
                    file_record['age_group'] = line[76:80]
                    file_record['event_date'] = line[80:88]
                    # parse entry time
                    file_record['entry_time'] = line[89:97]

                    # if entry_time.endswith('NT'):
                    #     file_record['entry_time'] = ''
                    #     file_record['course'] = 'NT'
                    # else:
                    #     file_record['entry_time'] = entry_time[0:-1]
                    #     file_record['course'] = entry_time[-1]

                    file_record['pre_end_time'] = line[97:106]
                    file_record['result_time'] = line[106:124].strip()

                    # file_record['preliminary_lane'] = line[126:128]
                    # file_record['preliminary_heat'] = line[124:126]
                    # file_record['final_heat'] = line[128:130]
                    # file_record['final_lane'] = line[130:132]
                    # file_record['finished_preliminary'] = line[133:135]
                    # file_record['finished_final'] = line[136:138]
                    # file_record['point'] = line[142:].strip()

                    file_data.append(file_record)
    return file_data

def get_file_names(path):
    files = [x for x in os.listdir(path) if x.endswith('.cl2')]
    return files

def string_to_seconds(time_str):

    secons_ext = tuple(['DQ', 'NS', 'SCR', 'NSY', 'SC', 'DNF', 'DN'])
    default_time = '00:00:00'
    time_str = time_str.strip()

    if time_str == np.nan:
        return np.nan

    if len(time_str) == 0:
        return np.nan

    if time_str[-3:].isalpha():
        return np.nan

    if time_str[-1].isalpha():
        time_str = time_str[:-1]

    # time_str = time_str.replace('Y', '')

    return_seconds = 0

    time_items = time_str.strip().split('.')
    r_seconds = default_time[:8 - len(time_items[0])] + time_items[0]

    try:
        h, m, s = r_seconds.split(':')
        return_seconds = int(h) * 3600 + int(m) * 60 + int(s)
    except:
        # print('----------------')
        print('|{}| -- error parsing time'.format(time_str))
        return np.nan


    if len(time_items) == 2:
        return_seconds += float('0.' + time_items[1])

    return return_seconds

def best_time(x):

    t1 = string_to_seconds(x[0])
    t2 = string_to_seconds(x[1])

    course = np.nan
    min_time = np.fmin(t1, t2)

    # last byte of the time represents the course description
    #  take the value of the course description from best time or initialize it with nan

    if min_time == t1:
        course = x[0][-1]

    if min_time == t2:
        course = x[1][-1]

    return min_time, course

if __name__ == '__main__':
    start_time = datetime.now()

    files = get_file_names(FOLDER_NAME)
    # df = pd.DataFrame()
    result_data = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        result = [executor.submit(read_files, file) for file in files]
    #
    try:
        for f in concurrent.futures.as_completed(result):
            for r in f.result():
                result_data.append(r)
    except:
        print('errr')

    df = pd.DataFrame(result_data)

    print('finished reading')

#%%
    # Calculate age in month at the event
    df['age_at_event'] = pd.to_datetime(df['event_date'], errors='coerce', format="%m%d%Y") \
                         - pd.to_datetime(df['dob'], errors='coerce', format="%m%d%Y")
    df['age_at_event'] = df['age_at_event'] / np.timedelta64(1, "Y")
    df['age_at_event'] = df['age_at_event'].astype('float').round(2)

    # dob month
    df['dob'] = pd.to_datetime(df['dob'], errors='coerce', format="%m%d%Y")
    df['event_mm'] = df['event_date'].map(lambda x: x[:-6 or None] + x[-4:] ).fillna(0)

    # Format result time to remove alphanumerics and convert to seconds
    # df['result_seconds'] = df['result_time'].str.slice(0, -1).apply(string_to_seconds)
    df['result'], df['course'] = zip(*df[['pre_end_time', 'result_time']].apply(best_time, axis=1))

    # Group by age, sex_code, event_dist, event_type and calculate ranking based on final result in seconds

    df['ak'] = df.groupby(['course', 'age', 'sex_code', 'event_dist', 'event_type'])['result']\
        .rank(method='dense',ascending=True).fillna(0).astype(int)
    df['aj'] = df.groupby(['event_mm', 'age', 'sex_code', 'event_dist', 'event_type'])['result']\
        .rank(method='dense', ascending=True).fillna(0).astype(int)

    # Write final csv file
    df = df.sort_values(by=['course','age', 'sex_code', 'event_dist', 'event_type', 'ak'],
                        ascending=[True, True, True, True, True, False])

    df.to_csv('result.csv',index=False, header=True)
    # futs = ddf.to_csv('result.csv', index=False, single_file = True)

    print("number of rows processed: {}".format(len(df)))
    print("Processed {} files in {} seconds".format(len(files), str(datetime.now() - start_time)))

#%%
    print(df.head(20))
