import cobaya
#slide21?

cobaya_info = {}
cobaya_info["likelihood"] = {}
cobaya_info["theory"] = {}
cobaya_info["sampler"] = {}
cobaya_info["params"] = {}
cobaya_info["output"] = {}

do_lowE = True
do_lensing = True
cobaya_info["likelihood"]["planck_2018_highl_plik.TTTEEE"] = {}

if do_lowE :
    cobaya_info["likelihood"]["planck_2018_lowl.TT_clik"] = {}
    cobaya_info["likelihood"]["planck_2018_lowl.EE_clik"] = {}

if do_lensing :
    cobaya_info["likelihood"]["planck_2018_lensing.clik"] = {}


cobaya_info["theory"] = {'classy': {'path': '/Users/fmrl/thesis_code/class_public/',
                         'extra_args': {'N_ncdm': 1,
                                        'm_ncdm': 0.06,
                                        'deg_ncdm': 1,
                                        'N_ur': 2.0308,
                                        'T_cmb': 2.7255,
                                        'YHe': 'BBN',
                                        'output': 'tCl,pCl,lCl,mPk',
                                        'modes': 's',
                                        'lensing': 'yes',
                                        'non linear': 'hmcode',
                                        'hmcode_version': '2020',
                                        'accurate_lensing': 1,
                                        'l_max_scalars': 9500}}}

cobaya_info["sampler"] = {'mcmc': {'Rminus1_stop': 0.01,
                                   'measure_speeds': True,
                                   'learn_proposal': True,
                                   'learn_proposal_Rminus1_max': 100,
                                   'output_every': 1}}

cobaya_info["params"] = {'H0': {'latex': 'H_0',
                                'prior': {'max': 80, 'min': 55},
                                'ref': {'dist': 'norm', 'loc': 70, 'scale': 1.0},
                                'proposal': 1.0},
                         'logA': {'latex': '\\log(10^{10} A_\\mathrm{s})',
                                  'prior': {'max': 3.2, 'min': 2.7},
                                  'ref': {'dist': 'norm', 'loc': 3.05, 'scale': 0.001},
                                  'proposal': 0.005,
                                  'drop': True},
                         'n_s': {'latex': 'n_\\mathrm{s}',
                                 'prior': {'max': 1.13, 'min': 0.868},
                                 'ref': {'dist': 'norm', 'loc': 0.965, 'scale': 0.004},
                                 'proposal': 0.01},
                         'omega_b': {'latex': '\\Omega_\\mathrm{b} h^2',
                                     'prior': {'max': 0.026, 'min': 0.018},
                                     'ref': {'dist': 'norm', 'loc': 0.0224, 'scale': 0.0001},
                                     'proposal': 0.00015},
                         'omega_cdm': {'latex': '\\Omega_\\mathrm{c} h^2',
                                       'prior': {'max': 0.16, 'min': 0.09},
                                       'ref': {'dist': 'norm', 'loc': 0.12, 'scale': 0.001},
                                       'proposal': 0.0025},
                         'tau_reio': {'latex': '\\tau_\\mathrm{reio}',
                                      'prior': {'dist': 'norm', 'loc': 0.054, 'scale': 0.0074},
                                      'ref': {'dist': 'norm', 'loc': 0.055, 'scale': 0.003},
                                      'proposal': 0.003}}

#cobaya_info["params"].update?
cobaya_info["params"] = {'A_s': {'latex': 'A_\\mathrm{s}',
                                 'value': 'lambda logA: 1e-10*np.exp(logA)'},
                         'Omega_m': {'latex': '\\Omega_\\mathrm{m}'},
                         'omegamh2': {'latex': '\\Omega_\\mathrm{m} h^2',
                                      'derived': 'lambda Omega_m, H0: Omega_m*(H0/100)**2'},
                         'Omega_Lambda': {'latex': '\\Omega_\\Lambda'},
                         'YHe': {'latex': 'Y_\\mathrm{P}'},
                         'z_reio': {'latex': 'z_\\mathrm{re}'},
                         'sigma8': {'latex': '\\sigma_8'},
                         'age': {'latex': '{\\rm{Age}}/\\mathrm{Gyr}'},
                         'rs_drag': {'latex': 'r_\\mathrm{drag}'}}

cobaya_info["output"] = 'thesis_code/Code/test_MCMC/chain'
cobaya_info["force"] = False
cobaya_info["resume"] = True
cobaya_info["timing"] = True
cobaya_info["debug"] = False
