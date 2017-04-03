import inspect
import bluesky.plans as bp
import os

def tscan(comment:str, prepare_traj:bool=True, **kwargs):
    """
    Trajectory Scan - Runs the monochromator along the trajectory that is previously loaded in the controller

    Parameters
    ----------
    comment : str
        Name of the scan - it will be stored in the metadata

    prepare_traj : bool (default = True)
        Boolean to tell the function to automatically run the routine "prepare trajectory" - the trajectory needs to be 'prepared' in the controller before every scan

    absorp : bool (default = True)
        Telling the function how to parse the data - TODO: remake this parameter


    Returns
    -------
    uid : str
        Unique id of the scan

    interp_filename : str
        Filename where the interpolated data was stored

    absorp : bool
        Just returning the parameter absorp that was passed to the scan


    See Also
    --------
    :func:`tscan_N`
    """

    if (prepare_traj == True):
        RE(prep_traj_plan())
    uid, = RE(execute_trajectory(comment))
    print(uid)

    print('Done!')
    return [uid]

def tscan_plan(comment:str, prepare_traj:bool=True, **kwargs):
    if prepare_traj:
        yield from prep_traj_plan()
    #uid = (yield from execute_trajectory(comment))
    yield from execute_trajectory(comment)
    uid = db[-1]['start']['uid']

    print('Done!')
    return [uid]
    

def tscan_N(comment:str, n_cycles:int=1, delay:float=0, **kwargs):
    """
    Trajectory Scan N - Runs the monochromator along the trajectory that is previously loaded in the controller N times

    Parameters
    ----------
    comment : str
        Name of the scan - it will be stored in the metadata

    prepare_traj : bool (default = True)
        Boolean to tell the function to automatically run the routine "prepare trajectory" - the trajectory needs to be 'prepared' in the controller before every scan

    absorp : bool (default = True)
        Telling the function how to parse the data - TODO: remake this parameter

    n_cycles : int (default = 1)
        Number of times to run the scan automatically

    delay : float (default = 0)
        Delay in seconds between scans


    Returns
    -------
    uid : str
        Unique id of the scan

    interp_filename : str
        Filename where the interpolated data was stored

    absorp : bool
        Just returning the parameter absorp that was passed to the scan


    See Also
    --------
    :func:`tscan`
    """

    uids = []
    for indx in range(0, n_cycles): 
        comment_n = comment + ' ' + str(indx + 1)
        print(comment_n) 
        RE(prep_traj_plan())
        uid, = RE(execute_trajectory(comment_n))
        uids.append(uid)
        time.sleep(delay)
    print('Done!')
    return uids
    

def tscan_N_plan(comment:str, prepare_traj:bool=True, n_cycles:int=1, delay:float=0, **kwargs):
    uids = []
    for indx in range(0, n_cycles): 
        comment_n = comment + ' ' + str(indx + 1)
        print(comment_n) 
        if prepare_traj:
            yield from prep_traj_plan()
        #uid = (yield from execute_trajectory(comment_n))
        yield from execute_trajectory(comment_n)
        uid = db[-1]['start']['uid']
        uids.append(uid)
			
        yield from bp.sleep(delay)
    print('Done!')
    return uids


def tscan_Rrep(comment:str, prepare_traj:bool=True, **kwargs):
    if (prepare_traj == True):
        RE(prep_traj_plan())

    uid, = RE(execute_trajectory(comment))
    print('Done!')
    return uid


def tloopscan(comment:str, prepare_traj:bool=True, **kwargs):
    if (prepare_traj == True):
        RE(prep_traj_plan())
    uid, = RE(execute_loop_trajectory(comment))
    print('Done!')
    return uid


