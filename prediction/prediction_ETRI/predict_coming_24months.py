import pandas as pd
import numpy as np
import prediction.prediction_ETRI.predict_common as predict_common
from API.api_helper.user_directory import folder_path

# # # # # # # # # # # # # # # # # # # # # # # #
#              F u n c t i o n s              #
# # # # # # # # # # # # # # # # # # # # # # # #

from calendar import monthrange


def write_prediction_to_file(daily_output_file, target_year, tmon, daily_pred_insu_list, category_list):
    '''
    This function writes daily prediction result into file.
    Args:
        daily_output_file: string, output file name
        target_year: int, target year of prediction
        tmon: int, target month of prediction
        daily_pred_insu_list: np.array, daily predicted insu
        category_list: list, a list of categories of prediction target
    '''

    # open the file to write the results
    f = open(daily_output_file, 'a+')

    # calculate the number of days of target_year.target_month
    mon_days = monthrange(target_year, tmon)[1]

    # for each day
    for tday in range(1, mon_days + 1):
        data = "%d %d %d " % (target_year, tmon, tday)

        pred_insu_sum = 0
        # prediction result of each category
        for tidx in range(len(category_list)):
            data += "%.1f " % (daily_pred_insu_list[tidx][tday - 1])
            pred_insu_sum += daily_pred_insu_list[tidx][tday - 1]

        data += "%.1f\n" % (pred_insu_sum)

        # write the result to the file
        f.write(data)

    f.close()


def write_prediction_to_tmp_file(area, target_year, tmon, daily_pred_insu_list, daily_pred_sub_list, category_list):
    '''
    This function writes daily prediction result into file.
    Args:
        daily_output_file: string, output file name
        target_year: int, target year of prediction
        tmon: int, target month of prediction
        daily_pred_insu_list: np.array, daily predicted insu
        daily_pred_sub_list: np.array, daily predicted sub num
        category_list: list, a list of categories of prediction target
    '''

    # open a file to write prediction result. the predicted results will be used for futher predictions.
    if not os.path.isfile(folder_path + 'data/tmp_for_pred/insu/%s_insu_%d' % (area, target_year)):
        insu_f = open(folder_path + 'data/tmp_for_pred/insu/%s_insu_%d' % (area, target_year), 'w')
        data = "year month date "
        for tidx in range(len(category_list)):
            data += "insu_%s " % (category_list[tidx])
        data += "insu_sum\n"
        insu_f.write(data)
    else:
        insu_f = open(folder_path + 'data/tmp_for_pred/insu/%s_insu_%d' % (area, target_year), 'a')

    if not os.path.isfile(folder_path + 'data/tmp_for_pred/sub/%s_sub_%d' % (area, target_year)):
        sub_f = open(folder_path + 'data/tmp_for_pred/sub/%s_sub_%d' % (area, target_year), 'w')
        data = "year month date "
        for tidx in range(len(category_list)):
            data += "sub_%s " % (category_list[tidx])
        data += "\n"
        sub_f.write(data)
    else:
        sub_f = open(folder_path + 'data/tmp_for_pred/sub/%s_sub_%d' % (area, target_year), 'a')

    # calculate the number of days of target_year.target_month
    mon_days = monthrange(target_year, tmon)[1]

    # for each day
    for tday in range(1, mon_days + 1):

        insu_data = "%d %d %d " % (target_year, tmon, tday)
        sub_data = "%d %d %d " % (target_year, tmon, tday)

        pred_insu_sum = 0
        # prediction result of each category
        for tidx in range(len(category_list)):
            insu_data += "%.1f " % (daily_pred_insu_list[tidx][tday - 1])
            pred_insu_sum += daily_pred_insu_list[tidx][tday - 1]
            sub_data += "%d " % (daily_pred_sub_list[tidx][tday - 1])

        insu_data += "%.1f\n" % (pred_insu_sum)
        sub_data += "\n"

        insu_f.write(insu_data)
        sub_f.write(sub_data)

    insu_f.close()
    sub_f.close()


import os


