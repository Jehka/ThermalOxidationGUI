from physics import N_OX, oxide_thickness

# ═══════════════════════════════════════════════════════════════════
#  THIN-FILM COLOR ENGINE & VALIDATION LOGIC
# ═══════════════════════════════════════════════════════════════════

def _wavelength_to_rgb(lam):
    if not (380 <= lam <= 780): return (0.55, 0.55, 0.55)
    if   380 <= lam < 440: r, g, b = -(lam-440)/(440-380), 0.0, 1.0
    elif 440 <= lam < 490: r, g, b = 0.0, (lam-440)/(490-440), 1.0
    elif 490 <= lam < 510: r, g, b = 0.0, 1.0, -(lam-510)/(510-490)
    elif 510 <= lam < 580: r, g, b = (lam-510)/(580-510), 1.0, 0.0
    elif 580 <= lam < 645: r, g, b = 1.0, -(lam-645)/(645-580), 0.0
    else:                  r, g, b = 1.0, 0.0, 0.0
    
    if   380 <= lam < 420: f = 0.3 + 0.7*(lam-380)/(420-380)
    elif 700 < lam <= 780: f = 0.3 + 0.7*(780-lam)/(780-700)
    else:                  f = 1.0
    return (r*f, g*f, b*f)

def thickness_to_color(x_nm):
    CHART = [
        (0,   10,  "#3A3A3A"), (10,  50,  "#C8A882"), (50,  70,  "#C8956A"),
        (70,  100, "#B8860B"), (100, 130, "#8B7355"), (130, 160, "#E8C86E"),
        (160, 190, "#F5E642"), (190, 220, "#FFA500"), (220, 260, "#FF6347"),
        (260, 310, "#DC143C"), (310, 360, "#4B0082"), (360, 410, "#0000CD"),
    ]
    if x_nm < 1.0: return "#3A3A3A", None, None

    best_lam, best_m, best_dist = None, None, float("inf")
    for m in range(0, 40):
        lam = 2.0 * N_OX * x_nm / (m + 0.5)
        if 400.0 <= lam <= 700.0:
            dist = abs(lam - 550.0)
            if dist < best_dist:
                best_dist = dist; best_lam = lam; best_m = m

    if best_lam is not None:
        r, g, b = _wavelength_to_rgb(best_lam)
        blend = 0.22
        r, g, b = min(1.0, r + blend*(1.0-r)), min(1.0, g + blend*(1.0-g)), min(1.0, b + blend*(1.0-b))
        return "#{:02X}{:02X}{:02X}".format(int(r*255), int(g*255), int(b*255)), best_m, best_lam

    for lo, hi, col in CHART:
        if lo <= x_nm < hi: return col, None, None
    return "#C8A882", None, None

def print_validation():
    print("=" * 65)
    print("  VALIDATION vs BYU Cleanroom Calculator (Includes Xi = 2.5nm)")
    print("=" * 65)
    cases = [
        (1000, 1.0, 1.0, "Dry", "111", 2.5, "BYU target ~38–39 nm"),
        (1000, 1.0, 1.0, "Dry", "100", 2.5, "Reduced B/A for <100>"),
    ]
    for T, P, t, mode, ori, xi, note in cases:
        x = oxide_thickness(T, P, t, mode, orientation=ori, x_i_nm=xi)
        hx, mo, lam = thickness_to_color(x)
        print(f"  {T}°C | {mode} ⟨{ori}⟩ | {t}hr → {x:6.1f} nm  ({note})")
    print("=" * 65)