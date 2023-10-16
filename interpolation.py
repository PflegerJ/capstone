import statistics


def interpolate_point(new_time, t1, t2, y1, y2):
    m = (y2 - y1) / (t2 - t1)
    return y1 + ((new_time - t1) *  m)

def interpolate(dps, hps, dtps, fight_dur, cut_off_time, step_size):
    steps = cut_off_time / step_size
    time_step = fight_dur / 241
    dps_interpolated_data = []
    hps_interpolated_data = []
    dtps_interpolated_data = []
    data_index_min = 0
    data_index_max = 1
    interpolated_data_index = 1
    new_time = interpolated_data_index * step_size
    while cut_off_time >= new_time and data_index_max < 241: #(data_index_min * time_step):
       
        dps_values = []
        hps_values = []
        dtps_values = []
        t1 = data_index_min * time_step
        t2 = data_index_max * time_step
        old_time = new_time
        
        dps_values.append(dps[data_index_min])
        hps_values.append(hps[data_index_min])
        dtps_values.append(dtps[data_index_min])
        if t2 < new_time:
            dps_values.append(dps[data_index_max])
            hps_values.append(hps[data_index_max])
            dtps_values.append(dtps[data_index_max])
            data_index_max = data_index_max + 1

        elif t1 < new_time and new_time < t2:
            if data_index_min + 1 == data_index_max:
                dps_new_value = interpolate_point(new_time, t1, t2, dps[data_index_min], dps[data_index_max])
                hps_new_value = interpolate_point(new_time, t1, t2, hps[data_index_min], hps[data_index_max])
                dtps_new_value = interpolate_point(new_time, t1, t2, dtps[data_index_min], dtps[data_index_max])
                #print("lower: ", dps[data_index_min], " high: ", dps[data_index_max], " new value: ", dps_new_value)


            else:
                dps_new_value = statistics.mean(dps_values)
                hps_new_value = statistics.mean(hps_values)
                dtps_new_value = statistics.mean(dtps_values)
                #print("values: ", dps_values, "new value: ", dps_new_value)
            
            dps_interpolated_data.append(dps_new_value)
            hps_interpolated_data.append(hps_new_value)
            dtps_interpolated_data.append(dtps_new_value)
            data_index_min = data_index_max
            data_index_max = data_index_max + 1
            interpolated_data_index = interpolated_data_index + 1
            new_time = interpolated_data_index * step_size
        elif t1 > new_time:
            data_index_max = data_index_min
            data_index_min = data_index_min - 1
        elif t1 == new_time:
            dps_interpolated_data.append(dps[data_index_min])
            hps_interpolated_data.append(hps[data_index_min])
            dtps_interpolated_data.append(dtps[data_index_min])
            data_index_min = data_index_min + 1
            data_index_max = data_index_max + 1
            interpolated_data_index = interpolated_data_index + 1
            new_time = interpolated_data_index * step_size
        elif t2 == new_time:
            dps_interpolated_data.append(dps[data_index_max])
            hps_interpolated_data.append(hps[data_index_max])
            dtps_interpolated_data.append(dtps[data_index_max])
            data_index_min = data_index_max
            data_index_max = data_index_max + 1
            interpolated_data_index = interpolated_data_index + 1
            new_time = interpolated_data_index * step_size

        
        #print("min: ", data_index_min, " max: ", data_index_max, " t1: ", t1, " t2: ", t2, " new_time: ", old_time, " value count: ", len(dps_interpolated_data) )
        #print("===========================")
    if data_index_max >= 241:
        dps_average_value = statistics.mean(dps_values)
        hps_average_value = statistics.mean(hps_values)
        dtps_average_value = statistics.mean(dtps_values)
        dps_interpolated_data.append(dps_average_value)
        hps_interpolated_data.append(hps_average_value)
        dtps_interpolated_data.append(dtps_average_value)

    while len(dps_interpolated_data) < steps:
        dps_interpolated_data.append(0)
        hps_interpolated_data.append(0)
        dtps_interpolated_data.append(0)
    
    return dps_interpolated_data, hps_interpolated_data, dtps_interpolated_data
        