def predict_temp(area, target_year, target_mon):
    '''
    This function estimates temperature of target_year.target_month by averaging the temperature of the same date of recent 4 years.
    Args:
        area: string, target area of prediction
        target_year: int, the target year of prediction
        target_mon: int, the target month of prediction
    Returns:
        prev_avg_temp: np.array, predicted daily temperature of target_year.target_mon
    '''

    # examine the existence of a target file to write prediction result. the prediction results will be used for further prediction.
    need_to_write = 0
    # - the target file does not exist
    if not os.path.isfile(folder_path + 'data/tmp_for_pred/temperature/%s_temp_%d' % (area, target_year)):
        tmp_f = open(folder_path + 'data/tmp_for_pred/temperature/%s_temp_%d' % (area, target_year), 'w')
        tmp_f.write("year month date avgTemp maxTemp minTemp\n")
        need_to_write = 1
    # - the target file exists
    else:
        temp_tmp = pd.read_csv(folder_path + 'data/tmp_for_pred/temperature/%s_temp_%d' % (area, target_year),
                               delim_whitespace=True)
        same_month = temp_tmp[temp_tmp['month'] == target_mon]

        # -- the prediction results of target_year.target_mon are already written.
        # -- note that this function can be called several times for multiple categoriesy for the same target_year.target_mon
        # -- just need to return the written results
        if len(same_month) > 0:
            return np.reshape(np.array(same_month['avgTemp']), (-1, 1))
        # -- need to conduct prediction
        else:
            need_to_write = 1
            tmp_f = open(folder_path + 'data/tmp_for_pred/temperature/%s_temp_%d' % (area, target_year), 'a')

    if need_to_write == 1:

        # load the temperature data of recent 4 years
        for tyear in range(target_year - 4, target_year):
            # read the temp data
            temp_data_tmp = pd.read_csv(folder_path + 'data/tmp_for_pred/temperature/%s_temp_%d' % (area, tyear),
                                        delim_whitespace=True)
            # merge the read data into one data for easy processing
            if tyear == target_year - 4:
                temp_data = temp_data_tmp
            else:
                temp_data = temp_data.append(temp_data_tmp)

        # get the number of days of target_year.target_month
        mon_days = monthrange(target_year, target_mon)[1]

        # for each day of target_year.target_month
        prev_avg_temp = []
        for tday in range(1, mon_days + 1):
            if target_mon == 2 and tday == 29:
                tday = 28
            prev_avg_temp_list = []

            # extract avgTemp from the data of recent 4 years
            for tyear in range(target_year - 4, target_year):
                prev_same_year = temp_data[temp_data['year'] == tyear]
                prev_same_month = prev_same_year[prev_same_year['month'] == target_mon]
                target_day = prev_same_month[prev_same_month['date'] == tday]

                avg_temp = target_day['avgTemp'].values[0]
                prev_avg_temp_list.append(avg_temp)

            # averaging 'avgTemp' of recent 4 years
            avg_over_years = np.mean(prev_avg_temp_list)
            prev_avg_temp.append([avg_over_years])

            tmp_f.write("%d %02d %02d %.2f %.2f %.2f\n" % (
            target_year, target_mon, tday, avg_over_years, avg_over_years, avg_over_years))

        tmp_f.close()

        # return predicted or true avgTemp
        return np.array(prev_avg_temp)


def predict_sub_num(area, cat, target_year, target_mon):
    '''
    This function estimates the number of subscribers of specified category of target_year.target_month by conducting curve fitting.
    Args:
        area: string, target area of prediction
        cat: string, target category of prediction
        target_year: int, the target year of prediction
        target_mon: int, the target month of prediction
    Returns:
        num_of_sub: float, the predicted number of subscribers
    '''

    # load the insu and sub data of recent 4 years
    for tyear in range(target_year - 4, target_year):
        # read the insu and sub ddata
        sub_data_tmp = pd.read_csv(folder_path + 'data/tmp_for_pred/sub/%s_sub_%d' % (area, tyear),
                                   delim_whitespace=True)
        # merge the read data into one data for easy processing
        if tyear == target_year - 4:
            sub_data = sub_data_tmp
        else:
            sub_data = sub_data.append(sub_data_tmp)

    # extract sub data from the data of recent 4 years
    sub_num_list = []
    for tyear in range(target_year - 4, target_year):
        prev_same_year = sub_data[sub_data['year'] == tyear]
        prev_same_month = prev_same_year[prev_same_year['month'] == target_mon]
        target_day = prev_same_month[prev_same_month['date'] == 1]
        sub_num_list.append(target_day['sub_%s' % (cat)].values[0])

    # if all elements of sub_num_list are same, curve fitting is useless. In this case, return the data itself.
    if all(x == sub_num_list[0] for x in sub_num_list):
        return sub_num_list[0]
    # otherwise, conduct curve fitting.
    else:
        popt_a, popt_b = predict_common.curve_fitting(range(1, len(sub_num_list) + 1), sub_num_list)
        return popt_a * (len(sub_num_list) + 1) + popt_b


