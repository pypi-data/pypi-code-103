from shutil import copyfile
def main():
    # Do not copy ACMSim.h
    for fname in ['pid_regulator.c',
                  'pid_regulator.h',
                  'shared_flux_estimator.c',
                  'shared_flux_estimator.h',
                  'pmsm_controller.c',
                  'pmsm_controller.h',
                  'pmsm_observer.c',
                  'pmsm_observer.h',
                  'pmsm_comm.c',
                  'pmsm_comm.h',
                  'global_variables_definitions.c',
                  'utility.c',
                  'ACMConfig.h',
                  'sweep_frequency.h',
               ]:
        copyfile(f'c/{fname}', rf'D:\DrH\CCSWS10\pangu-debug\The acmsimcv5/{fname}')
if __name__ == '__main__':
    main()
