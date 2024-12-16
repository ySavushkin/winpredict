import requests
import tkinter as tk
from tkinter import ttk
import csv


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

        window_width = 630
        window_height = 800

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)

        self.hero_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        tk.Label(self.hero_window, text="Сила Світла").grid(row=0, column=0, padx=10, pady=5)
        self.light_team_inputs = []
        self.create_team_inputs('light', 0)

        tk.Label(self.hero_window, text="Сила Темряви").grid(row=0, column=1, padx=10, pady=5)
        self.dark_team_inputs = []
        self.create_team_inputs('dark', 1)

        button_row = 7
        self.calculate_button = tk.Button(self.hero_window, text="Розрахувати ймовірність перемоги",
                                          command=self.calculate_win_rates)
        self.calculate_button.grid(row=button_row, column=0, columnspan=2, pady=20)

        self.results_text = tk.Text(self.hero_window, width=60, height=23)
        self.results_text.grid(row=button_row + 1, column=0, columnspan=2, padx=10, pady=10)
        self.results_text.config(state=tk.DISABLED)

    def create_team_inputs(self, team, column):
        for i in range(5):
            frame = tk.Frame(self.hero_window)
            frame.grid(row=i + 2, column=column, padx=10, pady=5)

            entry = ttk.Entry(frame, width=20)
            entry.pack(side=tk.LEFT)

            role_combobox = ttk.Combobox(frame, values=["Carry", "Mid", "Offlane", "Support", "Hard Support"], width=15)
            role_combobox.set("Carry")
            role_combobox.pack(side=tk.LEFT, padx=(5, 0))

            suggestions = tk.Listbox(frame, width=30, height=3)
            suggestions.pack(side=tk.LEFT, padx=(5, 0))
            suggestions.bind("<<ListboxSelect>>", lambda event, e=entry, s=suggestions, t=team, r=role_combobox: self.on_hero_select(event, e, s, t, r))
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
        self.results_text.config(state=tk.DISABLED)

    def adjusted_win_probability(self, base_win_rate, light_role_factor, dark_role_factor):
        return base_win_rate * light_role_factor / (base_win_rate * light_role_factor + (1 - base_win_rate) * dark_role_factor)