def predict_avg_insu_by_temp_regression(area, cat, target_year, target_mon):
    '''
    This function predicts avg insu per subscriber of a specified category through temp-based regression.
    Args:
        area: string, target area of prediction
        cat: string, target category of prediction
        target_year: int, the target year of prediction
        target_mon: int, the target month of prediction
    Returns:
        pred_avg_insu: np.array, the predicted daily average insu per subscriber
    '''
    print("target_mon: ", target_mon)

    # group three months that typically show similar weather for better curve fitting
    if target_mon in [12, 1, 2]:
        mon_list = [12, 1, 2]
    elif target_mon in [3, 4, 5]:
        mon_list = [3, 4, 5]
    elif target_mon in [6, 7, 8]:
        mon_list = [6, 7, 8]
    elif target_mon in [9, 10, 11]:
        mon_list = [9, 10, 11]

    train_data = []
    train_label = []

    # use the data of recent 4 years for curve fitting
    for tyear in range(target_year - 4, target_year):

        # read the temperature data
        temp_data = pd.read_csv(folder_path + 'data/tmp_for_pred/temperature/%s_temp_%d' % (area, tyear),
                                delim_whitespace=True)

        # print(folder_path + 'data/tmp_for_pred/temperature/%s_temp_%d' % (area, tyear))

        # read the insu data
        insu_data = pd.read_csv(folder_path + 'data/tmp_for_pred/insu/%s_insu_%d' % (area, tyear),
                                delim_whitespace=True)

        # read the subscriber data
        sub_data = pd.read_csv(folder_path + 'data/tmp_for_pred/sub/%s_sub_%d' % (area, tyear), delim_whitespace=True)

        # read the date data
        date_data = pd.read_csv(folder_path + 'data/tmp_for_pred/date/date_info_Y%d' % (tyear), delim_whitespace=True)

        # extract data realted to mon_list
        for tmon in mon_list:

            # extract temperature data of the target month
            temp_data_month = temp_data[temp_data['month'] == tmon]

            # extract date data of the target month
            date_data_month = date_data[date_data['month'] == tmon]

            # extract insu data of the target month
            insu_data_month = insu_data[insu_data['month'] == tmon]

            # extract sub data of the target month
            sub_data_month = sub_data[sub_data['month'] == tmon]

            # calculate the number of days of tyear.tmon
            mon_days = monthrange(tyear, tmon)[1]

            # for each day of tyear.tmon
            for tday in range(1, mon_days + 1):
                # prepare train DATA
                # - get 'avgTemp'
                temp_data_day = temp_data_month[temp_data_month['date'] == tday]
                # print("temp_data_day: ",temp_data_day)
                avg_temp = temp_data_day['avgTemp'].values[0]
                # print("avg_temp: ", avg_temp)
                # - get 'day' and 'holiday'
                date_data_day = date_data_month[date_data_month['date'] == tday]
                dayCode = date_data_day['day'].values[0]
                holidayCode = date_data_day['holiday'].values[0]
                #
                train_data.append([avg_temp, dayCode, holidayCode])

                # prepare train LABEL
                # - calculate the average insu per sub
                insu_data_day = insu_data_month[insu_data_month['date'] == tday]
                insu_target = insu_data_day['insu_%s' % (cat)].values[0]
                #
                sub_data_day = sub_data_month[sub_data_month['date'] == tday]
                sub_target = sub_data_day['sub_%s' % (cat)].values[0]
                #
                train_label.append(insu_target / sub_target)

    # train a boosting model
    trained_model = predict_common.train_boosting_model(train_data, train_label)

    # get the predicted temperature of the target_year.target_mon
    prev_avg_temp = predict_temp(area, target_year, target_mon)

    # get the date info of target_year.target_mon
    date_data = pd.read_csv(folder_path + 'data/tmp_for_pred/date/date_info_Y%d' % (target_year), delim_whitespace=True)

    # extract date data of the target month
    date_data_month = date_data[date_data['month'] == target_mon]
    #
    # calculate the number of days of tyear.tmon
    mon_days = monthrange(target_year, target_mon)[1]
    #
    # for each day of tyear.tmon
    target_date_list = []
    for tday in range(1, mon_days + 1):
        date_data_day = date_data_month[date_data_month['date'] == tday]
        dayCode = date_data_day['day'].values[0]
        holidayCode = date_data_day['holiday'].values[0]
        target_date_list.append([dayCode, holidayCode])

    # generate test data
    test_data = np.hstack([prev_avg_temp, target_date_list])

    # conduct prediction
    pred_avg_insu = trained_model.predict(test_data)
    # print("final-------")

    return pred_avg_insu


