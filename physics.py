import numpy as np

# ═══════════════════════════════════════════════════════════════════
#  PHYSICS ENGINE  —  BYU / SUPREM Constants (Deal-Grove)
# ═══════════════════════════════════════════════════════════════════

KB   = 8.617333e-5   # Boltzmann constant [eV/K]
N_OX = 1.46          # Refractive index of SiO2

T_REF = 1000.0 + 273.15  

PARAMS = {
    "Dry": {
        "Ea_B":  1.23,
        "Ea_BA": 2.00,
        "B0":    0.0117 * np.exp(1.23 / (KB * T_REF)),
        "BA0":   0.0450 * np.exp(2.00 / (KB * T_REF)), 
    },
    "Wet": {
        "Ea_B":  0.78,
        "Ea_BA": 2.05,
        "B0":    0.314  * np.exp(0.78 / (KB * T_REF)),
        "BA0":   1.21   * np.exp(2.05 / (KB * T_REF)),
    },
}

def _BG(T_C, P, mode, orientation="111"):
    p   = PARAMS[mode]
    T_K = T_C + 273.15
    B   = p["B0"]  * np.exp(-p["Ea_B"]  / (KB * T_K)) * P
    BA  = p["BA0"] * np.exp(-p["Ea_BA"] / (KB * T_K)) * P
    
    # Orientation scaling: Deal-Grove constants default to <111>.
    # For <100>, the linear rate B/A is reduced by a factor of 1.68.
    if orientation == "100":
        BA /= 1.68
        
    return B, BA

def oxide_thickness(T_C, P, t_hr, mode="Dry", orientation="111", x_i_nm=2.5):
    """Deal-Grove model incorporating initial thickness (tau shift)."""
    B, BA = _BG(T_C, P, mode, orientation)
    A     = B / BA
    x_i_um = x_i_nm / 1000.0
    
    # tau is the time it would have taken to grow the initial oxide
    tau = (x_i_um**2 + A * x_i_um) / B if x_i_um > 0 else 0.0
    
    disc  = A**2 + 4.0 * B * (t_hr + tau)
    x_um  = (-A + np.sqrt(max(disc, 0.0))) / 2.0
    return max(x_um * 1000.0, 0.0)

def growth_curve(T_C, P, t_max_hr, mode="Dry", orientation="111", x_i_nm=2.5, n=400):
    """Generates the array for the matplotlib plot."""
    B, BA = _BG(T_C, P, mode, orientation)
    A     = B / BA
    x_i_um = x_i_nm / 1000.0
    tau = (x_i_um**2 + A * x_i_um) / B if x_i_um > 0 else 0.0
    
    t     = np.linspace(0.0, t_max_hr, n)
    disc  = A**2 + 4.0 * B * (t + tau)
    x_nm  = (-A + np.sqrt(np.maximum(disc, 0.0))) / 2.0 * 1000.0
    return t, x_nm