def tscanxia(comment:str, prepare_traj:bool=True, **kwargs):
    """
    Trajectory Scan Xia - Runs the monochromator along the trajectory that is previously loaded in the controller and get data from the XIA

    Parameters
    ----------
    comment : str
        Name of the scan - it will be stored in the metadata

    prepare_traj : bool (default = True)
        Boolean to tell the function to automatically run the routine "prepare trajectory" - the trajectory needs to be 'prepared' in the controller before every scan

    absorp : bool (default = False)
        Telling the function how to parse the data - TODO: remake this parameter


    Returns
    -------
    uid : str
        Unique id of the scan

    interp_filename : str
        Filename where the interpolated data was stored

    absorp : bool
        Just returning the parameter absorp that was passed to the scan


    See Also
    --------
    :func:`tscan`
    """

    if (prepare_traj == True):
        RE(prep_traj_plan())
    uid, = RE(execute_xia_trajectory(comment))
    print('Done!')
    return [uid]


def tscanxia_N(comment:str, n_cycles:int=1, delay:float=0, **kwargs):
    uids = []

    for i in range(n_cycles):
        RE(prep_traj_plan())
        uid, = RE(execute_xia_trajectory(comment + '_' + str(i)))
        uids.append(uid)
        time.sleep(delay)

    return uids

def tscanxia_plan(comment:str, prepare_traj:bool=True, **kwargs):
    if prepare_traj:
        yield from prep_traj_plan()
    #uid = (yield from execute_xia_trajectory(comment))
    yield from execute_xia_trajectory(comment)
    uid = db[-1]['start']['uid']
	
    print('Done!')
    return [uid]


def get_offsets(num:int = 10, **kwargs):
    """
    Get Ion Chambers Offsets - Gets the offsets from the ion chambers and automatically subtracts from the acquired data in the next scans

    Parameters
    ----------
    num : int
        Number of points to acquire and average for each ion chamber


    Returns
    -------
    uid : str
        Unique id of the scan


    See Also
    --------
    :func:`tscan`
    """

    aver1=pba1.adc7.averaging_points.get()
    aver2=pba2.adc6.averaging_points.get()
    aver3=pba1.adc1.averaging_points.get()
    aver4=pba1.adc6.averaging_points.get()
    pba1.adc7.averaging_points.put(15)
    pba2.adc6.averaging_points.put(15)
    pba1.adc1.averaging_points.put(15)
    pba1.adc6.averaging_points.put(15)
    
    uid, = RE(get_offsets_plan([pba1.adc6, pba1.adc1, pba2.adc6, pba1.adc7], num = num))
    i0_array = db.get_table(db[-1])['pba1_adc7_volt']
    it_array = db.get_table(db[-1])['pba1_adc1_volt']
    ir_array = db.get_table(db[-1])['pba2_adc6_volt']
    iff_array = db.get_table(db[-1])['pba1_adc6_volt']
    i0_off = np.mean(i0_array[1:num])
    it_off = np.mean(it_array[1:num])
    ir_off = np.mean(ir_array[1:num])
    iff_off = np.mean(iff_array[1:num])

    if 'dummy_read' not in kwargs:
        print('Updating values...')
        pba1.adc7.offset.put(i0_off)
        pba1.adc1.offset.put(it_off)
        pba2.adc6.offset.put(ir_off)
        pba1.adc6.offset.put(iff_off)

        print('{}\nMean (i0) = {}'.format(i0_array, i0_off))
        print('{}\nMean (it) = {}'.format(it_array, it_off))
        print('{}\nMean (ir) = {}'.format(ir_array, ir_off))
        print('{}\nMean (iff) = {}'.format(iff_array, iff_off))

    pba1.adc7.averaging_points.put(aver1)
    pba2.adc6.averaging_points.put(aver2)
    pba1.adc1.averaging_points.put(aver3)
    pba1.adc6.averaging_points.put(aver4)
    
    run = db[uid]
    for i in run['descriptors']:
        if i['name'] != 'primary':
            os.remove(i['data_keys'][i['name']]['filename'])
    #os.remove(db[uid]['descriptors'][1]['data_keys']['pba2_adc6']['filename'])
    #os.remove(db[uid]['descriptors'][2]['data_keys']['pba1_adc1']['filename'])
    #os.remove(db[uid]['descriptors'][3]['data_keys']['pba1_adc6']['filename'])

    if 'dummy_read' in kwargs:
        print('Mean (i0) = {}'.format(i0_off))
        print('Mean (it) = {}'.format(it_off))
        print('Mean (ir) = {}'.format(ir_off))
        print('Mean (iff) = {}\n'.format(iff_off))

        if i0_off > -0.04:
            print('Increase i0 gain by 10^2')
        elif i0_off <= -0.04 and i0_off > -0.4:
            print('Increase i0 gain by 10^1')

        if it_off > -0.04:
            print('Increase it gain by 10^2')
        elif it_off <= -0.04 and it_off > -0.4:
            print('Increase it gain by 10^1')

        if ir_off > -0.04:
            print('Increase ir gain by 10^2')
        elif ir_off <= -0.04 and ir_off > -0.4:
            print('Increase ir gain by 10^1')

        if iff_off > -0.04:
            print('Increase iff gain by 10^2')
        elif iff_off <= -0.04 and iff_off > -0.4:
            print('Increase iff gain by 10^1')

    print(uid)
    print('Done!')
    return [uid]