def predict_avg_insu_by_averaging(area, cat, target_year, target_mon):
    '''
    This function predicts avg insu per sub by averaging data of recent 3 years
    Args:
        area: string, target area of prediction
        cat: string, target category of prediction
        target_year: int, the target year of prediction
        target_mon: int, the target month of prediction
    Returns:
        pred_avg_insu: np.array, the predicted daily average insu per subscriber
    '''

    # load the insu and sub data of recent 3 years
    for tyear in range(target_year - 3, target_year):

        # read the insu data
        insu_data_tmp = pd.read_csv(folder_path + 'data/tmp_for_pred/insu/%s_insu_%d' % (area, tyear),
                                    delim_whitespace=True)
        # - merge the read data into one data for easy processing
        if tyear == target_year - 3:
            insu_data = insu_data_tmp
        else:
            insu_data = insu_data.append(insu_data_tmp)

        # read the sub data
        sub_data_tmp = pd.read_csv(folder_path + 'data/tmp_for_pred/sub/%s_sub_%d' % (area, tyear),
                                   delim_whitespace=True)
        # - merge the read data into one data for easy processing
        if tyear == target_year - 3:
            sub_data = sub_data_tmp
        else:
            sub_data = sub_data.append(sub_data_tmp)

        # read the date data
        date_data_tmp = pd.read_csv(folder_path + 'data/tmp_for_pred/date/date_info_Y%d' % (tyear),
                                    delim_whitespace=True)
        # - merge the read data into one data for easy processing
        if tyear == target_year - 3:
            date_data = date_data_tmp
        else:
            date_data = date_data.append(date_data_tmp)

    # calculate the number of days of target_year.target_mon
    mon_days = monthrange(target_year, target_mon)[1]

    # read the date data of the target_year
    target_date_data = pd.read_csv(folder_path + 'data/tmp_for_pred/date/date_info_Y%d' % (target_year),
                                   delim_whitespace=True)

    # for each day of target_year.target_mmon
    prev_avg_insu = []
    for tday in range(1, mon_days + 1):

        same_month = target_date_data[target_date_data['month'] == target_mon]
        target_day = same_month[same_month['date'] == tday]
        c_holiday = target_day['holiday'].values[0]
        c_day = target_day['day'].values[0]

        # handle special case (i.e., 29 Feb)
        if target_mon == 2 and tday == 29:
            tday = 28

        prev_avg_insu_target = []

        # for recent 3 years
        for tyear in range(target_year - 3, target_year):

            # Fine relevant dates
            # - Find the index of the same date in previous years
            same_year = date_data[date_data['year'] == tyear]
            same_month = same_year[same_year['month'] == target_mon]
            same_date = same_month[same_month['date'] == tday]
            date_index = same_date.index.values
            #
            start_index = int(max(0, date_index - 10))
            end_index = int(min(len(date_data), date_index + 10))
            relevant_date_range = date_data.iloc[start_index:end_index]
            # -- holiday or not
            if c_holiday == 1:
                relevant_data = relevant_date_range[relevant_date_range['holiday'] == c_holiday]
                # -- some special holiday (e.g., election) does not exit in all years. In this case, we need to extract the data using 'day' code
                if len(relevant_data) == 0:
                    relevant_data = relevant_date_range[relevant_date_range['day'] == c_day]
            else:
                relevant_data = relevant_date_range[relevant_date_range['day'] == c_day]

            prev_avg_insu_target_tmp = []
            # Extract insu_per_sub of the relevant dates
            for index, row in relevant_data.iterrows():
                t_mon = row['month']
                t_date = row['date']

                # handle special case (i.e., 29 Feb)
                if t_mon == 2 and t_date == 29:
                    t_date = 28

                prev_same_year = insu_data[insu_data['year'] == tyear]
                prev_same_month = prev_same_year[prev_same_year['month'] == t_mon]
                target_day = prev_same_month[prev_same_month['date'] == t_date]
                insu_target = target_day['insu_%s' % (cat)].values[0]

                prev_same_year = sub_data[sub_data['year'] == tyear]
                prev_same_month = prev_same_year[prev_same_year['month'] == t_mon]
                target_day = prev_same_month[prev_same_month['date'] == t_date]
                sub_target = target_day['sub_%s' % (cat)].values[0]

                # get the average insu per sub
                prev_avg_insu_target_tmp.append(insu_target / sub_target)
            prev_avg_insu_target.append(np.mean(prev_avg_insu_target_tmp))

        # delete useless data
        prev_avg_insu_target = np.array(prev_avg_insu_target)
        prev_avg_insu_target = prev_avg_insu_target[prev_avg_insu_target != 0.]

        # if 'prev_avg_insu_target' includes data, use the average
        if len(prev_avg_insu_target) > 0:
            prev_avg_insu.append(np.average(prev_avg_insu_target))
        # otherwise, use 0
        else:
            prev_avg_insu.append(0)

    return np.array(prev_avg_insu)


