#import "@preview/charged-ieee:0.1.4": ieee

#show: ieee.with(
  title: [Improving Autonomous Robot Localization using GPS and IMU Data Fusion: Progress Report 3],
  abstract: [
    This report covers the Week~3 progress of the GPS/IMU sensor fusion project. Static noise characterization measurements were conducted for both the MPU-6050 IMU and the u-blox~7 GPS receiver. The resulting bias and standard-deviation values quantify sensor noise and serve as the measurement-noise covariance inputs for the upcoming Extended Kalman Filter. A notable gyroscope bias on the Y-axis was identified, which requires explicit bias compensation in the filter design.
  ],
  authors: (
    (
      name: "Steffen Ullmann",
      organization: [Florida Polytechnic University],
      location: [Lakeland, FL, USA],
      email: "sullmann3121@floridapoly.edu"
    ),
  ),
  index-terms: ("GPS", "IMU", "Sensor Fusion", "Kalman Filter", "Noise Characterization"),
  bibliography: bibliography("../refs.bib"),
  figure-supplement: [Fig.],
)


= Introduction

This project fuses GPS and IMU data on an RC-car platform to improve localization accuracy beyond what a standalone u-blox~7 GPS receiver provides @ublox7_datasheet @gps_accuracy. Progress Reports~1 and~2 covered hardware bring-up, IMU driver development, and the first ROS2 sensor nodes. Week~3 focused on quantifying the noise characteristics of both sensors, a prerequisite for setting the EKF covariance matrices.


= Progress to Date

Static recordings were taken with the vehicle stationary outdoors. IMU data (`/imu/data_raw`, 100~Hz) was captured for 90~s; the first 5~s were discarded to exclude initialization transients. GPS fixes (`/gps/fix`, 1~Hz) were recorded for ~5.5~min (345 valid fixes). All analysis was performed in a Jupyter notebook using the `rosbags` library @repo.

*IMU noise characterization*: @fig:imu shows the six raw channels over the recording window. Bias (mean at rest) and noise standard deviation were computed for each axis and are given in @tab:imu. The accelerometer Z-axis reads 9.654~m/s\u{00b2}, consistent with gravity at ±4~g full-scale. The most significant finding is a gyroscope Y-axis bias of 0.105~rad/s (≈6.0~°/s). Left uncorrected during integration, this bias would accumulate to a 360° heading error in under one minute. The EKF must therefore either subtract the measured bias before fusion or include it as an estimated state variable.

*GPS accuracy baseline*: @fig:gps shows the 2-D position scatter and altitude time series. With the receiver stationary, 50~\% of fixes fall within 1.84~m of the mean position (CEP50) and 95~\% within 3.49~m (CEP95), both within the 2.5--5~m specification of the u-blox~7 @ublox7_datasheet. The position standard deviations (1.60~m North, 1.26~m East) will be used directly as the diagonal entries of the GPS measurement-noise covariance matrix~$bold(R)$.

*EKF covariance initialization*: Both noise covariances follow from the measurements: $bold(R)_"GPS" = "diag"(1.60^2, 1.26^2)$~m\u{00b2} from the position scatter; $bold(R)_"IMU"$ will be finalized together with the state vector in Week~4. For the Gyro~Y bias, two approaches are considered: subtracting the measured offset as a pre-filter correction, or augmenting the state vector with an estimated bias. The choice will be made during Week~4.

#figure(
  image("../../04_Data/01_Static_sensor_noise_measurement/imu_static_timeseries.png"),
  caption: [IMU static recording (90~s, 100~Hz). Red lines indicate the per-axis bias. Gyro~Y shows a bias of 0.105~rad/s requiring compensation.],
) <fig:imu>

#figure(
  image("../../04_Data/01_Static_sensor_noise_measurement/gps_static_scatter.png"),
  caption: [Left: GPS position scatter with CEP50 (dashed) and CEP95 (dotted) circles. Right: altitude time series. CEP50~=~1.84~m, CEP95~=~3.49~m.],
) <fig:gps>


= Planned Work

*EKF implementation (Week~4)*: After being moved forward in Progress Report~2, the EKF implementation returns to its original Week~4 slot. The state vector and motion model will be finalized then, using $bold(R)_"GPS"$ and $bold(R)_"IMU"$ derived above. Localization accuracy will be quantified by comparing GPS-only against fused estimates.

*Field testing and final report (Week~5)*: Outdoor trajectory experiments and, if schedule allows, a Pure Pursuit or Stanley trajectory controller.

The updated project timeline is in @sec:appendix.


// ─── Appendix ──────────────────────────────────────────────────────────────────
#pagebreak()

= Appendix <sec:appendix>

#figure(
  table(
    columns: (2fr, 1fr,auto),
    inset: 6pt,
    align: (left, center, center),
    table.header([*Channel*], [*Bias (mean)*], [*Std dev (noise)*]),
    [Accel X], [-0.193~m/s\u{00b2}], [0.021~m/s\u{00b2}],
    [Accel Y], [-0.092~m/s\u{00b2}], [0.024~m/s\u{00b2}],
    [Accel Z], [+9.654~m/s\u{00b2}], [0.020~m/s\u{00b2}],
    [Gyro X],  [-0.021~rad/s],       [0.002~rad/s],
    [Gyro Y],  [*+0.105~rad/s*],     [0.002~rad/s],
    [Gyro Z],  [+0.004~rad/s],       [0.001~rad/s],
  ),
  caption: [MPU-6050 static noise statistics (8438 samples, 84.4~s at 100~Hz after 5~s warm-up). Gyro~Y bias in bold due to magnitude.],
) <tab:imu>

#figure(
  table(
    columns: (auto, 1fr, auto),
    inset: 6pt,
    align: (center, left, center),
    table.header([*Week*], [*Task*], [*Status*]),
    [1], [Hardware assembly, sensor interface verification],                          [#sym.checkmark],
    [2], [IMU accel/gyro reads, ROS2 environment and sensor nodes],                  [#sym.checkmark],
    [3], [Static sensor noise characterization, EKF parameter derivation],           [#sym.checkmark],
    [4], [EKF implementation, state vector definition, localization evaluation],     [],
    [5], [Field testing, trajectory controller _(if schedule allows)_, final report],[],
  ),
  caption: [Project timeline. Weeks~1--3 complete.],
)