def general_scan(detector, det_plot_name, motor, rel_start, rel_stop, num, **kwargs):
    if type(detector) == str:
        detector = [eval(detector)]

    if type(motor) == str:
        motor = eval(motor)

    ax = kwargs.get('ax')
    return RE(general_scan_plan([detector], motor, rel_start, rel_stop, num), LivePlot(det_plot_name, motor.name, ax=ax))


def xia_step_scan(comment:str, e0:int=8333, preedge_start:int=-200, xanes_start:int=-50, xanes_end:int=30, exafs_end:int=16, preedge_spacing:float=10, xanes_spacing:float=0.2, exafs_spacing:float=0.04, **kwargs):
    '''
    xia_step_scan - Runs the monochromator along the trajectory defined in the parameters. Gets data from the XIA and the ion chambers after each step. 

    Parameters
    ----------
    comment : str
        Name of the scan - it will be stored in the metadata
        Other parameters: TODO


    Returns
    -------
    uid : str
        Unique id of the scan

    interp_filename : str
    Filename where the interpolated data was stored


    See Also
    --------
    :func:`tscan`

    '''

    energy_grid, time_grid = get_xia_energy_grid(e0, preedge_start, xanes_start, xanes_end, exafs_end, preedge_spacing, xanes_spacing, exafs_spacing)
    positions_grid = xray.energy2encoder(energy_grid) / 360000

    ax = kwargs.get('ax')
    if ax is not None:
        uid, = RE(step_list_plan([xia1, i0, it, iff, ir], hhm.theta, positions_grid, comment), LivePlot(xia1.mca1.roi0.sum.name, hhm.theta.name, ax=ax))
    else:
        uid, = RE(step_list_plan([xia1, i0, it, iff, ir], hhm.theta, positions_grid, comment))

    path = '/GPFS/xf08id/User Data/{}.{}.{}/'.format(db[uid]['start']['year'], db[uid]['start']['cycle'], db[uid]['start']['PROPOSAL'])
    filename = parse_xia_step_scan(uid, comment, path)

    ax.cla()
    plot_xia_step_scan(uid, ax=ax) 

    print('Done!')
    return uid

    

def samplexy_scan(detectors, motor, rel_start, rel_stop, num, **kwargs):
    if type(detectors) is not list:
        detectors = [detectors]
    return RE(sampleXY_plan(detectors, motor, rel_start, rel_stop, num), LivePlot(detectors[0].volt.name, motor.name))