def predict_avg_insu_by_curve_fitting(area, cat, target_year, target_mon):
    '''
    This function predicts avg insu per sub by conducting curve fitting with data of recent 3 years
    Args:
        area: string, target area of prediction
        cat: string, target category of prediction
        target_year: int, the target year of prediction
        target_mon: int, the target month of prediction
    Returns:
        pred_avg_insu: np.array, the predicted daily average insu per subscriber
    '''
    # read the insu and sub data of recent 3 years
    for tyear in range(target_year - 3, target_year):

        # load the insu data
        insu_data_tmp = pd.read_csv(folder_path + 'data/tmp_for_pred/insu/%s_insu_%d' % (area, tyear),
                                    delim_whitespace=True)
        # - merge the read data into one data for easy handling
        if tyear == target_year - 3:
            insu_data = insu_data_tmp
        else:
            insu_data = insu_data.append(insu_data_tmp)

        # load the sub data
        sub_data_tmp = pd.read_csv(folder_path + 'data/tmp_for_pred/sub/%s_sub_%d' % (area, tyear),
                                   delim_whitespace=True)
        # - merge the read data into one data for easy handling
        if tyear == target_year - 3:
            sub_data = sub_data_tmp
        else:
            sub_data = sub_data.append(sub_data_tmp)

        # date data
        date_data_tmp = pd.read_csv(folder_path + 'data/tmp_for_pred/date/date_info_Y%d' % (tyear),
                                    delim_whitespace=True)
        # - merge the read data into one data for easy handling
        if tyear == target_year - 3:
            date_data = date_data_tmp
        else:
            date_data = date_data.append(date_data_tmp)

    # calculate the number of days of target_year.target_mon
    mon_days = monthrange(target_year, target_mon)[1]

    # read the date data of the target_year
    target_date_data = pd.read_csv(folder_path + 'data/tmp_for_pred/date/date_info_Y%d' % (target_year),
                                   delim_whitespace=True)

    # for each day of target_year.target_mmon
    prev_avg_insu = []
    for tday in range(1, mon_days + 1):

        same_month = target_date_data[target_date_data['month'] == target_mon]
        target_day = same_month[same_month['date'] == tday]
        c_holiday = target_day['holiday'].values[0]
        c_day = target_day['day'].values[0]

        # handle special case (i.e., 29 Feb)
        if target_mon == 2 and tday == 29:
            tday = 28

        prev_avg_insu_target = []

        # for recent 3 years
        for tyear in range(target_year - 3, target_year):

            # Fine relevant dates
            # - Find the index of the same date in previous years
            same_year = date_data[date_data['year'] == tyear]
            same_month = same_year[same_year['month'] == target_mon]
            same_date = same_month[same_month['date'] == tday]
            date_index = same_date.index.values
            #
            start_index = int(max(0, date_index - 10))
            end_index = int(min(len(date_data), date_index + 10))
            relevant_date_range = date_data.iloc[start_index:end_index]
            # -- holiday or not
            if c_holiday == 1:
                relevant_data = relevant_date_range[relevant_date_range['holiday'] == c_holiday]
                # -- some special holiday (e.g., election) does not exit in all years. In this case, we need to extract the data using 'day' code
                if len(relevant_data) == 0:
                    relevant_data = relevant_date_range[relevant_date_range['day'] == c_day]
            else:
                relevant_data = relevant_date_range[relevant_date_range['day'] == c_day]

            prev_avg_insu_target_tmp = []
            # Extract insu_per_sub of the relevant dates
            for index, row in relevant_data.iterrows():
                t_mon = row['month']
                t_date = row['date']

                # handle special case (i.e., 29 Feb)
                if t_mon == 2 and t_date == 29:
                    t_date = 28

                prev_same_year = insu_data[insu_data['year'] == tyear]
                prev_same_month = prev_same_year[prev_same_year['month'] == t_mon]
                target_day = prev_same_month[prev_same_month['date'] == t_date]
                insu_target = target_day['insu_%s' % (cat)].values[0]

                prev_same_year = sub_data[sub_data['year'] == tyear]
                prev_same_month = prev_same_year[prev_same_year['month'] == t_mon]
                target_day = prev_same_month[prev_same_month['date'] == t_date]
                sub_target = target_day['sub_%s' % (cat)].values[0]

                # get the average insu per sub
                prev_avg_insu_target_tmp.append(insu_target / sub_target)
            prev_avg_insu_target.append(np.mean(prev_avg_insu_target_tmp))

        # delete useless data
        prev_avg_insu_target = np.array(prev_avg_insu_target)
        prev_avg_insu_target = np.array(prev_avg_insu_target[prev_avg_insu_target != 0.])

        # if 'prev_avg_insu_target' includes more than one data, conduct curve fitting
        if len(prev_avg_insu_target) > 1:
            popt_a, popt_b = predict_common.curve_fitting(range(1, len(prev_avg_insu_target) + 1), prev_avg_insu_target)
            prev_avg_insu.append(popt_a * (len(prev_avg_insu_target) + 1) + popt_b)
        # if 'prev_avg_insu_target' contains only one data, use that data
        elif len(prev_avg_insu_target) == 1:
            prev_avg_insu.append(prev_avg_insu_target[0])
        # otherwise, use 0
        else:
            prev_avg_insu.append(0)

    return np.array(prev_avg_insu)


