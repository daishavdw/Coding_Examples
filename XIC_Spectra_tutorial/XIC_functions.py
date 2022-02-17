import pandas as pd
import spectrum_utils.plot as sup
import spectrum_utils.spectrum as sus
import altair as alt
import matplotlib.pyplot as plt

#Searching through all of our data from MS1 scans that have a mz score in a specific range, and then keeping track of the intensity of the scan that found that mz score, along with the time that it was found at.
def get_MS1_values(target_mz, peak_time, data):
    """parameters:
        target_mz: mz that we are looking for
        peak_time: time that we found the mz at
        data is the mz file that we are looking in     
    """
    #dataframe to store our information
    df = pd.DataFrame(columns={'scan', 'time', 'intensity', "mz"})

    tol = 0.1
    mz_min = target_mz - tol
    mz_max = target_mz + tol
    times = data.time[peak_time - 45/60: peak_time + 45/60]

    for spectra in times:
        # checking that we have an MS1 scan
        if spectra['ms level'] == 1:

            # getting the time
            time = (spectra['scanList']['scan'][0].get('scan start time'))

            # get scan number
            scanString = spectra['id']
            startSpot = scanString.find('scan=')
            scanNum = scanString[startSpot + 5:]

            # get intensity and mz
            intensity_array = spectra['intensity array']
            mz_array = spectra["m/z array"]

            # checking through all mz array for anything in our range of mz values
            for x in range(0, len(mz_array)):
                if mz_array[x] > mz_min and mz_array[x] < mz_max:
                    intensity = intensity_array[x]

                    # creating a new row and adding it into the df
                    row = {'scan': scanNum, 'time': time, 'intensity': intensity, 'mz': mz_array[x]}
                    df = df.append(row, ignore_index=True)
    cleaned_df = clean_values(df)

    return cleaned_df


# Many scans are duplicated with lots of the duplicates having an intensity of 0. Here we filter and keep the one with the highest scoring intensity. 
def clean_values(df):
    # sort based on intensity value
    df_slim = df.sort_values('intensity')
    # drop duplicate scans and keep the one with the highest intensity
    df_slim = df_slim.drop_duplicates(subset=["scan"], keep="last")  # keep highest scoring intensity

    # sort on time, easier to read
    df_slim = df_slim.sort_values('time')

    return (df_slim)


# The purpose of this function is to look for MS2s.
#the function take a target_mz and a peak_time and is looking for an ms spectra based off of the precursor information. It will return scan numbers, times, and precursor mz that the ms2 likely came from
def get_MS2_values(target_mz, peak_time, data):
    """parameters:
        target_mz: the mz that we are looking for
        peak_time: the time that we found the mz at
        data: a parse of the mzML file, an object from pyteomics     
    """
    # criteria for returning
    # 0. MS2 spe3ctrum
    # 1. the time frame is within a tolderance of the 'peak_time' parameter
    # 2. the precursor is within a mass tolerance of the target_mz
    to_return = []  # list of tuples (scanNum, time, precursor_mz)

    tol = 0.8  # m/z - this is the isolation window tolerance for an orbi

    # this line below will fulfill criteria 1, all spectra will be within the time window
    times = data.time[peak_time - 45/60: peak_time + 45/60]  # a list of the spectra within a time frame
    
    for spectra in times:
        # checking that we have an MS1 scan
        if spectra['ms level'] != 2:  # criteria 0
            continue

        # get scan number
        scanString = spectra['id']
        startSpot = scanString.find('scan=')
        scanNum = scanString[startSpot + 5:]
        # getting the time
        time = (spectra['scanList']['scan'][0].get('scan start time'))
        
        time_diff = abs(peak_time - time)

        # criteria 2, does the precursor match the input parameter
        precursor = spectra['precursorList']['precursor'][0]  # This data is one precursor only. thus [0]
        precursor_ion = precursor['selectedIonList']['selectedIon'][0]
        precursor_mz = precursor_ion['selected ion m/z']

        if abs(precursor_mz - target_mz) > tol:
            continue

        to_return.append((scanNum, time, precursor_mz, time_diff))

    labels = ['scan', 'time', 'precursor', 'time_diff']
    df = pd.DataFrame(to_return, columns=labels)
    
    return df


#This function takes a list of scan numbers that come from MS2 data and will return the information in the psm file associated with the scan number. Returns a dataframe of the rows in the psm with the same scan numbers given. 
def get_MS2_psms(scan_list, data):
    df = pd.DataFrame()
    for scan in scan_list:
        row = (data.loc[data['scan'] == scan])
        df = df.append(row) 
    
    return df


