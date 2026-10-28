# Automated Imagery Unit & Incubator Hardware Testing Suite

![Platform](https://img.shields.io/badge/Platform-Raspberry_Pi-C51A4A?style=for-the-badge&logo=raspberrypi&logoColor=white)
![Language](https://img.shields.io/badge/Language-Python_3-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Vision](https://img.shields.io/badge/Computer_Vision-OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Hardware-Operational-brightgreen?style=for-the-badge)

An automated biomedical laboratory platform engineered on **Raspberry Pi** for motorized multi-dish specimen positioning, high-precision camera autofocusing, 7×7 tile mosaic imaging, and closed-loop incubator thermal profiling.

---

## 👨‍💻 Developer & Attribution

| Attribute | Details |
|---|---|
| **Engineer** | **Engr. Hanif Khan** |
| **Title** | Hardware & Embedded Systems Engineer |
| **Institution** | Centre of Intelligent Systems & Network Research (CISNR), UET Peshawar |
| **WhatsApp / Phone** | [+92 315 9915537](https://wa.me/923159915537) |
| **LinkedIn** | [Engr. Hanif Khan Profile](https://www.linkedin.com/in/engr-hanif-khan-628a04259/) |
| **Email** | [Hanifullahshams@gmail.com](mailto:Hanifullahshams@gmail.com) |

---

## 🔬 System Overview

This hardware testing suite provides automated motion control and computer-vision-driven diagnostics for a multi-dish incubator imaging unit:

1. **3-Axis Motor Control:** Stepper motors and high-current H-bridges (**BTS7960**) manage X, Y, and Z axes for tray positioning and optical focusing.
2. **Limit Switch Homing:** Optical and mechanical limit switches ensure repeatable zeroing and safe motion boundaries.
3. **Automated 10-Petri Dish Tray Management:** Organized in a 2-row × 5-column motorized tray configuration with individual dish coordinate offsets.
4. **7×7 Grid Mosaic Imaging:** High-resolution microscopic tile capture with automated sub-dish step travel and seamless mosaic stitching.
5. **Incubation Temperature Regulation:** Closed-loop thermal regulation ($20^\circ\text{C}$ to $55^\circ\text{C}$) supporting up to 50 configurable study cycles.
6. **Diagnostic Master GUI:** Interactive dark-themed Tkinter workstation for manual calibration, live camera feed inspection, and automated batch runs.

---

## ⚡ Hardware Pinout Configuration (Raspberry Pi BCM)

| Component / Function | BCM GPIO | Type | Description |
|---|---|---|---|
| **Motor 1 Direction (M1_CW)** | GPIO 17 | Output | X-Axis Stepper direction |
| **Motor 1 Clock (M1_CLK)** | GPIO 18 | Output | X-Axis Stepper pulse |
| **Motor 2 Direction (M2_CW)** | GPIO 27 | Output | Y-Axis Stepper direction |
| **Motor 2 Clock (M2_CLK)** | GPIO 22 | Output | Y-Axis Stepper pulse |
| **Motor 3 Direction (M3_CW)** | GPIO 23 | Output | Z-Focus Stepper direction |
| **Motor 3 Clock (M3_CLK)** | GPIO 24 | Output | Z-Focus Stepper pulse |
| **Heater / Fan Relay** | GPIO 25 | Output | Incubator heating element control |
| **BTS7960 Driver 1 (RPWM)** | GPIO 26 | PWM Output | High-power DC actuator drive |
| **BTS7960 Driver 2 (RPWM)** | GPIO 19 | PWM Output | High-power DC actuator drive |
| **Limit Switch 1 (M1 Limit)** | GPIO 8 | Input (Pull-up) | X-Axis home limit detection |
| **Limit Switch 2 (M2 Limit)** | GPIO 6 | Input (Pull-up) | Y-Axis home limit detection |
| **Limit Switch 3 (M3 Limit)** | GPIO 13 | Input (Pull-up) | Z-Axis / Focus limit detection |

---

## 📁 Repository Structure

```text
automatic_imagery_unit_hardware_testing_tool/
├── automatic_imagery_unit_hardware_testing_tool.py  # Diagnostic Master GUI & hardware test harness
├── device_config.py                                 # Grid steps, tray offsets, and incubation constants
├── imaging.py                                       # 7x7 tile capture, image preprocessing & stitching
├── camera_module.py                                 # Camera feed initialization & streaming
├── camera_focus_test.py                             # Optical autofocus calibration routines
├── petri_dishes.py                                  # 10-dish tray geometry and coordinate math
├── incubation_module.py                             # Closed-loop thermal PID/relay control logic
├── incubation_gui.py                                # Incubation cycle monitoring dashboard
├── workflow_steps.py                                # Automated multi-step study runner
├── relays.py / relay_control.py                     # GPIO relay switching interfaces
├── motor1.py / motor2.py / motor3.py                # Dedicated single-axis diagnostic scripts
└── temp.py / temp1.py                               # Thermal sensor calibration
```

---

## 🚀 Setup & Execution

### 1. Prerequisites
Ensure your Raspberry Pi is running Raspberry Pi OS with camera and GPIO enabled:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-tk python3-opencv
pip3 install RPi.GPIO pillow
```

### 2. Launching Hardware Diagnostics
```bash
python3 automatic_imagery_unit_hardware_testing_tool.py
```

### 3. Automated Study Workflow
```bash
python3 workflow_steps.py
```

---

## 📞 Support & Inquiries
For hardware engineering inquiries, circuit design, or embedded software development:
- **Engr. Hanif Khan** — [+92 315 9915537](https://wa.me/923159915537)
- **Email:** [Hanifullahshams@gmail.com](mailto:Hanifullahshams@gmail.com)