def predict_avg_insu(area, cat, target_year, target_mon):
    '''
    This function estimates the average insu per subscriber of specified category of target_year.target_month through temmp-based linear regression.
    This function applies different prediction methods for target categories.
    Args:
        area: string, target area of prediction
        cat: string, target category of prediction
        target_year: int, the target year of prediction
        target_mon: int, the target month of prediction
    Returns:
        pred_avg_insu: np.array, the predicted daily average insu per subscriber
    '''

    # temp-based linear regression (i.e., input: temp, output: avg insu per sub)
    if cat in ['house', 'houseJHeating', 'salesTwo', 'industry']:

        return predict_avg_insu_by_temp_regression(area, cat, target_year, target_mon)

    # averaging data of recent 3 years
    elif cat in ['houseCooking', 'salesOne', 'bizHeating', 'bizCooling', 'heatFacility', 'heatCombined']:

        return predict_avg_insu_by_averaging(area, cat, target_year, target_mon)

    # curve fitting. 'CNG'
    else:
        return predict_avg_insu_by_curve_fitting(area, cat, target_year, target_mon)


def estimate_insu_per_cat(area, cat, target_year, target_month):
    '''
    This function estimates insu per category for target_year.target_month.
    Args:
        area: string, target area of prediction
        cat: string, a category to be predicted
        target_year: int, target year of prediction
        target_month: int, target month of prediction
    Returns:
        daily_cat_pred_insu: list, a list of daily predictions for target_year.target_month
        true_insu_list: list, a list of daliy true insu data for target_year.target_month
    '''

    # Estimate daily insu per category
    # - get the predicted avg insu per sub
    pred_avg_insu = predict_avg_insu(area, cat, target_year, target_month)

    # - get the predicted subscriber number
    pred_sub_num = math.ceil(predict_sub_num(area, cat, target_year, target_month))

    # - estimate insu volume of target month. 'daily_cat_pred_insu' contains daily predicted insu
    daily_cat_pred_insu = pred_avg_insu * pred_sub_num

    return daily_cat_pred_insu, pred_sub_num * np.ones(len(daily_cat_pred_insu))


