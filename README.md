# Thermal Oxidation Calculator: Deal-Grove Simulation

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Physics](https://img.shields.io/badge/Domain-Semiconductor_Physics-purple)
![UI](https://img.shields.io/badge/GUI-Tkinter-lightgrey)

A comprehensive physical simulation and interactive dashboard for predicting the growth of silicon dioxide ($SiO_2$) on silicon wafers. This application leverages the industry-standard **Deal-Grove Model** using BYU/SUPREM physical constants to calculate oxide thickness, generate growth curves, and predict the resulting thin-film interference color of the wafer.

## 📑 Table of Contents
1. [Project Overview](#-project-overview)
2. [The Physics: Deal-Grove Model](#-the-physics-deal-grove-model)
3. [Thin-Film Interference (Optical Model)](#-thin-film-interference-optical-model)
4. [Software Architecture](#-software-architecture)
5. [Features](#-features)
6. [Installation & Setup](#-installation--setup)
7. [Usage Guide](#-usage-guide)

---

## 🚀 Project Overview
In semiconductor manufacturing, growing a highly controlled layer of $SiO_2$ on a bare silicon wafer is a foundational step. This project provides a graphical tool for process engineers and students to simulate thermal oxidation without needing access to a cleanroom or heavy TCAD software. It calculates the final oxide thickness based on temperature, pressure, time, oxidation mode (Wet/Dry), and crystal orientation, while providing a real-time graphical plot and color visualization.

---

## 🔬 The Physics: Deal-Grove Model

The core of the simulation relies on the **Deal-Grove model**, which mathematically describes the kinetics of oxide growth. The relationship between oxide thickness ($x$) and oxidation time ($t$) is given by the general rate equation:

$$x^2 + Ax = B(t + \tau)$$

Solving this quadratic equation for $x$ yields the thickness at any given time. The behavior is governed by two primary rate constants:

### 1. Parabolic Rate Constant ($B$)
Dominates the reaction for **thick oxides**. At this stage, the process is *diffusion-limited* because the oxidant ($O_2$ or $H_2O$) must travel through the existing oxide layer to reach the silicon interface.

### 2. Linear Rate Constant ($B/A$)
Dominates the reaction for **thin oxides**. At this stage, the process is *reaction-rate limited* by how fast the oxidant can chemically bond with the silicon atoms at the $Si-SiO_2$ interface.

### Arrhenius Temperature Dependence
Both $B$ and $B/A$ are highly sensitive to the furnace temperature ($T$) and are modeled using Arrhenius equations:

$$B = B_0 \cdot \exp\left(-\frac{E_{a,B}}{k_B T}\right) \cdot P$$
$$\frac{B}{A} = \left(\frac{B}{A}\right)_0 \cdot \exp\left(-\frac{E_{a,B/A}}{k_B T}\right) \cdot P$$

Where:
* $k_B$ = Boltzmann constant ($8.617 \times 10^{-5}$ eV/K)
* $T$ = Temperature in Kelvin
* $P$ = Pressure in atmospheres
* $E_a$ = Activation energy (varies strictly between Dry $O_2$ and Wet $H_2O$ environments)

### Initial Thickness Shift ($\tau$)
Real wafers often have a native oxide layer ($\approx 2.5$ nm) before entering the furnace. $\tau$ calculates the hypothetical time it would have taken to grow this initial layer ($x_i$), shifting the time axis to ensure accurate forward modeling:
$$\tau = \frac{x_i^2 + A x_i}{B}$$

### Crystal Orientation Dependency
The linear rate constant is sensitive to the atomic density of the silicon surface. The script defaults to the `<111>` orientation. For `<100>` silicon (which has fewer available bonds at the surface), the $B/A$ constant is mathematically reduced by a factor of **1.68**.

---

## 🌈 Thin-Film Interference (Optical Model)

As the transparent $SiO_2$ layer grows, light reflecting off the top of the oxide interferes with light reflecting off the silicon interface below. This creates specific visual colors on the wafer surface. 

The application calculates the dominant visible wavelength ($\lambda$) using the condition for constructive interference:

$$\lambda = \frac{2 \cdot N_{ox} \cdot x_{nm}}{m + 0.5}$$

Where:
* $N_{ox}$ = Refractive index of $SiO_2$ ($\approx 1.46$)
* $m$ = The interference order (integer)
* $x_{nm}$ = Oxide thickness in nanometers

The `results.py` engine iterates through visible wavelengths (380nm - 780nm) to find the closest match to $550nm$ (the peak sensitivity of the human eye) and converts that dominant wavelength into a calibrated RGB Hex code for UI rendering.

---

## 🏗 Software Architecture

The project is modularized into four cleanly separated Python scripts:

* **`physics.py` (The Backend):** Contains the physical constants, Arrhenius calculations (`_BG`), the quadratic solver (`oxide_thickness`), and the vector-based growth curve generator.
* **`results.py` (The Optical Engine):** Houses the `wavelength_to_rgb` conversion logic and the fallback empirical color charting. It also includes the `print_validation` routine to ensure mathematical accuracy against BYU cleanroom data.
* **`gui.py` (The Frontend):** An object-oriented `tkinter` application. It manages the state of the sliders, coordinates the Matplotlib `FigureCanvasTkAgg` plotting, renders the dynamic color swatch, and handles the historical data log.
* **`main.py` (The Entry Point):** Bootstraps the application by running backend validation checks and initializing the main UI event loop.

---

## ✨ Features
* **Real-Time Parameter Adjustment:** Sliders for Temperature ($800-1200^\circ C$), Pressure ($0.1-15$ atm), Time, and Initial Thickness update the calculations instantly.
* **Dynamic Matplotlib Integration:** The Deal-Grove growth curve is plotted dynamically inside the Tkinter window, highlighting the specific time/thickness target.
* **Optical Wafer Simulation:** Generates the exact hex-color visual representation of what the physical wafer would look like under cleanroom lighting.
* **History Logger:** A built-in tracking log allowing users to save and compare up to 10 previous simulation results side-by-side.

---

## ⚙️ Installation & Setup

### Prerequisites
You need **Python 3.8+** and the following scientific computing libraries:

```bash
pip install numpy matplotlib

*(Note: `tkinter` is part of the standard Python library, but Linux users may need to install it via their package manager, e.g., `sudo apt-get install python3-tk`).*
```

### Running the Application
Clone the repository and run the main application file:
```bash
python main.py

```
---

## 📖 Usage Guide
1. Define the Environment: Select Dry $O_2$ (slower growth, denser oxide) or Wet $H_2O$ (faster growth, steam-based).
2. Select the Lattice: Choose your wafer's crystal orientation (<111> or <100>).
3. Dial in the Variables: Use the sliders to input your initial native oxide ($x_i$), target temperature ($T$), furnace pressure ($P$), and desired time in the tube ($t$).
4. Read the Output: Look at the bottom-right metrics panel for the exact physical thickness in nanometers and micrometers.
5. Save Configuration: Click "Save Result" to log the exact parameters into the history sidebar for process comparison.

---
---
