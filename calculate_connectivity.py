import mne, mne_connectivity, os
import numpy as np

def calculate_connectivity(preprocessed_data, stcs, src, subjects_dir, subject, data_folder, con_methods=['coh', 'pli', 'wpli2_debiased', 'ciplv'], n_jobs=-1):
    
    # Get a connectivity results folder in subject dir
    results_folder = os.path.join(data_folder, 'connectivity_results')
    if not os.path.exists(results_folder):
        os.system('mkdir %s' % results_folder)
    
    # Get labels 
    labels = mne.read_labels_from_annot(subject, parc='aparc',
                                        subjects_dir=subjects_dir)
    
    # If subject is fsaverage, remove the last label as it is unknown
    if subject == 'fsaverage':
        labels = labels[:-1]
    
    # Average the source estimates within each label using sign-flips to reduce
    # signal cancellations, also here we return a generator
    if isinstance(src,str) == True:
        src = mne.read_source_spaces(src)
    label_ts = mne.extract_label_time_course(stcs, labels, src, 
                                             mode='mean_flip', return_generator=True)

    # Calculate connectivity profiles for theta, alpha, beta, gamma.
    fmin = (4., 8., 13., 30.)
    fmax = (8., 13., 30., 100.)
    
    # Get sampling frequency from the MEG data
    sfreq = preprocessed_data.info['sfreq']
    con = mne_connectivity.spectral_connectivity_epochs(label_ts, method=con_methods, 
                                                        mode='multitaper', sfreq=sfreq, 
                                                        fmin=fmin, fmax=fmax, faverage=True, 
                                                        mt_adaptive=True, n_jobs=n_jobs)
    
    # Get all connectivity matrices for all methods and frequencies 
    con_mat_theta = dict()
    con_mat_alpha = dict()
    con_mat_beta = dict()
    con_mat_gamma = dict()
    
    for method, c in zip(con_methods, con):
        con_mat_theta[method] = c.get_data(output='dense')[:, :, 0]
        
    for method, c in zip(con_methods, con):
        con_mat_alpha[method] = c.get_data(output='dense')[:, :, 1]

    for method, c in zip(con_methods, con):
        con_mat_beta[method] = c.get_data(output='dense')[:, :, 2]
        
    for method, c in zip(con_methods, con):
        con_mat_gamma[method] = c.get_data(output='dense')[:, :, 3]
        
    # Save dictionaries to the results folder. Get these back with .items() 
    # method
    np.save(os.path.join(results_folder,'theta_connectivity.npy'), con_mat_theta)    
    np.save(os.path.join(results_folder,'alpha_connectivity.npy'), con_mat_alpha)    
    np.save(os.path.join(results_folder,'beta_connectivity.npy'), con_mat_beta)    
    np.save(os.path.join(results_folder,'gamma_connectivity.npy'), con_mat_gamma)            
        
    return (con_mat_theta, con_mat_alpha, con_mat_beta, con_mat_gamma, labels)