import math
import datetime


def conduct_prediction(area, start_year, start_month, month_range, start_date):
    '''
    This function conducts prediction for coming 24 months.
    Args:
        area: string, target area of prediction
        start_year: int, start year of target prediction
        start_month: int, start month of target prediction
        month_range: int, the number of months to be predicted (e.g., prediction target => FROM start_year.start_month TO start_year.start_month + month_range)
    '''

    if not os.path.isdir(folder_path + 'result/%d' % (start_date)):
        os.mkdir(folder_path + 'result/%d' % (start_date))

    # step 1: prepare the required things
    # - a list of categories relevant to target area
    category = predict_common.get_category(area)

    # - prepare the output file for daily prediction
    daily_output_file = folder_path + 'result/%d/coming_%s_%d_%d_%d_daily' % (
    start_date, area, start_year, start_month, month_range)
    # daily_f = open(daily_output_file, 'a+')
    daily_f = open(daily_output_file, 'w')
    data = "year month date "
    for tidx in range(len(category)):
        data += "%s_pred " % (category[tidx])
    data += "pred_sum\n"
    daily_f.write(data)
    daily_f.close()

    # - prepare the output file for monthly prediction
    monthly_output_file = folder_path + 'result/%d/coming_%s_%d_%d_%d_monthly' % (
    start_date, area, start_year, start_month, month_range)
    # monthly_f = open(monthly_output_file, 'a+')
    monthly_f = open(monthly_output_file, 'w')
    data = "year month "
    for tidx in range(len(category)):
        data += "%s_pred " % (category[tidx])
    data += "pred_sum\n"
    monthly_f.write(data)

    # step 2: conduct predictions
    # - for each month from the start_year.start_month to start_year.start_month + month_range
    current = datetime.date(start_year, start_month, 1)
    current = current - datetime.timedelta(days=monthrange(current.year, current.month)[1])
    for ridx in range(1, month_range + 1):
        current = current + datetime.timedelta(days=monthrange(current.year, current.month)[1])

        print("curent", current)
        print("current.yaer: ", current.year)

        output_data = "%d %d " % (current.year, current.month)
        monthly_pred_sum = 0
        daily_pred_insu_list = []  # a list of predicted insu of all categories of a targer month. used for writing result into a file.
        daily_pred_sub_list = []  # a list of predicted number of subscribers of all categories of a targer month. used for writing result into a file.

        # for each category
        for cat in category:
            # estimate daily insu and sub per category
            # print('---------1----------')
            # print("cat: ",cat)
            est_insu, est_sub = estimate_insu_per_cat(area, cat, current.year, current.month)

            monthly_pred_sum += np.sum(est_insu)
            daily_pred_insu_list.append(est_insu)
            daily_pred_sub_list.append(est_sub)

            output_data += "%.1f " % (np.sum(est_insu))

        output_data += "%.1f\n" % (monthly_pred_sum)

        print(output_data, end='')

        # write monthly prediction results into a file
        monthly_f.write(output_data)
        # print('---------2----------')

        # write daily prediction results into a file
        write_prediction_to_file(daily_output_file, current.year, current.month, daily_pred_insu_list, category)

        # print('---------tmp_file_w-----------')

        # write daily prediction results into a file to use them for further predictions
        write_prediction_to_tmp_file(area, current.year, current.month, daily_pred_insu_list, daily_pred_sub_list,
                                     category)

    monthly_f.close()


# /home/lee/PredictionServer/prediction/prediction_ETRI/result/coming_naju_2019_1_24_daily
# /home/lee/PredectionServer/prediction/prediction_ETRI/result/coming_naju_2019_1_24_daily'
# conduct_prediction('naju', 2020, 12, 24, 20191101)
