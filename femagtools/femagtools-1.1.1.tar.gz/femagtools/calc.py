import os
import sys
import json
import femagtools.femag
import femagtools.machine
import ldpem.psidq_norot
import ldpem.bchop
import logging

execpath = os.path.normpath(os.path.realpath(
    sys.argv[0] + '/../../bch'))

def get_norot_results(workdir, pmBase, bchReader):
    fingerprint = ldpem.psidq_norot.main(
        os.path.join(workdir, 'dq0.dat'))
    r = dict(fingerprint=fingerprint)
    m = {'Magnet height': 'hM',
         'Magnet width': 'bM',
         'Alpha': 'alpha',
         'Winkel zwischen den Magneten': 'gamma',
         'Magnetflaeche': 'marea'}
    try:
        with open(os.path.join(workdir, 'npar.dat')) as f:
            for l in f.readlines():
                k, v = l.split(':')
                if k in m:
                    r[m[k]] = float(v)
    except FileNotFoundError:  # ValueError also?
        pass
 
    par = dict(pmBase=pmBase,
               fingerprint=fingerprint,
               bchReader=bchReader)
    rbch = ldpem.bchop.main(par, execpath, task.directory)
    r['i1'] = rbch['I1'][0][1]
        
    return r


def get_magnet_materials(magmat):
    return [dict(
        name=m['name'],
        id=m['id'],
        remanenc=m['Brem'],
        temcoefbr=m['tempcoefbr'],
        temcoefhc=m['tempcoefhc'],
        hcb=m['hcb'],
        relperm=m['muerel']) for m in magmat]
 

def get_machine(pmBase):
    slottype = pmBase['stator']['slottype']
    dy1 = pmBase['stator']['da']
    da1 = pmBase['stator']['di']
    return {
        'name': pmBase['name'],
        'lfe': pmBase['stator']['l_fe'],
        'poles': 2*pmBase['p'],
        'outer_diam': dy1,
        'bore_diam': da1,
        'inner_diam': pmBase['rotor']['di'],
        'airgap': abs(da1-pmBase['rotor']['da'])/2,
        'stator': {
            'num_slots': pmBase['stator']['N1'],
            'num_slots_gen': pmBase['stator']['numSlotsGen'],
            'mcvkey_yoke': pmBase['stator']['mcvNameYoke'],
            'fillfac': pmBase['stator']['mcvFillFac'],
            'node_angle': pmBase['node_angle'],
            slottype: {k: pmBase['stator'][k] for k in pmBase['stator']}},
        'magnet': {
            'mcvkey_yoke': pmBase['rotor']['mcvNameYoke'],
            'material': pmBase['rotor']['magnet'],
            'fillfac': pmBase['rotor']['mcvFillFac'],
            'VMAGN': {p['key']: float(p['value'])
                      for p in pmBase['rotor']['magnetFsl']['parameter']}},
        'windings': {
            'num_phases': pmBase['winding']['n_phases'],
            'num_wires': pmBase['winding']['n_wires'],
            'coil_span': pmBase['winding']['coil_span'],
            'slot_indul': 1,
            'num_layers': pmBase['winding']['n_layers']}
        }


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(message)s')
    #FORMAT = "%(asctime)s %(levelname)s: %(message)s"
    #logging.basicConfig(level=logging.INFO, format=FORMAT)

    with open('VMagnet.json') as f:
        vmag = json.load(f)

    global bchReader, pmBase
    pmBase = vmag['pmBase']
    
    machine = get_machine(vmag['pmBase'])
    machine['magnet']['VMAGN']['bM'] = 26.0924
    machine['magnet']['VMAGN']['d5'] = 28.6410
    
    bchReader = vmag['bchReader']
    
    userdir = os.path.expanduser('~')
    workdir = os.path.join(userdir, 'vmagnopt-test')
    try:
        os.makedirs(workdir)
    except OSError:
        pass
    
    femag = femagtools.femaf.Femag(workdir,
                                 magnetizingCurves=vmag['magnetizingCurve'],
                                 magnetMat=get_magnet_materials(vmag['magnet']))

    # start calculation
    # the active fingerprint range is used
    simulation = dict(
        calculationMode="psd_psq_norot",
        magn_temp = vmag['psidq']['magn_temp'],
        num_par_wdgs = vmag['pmBase']['winding']['n_parcir'],
        theta_q = vmag['pmBase']['rotor']['theta_q'],
        theta_a = vmag['pmBase']['winding']['theta_a'],
        id_min = vmag['psidq']['minid'],
        id_max = vmag['psidq']['maxid'],
        iq_min = vmag['psidq']['miniq'],
        iq_max = vmag['psidq']['maxiq'],
        id_n = vmag['psidq']['stepsId'],
        iq_n = vmag['psidq']['stepsIq'])

    print('START...')
    r = femag(machine, simulation)

    r['bchReader'] = get_norot_results(workdir, pmBase, bchReader)
    with open('results.json', 'w') as fp:
        json.dump(r, fp)
