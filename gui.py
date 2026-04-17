import tkinter as tk
from tkinter import font as tkfont
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import physics
import results

C = {
    "bg":    "0A0E14", "panel":  "141A22", "card":   "1A2030",
    "border":"2A3444", "text":   "E0E8F0", "muted":  "7A8FA0",
    "accent":"4FC3F7", "green":  "66BB6A", "dry":    "FFA726",
    "wet":   "29B6F6", "result": "FFD54F",
}

def _hex(key): return f"#{C[key]}"

class App:
    def __init__(self, root):
        self.root = root
        root.title("Thermal Oxidation — Deal–Grove  |  BYU/SUPREM Constants")
        root.configure(bg=_hex("bg"))
        root.minsize(1050, 720)
        self.current_x_nm = 0.0 # Track latest result for history
        self._fonts()
        self._ui()
        self._update()

    def _fonts(self):
        F = lambda s, w="normal": tkfont.Font(family="Courier New", size=s, weight=w)
        self.fT = F(14,"bold"); self.fL = F(9); self.fV = F(11,"bold")
        self.fR = F(20,"bold"); self.fS = F(8); self.fM = F(10)

    def _ui(self):
        hdr = tk.Frame(self.root, bg=_hex("panel"), pady=9, highlightbackground=_hex("border"), highlightthickness=1)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⬡  THERMAL OXIDATION CALCULATOR", font=self.fT, fg=_hex("accent"), bg=_hex("panel")).pack(side="left", padx=18)
        tk.Label(hdr, text="Deal–Grove  |  BYU/SUPREM Physics", font=self.fS, fg=_hex("muted"), bg=_hex("panel")).pack(side="right", padx=18)
        
        body = tk.Frame(self.root, bg=_hex("bg"))
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg=_hex("bg"), width=360)
        left.pack(side="left", fill="y", padx=(14,6), pady=14)
        left.pack_propagate(False)

        right = tk.Frame(body, bg=_hex("bg"))
        right.pack(side="left", fill="both", expand=True, padx=(0,14), pady=14)

        self._controls(left)
        self._chart(right)
        self._stats(right)
        self._history(right) # <--- New History Component

    def _controls(self, p):
        def card(title, col="accent"):
            f = tk.Frame(p, bg=_hex("card"), highlightbackground=_hex("border"), highlightthickness=1, padx=10, pady=8)
            f.pack(fill="x", pady=(0,9))
            tk.Label(f, text=title, font=self.fS, fg=_hex(col), bg=_hex("card")).pack(anchor="w")
            return f

        def slider(parent, label, lo, hi, res, var, fmt):
            row = tk.Frame(parent, bg=_hex("card")); row.pack(fill="x", pady=3)
            hdr = tk.Frame(row,   bg=_hex("card")); hdr.pack(fill="x")
            tk.Label(hdr, text=label, font=self.fL, fg=_hex("muted"), bg=_hex("card"), width=16, anchor="w").pack(side="left")
            vl = tk.Label(hdr, text=fmt(var.get()), font=self.fV, fg=_hex("accent"), bg=_hex("card"), width=10, anchor="e")
            vl.pack(side="right")
            def cmd(v, lbl=vl, f=fmt):
                lbl.config(text=f(float(v))); self._update()
            tk.Scale(row, from_=lo, to=hi, resolution=res, orient="horizontal", variable=var, showvalue=False, command=cmd,
                     bg=_hex("card"), fg=_hex("text"), troughcolor=_hex("panel"), activebackground=_hex("accent"), highlightthickness=0).pack(fill="x")

        # Mode
        mc = card("OXIDATION MODE")
        self.mode = tk.StringVar(value="Dry")
        for m, col in (("Dry","dry"), ("Wet","wet")):
            tk.Radiobutton(mc, text="Dry  O₂" if m=="Dry" else "Wet  H₂O", variable=self.mode, value=m, command=self._update,
                           font=self.fL, fg=_hex(col), bg=_hex("card"), selectcolor=_hex("panel"), activeforeground=_hex(col), activebackground=_hex("card")).pack(side="left", padx=10)

        # Orientation
        oc = card("CRYSTAL ORIENTATION")
        self.ori = tk.StringVar(value="111")
        for o in ("111", "100"):
            tk.Radiobutton(oc, text=f"⟨{o}⟩", variable=self.ori, value=o, command=self._update,
                           font=self.fL, fg=_hex("text"), bg=_hex("card"), selectcolor=_hex("panel"), activebackground=_hex("card")).pack(side="left", padx=10)

        self.xi = tk.DoubleVar(value=2.5) # Default 25A Native Oxide
        slider(card("INITIAL THICKNESS"), "x_i (nm)", 0, 50, 0.5, self.xi, lambda v: f"{v:.1f} nm")

        self.T = tk.DoubleVar(value=1000.0)
        slider(card("TEMPERATURE"), "T  (°C)", 800, 1200, 10, self.T, lambda v: f"{v:.0f} °C")

        self.P = tk.DoubleVar(value=1.0)
        slider(card("PRESSURE"), "P  (atm)", 0.1, 15.0, 0.1, self.P, lambda v: f"{v:.2f} atm")

        self.t = tk.DoubleVar(value=60.0)
        slider(card("OXIDATION TIME"), "t  (min)", 1, 600, 1, self.t, lambda v: f"{v:.0f} min")

        # Color Box
        cc = card("THIN-FILM INTERFERENCE COLOR", col="green")
        self.cvs  = tk.Canvas(cc, height=60, bg=_hex("panel"), highlightthickness=0)
        self.cvs.pack(fill="x", pady=4)
        self.rect = self.cvs.create_rectangle(0, 0, 360, 60, fill="#888888", outline="")
        self.clbl = tk.Label(cc, text="—", font=self.fM, fg=_hex("muted"), bg=_hex("card"))
        self.clbl.pack()

    def _chart(self, parent):
        ff = tk.Frame(parent, bg=_hex("card"), highlightbackground=_hex("border"), highlightthickness=1)
        ff.pack(fill="both", expand=True)
        self.fig = Figure(figsize=(5.5, 3.0), facecolor=_hex("card"))
        self.ax  = self.fig.add_subplot(111)
        self.ax.set_facecolor(_hex("panel"))
        for sp in self.ax.spines.values(): sp.set_edgecolor(_hex("border"))
        self.ax.tick_params(colors=_hex("muted"), labelsize=8)
        self.ax.set_title("Deal–Grove Growth Curve", color=_hex("text"), fontsize=9, pad=5)
        self.fig.tight_layout(pad=1.4)
        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=ff)
        self.canvas_fig.get_tk_widget().pack(fill="both", expand=True)

    def _stats(self, parent):
        sf = tk.Frame(parent, bg=_hex("panel"), highlightbackground=_hex("border"), highlightthickness=1, pady=6)
        sf.pack(fill="x", pady=(8,0))
        def cell(lbl, attr, unit, col="result"):
            c = tk.Frame(sf, bg=_hex("panel"), padx=14); c.pack(side="left", expand=True)
            tk.Label(c, text=lbl,  font=self.fS, fg=_hex("muted"), bg=_hex("panel")).pack()
            w = tk.Label(c, text="—", font=self.fR, fg=_hex(col),  bg=_hex("panel")); w.pack()
            tk.Label(c, text=unit, font=self.fS, fg=_hex("muted"), bg=_hex("panel")).pack()
            setattr(self, attr, w)
        cell("THICKNESS", "s_nm",  "nm", "result")
        tk.Frame(sf, bg=_hex("border"), width=1).pack(side="left", fill="y", pady=6)
        cell("THICKNESS", "s_um",  "µm", "muted")
        tk.Frame(sf, bg=_hex("border"), width=1).pack(side="left", fill="y", pady=6)
        cell("λ DOMINANT","s_lam", "nm", "green")

    def _history(self, parent):
        hf = tk.Frame(parent, bg=_hex("panel"), highlightbackground=_hex("border"), highlightthickness=1)
        hf.pack(fill="both", expand=True, pady=(8,0))
        
        hdr = tk.Frame(hf, bg=_hex("card"), pady=5)
        hdr.pack(fill="x")
        tk.Label(hdr, text="HISTORY LOG (Last 10)", font=self.fS, fg=_hex("accent"), bg=_hex("card")).pack(side="left", padx=10)
        
        save_btn = tk.Button(hdr, text="💾 Save Result", command=self._save_history, 
                             bg=_hex("border"), fg=_hex("text"), font=self.fS, 
                             relief="flat", activebackground=_hex("accent"), activeforeground=_hex("bg"))
        save_btn.pack(side="right", padx=10)
        
        self.hist_list = tk.Listbox(hf, bg=_hex("panel"), fg=_hex("text"), font=self.fM, 
                                    selectbackground=_hex("border"), highlightthickness=0, borderwidth=0)
        self.hist_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.history_data = []

    def _save_history(self):
        m = self.mode.get()
        o = self.ori.get()
        T = self.T.get()
        t = self.t.get()
        xi = self.xi.get()
        
        entry = f"{m} ⟨{o}⟩ | xi: {xi}nm | {T:.0f}°C | {t:.0f}min  ➜  {self.current_x_nm:.1f} nm"
        self.history_data.insert(0, entry)
        if len(self.history_data) > 10:
            self.history_data.pop()
            
        self.hist_list.delete(0, tk.END)
        for i, item in enumerate(self.history_data):
            self.hist_list.insert(tk.END, f" {i+1}.   {item}")

    def _update(self, *_):
        T_C  = self.T.get(); P = self.P.get()
        t_hr = self.t.get() / 60.0; mode = self.mode.get()
        ori  = self.ori.get(); xi = self.xi.get()

        x_nm   = physics.oxide_thickness(T_C, P, t_hr, mode, ori, xi)
        self.current_x_nm = x_nm # Track state for history
        
        t_max  = max(t_hr * 1.6, 0.3)
        ts, xs = physics.growth_curve(T_C, P, t_max, mode, ori, xi)
        hex_col, m_ord, lam = results.thickness_to_color(x_nm)

        # Chart update
        ax = self.ax; ax.clear()
        ax.set_facecolor(_hex("panel"))
        lc = C["dry"] if mode=="Dry" else C["wet"]
        ax.plot(ts, xs, color=f"#{lc}", lw=2, label=f"{mode} ⟨{ori}⟩")
        ax.axvline(t_hr, color=f"#{C['muted']}", lw=1, ls="--", alpha=0.5)
        ax.axhline(x_nm, color=f"#{C['accent']}", lw=1, ls="--", alpha=0.5)
        ax.scatter([t_hr], [x_nm], color=f"#{C['accent']}", zorder=6, s=60)
        for sp in ax.spines.values(): sp.set_edgecolor(_hex("border"))
        ax.tick_params(colors=_hex("muted"), labelsize=8)
        ax.legend(facecolor=_hex("card"), edgecolor=_hex("border"), labelcolor=_hex("text"), fontsize=8)
        self.canvas_fig.draw_idle()

        # Swatch and Stats update
        self.cvs.itemconfig(self.rect, fill=hex_col)
        self.clbl.config(text=f"λ ≈ {lam:.1f} nm   |   m = {m_ord}" if lam else "Empirical chart (Tan/Brown)")
        self.s_nm.config(text=f"{x_nm:.1f}"); self.s_um.config(text=f"{x_nm/1000:.4f}")
        self.s_lam.config(text=f"{lam:.1f}" if lam else "—")