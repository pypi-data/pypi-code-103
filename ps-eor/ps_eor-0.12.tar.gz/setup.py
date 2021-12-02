# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ps_eor', 'ps_eor.tests', 'ps_eor.tools']

package_data = \
{'': ['*'], 'ps_eor': ['config/*', 'instru/*']}

install_requires = \
['GPy>=1.9,<2.0',
 'astropy>=3.2,<5',
 'click>=7.0,<8.0',
 'configparser>=4.0,<5.0',
 'corner>=2.0,<3.0',
 'emcee>=3.0.2,<4.0.0',
 'fast-histogram>=0.9,<0.10',
 'h5py>=3.0,<4.0',
 'healpy>=1.12,<2.0',
 'joblib>=1.0,<2.0',
 'libpipe>=0.1.5',
 'matplotlib>=3,<4',
 'pyfftw>=0.12,<0.13',
 'reproject>=0.7,<0.8',
 'scikit-learn>=0.20',
 'scipy>=1.4,<2.0',
 'tables>=3.2,<4.0',
 'torch>=1.9.0,<2.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0']}

entry_points = \
{'console_scripts': ['pstool = ps_eor.tools.pstool:main']}

setup_kwargs = {
    'name': 'ps-eor',
    'version': '0.12',
    'description': 'Foreground modeling/removal and Power Spectra generation',
    'long_description': 'Python package for foreground removal and power spectra calculation:\n===================================================================\n\nInstallation\n------------\n\nFrom git (development version):\n\n    git clone https://gitlab.com/flomertens/ps_eor.git\n    pip install -f ./ps_eor\n\nfrom [pypi](https://pypi.org/project/ps-eor/) (latest stable version):\n\n    pip install ps_eor\n\nThe following packages will also be installed:\n\n- click\n- numpy\n- scipy\n- astropy\n- matplotlib\n- pytable (for saving loading in h5 format)\n- pyfftw (optional, can save time)\n- sklearn (for PCA)\n- GPy (for GPR)\n- healpy,reproject (optional)\n\n\nCommand-line usage:\n-------------------\n\nThe ps_eor package comes with a command line tool: pstool, which can:\n- Generate gridded visibility cube from fits images cubes (gen_vus_cube)\n- Produce power-spectra from gridded visibility cube (make_ps)\n- Combine different visibility cube (combine)\n- Remove foregrounds using GPR (run_gpr)\n- ... and several more\n\nUsage of pstool is as follow:\n\n    Usage: pstool [OPTIONS] COMMAND [ARGS]...\n\n    Options:\n      --version  Show the version and exit.\n      --help     Show this message and exit.\n\n    Commands:\n      combine               Combine all datacubes listed in FILE_LIST...\n      combine_sph           Combine all sph datacubes listed in FILE_LIST...\n      diff_cube             Compute the difference between CUBE1 and CUBE2\n      even_odd_to_sum_diff  Create SUM / DIFF datacubes from EVEN / ODD...\n      gen_vis_cube          Create a datacube from image and psf fits files.\n      make_ps               Produce power-spectra of datacubes FILE_I: Input...\n      run_flagger           Run flagger on datacubes and save flag.\n      run_gpr               Run GPR & generate power spectra FILE_I: Input...\n      simu_noise_img        Compute noise fits cube from a simulated UV\n                            coverage...\n\n      simu_noise_ps         Compute noise PS from a simulated UV coverage...\n      simu_uv               Compute gridded UV coverage.\n      vis_to_sph            Load visibilities datacubes VIS_CUBE, transform to...\n\n\nTo get help for any of the pstool command, execute:\n\n    pstool CMD --help\n\n\nAPI usage:\n----------\n\nThis package provide a simple interface for Foreground removal and PS estimation tasks which can complete the command line tool.\n\nBelow we briefly document the main tasks that can be perform with this package:\n\n\n1. Loading your data: \n---------------------\n\n    data_cube_i = datacube.CartDataCube.load_from_fits_image(files, umin, umax, theta_fov)\n\nThis will do the following steps:\n- Read Fits image file\n- Trim image to theta_fov\n- Convert image from Jy/PSF to K, using imager_scale_factor or WSCNORMF\n attribute to get PSF "solid angle" (otherwise use Gaussian approx of the PSF)\n- FFT image per frequencies to get visibilities\n- Keep only non-zero visibilities between umin and umax.\nand return a CartDataCube object storing the visibilities in an ungridded way.\n\nIt is possible (recommended) to save/load to an h5 format with the save()/load() method.\n\nOne can also regrid the data and make an image with the regrid() and image() method.\n\n\n2. Run FG removal algorithm:\n----------------------------\n\nThe main FG removal code is GPR, but PCA, GMCA (the python version) and Polynamial fitting are also implemented.\n\nTo run GPR, one do the following:\n\n    data_cube_i = datacube.CartDataCube.load_from_fits_image(files_i, umin, umax, theta_fov)\n    data_cube_v = datacube.CartDataCube.load_from_fits_image(files_v, umin, umax, theta_fov)\n\n    eor_bin_list = pspec.EorBinList(data_cube_i.freqs)\n    # Create an EoR bin 122-134 MHz with a 120-136MHz range for the FG fitting\n    eor_bin_list.add_freq(1, 122, 134, 120, 136)\n    eor = eor_bin_list.get(1)\n\n    gpr_config = fitutil.GprConfig.load(gpr_config_filename)\n    gpr_fit = fgfit.GprForegroundFit(gpr_config)\n    gpr_res = gpr_fit.run(eor.get_slice_fg(data_cube_i), eor.get_slice_fg(data_cube_v))\n\nThis return a GprForegroundResult object which have the following attributes:\n- fit: The FG model in a form of a CartDataCube object\n- sub: The residual \n- pre_fit: The pre-fit FG model\n- post_fit: The post-fit FG model\n\nAnd the following method:\n- get_fg_model(): return the GPR fg model\n- get_eor_model(): return the GPR eor model\n\nOn can then save/load those CartDataCube as needed for later processing.\n\nThe CartDataCube cubes of the GPR model and residual contains the error covariance \nfrom the GPR model that need to be taken into account when generating the \npower spectra.\n\nLook at gpr_config.parset and gpr_config_v.parset for examples of GPR configuration.\n\n\n3. Generate Power Spectra:\n--------------------------\n\nThe PS code into account automatically the error covariance of the GPR model.\n\nIt is possible to generate spatial only PS, Cylindrically averaged PS (2D) or spherically averaged PS (3D).\n\n    # Create a PS configuration\n    el = 2 * np.pi * (np.arange(data_cube.ru.min(), data_cube.ru.max(), du))\n    ps_conf = pspec.PowerSpectraConfig(el)\n\n    pb = datacube.LofarHBAPrimaryBeam()\n    \n    # Create a PS generation object\n    ps_gen = pspec.PowerSpectraCart(eor, ps_conf, pb)\n\n    # Create a Spatial PS, plot it and save it to a file\n    ps = ps_gen.get_ps(data_cube)\n    ps.plot(title=\'Spatial power spectra\')\n    plt.savefig(\'ps.pdf\')\n    ps.save_to_txt(\'ps.txt\')\n\n    # Create a Cylindrically averaged PS\n    ps2d = ps_gen.get_ps2d(data_cube)\n    ps2d.plot(title=\'Cylindrically averaged power spectra\')\n    plt.savefig(\'ps2d.pdf\')\n    ps2d.save_to_txt(\'ps2d.txt\')\n\n    # Create a Spherically averaged PS\n    kbins = np.logspace(np.log10(ps_gen.kmin), np.log10(0.5), 10)\n    ps3d = ps_gen.get_ps3d(kbins, data_cube)\n    ps3d.plot(title=\'Spherically averaged power spectra\')\n    plt.savefig(\'ps3d.pdf\')\n    ps3d.save_to_txt(\'ps3d.txt\')\n\n',
    'author': 'Florent Mertens',
    'author_email': 'flomertens@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/flomertens/ps_eor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
