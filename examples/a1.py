import a1_simulator
import numpy as np
import legged_state_estimator 
from scipy.spatial.transform import Rotation
import matplotlib.pyplot as plt


PATH_TO_URDF = "a1_description/urdf/a1.urdf"
TIME_STEP = 0.0025
sim = a1_simulator.A1Simulator(PATH_TO_URDF, TIME_STEP, 
                               imu_gyro_noise=0.01, imu_lin_accel_noise=0.1,
                               imu_gyro_bias_noise=0.00001,
                               imu_lin_accel_bias_noise=0.0001,
                               qJ_noise=0.001, dqJ_noise=0.1, 
                               ddqJ_noise=1.0, tauJ_noise=0.1)

estimator_settings = legged_state_estimator.StateEstimatorSettings.a1_settings(PATH_TO_URDF, TIME_STEP)
estimator_settings.contact_estimator_settings.beta0 = -4.0
estimator_settings.contact_estimator_settings.beta1 = 0.25
estimator_settings.inekf_noise_params.contact_cov = 0.01 * np.eye(3, 3)
estimator_settings.contact_position_noise = 0.1 
estimator_settings.contact_rotation_noise = 0.1 
estimator_settings.lpf_gyro_cutoff = 250
estimator_settings.lpf_gyro_cutoff = 50
estimator = legged_state_estimator.StateEstimator(estimator_settings)

sim.init()
for i in range(200):
    sim.step_simulation()

base_pos, base_quat, base_lin_vel, base_ang_vel = sim.get_base_state()
estimator.init(base_pos=base_pos, base_quat=base_quat, base_lin_vel=base_lin_vel,
               imu_gyro_bias=np.zeros(3), imu_lin_accel_bias=np.zeros(3))

base_pos_true = []
base_quat_true = []
base_lin_vel_true = []
base_ang_vel_true = []
base_pos_est = []
base_quat_est = []
base_lin_vel_est = []
base_ang_vel_est = []

plt.ion()
fig, axes = plt.subplots(2, 2)
ax_pos, ax_quat, ax_lin_vel, ax_ang_vel = axes[0][0], axes[0][1], axes[1][0], axes[1][1],
ax_pos.set_ylim([-0.5, 0.5])
ax_quat.set_ylim([-0.5, 1.2])
ax_lin_vel.set_ylim([-1.5, 1.5])
ax_ang_vel.set_ylim([-1.5, 1.5])
PLT_WINDOW_SIZE = 200

