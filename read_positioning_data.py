
import numpy as np
filename = "BUILDING1/FingerprintingData_UniversityBuilding1.mat"

class indoor_positioning:
    def __init__(self, fingerprint_file=filename):
        self.fingerprint_file = fingerprint_file
        
    @staticmethod    
    def load_data (fname, dkey):
        raise NotImplementedError()
        
    def load_fp_data (self):
        import scipy.io as sio
        all_data = sio.loadmat (self.fingerprint_file)
        
        self.floor_heights = all_data['floor_heights'][0]
        self.n_floors = np.asscalar(all_data['N_floors'])
        self.n_fp = all_data['WLAN_data_per_synthpoint'].shape[0]
        self.n_ap = all_data['WLAN_grid_synthpoint'].shape[1]
        
        FPAP_matrix = np.full([self.n_fp, self.n_ap],np.nan)
        FP_coords = np.zeros([self.n_fp, 3])
        WLAN_data = all_data['WLAN_data_per_synthpoint']
        for n in range(self.n_fp):
            try:
                heard_aps = WLAN_data[n,1][0]
                #print(n)
                heard_aps = heard_aps.astype(int)
                heard_rss = WLAN_data[n,1][1]            
                FPAP_matrix[n,heard_aps] = heard_rss
                FP_coords[n,:] = WLAN_data[n,0]
            except:
                print("no AP was heard at {}-th fingerprint".format(n))
                    
        self.FPAP_matrix = FPAP_matrix
        self.FP_coords = FP_coords
        z = FP_coords[:,2]
        FP_floors = np.empty(np.shape(z))
        for i in range(self.n_floors):
            FP_floors [np.where(z==self.floor_heights[i])[0]] = i
        self.FP_floors = FP_floors        
        return FPAP_matrix, FP_coords, FP_floors
        
    def load_test_data (self, test_fname='BUILDING1/UserTrack1_UniversityBuilding1.mat'):
        import scipy.io as sio
        test_data = sio.loadmat(test_fname)
        WLAN_data = test_data['user_data_per_measpoint']
        n_test = WLAN_data.shape[0]
        test_matrix = np.full([n_test, self.n_ap],np.nan)
        test_coords = np.zeros([n_test, 3])
        for n in range(n_test):
            try:
                heard_aps = WLAN_data[n,1][0].astype(int)
                heard_rss = WLAN_data[n,1][1]            
                test_matrix[n,heard_aps] = heard_rss
                test_coords[n,:] = WLAN_data[n,0]
            except:
                print("no AP was heard at {}-th test point".format(n))
        z = test_coords[:,2]
        test_floors = np.empty(np.shape(z))
        for i in range(self.n_floors):
            test_floors [np.where(z==self.floor_heights[i])[0]] = i
        return test_matrix, test_coords, test_floors
        
        
    
    def convert_FPAP (self, FPAP_matrix=None, mode='linear', bogus_val=0):
        if FPAP_matrix is None:
            FPAP_matrix = self.FPAP_matrix.copy()
        if mode == 'linear':
            FPAP_matrix[~np.isnan(FPAP_matrix)] = 10**(FPAP_matrix[~np.isnan(FPAP_matrix)]/10)
            FPAP_matrix[np.isnan(FPAP_matrix)] = 0
        elif mode == 'negdb':
            bogus_val = 20            
            FPAP_matrix = -np.nanmin(FPAP_matrix) + FPAP_matrix + bogus_val            
            FPAP_matrix[np.isnan(FPAP_matrix)] = 0
        elif mode == 'bw':
            FPAP_matrix[~np.isnan(FPAP_matrix)] = 1
            FPAP_matrix[np.isnan(FPAP_matrix)] = 0
        if FPAP_matrix is None:
            self.FPAP_matrix_converted = FPAP_matrix
        return FPAP_matrix
        