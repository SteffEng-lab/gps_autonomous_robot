# GPS Autonomous Robot

A 5-week independent study project exploring GPS/IMU sensor fusion for precise localization on a small autonomous ground vehicle, with trajectory control as a follow-up application.

## Project Goals

**Primary**: Improve GPS positional accuracy by fusing GPS data with IMU measurements.

**Secondary**: Implement trajectory tracking/control using the fused localization output.

**Long-term (optional)**: Add camera and LiDAR for full autonomous navigation.

## Platform

![Full vehicle](01_Documents/01_Progress_Report_01/Media/Car_whole_view.jpeg)
![Rock5C compute board](01_Documents/01_Progress_Report_01/Media/Car_Rock5C_Closeup.jpeg)
![MPU-6050 IMU](01_Documents/01_Progress_Report_01/Media/Car_IMU_Closeup.jpeg)

**Compute**: Radxa Rock5C (RK3588S)

**Robot**: 4-wheeled RC car frame
- Ackermann front-wheel steering (servo)
- All-wheel drive via central BLDC motor
- Differential per axle

## Sensors

| Sensor | Interface | Role |
|--------|-----------|------|
| u-blox 7 USB GPS dongle | USB | Absolute position (GNSS) |
| MPU-6050 | I2C | Linear acceleration + angular velocity |

## Motor Controller (VESC)

The BLDC motor and steering servo are controlled by a VESC motor controller, configured via [VESC Tool](https://vesc-project.com/) — an open-source GUI application that connects over USB or UART. Key settings include motor type (BLDC), current limits, and servo output range.

![VESC Tool Start Screen](01_Documents/01_Progress_Report_01/Media/VESC_Tool_Start_Screen.png)
![VESC Tool General Settings](01_Documents/01_Progress_Report_01/Media/VESC_Tool_General_Settings_Screen.png)

## Software Stack

- **OS**: Linux (Rock5C)
- **Middleware**: ROS2
- **Sensor fusion**: -TBD-
- **GPS driver**: -TBD-
- **IMU driver**: -TBD-

## Architecture (planned)

-TBD-

## Project Structure

```
gps_autonomous_robot/
├── 01_Documents/          # Reports and references
└── README.md
```

## Status

- [x] Hardware platform selected
- [ ] Hardware assembly
- [ ] ROS2 environment setup on Rock5C
- [ ] GPS driver integration & testing
- [ ] IMU driver integration & testing
- [ ] EKF sensor fusion tuning
- [ ] Trajectory controller implementation
- [ ] Field testing

## Notes

- MPU-6050 provides 6-DOF (accel + gyro), no magnetometer