line_pos_x_true, = ax_pos.plot([0], [0], linestyle='solid', color='blue', label='x(est)')
line_pos_y_true, = ax_pos.plot([0], [0], linestyle='solid', color='red', label='y(est)')
line_pos_z_true, = ax_pos.plot([0], [0], linestyle='solid', color='green', label='z(est)')
line_pos_x_est,  = ax_pos.plot([0], [0], linestyle='dashed', color='blue', label='x(true)')
line_pos_y_est,  = ax_pos.plot([0], [0], linestyle='dashed', color='red', label='y(true)')
line_pos_z_est,  = ax_pos.plot([0], [0], linestyle='dashed', color='green', label='z(true)')
line_quat_x_true, = ax_quat.plot([0], [0], linestyle='solid', color='blue', label='qx(est)')
line_quat_y_true, = ax_quat.plot([0], [0], linestyle='solid', color='red', label='qy(est)')
line_quat_z_true, = ax_quat.plot([0], [0], linestyle='solid', color='green', label='qz(est)')
line_quat_w_true, = ax_quat.plot([0], [0], linestyle='solid', color='yellow', label='qw(est)')
line_quat_x_est,  = ax_quat.plot([0], [0], linestyle='dashed', color='blue', label='qx(true)')
line_quat_y_est,  = ax_quat.plot([0], [0], linestyle='dashed', color='red', label='qy(true)')
line_quat_z_est,  = ax_quat.plot([0], [0], linestyle='dashed', color='green', label='qz(true)')
line_quat_w_est,  = ax_quat.plot([0], [0], linestyle='dashed', color='yellow', label='qw(true)')
line_lin_vel_x_true, = ax_lin_vel.plot([0], [0], linestyle='solid', color='blue', label='vx(est)')
line_lin_vel_y_true, = ax_lin_vel.plot([0], [0], linestyle='solid', color='red', label='vy(est)')
line_lin_vel_z_true, = ax_lin_vel.plot([0], [0], linestyle='solid', color='green', label='vz(est)')
line_lin_vel_x_est,  = ax_lin_vel.plot([0], [0], linestyle='dashed', color='blue', label='vx(true)')
line_lin_vel_y_est,  = ax_lin_vel.plot([0], [0], linestyle='dashed', color='red', label='vy(true)')
line_lin_vel_z_est,  = ax_lin_vel.plot([0], [0], linestyle='dashed', color='green', label='vz(true)')
line_ang_vel_x_true, = ax_ang_vel.plot([0], [0], linestyle='solid', color='blue', label='dqx(est)')
line_ang_vel_y_true, = ax_ang_vel.plot([0], [0], linestyle='solid', color='red', label='dqy(est)')
line_ang_vel_z_true, = ax_ang_vel.plot([0], [0], linestyle='solid', color='green', label='dqz(est)')
line_ang_vel_x_est,  = ax_ang_vel.plot([0], [0], linestyle='dashed', color='blue', label='dqx(true)')
line_ang_vel_y_est,  = ax_ang_vel.plot([0], [0], linestyle='dashed', color='red', label='dqy(true)')
line_ang_vel_z_est,  = ax_ang_vel.plot([0], [0], linestyle='dashed', color='green', label='dqz(true)')


