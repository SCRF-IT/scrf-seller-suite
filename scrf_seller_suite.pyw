#!/usr/bin/env python3
"""
SCRF Seller Suite - AI Reseller Workstation
Starchild Rare Finds | Powered by Claude
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import base64
import os
import urllib.request
import urllib.error

# ── THEME ──────────────────────────────────────────────────────────────────
BG        = "#0d0d16"
SURF      = "#13131f"
ELEV      = "#1c1c30"
CARD      = "#22223a"
CARD2     = "#2a2a44"
BORDER    = "#383860"
BORDER_HI = "#5a5a90"
STAR      = "#e8ff47"
PLASMA    = "#c044ff"
NEON      = "#00ffcc"
EMBER     = "#ff6b35"
SUCCESS   = "#00e676"
T1        = "#ffffff"
T2        = "#c0c0e0"
T3        = "#7070a0"
T4        = "#454568"

FONT_MONO   = ("Courier New", 10)
FONT_MONO_S = ("Courier New", 9)
FONT_MONO_B = ("Courier New", 11, "bold")
FONT_DISP   = ("Arial", 14, "bold")
FONT_DISP_L = ("Arial", 20, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_BODY_S = ("Segoe UI", 9)
FONT_LABEL  = ("Courier New", 8, "bold")

MODEL = "claude-sonnet-4-5"

def _apply_dark_titlebar(win):
    try:
        import ctypes
        hwnd = ctypes.windll.user32.GetParent(win.winfo_id())
        if not hwnd:
            hwnd = win.winfo_id()
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(ctypes.c_int(1)), 4)
    except Exception:
        pass


class Tag(tk.Label):
    """Small colored pill label."""
    def __init__(self, parent, text, fg=T3, bg=CARD2, **kw):
        super().__init__(parent, text=f"  {text}  ", font=FONT_LABEL,
                         fg=fg, bg=bg, padx=0, pady=2, **kw)


class Divider(tk.Frame):
    def __init__(self, parent, color=BORDER, **kw):
        super().__init__(parent, bg=color, height=1, **kw)


class SectionLabel(tk.Frame):
    def __init__(self, parent, text, color=T3, **kw):
        super().__init__(parent, bg=BG, **kw)
        tk.Label(self, text=text, font=FONT_LABEL, bg=BG, fg=color).pack(side="left")
        tk.Frame(self, bg=BORDER, height=1).pack(side="left", fill="x", expand=True, padx=(8, 0), pady=1)


class Card(tk.Frame):
    """Bordered card with optional accent color."""
    def __init__(self, parent, border=BORDER, bg=CARD, pad=14, **kw):
        super().__init__(parent, bg=border, **kw)
        self._inner = tk.Frame(self, bg=bg, padx=pad, pady=pad)
        self._inner.pack(fill="both", expand=True, padx=1, pady=1)

    def inner(self):
        return self._inner


class SCRFApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SCRF // Seller Suite")
        self.configure(bg=BG)
        self.geometry("800x920")
        self.minsize(720, 700)

        self._api_key_value = ""
        self._photo_b64 = None       # base64 string of uploaded image
        self._photo_mime = "image/jpeg"
        self.active_social = tk.StringVar(value="ig")
        self.social_texts = {}

        # Window icon — place scrf.ico in same folder as this file
        try:
            import sys, os
            base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            self.iconbitmap(os.path.join(base, "scrf.ico"))
        except Exception:
            pass

        self._build()
        self.after(200, lambda: _apply_dark_titlebar(self))

    # ─────────────────────────────────────────────────────────────── BUILD ──
    def _build(self):
        self._build_header()
        self._build_scrollbody()

    def _build_header(self):
        hdr = tk.Frame(self, bg=SURF)
        hdr.pack(fill="x")
        # Accent line at top
        tk.Frame(hdr, bg=PLASMA, height=2).pack(fill="x")
        inner = tk.Frame(hdr, bg=SURF, pady=12)
        inner.pack(fill="x")
        tk.Label(inner, text="SCRF", font=("Courier New", 22, "bold"),
                 bg=SURF, fg=STAR).pack(side="left", padx=(20, 0))
        tk.Label(inner, text=" // SELLER SUITE", font=("Courier New", 14, "bold"),
                 bg=SURF, fg=T2).pack(side="left")
        tk.Label(inner, text="starchild rare finds", font=FONT_BODY_S,
                 bg=SURF, fg=T4).pack(side="left", padx=(16, 0))

        right = tk.Frame(inner, bg=SURF)
        right.pack(side="right", padx=20)
        dot = tk.Canvas(right, width=8, height=8, bg=SURF, highlightthickness=0)
        dot.create_oval(1, 1, 7, 7, fill=NEON, outline="")
        dot.pack(side="left", pady=2)
        tk.Label(right, text=" AI POWERED", font=FONT_LABEL, bg=SURF, fg=NEON).pack(side="left")

    def _build_scrollbody(self):
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self.body = tk.Frame(self._canvas, bg=BG)
        self._body_win = self._canvas.create_window((0, 0), window=self.body, anchor="nw")
        self.body.bind("<Configure>", lambda e: self._canvas.configure(
            scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(
            self._body_win, width=e.width))
        self._canvas.bind_all("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        self._build_api_section()
        self._build_form()
        self._build_go_button()

        # status + progress
        self.status_var = tk.StringVar(value="")
        self._status_lbl = tk.Label(self.body, textvariable=self.status_var,
                                     font=FONT_BODY_S, bg=BG, fg=T3)
        self._status_lbl.pack(padx=20, anchor="w", pady=(2, 0))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("SCRF.Horizontal.TProgressbar",
                         background=NEON, troughcolor=ELEV, borderwidth=0, thickness=2)
        self._progress = ttk.Progressbar(self.body, style="SCRF.Horizontal.TProgressbar",
                                          mode="indeterminate")
        self._progress.pack(fill="x", padx=20, pady=(2, 0))

        self._results_frame = tk.Frame(self.body, bg=BG)
        # Don't pack until we have results

    # ─────────────────────────────────────── API KEY SECTION ──
    def _build_api_section(self):
        SectionLabel(self.body, "⚡ API KEY").pack(fill="x", padx=20, pady=(16, 6))

        self._key_container = tk.Frame(self.body, bg=BG)
        self._key_container.pack(fill="x", padx=20, pady=(0, 10))

        # Entry state
        self._key_entry_frame = tk.Frame(self._key_container, bg=ELEV,
                                          highlightbackground=BORDER,
                                          highlightthickness=1)
        self._key_entry_frame.pack(fill="x")

        row = tk.Frame(self._key_entry_frame, bg=ELEV)
        row.pack(fill="x", padx=10, pady=8)

        self._key_entry = tk.Entry(row, show="●", bg=ELEV, fg=T2,
                                    insertbackground=T1, relief="flat",
                                    font=FONT_MONO, bd=0)
        self._key_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self._key_entry.bind("<Return>", lambda e: self._save_key())

        self._save_btn = tk.Button(row, text="SAVE  →", font=FONT_LABEL,
                                    bg=PLASMA, fg=BG, relief="flat",
                                    activebackground="#d060ff", activeforeground=BG,
                                    cursor="hand2", padx=10, pady=5,
                                    command=self._save_key)
        self._save_btn.pack(side="right")

        tk.Label(self._key_entry_frame,
                 text="  console.anthropic.com → API Keys  ·  never stored to disk",
                 font=FONT_LABEL, bg=ELEV, fg=T4).pack(anchor="w", padx=10, pady=(0, 6))

        # Saved state (hidden until key is saved)
        self._key_saved_frame = tk.Frame(self._key_container, bg=ELEV,
                                          highlightbackground=BORDER,
                                          highlightthickness=1)
        row2 = tk.Frame(self._key_saved_frame, bg=ELEV)
        row2.pack(fill="x", padx=12, pady=10)
        dot2 = tk.Canvas(row2, width=8, height=8, bg=ELEV, highlightthickness=0)
        dot2.create_oval(1, 1, 7, 7, fill=SUCCESS, outline="")
        dot2.pack(side="left", pady=2)
        tk.Label(row2, text="  API key saved for this session",
                 font=FONT_MONO_S, bg=ELEV, fg=SUCCESS).pack(side="left")
        tk.Button(row2, text="change", font=FONT_LABEL, bg=ELEV, fg=T3,
                  relief="flat", cursor="hand2", command=self._show_key_entry
                  ).pack(side="right")

    def _save_key(self):
        key = self._key_entry.get().strip()
        if not key:
            return
        self._api_key_value = key
        self._key_entry_frame.pack_forget()
        self._key_saved_frame.pack(fill="x")
        self.status_var.set("")

    def _show_key_entry(self):
        self._key_saved_frame.pack_forget()
        self._key_entry.delete(0, "end")
        self._key_entry_frame.pack(fill="x")

    # ─────────────────────────────────────────────── FORM ──
    def _build_form(self):
        SectionLabel(self.body, "ITEM DETAILS").pack(fill="x", padx=20, pady=(14, 6))

        form = tk.Frame(self.body, bg=BG)
        form.pack(fill="x", padx=20)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        # Item name
        self._flabel(form, "ITEM NAME / DESCRIPTION").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 3))
        self._iname = self._entry(form)
        self._iname.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Category / Condition
        self._flabel(form, "CATEGORY").grid(row=2, column=0, sticky="w", pady=(0, 3))
        self._flabel(form, "CONDITION").grid(row=2, column=1, sticky="w", pady=(0, 3), padx=(8, 0))

        cats = ["Auto-detect", "Trading Cards", "Video Games / Consoles", "Vinyl Records",
                "VHS / Physical Media", "Retro Electronics", "Toys & Figures",
                "Antiques / Vintage", "Clothing / Accessories", "Other Collectibles"]
        self._icat = self._optmenu(form, cats)
        self._icat.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        conds = ["New / Sealed", "Near Mint", "Very Good", "Good",
                 "Acceptable / Played", "For Parts / As-Is"]
        self._icond = self._optmenu(form, conds)
        self._icond.grid(row=3, column=1, sticky="ew", pady=(0, 10), padx=(8, 0))

        # Buy price / Platform
        self._flabel(form, "BUY PRICE ($)").grid(row=4, column=0, sticky="w", pady=(0, 3))
        self._flabel(form, "TARGET PLATFORM").grid(row=4, column=1, sticky="w", pady=(0, 3), padx=(8, 0))

        self._ibuy = self._entry(form, width=16)
        self._ibuy.grid(row=5, column=0, sticky="ew", pady=(0, 10))

        platforms = ["eBay", "Hello Skip", "Facebook Marketplace", "Mercari", "OfferUp"]
        self._iplatform = self._optmenu(form, platforms)
        self._iplatform.grid(row=5, column=1, sticky="ew", pady=(0, 10), padx=(8, 0))

        # Notes
        self._flabel(form, "NOTES  (flaws · extras · variants · what's included)").grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(0, 3))
        note_frame = tk.Frame(form, bg=BORDER, highlightthickness=0)
        note_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 2))
        self._inotes = tk.Text(note_frame, bg=ELEV, fg=T2, insertbackground=T1,
                                relief="flat", font=FONT_BODY, height=4,
                                wrap="word", bd=6)
        self._inotes.pack(fill="both", expand=True, padx=1, pady=1)

        # Photo upload
        self._flabel(form, "PHOTOS  (optional — Claude will identify & auto-fill)").grid(
            row=8, column=0, columnspan=2, sticky="w", pady=(10, 3))
        photo_row = tk.Frame(form, bg=BG)
        photo_row.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0, 4))

        self._photo_btn = tk.Button(photo_row, text="📷  UPLOAD PHOTO",
                                     font=FONT_LABEL, bg=ELEV, fg=T2,
                                     relief="flat", cursor="hand2",
                                     highlightthickness=1, highlightbackground=BORDER,
                                     padx=12, pady=7, command=self._upload_photo)
        self._photo_btn.pack(side="left")

        self._photo_lbl = tk.Label(photo_row, text="no photo attached",
                                    font=FONT_LABEL, bg=BG, fg=T4)
        self._photo_lbl.pack(side="left", padx=(10, 0))

    def _upload_photo(self):
        path = filedialog.askopenfilename(
            title="Select item photo",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.gif"), ("All files", "*.*")]
        )
        if not path:
            return
        ext = os.path.splitext(path)[1].lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                    ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif"}
        self._photo_mime = mime_map.get(ext, "image/jpeg")
        with open(path, "rb") as f:
            self._photo_b64 = base64.standard_b64encode(f.read()).decode("utf-8")
        fname = os.path.basename(path)
        self._photo_lbl.configure(text=f"✓  {fname}", fg=SUCCESS)
        self._photo_btn.configure(text="📷  CHANGE PHOTO", fg=NEON)

    # ─────────────────────────────────────────── GO BUTTON ──
    def _build_go_button(self):
        f = tk.Frame(self.body, bg=BG)
        f.pack(fill="x", padx=20, pady=(14, 6))

        self._go_btn = tk.Button(f, text="⚡  ANALYZE  +  GENERATE EVERYTHING",
                                  font=("Courier New", 11, "bold"),
                                  bg=STAR, fg="#050510", relief="flat",
                                  activebackground="#f5ff20", activeforeground="#050510",
                                  cursor="hand2", pady=11, command=self._run)
        self._go_btn.pack(fill="x")

    # ─────────────────────────────────────────── RESULTS ──
    def _render_results(self, d):
        for w in self._results_frame.winfo_children():
            w.destroy()
        self._results_frame.pack(fill="x", padx=20, pady=(10, 30))

        # ── Verdict + ROI row ──
        SectionLabel(self._results_frame, "ANALYSIS").pack(fill="x", pady=(0, 8))
        top_row = tk.Frame(self._results_frame, bg=BG)
        top_row.pack(fill="x", pady=(0, 6))
        top_row.columnconfigure(0, weight=1)
        top_row.columnconfigure(1, weight=1)

        verdict_map = {"FLIP NOW": NEON, "HOLD": STAR, "BUNDLE": STAR,
                       "GRADE IT": EMBER, "PASS": T3}
        vc = verdict_map.get(d.get("verdict", ""), T1)

        v_card = Card(top_row, border=BORDER_HI if vc != T3 else BORDER, bg=CARD)
        v_card.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        vi = v_card.inner()
        tk.Label(vi, text="VERDICT", font=FONT_LABEL, bg=CARD, fg=T4).pack(anchor="w")
        tk.Label(vi, text=d.get("verdict", "—"), font=("Courier New", 20, "bold"),
                 bg=CARD, fg=vc).pack(anchor="w", pady=(4, 0))

        r_card = Card(top_row, border=BORDER, bg=CARD)
        r_card.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        ri = r_card.inner()
        tk.Label(ri, text="EST. ROI", font=FONT_LABEL, bg=CARD, fg=T4).pack(anchor="w")
        tk.Label(ri, text=d.get("roi", "N/A"), font=("Courier New", 20, "bold"),
                 bg=CARD, fg=NEON).pack(anchor="w", pady=(4, 0))

        # ── Price tiles ──
        SectionLabel(self._results_frame, "PRICING").pack(fill="x", pady=(10, 8))
        p_row = tk.Frame(self._results_frame, bg=BG)
        p_row.pack(fill="x", pady=(0, 6))
        prices = [
            ("FLOOR", d.get("price_low", "—"), "conservative", False),
            ("RECOMMENDED", d.get("price_mid", "—"), "sweet spot", True),
            ("HIGH / GRADED", d.get("price_high", "—"), d.get("platform_rec", ""), False),
        ]
        for i, (lbl, val, note, best) in enumerate(prices):
            bc = NEON if best else BORDER
            bg = CARD if not best else "#1a2e28"
            c = Card(p_row, border=bc, bg=bg, pad=12)
            c.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 4, 0))
            p_row.columnconfigure(i, weight=1)
            ci = c.inner()
            tk.Label(ci, text=lbl, font=FONT_LABEL, bg=bg,
                     fg=NEON if best else T4).pack(anchor="center")
            tk.Label(ci, text=f"${val}", font=("Arial", 22, "bold"),
                     bg=bg, fg=NEON if best else T1).pack(anchor="center", pady=(4, 2))
            tk.Label(ci, text=note, font=FONT_LABEL, bg=bg, fg=T3).pack(anchor="center")

        # ── Listing ──
        SectionLabel(self._results_frame, "LISTING").pack(fill="x", pady=(12, 8))

        title_card = Card(self._results_frame, border=BORDER, bg=CARD)
        title_card.pack(fill="x", pady=(0, 6))
        ti = title_card.inner()
        tk.Label(ti, text="TITLE", font=FONT_LABEL, bg=CARD, fg=T4).pack(anchor="w")
        tk.Label(ti, text=d.get("listing_title", ""),
                 font=("Courier New", 10, "bold"),
                 bg=CARD, fg=STAR, wraplength=700, justify="left").pack(anchor="w", pady=(6, 0))

        desc_card = Card(self._results_frame, border=BORDER, bg=CARD)
        desc_card.pack(fill="x", pady=(0, 6))
        di = desc_card.inner()
        tk.Label(di, text="DESCRIPTION", font=FONT_LABEL, bg=CARD, fg=T4).pack(anchor="w")
        desc_txt = tk.Text(di, bg=ELEV, fg=T2, font=FONT_BODY_S, relief="flat",
                            height=8, wrap="word", bd=4)
        desc_txt.insert("1.0", d.get("listing_desc", ""))
        desc_txt.configure(state="disabled")
        desc_txt.pack(fill="x", pady=(8, 0))
        self._pill_btn(di, "COPY LISTING",
                       lambda: self._copy(d.get("listing_title", "") + "\n\n" + d.get("listing_desc", "")),
                       STAR).pack(anchor="e", pady=(10, 0))

        # ── Social Funnel ──
        SectionLabel(self._results_frame, "SOCIAL FUNNEL").pack(fill="x", pady=(12, 8))
        self.social_texts = {
            "ig": d.get("social_ig", ""), "tt": d.get("social_tt", ""),
            "fb": d.get("social_fb", ""), "tw": d.get("social_tw", ""),
            "skip": d.get("social_skip", "")
        }
        soc_card = Card(self._results_frame, border=BORDER, bg=CARD)
        soc_card.pack(fill="x", pady=(0, 6))
        si = soc_card.inner()

        # Tab pills
        tab_row = tk.Frame(si, bg=CARD)
        tab_row.pack(fill="x", pady=(0, 10))
        self._soc_btns = {}
        tabs = [("ig", "Instagram"), ("tt", "TikTok"), ("fb", "Facebook"),
                ("tw", "Twitter/X"), ("skip", "Skip Blog")]
        for key, label in tabs:
            b = tk.Button(tab_row, text=label, font=FONT_LABEL,
                          bg=CARD2, fg=T3, relief="flat", cursor="hand2",
                          padx=10, pady=5,
                          command=lambda k=key: self._switch_social(k))
            b.pack(side="left", padx=(0, 4))
            self._soc_btns[key] = b

        self._soc_text = tk.Text(si, bg=ELEV, fg=T2, font=FONT_BODY_S,
                                  relief="flat", height=7, wrap="word", bd=4)
        self._soc_text.pack(fill="x")
        self._pill_btn(si, "COPY SOCIAL COPY",
                       lambda: self._copy(self._soc_text.get("1.0", "end").strip()),
                       PLASMA).pack(anchor="e", pady=(10, 0))
        self._switch_social("ig")

    def _switch_social(self, key):
        self.active_social.set(key)
        for k, b in self._soc_btns.items():
            active = k == key
            b.configure(
                bg=PLASMA if active else CARD2,
                fg=BG if active else T3
            )
        self._soc_text.configure(state="normal")
        self._soc_text.delete("1.0", "end")
        self._soc_text.insert("1.0", self.social_texts.get(key, ""))
        self._soc_text.configure(state="disabled")

    # ─────────────────────────────────────────────── API ──
    def _run(self):
        name = self._iname.get().strip()
        if not name:
            messagebox.showwarning("Missing Info", "Enter an item name first.")
            return
        if not self._api_key_value:
            messagebox.showwarning("No API Key", "Paste and save your Anthropic API key first.")
            return
        self._go_btn.configure(state="disabled")
        self._results_frame.pack_forget()
        self._progress.start(10)
        self.status_var.set("Analyzing photo with Claude Vision…" if self._photo_b64 else "Contacting Claude API…")
        self._status_lbl.configure(fg=T3)
        threading.Thread(target=self._call_api, args=(name,), daemon=True).start()

    def _call_api(self, name):
        cat = self._icat_var.get()
        cond = self._icond_var.get()
        buy = self._ibuy.get().strip()
        platform = self._iplatform_var.get()
        notes = self._inotes.get("1.0", "end").strip()
        has_photo = bool(self._photo_b64)

        photo_note = "A photo of the item has been provided — use it to help identify the item, assess condition, read any visible labels or serial numbers, and improve your analysis." if has_photo else ""

        prompt = f"""You are an expert reseller analyst and copywriter for Starchild Rare Finds (SCRF), a collectibles and resale business specializing in Pokémon cards, Yu-Gi-Oh, vinyl records, VHS, retro gaming, antiques, and general collectibles. The owner sells on eBay and Hello Skip.

