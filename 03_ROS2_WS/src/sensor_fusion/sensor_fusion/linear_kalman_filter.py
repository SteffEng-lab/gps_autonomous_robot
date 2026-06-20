import numpy as np

class Linear_Kalman_Filter():
    def __init__(self, sys_A, sys_B, sys_H, cov_Q, cov_R):
        # System
        self.sys_A = sys_A
        self.sys_B = sys_B
        self.sys_H = sys_H

        self.num_states = np.size(sys_A, 1)

        # Noise characteristics
        self.cov_Q = cov_Q
        self.cov_R = cov_R
        
        # Variables after prediction
        self.pred_state = np.zeros((self.num_states, 1))
        self.pred_error_cov = np.zeros((self.num_states, self.num_states))

        self.kalman_gain = None

        # Final estimated variables
        self.est_state = np.zeros((np.size(sys_A, 1), 1))
        self.est_error_cov = np.eye(self.num_states) * 100      # High initial uncertainty

        # Inputs
        self.current_z = 0      # Current measurement
        self.current_u = 0      # Current system input

    def predict(self):
        # Predict new state based on previous estimated state
        self.pred_state = self.sys_A @ self.est_state + self.sys_B @ self.current_u

        # Predict error covariance matrix
        self.pred_error_cov = self.sys_A @ self.est_error_cov @ self.sys_A.T + self.cov_Q

        # Calculate Kalman Gain
        self.kalman_gain = self.pred_error_cov @ self.sys_H.T @ np.linalg.inv(self.sys_H @ self.pred_error_cov @ self.sys_H.T + self.cov_R)

    def correct(self):
        if self.kalman_gain is None:
            return      # Predict step has not run yet

        # Correct predicted state using measurement
        self.est_state = self.pred_state + self.kalman_gain @ (self.current_z - self.sys_H @ self.pred_state)

        # Correct predicted error covariance matrix
        self.est_error_cov = self.pred_error_cov - self.kalman_gain @ self.sys_H @ self.pred_error_cov