def xymove_repeat(numrepeat=1, xyposlist=[], samplelist=[], sleeptime = 2, testing = False, simulation = True, runnum_start = 0, usexia = True, **kwargs):

    '''
    collect EXAFS scans on given sample locations repeatedly.

    variables:
    numrepeat (int): number of repeated runs
    xyposlist (list of of [x,y] positions in pairs, x, y are floats): \
                     list of [x, y] positions, e.g. [[2.3, 23], [34.5, 23.2]]
    samplelist (list of strings) sample/file names for each scans
    sleeptime (int): how long (in sec.) to wait between samples
    testing (bool): if True, no sample motion, no EXAFS scans but just print the process
    simulation (bool): if True, only sample motions, no EXAFS scans

    each scan file name will be: [samplename]_[current-runnum+runnum_start].txt

    '''
    if len(xyposlist) < 1:
        print('xyposlist is empty')
        raise
    if len(samplelist) < 1:
        print('samplelist is empty')
        raise

    if len(xyposlist) is not len(samplelist):
        print('xypolist and samplelist must have the same length')
        raise

    gen_parser = xasdata.XASdataGeneric(db)
    uids = []
    for runnum in range(numrepeat):
        print('current run', runnum)
        print('current run + run start', runnum+runnum_start)
        for i in range(len(xyposlist)):
            print('moving sample xy to', xyposlist[i])
            if testing is not True:
                samplexy.x.move(xyposlist[i][0])
                samplexy.y.move(xyposlist[i][1])

            print('done moving, taking a nap with wait time (s)', sleeptime)
            time.sleep(sleeptime)

            print('done napping, starting taking the scan')
            if testing is not True:
                if simulation is not True:
                    tscan_comment = samplelist[i]+'_'+str(runnum+runnum_start).zfill(3)
                    if usexia is False:
                        uid = tscan(tscan_comment)[0]
                    else:
                        uid = tscanxia(tscan_comment)[0]

            print('done taking the current scan')

            print('parsing the current scan')
            current_filepath = '/GPFS/xf08id/User Data/{}.{}.{}/' \
                               '{}.txt'.format(db[uid]['start']['year'],
                                               db[uid]['start']['cycle'],
                                               db[uid]['start']['PROPOSAL'],
                                               db[uid]['start']['comment'])
    
            gen_parser.load(uid)
            key_base = 'i0'
            if 'xia_filename' in db[uid]['start']:
                 key_base = 'xia_trigger'
            gen_parser.interpolate(key_base = key_base)
    
            if 'xia_filename' in db[uid]['start']:
                # Parse xia
                xia_filename = db[uid]['start']['xia_filename']
                xia_filepath = 'smb://elistavitski-ni/epics/{}'.format(xia_filename)
                xia_destfilepath = '/GPFS/xf08id/xia_files/{}'.format(xia_filename)
                smbclient = xiaparser.smbclient(xia_filepath, xia_destfilepath)
                smbclient.copy()
                xia_parser.parse(xia_filename, '/GPFS/xf08id/xia_files/')
                xia_parsed_filepath = current_filepath[0 : current_filepath.rfind('/') + 1]
                xia_parser.export_files(dest_filepath = xia_parsed_filepath, all_in_one = True)
    
                length = min(len(xia_parser.exporting_array1), len(gen_parser.interp_arrays['energy']))
    
                mcas = []
                if 'xia_rois' in db[uid]['start']:
                    xia_rois = db[uid]['start']['xia_rois']
                    for mca_number in range(1, 5):
                        mcas.append(xia_parser.parse_roi(range(0, length), mca_number, xia_rois['xia1_mca{}_roi0_low'.format(mca_number)], xia_rois['xia1_mca{}_roi0_high'.format(mca_number)]))
                    mca_sum = sum(mcas)
                else:
                    for mca_number in range(1, 5):
                        mcas.append(xia_parser.parse_roi(range(0, length), mca_number, 6.7, 6.9))
                    mca_sum = sum(mcas)
    
                gen_parser.interp_arrays['XIA_SUM'] = np.array([gen_parser.interp_arrays['energy'][:, 0], mca_sum]).transpose()
    
                gen_parser.export_trace(current_filepath[:-4], '')

        print('done with the current run')

    print('done with all the runs! congratulations!')