{photo_note}
Analyze this item and return a JSON object ONLY — no markdown fences, no explanation, just raw JSON.

Item: {name}
Category: {cat}
Condition: {cond}
Buy Price: {('$'+buy) if buy else 'unknown'}
Target Platform: {platform}
Notes: {notes or 'none'}

Return this exact JSON structure:
{{
  "verdict": "FLIP NOW" or "HOLD" or "BUNDLE" or "GRADE IT" or "PASS",
  "roi": "estimated ROI % range or N/A if no buy price",
  "price_low": "low end sell price as number string e.g. 12.00",
  "price_mid": "recommended sell price as number string",
  "price_high": "high end if graded/mint as number string",
  "platform_rec": "best platform to sell on",
  "listing_title": "SEO-optimized listing title for {platform}, max 80 chars",
  "listing_desc": "Full listing description with condition details, what's included, keywords, and shipping note. 150-250 words.",
  "social_ig": "Instagram caption with emojis and 10-15 hashtags",
  "social_tt": "TikTok hook (first 3 seconds script) + caption + hashtags",
  "social_fb": "Facebook Marketplace/group post, friendly and detailed, no hashtags",
  "social_tw": "X/Twitter post under 280 chars, punchy, 2-3 hashtags",
  "social_skip": "Skip blog intro paragraph, 100 words, storytelling angle about this item history/collectibility"
}}"""

        # Build message content — text only, or text + image
        if has_photo:
            user_content = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": self._photo_mime,
                        "data": self._photo_b64
                    }
                },
                {"type": "text", "text": prompt}
            ]
        else:
            user_content = prompt

        payload = json.dumps({
            "model": MODEL,
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": user_content}]
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self._api_key_value,
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                resp = json.loads(r.read())
            raw = resp["content"][0]["text"]
            clean = raw.replace("```json", "").replace("```", "").strip()
            d = json.loads(clean)
            self.after(0, lambda: self._done(d))
        except urllib.error.HTTPError as e:
            err = e.read().decode()
            self.after(0, lambda: self._error(f"API Error {e.code}: {err[:200]}"))
        except Exception as e:
            self.after(0, lambda: self._error(str(e)))

    def _done(self, d):
        self._progress.stop()
        self.status_var.set("")
        self._go_btn.configure(state="normal")
        self._render_results(d)

    def _error(self, msg):
        self._progress.stop()
        self.status_var.set(f"✕  {msg}")
        self._status_lbl.configure(fg=EMBER)
        self._go_btn.configure(state="normal")

    # ─────────────────────────────────────────── HELPERS ──
    def _copy(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)

    def _flabel(self, parent, text):
        return tk.Label(parent, text=text, font=FONT_LABEL, bg=BG, fg=T3)

    def _entry(self, parent, width=None):
        f = tk.Frame(parent, bg=BORDER, highlightthickness=0)
        e = tk.Entry(f, bg=ELEV, fg=T2, insertbackground=T1,
                     relief="flat", font=FONT_BODY, bd=6)
        if width:
            e.configure(width=width)
        e.pack(fill="both", expand=True, padx=1, pady=1)
        # Proxy get/delete to Entry
        f.get = e.get
        f.delete = e.delete
        return f

    def _optmenu(self, parent, values):
        var = tk.StringVar(value=values[0])
        m = tk.OptionMenu(parent, var, *values)
        m.configure(bg=ELEV, fg=T2, activebackground=CARD2,
                    activeforeground=T1, relief="flat",
                    highlightthickness=1, highlightbackground=BORDER,
                    font=FONT_BODY, indicatoron=True,
                    bd=0, padx=8, pady=6, cursor="hand2")
        m["menu"].configure(bg=ELEV, fg=T1, activebackground=PLASMA,
                             activeforeground=BG, relief="flat", bd=0)
        # attach var to widget so we can retrieve it
        m._var = var
        return m

    def _pill_btn(self, parent, text, cmd, color):
        return tk.Button(parent, text=text, font=FONT_LABEL,
                         bg=color, fg=BG, relief="flat",
                         activebackground=color, activeforeground=BG,
                         cursor="hand2", padx=12, pady=5, command=cmd)

    # ── OptionMenu value accessors (set up after grid) ──
    @property
    def _icat_var(self):
        return self._icat._var

    @property
    def _icond_var(self):
        return self._icond._var

    @property
    def _iplatform_var(self):
        return self._iplatform._var


if __name__ == "__main__":
    app = SCRFApp()
    app.mainloop()
