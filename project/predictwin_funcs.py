import requests
import tkinter as tk
from tkinter import ttk
import csv
import random
from PIL import Image, ImageTk
import os


class PredictWinFuncs:
    def __init__(self, root, ui):
        self.root = root
        self.ui = ui
        self.heroes = self.fetch_heroes()
        self.selected_heroes = {'light': [], 'dark': []}
        self.selected_hero_ids = {'light': [], 'dark': []}
        self.selected_roles = {'light': [], 'dark': []}
        self.selected_team = None
        self.hero_roles = self.load_hero_roles()
        self.minimap_canvas = None
        self.minimap_image = None
        self.hero_icons = {}  # Для хранения загруженных иконок героев
        self.minimap_positions = {
            'light_carry': (300, 335),  # Нижняя линия, carry
            'light_hard_support': (270, 335),  # Нижняя линия, hard support
            'light_mid': (170, 230),  # Центр, mid
            'light_offlane': (67, 140),  # Верхняя линия, offlane
            'light_support': (67, 175),  # Верхняя линия, support

            'dark_carry': (100, 75),  # Верхняя линия, carry
            'dark_hard_support': (135, 75),  # Верхняя линия, hard support
            'dark_mid': (210, 180),  # Центр, mid
            'dark_offlane': (330, 270),  # Нижняя линия, offlane
            'dark_support': (330, 235)  # Нижняя линия, support
        }

    def fetch_heroes(self):
        response = requests.get("https://api.opendota.com/api/heroes")
        response.raise_for_status()
        heroes_data = response.json()
        return {hero['localized_name']: hero['id'] for hero in heroes_data}

    def load_hero_roles(self):
        hero_roles = {}
        with open('full_hero_scores.csv', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                hero_roles[row['Hero']] = {
                    'Carry': int(row['Carry']),
                    'Mid': int(row['Mid']),
                    'Offlane': int(row['Offlane']),
                    'Support': int(row['Support']),
                    'Hard Support': int(row['Hard Support'])
                }
        return hero_roles


    def create_hero_selection_window(self):
        self.hero_window = tk.Toplevel(self.root)
        self.hero_window.title("Вибір героїв")


        window_width = 1400
        window_height = 880

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 15)

        self.hero_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.hero_window.configure(bg="#212121")
        # Размещаем миникарту в отдельном столбце
        self.minimap_canvas = tk.Canvas(self.hero_window, width=400, height=400)
        self.minimap_canvas.grid(row=0, column=0, rowspan=8, padx=10, pady=10, sticky="ns")

        # Загрузка миникарты
        minimap_path = "minimap.jpg"
        if os.path.exists(minimap_path):
            self.minimap_image = ImageTk.PhotoImage(Image.open(minimap_path).resize((400, 400)))
            self.minimap_canvas.create_image(0, 0, anchor=tk.NW, image=self.minimap_image)
        else:
            print(f"Миникарта не найдена по пути: {minimap_path}")

        default_font = ('Arial', 12)
        # Команда для Світла (Light)
        tk.Label(self.hero_window, text="Сила Світла", font=default_font, fg="#E0E0E0", bg="#1e1e1e").grid(row=0,
                                                                                                           column=1,
                                                                                                           padx=10,
                                                                                                           pady=5)
        self.light_team_inputs = []
        self.create_team_inputs('light', 1)

        # Команда для Темряви (Dark)
        tk.Label(self.hero_window, text="Сила Темряви", font=default_font, fg="#E0E0E0", bg="#1e1e1e").grid(row=0,
                                                                                                            column=2,
                                                                                                            padx=10,
                                                                                                            pady=5)
        self.dark_team_inputs = []
        self.create_team_inputs('dark', 2)

        button_row = 7
        self.calculate_button = tk.Button(
            self.hero_window,
            text="Розрахувати ймовірність перемоги",
            font=default_font,
            bg="#2E3440",
            fg="#E0E0E0",
            command=self.calculate_win_rates
        )
        self.calculate_button.grid(row=button_row, column=1, columnspan=2, pady=20)

        self.results_text = tk.Text(self.hero_window, width=80, height=20, font=default_font, bg="#2E2E2E",
                                    fg="#E0E0E0")
        self.results_text.grid(row=button_row + 1, column=1, columnspan=2, padx=10, pady=10)
        self.results_text.config(state=tk.DISABLED)

    def create_team_inputs(self, team, column):
        for i in range(5):
            frame = tk.Frame(self.hero_window, bg="#37474F")
            frame.grid(row=i + 2, column=column, padx=10, pady=5)

            # Ввод имени героя - светло-серый фон
            entry = tk.Entry(frame, width=20, font=('Arial', 12), bg="#2E3440", fg="white")
            entry.pack(side=tk.LEFT, padx=5)
            entry_style = ttk.Style()
            entry_style.configure("TEntry", fieldbackground="#B0BEC5")


            style = ttk.Style()
            style.theme_use('clam')
            style.configure('TCombobox', fieldbackground="#2E3440", background="#2E3440", foreground="#2E3440")

            # Комбобокс для выбора роли - светло-серый фон
            role_combobox = ttk.Combobox(frame, values=["Carry", "Mid", "Offlane", "Support", "Hard Support"], width=15)
            role_combobox.set("Carry")
            role_combobox.pack(side=tk.LEFT, padx=(5, 0))

            combobox_style = ttk.Style()
            combobox_style.configure("TCombobox", fieldbackground="#B0BEC5")

            suggestions = tk.Listbox(frame, height=3, bg="#2E2E2E", fg="#E0E0E0")
            suggestions.pack(side=tk.LEFT, padx=(5, 0))
            suggestions.bind("<<ListboxSelect>>",
                             lambda event, e=entry, s=suggestions, t=team, r=role_combobox: self.on_hero_select(event,
                                                                                                                e, s, t,
                                                                                                                r))
            suggestions.pack_forget()

            entry.bind("<KeyRelease>", lambda event, e=entry, s=suggestions: self.update_suggestions(e, s))
            entry.bind("<FocusIn>", lambda event, s=suggestions: s.pack(side=tk.LEFT, padx=(5, 0)))
            entry.bind("<FocusOut>", lambda event, s=suggestions: s.pack_forget())

            if team == 'light':
                self.light_team_inputs.append((entry, suggestions, role_combobox))
            else:
                self.dark_team_inputs.append((entry, suggestions, role_combobox))

    def update_suggestions(self, entry, suggestions):
        typed_text = entry.get().lower()
        suggestions.delete(0, tk.END)

        if not typed_text:
            return

        for hero_name in self.heroes:
            if typed_text in hero_name.lower() and hero_name not in self.selected_heroes['light'] + self.selected_heroes['dark']:
                suggestions.insert(tk.END, hero_name)

    def display_hero_on_minimap(self, hero_name, role, team):
        """
        Отображение иконки героя на миникарте
        """
        icon_path = f"icons/{hero_name}.png"  # Путь к локальному файлу иконки героя

        # Загрузка локальной иконки героя
        if os.path.exists(icon_path):
            hero_icon = ImageTk.PhotoImage(Image.open(icon_path).resize((32, 32)))
        else:
            # Альтернативный вариант: загрузка иконки через API
            # api_icon_url = f"https://api.opendota.com/apps/dota2/images/heroes/{hero_name.lower().replace(' ', '_')}_icon.png"
            # response = requests.get(api_icon_url, stream=True)
            # if response.status_code == 200:
            #     hero_icon = ImageTk.PhotoImage(Image.open(response.raw).resize((40, 40)))
            # else:
            print(f"Иконка героя не найдена локально: {icon_path}")
            return

        # Сохраняем иконку, чтобы она не удалилась сборщиком мусора
        self.hero_icons[hero_name] = hero_icon

        # Получение позиции на карте
        position_key = f"{team}_{role.lower().replace(' ', '_')}"
        if position_key in self.minimap_positions:
            x, y = self.minimap_positions[position_key]
            self.minimap_canvas.create_image(x, y, anchor=tk.CENTER, image=hero_icon)

    def on_hero_select(self, event, entry, suggestions, team, role_combobox):
        selection = suggestions.curselection()
        if not selection:
            return

        selected = suggestions.get(selection).split(' - ')[0]
        entry.delete(0, tk.END)
        entry.insert(0, selected)

        if selected not in self.selected_heroes[team]:
            self.selected_heroes[team].append(selected)
            self.selected_hero_ids[team].append(self.heroes[selected])
            selected_role = role_combobox.get()
            self.selected_roles[team].append((selected, selected_role))

        # Отображение героя на карте
        selected_hero = entry.get()
        selected_role = role_combobox.get()
        self.display_hero_on_minimap(selected_hero, selected_role, team)

        self.clear_other_suggestions()

    def clear_other_suggestions(self):
        for inputs in (self.light_team_inputs, self.dark_team_inputs):
            for _, suggestions, _ in inputs:
                suggestions.delete(0, tk.END)

    def calculate_win_rates(self):
        if len(self.selected_heroes['light']) != 5 or len(self.selected_heroes['dark']) != 5:
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Оберіть 5 героїв для кожної команди.\n")
            self.results_text.config(state=tk.DISABLED)
            return

        results = {
            "Легка лінія": {"light": 0, "dark": 0},
            "Середня лінія": {"light": 0, "dark": 0},
            "Складна лінія": {"light": 0, "dark": 0}
        }

        light_roles = {
            "Carry": self.selected_heroes['light'][0],
            "Hard Support": self.selected_heroes['light'][4],
            "Mid": self.selected_heroes['light'][1],
            "Offlane": self.selected_heroes['light'][2],
            "Support": self.selected_heroes['light'][3]
        }

        dark_roles = {
            "Carry": self.selected_heroes['dark'][0],
            "Hard Support": self.selected_heroes['dark'][4],
            "Mid": self.selected_heroes['dark'][1],
            "Offlane": self.selected_heroes['dark'][2],
            "Support": self.selected_heroes['dark'][3]
        }

        line_matchups = {
            "Легка лінія": [("Carry", "Offlane"), ("Carry", "Support"), ("Hard Support", "Offlane"), ("Hard Support", "Support")],
            "Середня лінія": [("Mid", "Mid")],
            "Складна лінія": [("Offlane", "Carry"), ("Offlane", "Hard Support"), ("Support", "Carry"), ("Support", "Hard Support")]
        }

        detailed_results = []
        midgame_results = {"light": 0, "dark": 0}

        for line, matchups in line_matchups.items():
            for light_role, dark_role in matchups:
                light_hero_name = light_roles[light_role]
                dark_hero_name = dark_roles[dark_role]

                light_hero_id = self.heroes[light_hero_name]
                dark_hero_id = self.heroes[dark_hero_name]

                try:
                    response = requests.get(f"https://api.opendota.com/api/heroes/{light_hero_id}/matchups")
                    response.raise_for_status()
                    matchups_data = response.json()

                    matchup = next((m for m in matchups_data if m["hero_id"] == dark_hero_id), None)
                    if matchup:
                        win_rate = matchup["wins"] / matchup["games_played"] * 100

                        light_role_factor = self.hero_roles[light_hero_name][light_role]
                        dark_role_factor = self.hero_roles[dark_hero_name][dark_role]

                        adjusted_win_rate = self.adjusted_win_probability(win_rate / 100, light_role_factor, dark_role_factor)

                        detailed_results.append(f"{light_hero_name} ({light_role}) має {adjusted_win_rate * 100:.2f}% ймовірності перемоги проти {dark_hero_name} ({dark_role})\n")

                        if adjusted_win_rate > 0.5:
                            results[line]["light"] += adjusted_win_rate
                        else:
                            results[line]["dark"] += (1 - adjusted_win_rate)

                        # Midgame contribution
                        midgame_results["light"] += adjusted_win_rate
                        midgame_results["dark"] += (1 - adjusted_win_rate)

                except requests.exceptions.RequestException as e:
                    print(f"Помилка запиту даних для героя {light_hero_id}: {e}")

        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)

        self.results_text.insert(tk.END, "\n".join(detailed_results) + "\n\n")

        for line, scores in results.items():
            light_score = scores["light"] / len(line_matchups[line]) * 100
            dark_score = scores["dark"] / len(line_matchups[line]) * 100

            if light_score > dark_score:
                self.results_text.insert(tk.END, f"{line} Сили Світла має більше шансів на перемогу на лайнінгу ({light_score:.2f}%).\n")
            else:
                self.results_text.insert(tk.END, f"{line} Сили Темряви має більше шансів на перемогу на лайнінгу ({dark_score:.2f}%).\n")

        # Midgame results
        total_light_midgame = midgame_results["light"] / sum(len(v) for v in line_matchups.values()) * 100
        total_dark_midgame = midgame_results["dark"] / sum(len(v) for v in line_matchups.values()) * 100

        self.results_text.insert(tk.END, "\nРезультати мідгейму:\n")
        if total_light_midgame > total_dark_midgame:
            self.results_text.insert(tk.END, f"Сили Світла мають більше шансів на перемогу у мідгеймі ({total_light_midgame:.2f}%).\n")
        else:
            self.results_text.insert(tk.END, f"Сили Темряви мають більше шансів на перемогу у мідгеймі ({total_dark_midgame:.2f}%).\n")

        # Midgame detailed results
        midgame_detailed_results = []

        for light_hero_name in light_roles.values():
            for dark_hero_name in dark_roles.values():
                light_hero_id = self.heroes[light_hero_name]
                dark_hero_id = self.heroes[dark_hero_name]

                try:
                    response = requests.get(f"https://api.opendota.com/api/heroes/{light_hero_id}/matchups")
                    response.raise_for_status()
                    matchups_data = response.json()

                    matchup = next((m for m in matchups_data if m["hero_id"] == dark_hero_id), None)
                    if matchup:
                        win_rate = matchup["wins"] / matchup["games_played"] * 100

                        midgame_detailed_results.append(
                            f"{light_hero_name} має {win_rate:.2f}% ймовірності перемоги проти {dark_hero_name}\n"
                        )

                except requests.exceptions.RequestException as e:
                    print(f"Помилка запиту даних для героя {light_hero_id}: {e}")



        self.results_text.insert(tk.END, "\nДеталізовані результати мідгейму:\n")
        self.results_text.insert(tk.END, "\n".join(midgame_detailed_results) + "\n\n")
        self.results_text.insert(tk.END, "\nРезультати лейту:\n")

        error_chance = 0.2

        if random.random() < error_chance:
            light_penalty = total_light_midgame * 0.1
            total_light_midgame -= light_penalty
            total_dark_midgame += light_penalty
            self.results_text.insert(tk.END, f"Сили Світла зробили помилку! Віддають 10% шансів Силам Темряви.\n")

        if random.random() < error_chance:
            dark_penalty = total_dark_midgame * 0.1
            total_dark_midgame -= dark_penalty
            total_light_midgame += dark_penalty
            self.results_text.insert(tk.END, f"Сили Темряви зробили помилку! Віддають 10% шансів Силам Світла.\n")

        if total_light_midgame > total_dark_midgame:
            self.results_text.insert(tk.END,
                                     f"Сили Світла мають більше шансів на перемогу у лейті ({total_light_midgame:.2f}%).\n")
        else:
            self.results_text.insert(tk.END,
                                     f"Сили Темряви мають більше шансів на перемогу у лейті ({total_dark_midgame:.2f}%).\n")

        self.results_text.config(state=tk.DISABLED)

    def adjusted_win_probability(self, base_win_rate, light_role_factor, dark_role_factor):
        return base_win_rate * light_role_factor / (base_win_rate * light_role_factor + (1 - base_win_rate) * dark_role_factor)