for i in range(10000):
    sim.step_simulation()
    if i%100 == 0:
        qJ_cmd = 0.01 * np.random.normal(12) + sim.qJ_ref
        sim.apply_position_command(qJ_cmd)
    # estimate state
    imu_gyro_raw, imu_lin_acc_raw = sim.get_imu_state()
    qJ, dqJ, ddqJ, tauJ = sim.get_joint_state()
    estimator.update(imu_gyro_raw=imu_gyro_raw, imu_lin_accel_raw=imu_lin_acc_raw, 
                     qJ=qJ, dqJ=dqJ, ddqJ=ddqJ, tauJ=tauJ, f=[0, 0, 0, 0])
    base_pos_est.append(estimator.base_position_estimate.copy())
    base_quat_est.append(estimator.base_quaternion_estimate.copy())
    base_lin_vel_est.append(estimator.base_linear_velocity_estimate.copy())
    base_ang_vel_est.append(estimator.base_angular_velocity_estimate.copy())
    # true state
    base_pos, base_quat, base_lin_vel, base_ang_vel = sim.get_base_state()
    base_pos_true.append(base_pos.copy())
    base_quat_true.append(base_quat.copy())
    base_lin_vel_true.append(base_lin_vel.copy())
    base_ang_vel_true.append(base_ang_vel.copy())

    # estimation error 
    R_true = Rotation.from_quat(base_quat).as_matrix()
    diff = Rotation.from_matrix(R_true.T@estimator.base_rotation_estimate).as_quat()[0:3]
    print('base_pos error:', base_pos-estimator.base_position_estimate)
    print('base_rot error:', diff)
    print('base_lin_vel error:', base_lin_vel-estimator.base_linear_velocity_estimate)
    print('base_ang_vel error:', base_ang_vel-estimator.base_angular_velocity_estimate)
    print('contact_probability:', estimator.contact_probability)

    if len(base_pos_est) > PLT_WINDOW_SIZE:
        base_pos_true.pop(0)
        base_quat_true.pop(0) 
        base_lin_vel_true.pop(0) 
        base_ang_vel_true.pop(0) 
        base_pos_est.pop(0) 
        base_quat_est.pop(0) 
        base_lin_vel_est.pop(0) 
        base_ang_vel_est.pop(0) 

    ndata = len(base_pos_est)
    tstart = (i-ndata) * TIME_STEP
    tend = i * TIME_STEP
    times = np.linspace(tstart, tend, ndata)
    line_pos_x_true.set_xdata(times)
    line_pos_y_true.set_xdata(times)
    line_pos_z_true.set_xdata(times)
    line_pos_x_est.set_xdata(times)
    line_pos_y_est.set_xdata(times)
    line_pos_z_est.set_xdata(times)
    line_quat_x_true.set_xdata(times)
    line_quat_y_true.set_xdata(times)
    line_quat_z_true.set_xdata(times)
    line_quat_w_true.set_xdata(times)
    line_quat_x_est.set_xdata(times)
    line_quat_y_est.set_xdata(times)
    line_quat_z_est.set_xdata(times)
    line_quat_w_est.set_xdata(times)
    line_lin_vel_x_true.set_xdata(times)
    line_lin_vel_y_true.set_xdata(times)
    line_lin_vel_z_true.set_xdata(times)
    line_lin_vel_x_est.set_xdata(times)
    line_lin_vel_y_est.set_xdata(times)
    line_lin_vel_z_est.set_xdata(times)
    line_ang_vel_x_true.set_xdata(times)
    line_ang_vel_y_true.set_xdata(times)
    line_ang_vel_z_true.set_xdata(times)
    line_ang_vel_x_est.set_xdata(times)
    line_ang_vel_y_est.set_xdata(times)
    line_ang_vel_z_est.set_xdata(times)
    line_pos_x_true.set_ydata(np.array(base_pos_true).T[0])
    line_pos_y_true.set_ydata(np.array(base_pos_true).T[1])
    line_pos_z_true.set_ydata(np.array(base_pos_true).T[2])
    line_pos_x_est.set_ydata(np.array(base_pos_est).T[0])
    line_pos_y_est.set_ydata(np.array(base_pos_est).T[1])
    line_pos_z_est.set_ydata(np.array(base_pos_est).T[2])
    line_quat_x_true.set_ydata(np.array(base_quat_true).T[0])
    line_quat_y_true.set_ydata(np.array(base_quat_true).T[1])
    line_quat_z_true.set_ydata(np.array(base_quat_true).T[2])
    line_quat_w_true.set_ydata(np.array(base_quat_true).T[3])
    line_quat_x_est.set_ydata(np.array(base_quat_est).T[0])
    line_quat_y_est.set_ydata(np.array(base_quat_est).T[1])
    line_quat_z_est.set_ydata(np.array(base_quat_est).T[2])
    line_quat_w_est.set_ydata(np.array(base_quat_est).T[3])
    line_lin_vel_x_true.set_ydata(np.array(base_lin_vel_true).T[0])
    line_lin_vel_y_true.set_ydata(np.array(base_lin_vel_true).T[1])
    line_lin_vel_z_true.set_ydata(np.array(base_lin_vel_true).T[2])
    line_lin_vel_x_est.set_ydata(np.array(base_lin_vel_est).T[0])
    line_lin_vel_y_est.set_ydata(np.array(base_lin_vel_est).T[1])
    line_lin_vel_z_est.set_ydata(np.array(base_lin_vel_est).T[2])
    line_ang_vel_x_true.set_ydata(np.array(base_ang_vel_true).T[0])
    line_ang_vel_y_true.set_ydata(np.array(base_ang_vel_true).T[1])
    line_ang_vel_z_true.set_ydata(np.array(base_ang_vel_true).T[2])
    line_ang_vel_x_est.set_ydata(np.array(base_ang_vel_est).T[0])
    line_ang_vel_y_est.set_ydata(np.array(base_ang_vel_est).T[1])
    line_ang_vel_z_est.set_ydata(np.array(base_ang_vel_est).T[2])
    ax_pos.set_xlim([tstart, tend])
    ax_quat.set_xlim([tstart, tend])
    ax_lin_vel.set_xlim([tstart, tend])
    ax_ang_vel.set_xlim([tstart, tend])
    fig.canvas.draw()
    fig.canvas.flush_events()

sim.disconnect()