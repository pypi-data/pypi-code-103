from pyhrms import *
from multiprocessing import Pool



if __name__ == '__main__':
    path = r'D:\TOF-Ms DATA\tangting_DPG\TEST_one_step'
    company = 'Waters'
    processors = 2

    files_mzml = glob(os.path.join(path,'*.mzML'))

    ### 第一个过程
    pool = Pool(processes=processors)
    for file in files_mzml:
        pool.apply_async(first_process,args=(file,company,))
    print('Finished')
    pool.close()
    pool.join()

    ### 中间过程
    files_excel = glob(os.path.join(path,'*.xlsx'))
    peak_alignment(files_excel)
    ref_all = pd.read_excel(os.path.join(path, 'peak_ref.xlsx'), index_col='Unnamed: 0')

    ### 第二个过程
    pool = Pool(processes=processors)
    for file in files_mzml:
        pool.apply_async(second_process, args=(file, ref_all, company,))
    print('Finished')
    pool.close()
    pool.join()