#MsFragger combines the scan number with the file name. This function extracts the scan number puts it into its own column so it may be used in searches later.
def extractScanNum(row):
    string = row
    spot = string.find('.')
    new_st = string[spot + 1:]
    spot = new_st.find('.')
    final_st = new_st[:spot]
    
    if final_st[0] == "0":
        final_st = final_st[1:]
        
    return final_st


#Returns a spectrum given a scan number and a peptide sequence
def get_spec(my_scan, my_peptide, mzml):
    my_id = 'controllerType=0 controllerNumber=1 scan='+ my_scan
    spectrum_dict = mzml.get_by_id(my_id)
    
    spectrum_id = spectrum_dict['id']
    mz_array = spectrum_dict['m/z array']
    intensity_array = spectrum_dict['intensity array']
    retention_time = (spectrum_dict['scanList']['scan'][0].get('scan start time', -1))
    precursor = spectrum_dict['precursorList']['precursor'][0]
    precursor_ion = precursor['selectedIonList']['selectedIon'][0]
    precursor_mz = precursor_ion['selected ion m/z']

    if 'charge state' in precursor_ion:
        precursor_charge = int(precursor_ion['charge state'])
    elif 'possible charge state' in precursor_ion:
        precursor_charge = int(precursor_ion['possible charge state'])
    else:
        raise ValueError('Unknown precursor charge')

    scan_num = spectrum_dict["id"][spectrum_dict["id"].find('scan=') + 5:]
    ms_level = spectrum_dict["ms level"]
    total_ion_curr = spectrum_dict["total ion current"]
    ion_time = spectrum_dict["scanList"]['scan'][0]["ion injection time"]

    spectrum = sus.MsmsSpectrum(spectrum_id, precursor_mz, precursor_charge,
                        mz_array, intensity_array, None, retention_time, peptide=my_peptide)
 
    # Process the MS/MS spectrum.
    fragment_tol_mass = 50
    fragment_tol_mode = 'ppm'    
    spectrum = (spectrum.annotate_peptide_fragments(fragment_tol_mass, fragment_tol_mode,
                                            ion_types='by',max_ion_charge=precursor_charge))
    return spectrum



#Making a single interactive xic given a time and mz. The MS2 data points on the graph can be hovered over and will give back it's precursor mz value, time, scan number, and color classification.
def make_interactive_xic(mz, time, mz_data):
    """ parameters: 
    mz: a m/z value for a specific ion
    time: a time (in seconds) that the mz species elutes
    mz_data = an parse of the mzML file, an object from pyteomics
    """

    #time in most the output files is in seconds, but time in MZML files is in minutes. Making conversion here.
    time = time/60
    
    #getting the main XIC with the MS1 data
    xic = get_MS1_values(mz, time, mz_data)

    #getting all MS2 events that are at the MS1s time with almost identical m/z
    MS2_events = get_MS2_values(mz, time, mz_data)

     #This is the line for the MS1s
    xic_line = alt.Chart(xic).mark_line().encode(
        alt.X('time', title = 'Retention Time'),
        alt.Y('intensity', title = 'Intensity')).properties(
        title=f'XIC for {mz} mz at time {time}'
    ).interactive()

    #Line for the time given
    time_line = alt.Chart(pd.DataFrame({'x': [time]})).mark_rule(color = 'red').encode(x='x')

    #only if any MS2 events were found will we classify them and make a graph out of them
    if MS2_events.empty != True:
     
        MS2_points = alt.Chart(MS2_events).mark_point(filled = True).encode(
            alt.X('time'),
            alt.Y('precursor'),
            color = alt.value('black'),
            tooltip = [alt.Tooltip('precursor'), 
            alt.Tooltip('time'),
            alt.Tooltip('scan')]).interactive()  

        graph = xic_line + MS2_points + time_line

    else:
        graph = xic_line + time_line

    return graph


#the interactive XIC's won't show up in GitHub, these is a regular copy that will show up
def make_static_xic(mz, time, mz_data):
    """ parameters: 
    mz: m/z value for a specific ion
    time: time (in seconds) that the mz species elutes
    mz_data: a parse of the mzML file, an object from pyteomics
    """
    
    #time in most the output files is in seconds, but time in MZML files is in minutes. Making conversion here. 
    time = time/60
    
    xic = get_MS1_values(mz, time, mz_data)
    MS2_events = get_MS2_values(mz, time, mz_data)

    plt.figure(figsize=(8,6))    
    plt.plot(xic['time'], xic['intensity'])
    plt.axvline(time, color = 'red')
    plt.scatter(x = MS2_events['time'], y = MS2_events['precursor'], color = 'black')
    plt.xlabel("Retention Time")
    plt.ylabel("intensity")
    plt.title(f'XIC for mz {mz} at time {time}')
    plt.grid()