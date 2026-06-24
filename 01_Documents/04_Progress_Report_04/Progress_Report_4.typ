#import "@preview/charged-ieee:0.1.4": ieee

#show: ieee.with(
  title: [Improving Autonomous Robot Localization using GPS and IMU Data Fusion: Progress Report 4],
  abstract: [
    This report covers the Week~4 progress of the GPS/IMU sensor fusion project. A Linear Kalman Filter (LKF) was selected over the Extended Kalman Filter (EKF) planned in previous reports, as the chosen motion model and measurement model are both fully linear. A four-state vector comprising 2-D position and velocity was defined; the IMU provides acceleration inputs to the prediction step at 100~Hz, while GPS fixes drive the correction step at 1~Hz. The filter and a new `sensor_fusion` ROS2 package were implemented and are ready for field evaluation in Week~5.
  ],
  authors: (
    (
      name: "Steffen Ullmann",
      organization: [Florida Polytechnic University],
      location: [Lakeland, FL, USA],
      email: "sullmann3121@floridapoly.edu"
    ),
  ),
  index-terms: ("GPS", "IMU", "Sensor Fusion", "Kalman Filter", "ROS2", "Localization"),
  bibliography: bibliography("../refs.bib"),
  figure-supplement: [Fig.],
)


= Introduction

This project fuses GPS and IMU measurements on an RC-car platform to improve localization accuracy beyond what a standalone u-blox~7 GPS receiver provides @ublox7_datasheet @gps_accuracy. Progress Reports~1--3 covered hardware bring-up, ROS2 sensor nodes, and static noise characterization of both sensors. Upon formalizing the motion model, the EKF and UKF proved unnecessary, as the constant-velocity model with explicit acceleration input is linear in both the state transition and measurement equations. A standard Linear Kalman Filter (LKF) was implemented instead.


= Progress to Date

== State Vector and Motion Model

The filter tracks four states: 2-D position and velocity, $bold(x)_k = [p_(x,k), p_(y,k), v_(x,k), v_(y,k)]^top$. With sample period $T = 0.01$~s (100~Hz IMU rate), the discrete-time state transition is

$ bold(x)_(k+1) = bold(A) bold(x)_k + bold(B) mat(hat(a)_(x,k); hat(a)_(y,k)) $

The IMU acceleration enters as system input $bold(u)_k$ rather than a measurement because it drives the state transition as the cause of position and velocity changes, not as an observation of the current state. Treating it as an input avoids extending the state vector with acceleration states; the IMU noise instead propagates into the filter through $bold(Q)_"IMU"$.

$ bold(A) = mat(1, 0, T, 0; 0, 1, 0, T; 0, 0, 1, 0; 0, 0, 0, 1), quad bold(B) = mat(frac(1,2) T^2, 0; 0, frac(1,2) T^2; T, 0; 0, T) $

GPS fixes provide position-only measurements through the linear observation model

$ bold(z)_k = bold(H) bold(x)_k, quad bold(H) = mat(1, 0, 0, 0; 0, 1, 0, 0) $

Latitude and longitude are converted to local East/North offsets in meters using a flat-Earth approximation ($R = 6\,371\,000$~m) centered on the first valid fix.

== Noise Covariances

Both matrices follow from the Week~3 static noise measurements @repo. The GPS covariance uses the position standard deviations (1.26~m East, 1.60~m North):

$ bold(R) = mat(sigma_(p_x)^2, 0; 0, sigma_(p_y)^2) = mat(1.255^2, 0; 0, 1.599^2) "m"^2 $

The process noise is propagated from the IMU accelerometer noise through the input matrix $bold(B)$. Since no additional process disturbances are modeled ($bold(Q) = bold(0)$):

$ bold(Q)_"total" = underbrace(bold(B) "Cov"(bold(eta)_k) bold(B)^top, bold(Q)_"IMU"), quad "Cov"(bold(eta)_k) = mat(sigma_(a_x)^2, 0; 0, sigma_(a_y)^2) $

with $sigma_(a_x) = 0.021$~m/s² and $sigma_(a_y) = 0.024$~m/s² from Week~3.

== ROS2 Implementation

A new `ament_python` package `sensor_fusion` was created containing two modules @repo. `linear_kalman_filter.py` is a self-contained LKF class; `predict()` advances the state and computes the Kalman gain, `correct()` applies a GPS position measurement. `sensor_fusion_node.py` subscribes to `/imu/data_raw` (100~Hz) and `/gps/fix` (1~Hz). IMU messages trigger `predict()`, GPS fixes trigger `correct()` followed by an immediate re-prediction. The predicted state is published as `nav_msgs/Odometry` on `/odom` at 100~Hz.


= Planned Work

Week~5 is the final project week. It will evaluate the fused localization against the GPS-only baseline in outdoor experiments, measuring position error and trajectory smoothness. If time allows, the fusion algorithm will be tested using a trajectory following controller. The updated project timeline is in @sec:appendix.


// ─── Appendix ──────────────────────────────────────────────────────────────────
#pagebreak()

= Appendix <sec:appendix>

#figure(
  table(
    columns: (auto, 1fr, auto),
    inset: 6pt,
    align: (center, left, center),
    table.header([*Week*], [*Task*], [*Status*]),
    [1], [Hardware assembly, sensor interface verification],                                              [#sym.checkmark],
    [2], [IMU accel/gyro reads, ROS2 environment and sensor nodes],                                      [#sym.checkmark],
    [3], [Static sensor noise characterization, filter parameter derivation],                            [#sym.checkmark],
    [4], [Linear Kalman Filter implementation, `sensor_fusion` ROS2 package],                           [#sym.checkmark],
    [5], [Field testing, localization evaluation, trajectory controller _(if schedule allows)_, final report], [],
  ),
  caption: [Project timeline. Weeks~1--4 complete.],
)
