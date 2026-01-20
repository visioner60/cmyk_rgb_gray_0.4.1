"""
Pro Color Mode Converter v0.4.1
Copyright (C) 2026 Денис Тяжкин (visioner60@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageCms, ImageOps

class FinalProConverter(tk.Tk):
    def __init__(self):
        super().__init__()
        # Заголовок окна
        self.title("Pro Color Mode Converter v0.4.1 (GPL v3 Free Software)")
        self.geometry("680x780")
        
        # --- НАСТРОЙКИ ЦВЕТА И ПРОЗРАЧНОСТИ ---
        self.window_bg = "#001f3f"  # Темно-синий
        self.flash_color = "#FFD700" # Золотисто-желтый для мигания
        self.configure(bg=self.window_bg)
        self.attributes("-alpha", 0.85) # Прозрачность окна
        
        self.file_paths = []
        self.win_color_dir = r"C:\Windows\System32\spool\drivers\color"

        # --- ВЕРХНЯЯ ПАНЕЛЬ С АВТОРОМ И EMAIL ---
        top_bar = tk.Frame(self, bg=self.window_bg)
        top_bar.pack(fill=tk.X, padx=20, pady=5)
        
        author_info = "Автор: Денис Тяжкин, e-mail: Visioner60@gmail.com"
        tk.Label(top_bar, text=author_info, font=("Arial", 8, "italic"), 
                 fg="#0074D9", bg=self.window_bg).pack(side=tk.RIGHT)

        # --- СПИСОК ФАЙЛОВ ---
        self.files_frame = tk.LabelFrame(self, text=" Список файлов ", padx=10, pady=10, 
                                    fg="white", bg=self.window_bg)
        self.files_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.listbox = tk.Listbox(self.files_frame, height=8, font=("Courier New", 9), 
                                  bg="#001a35", fg="#7FDBFF", borderwidth=0)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        btn_files_frame = tk.Frame(self.files_frame, bg=self.window_bg)
        btn_files_frame.pack(pady=5)
        tk.Button(btn_files_frame, text="✚ Добавить файлы", command=self.add_files, 
                  width=20, bg="#0074D9", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_files_frame, text="✖ Очистить", command=self.clear_list, 
                  width=20, bg="#39CCCC", fg="black").pack(side=tk.LEFT, padx=5)

        # --- НАСТРОЙКИ ---
        self.controls_frame = tk.LabelFrame(self, text=" Настройки конвертации ", padx=10, pady=10, 
                                       fg="white", bg=self.window_bg)
        self.controls_frame.pack(fill=tk.X, padx=20, pady=10)

        self.profiles = self.get_system_profiles()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground="#001a35", background="#0074D9", foreground="white")

        self.cmyk_combo = self.create_mode_row(self.controls_frame, "Преобразовать в CMYK", "#2E7D32", "CMYK", 0)
        self.rgb_combo = self.create_mode_row(self.controls_frame, "Преобразовать в RGB", "#1565C0", "RGB", 1)
        self.grey_combo = self.create_mode_row(self.controls_frame, "Преобразовать в Grey", "#616161", "L", 2)

        # Метка для уведомления "ВЫПОЛНЕНО"
        self.status_label = tk.Label(self, text="ВЫПОЛНЕНО", font=("Arial", 24, "bold"), 
                                     fg=self.flash_color, bg=self.window_bg)

        # --- ПОДВАЛ С ЛИЦЕНЗИЕЙ ---
        tk.Label(self, text="This is free software under GNU GPL v3 terms.", 
                 font=("Arial", 7), fg="#555", bg=self.window_bg).pack(side=tk.BOTTOM, pady=5)

    def get_system_profiles(self):
        if not os.path.exists(self.win_color_dir): return ["sRGB"]
        return [f for f in os.listdir(self.win_color_dir) if f.lower().endswith(('.icc', '.icm'))]

    def create_mode_row(self, parent, text, color, mode, row):
        btn = tk.Button(parent, text=text, bg=color, fg="white", font=("Arial", 9, "bold"),
                        width=25, height=2, command=lambda m=mode: self.process(m))
        btn.grid(row=row, column=0, pady=8, padx=5, sticky="we")
        combo = ttk.Combobox(parent, values=self.profiles, width=45, state="readonly")
        combo.grid(row=row, column=1, pady=8, padx=5)
        
        search_map = {"CMYK": ["fogra39", "coated"], "RGB": ["srgb"], "L": ["gray", "gamma", "black"]}
        for term in search_map[mode]:
            for p in self.profiles:
                if term in p.lower():
                    combo.set(p); return combo
        if self.profiles: combo.set(self.profiles[0])
        return combo

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.jpeg *.png *.tif")])
        for f in files:
            if f not in self.file_paths:
                self.file_paths.append(f); self.listbox.insert(tk.END, os.path.basename(f))

    def clear_list(self):
        self.file_paths = []; self.listbox.delete(0, tk.END)

    def flash_success(self):
        """Мигание желтым и текст ВЫПОЛНЕНО"""
        self.configure(bg=self.flash_color)
        self.files_frame.configure(bg=self.flash_color, fg="black")
        self.controls_frame.configure(bg=self.flash_color, fg="black")
        self.status_label.pack(pady=10)
        self.status_label.configure(bg=self.flash_color, fg="black")
        self.after(300, self.reset_colors)
        self.after(2000, lambda: self.status_label.pack_forget())

    def reset_colors(self):
        self.configure(bg=self.window_bg)
        self.files_frame.configure(bg=self.window_bg, fg="white")
        self.controls_frame.configure(bg=self.window_bg, fg="white")

    def process(self, target_mode):
        if not self.file_paths: return
        combo = {"CMYK": self.cmyk_combo, "RGB": self.rgb_combo, "L": self.grey_combo}[target_mode]
        selected_p_name = combo.get()
        target_prof_path = os.path.join(self.win_color_dir, selected_p_name)
        input_prof = os.path.join(self.win_color_dir, "sRGB Color Space Profile.icm")
        if not os.path.exists(input_prof): input_prof = "sRGB"
        success_count = 0
        for path in self.file_paths:
            try:
                img = Image.open(path).convert("RGB")
                icc_data = None
                try:
                    out_img = ImageCms.profileToProfile(img, input_prof, target_prof_path, outputMode=target_mode)
                    with open(target_prof_path, "rb") as f:
                        icc_data = f.read()
                except Exception:
                    if target_mode == "L":
                        out_img = ImageOps.grayscale(img)
                        out_img = ImageOps.autocontrast(out_img, cutoff=0) 
                    else:
                        out_img = img.convert(target_mode)
                folder = os.path.dirname(path)
                save_path = os.path.join(folder, f"{os.path.splitext(os.path.basename(path))[0]}_{target_mode}.jpg")
                out_img.save(save_path, "JPEG", quality=95, icc_profile=icc_data)
                success_count += 1
            except Exception as e: print(e)
        if success_count > 0:
            self.flash_success()

if __name__ == "__main__":
    FinalProConverter().mainloop()