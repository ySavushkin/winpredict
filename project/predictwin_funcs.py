import requests
import tkinter as tk
from tkinter import ttk


class PredictWinFuncs:
    def __init__(self, root, ui):
        self.root = root
        self.ui = ui
        self.heroes = self.fetch_heroes()
        self.selected_heroes = {'light': [], 'dark': []}
        self.selected_hero_ids = {'light': [], 'dark': []}
        self.selected_team = None

    def fetch_heroes(self):
        response = requests.get("https://api.opendota.com/api/heroes")
        response.raise_for_status()
        heroes_data = response.json()
        return {hero['localized_name']: hero['id'] for hero in heroes_data}

    def create_hero_selection_window(self):
        self.hero_window = tk.Toplevel(self.root)
        self.hero_window.title("Выбор героев")

        # Получаем размеры экрана и окна
        window_width = 630
        window_height = 800

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)

        self.hero_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Сторона Силы Света
        tk.Label(self.hero_window, text="Сила Света").grid(row=0, column=0, padx=10, pady=5)
        self.light_team_inputs = []
        self.create_team_inputs('light', 0)

        # Сторона Силы Тьмы
        tk.Label(self.hero_window, text="Сила Тьмы").grid(row=0, column=1, padx=10, pady=5)
        self.dark_team_inputs = []
        self.create_team_inputs('dark', 1)

        # Кнопка для подсчёта винрейтов
        button_row = 7
        self.calculate_button = tk.Button(self.hero_window, text="Рассчитать винрейты",
                                          command=self.calculate_win_rates)
        self.calculate_button.grid(row=button_row, column=0, columnspan=2, pady=20)

        # Виджет для отображения результатов (увеличиваем высоту)
        self.results_text = tk.Text(self.hero_window, width=60, height=23)  # Высота в 1.5 раза больше стандартной
        self.results_text.grid(row=button_row + 1, column=0, columnspan=2, padx=10, pady=10)
        self.results_text.config(state=tk.DISABLED)  # Отключаем редактирование текста пользователем

    def create_team_inputs(self, team, column):
        for i in range(5):
            frame = tk.Frame(self.hero_window)
            frame.grid(row=i + 2, column=column, padx=10, pady=5)

            entry = ttk.Entry(frame, width=20)
            entry.pack(side=tk.LEFT)

            suggestions = tk.Listbox(frame, width=30, height=3)
            suggestions.pack(side=tk.LEFT, padx=(5, 0))
            suggestions.bind("<<ListboxSelect>>", lambda event, e=entry, s=suggestions, t=team: self.on_hero_select(event, e, s, t))
            suggestions.pack_forget()  # Скрываем подсказки изначально

            entry.bind("<KeyRelease>", lambda event, e=entry, s=suggestions: self.update_suggestions(e, s))
            entry.bind("<FocusIn>", lambda event, s=suggestions: s.pack(side=tk.LEFT, padx=(5, 0)))
            entry.bind("<FocusOut>", lambda event, s=suggestions: s.pack_forget())

            if team == 'light':
                self.light_team_inputs.append((entry, suggestions))
            else:
                self.dark_team_inputs.append((entry, suggestions))

    def update_suggestions(self, entry, suggestions):
        typed_text = entry.get().lower()
        suggestions.delete(0, tk.END)

        if not typed_text:
            return

        for hero_name in self.heroes:
            if typed_text in hero_name.lower() and hero_name not in self.selected_heroes['light'] + self.selected_heroes['dark']:
                suggestions.insert(tk.END, hero_name)

    def on_hero_select(self, event, entry, suggestions, team):
        # Проверяем, выбран ли элемент
        selection = suggestions.curselection()
        if not selection:
            return  # Если ничего не выбрано, просто выходим

        selected = suggestions.get(selection).split(' - ')[0]
        entry.delete(0, tk.END)
        entry.insert(0, selected)

        if selected not in self.selected_heroes[team]:
            self.selected_heroes[team].append(selected)
            self.selected_hero_ids[team].append(self.heroes[selected])

        self.clear_other_suggestions()

    def clear_other_suggestions(self):
        for inputs in (self.light_team_inputs, self.dark_team_inputs):
            for _, suggestions in inputs:
                suggestions.delete(0, tk.END)

    def calculate_win_rates(self):
        if len(self.selected_heroes['light']) != 5 or len(self.selected_heroes['dark']) != 5:
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Выберите 5 героев для каждой команды.\n")
            self.results_text.config(state=tk.DISABLED)
            return

        win_rate_texts = []
        overall_light_score = 0
        overall_dark_score = 0

        enemy_team = 'dark' if self.selected_team == 'light' else 'light'

        for light_hero_id in self.selected_hero_ids[self.selected_team]:
            for enemy_hero_id in self.selected_hero_ids[enemy_team]:
                try:
                    response = requests.get(f"https://api.opendota.com/api/heroes/{light_hero_id}/matchups")
                    response.raise_for_status()
                    matchups_data = response.json()

                    win_rate = None
                    for matchup in matchups_data:
                        if matchup["hero_id"] == enemy_hero_id:
                            win_rate = matchup["wins"] / matchup["games_played"] * 100
                            break

                    if win_rate is not None:
                        light_hero_name = list(self.heroes.keys())[list(self.heroes.values()).index(light_hero_id)]
                        enemy_hero_name = list(self.heroes.keys())[list(self.heroes.values()).index(enemy_hero_id)]
                        text = f"{light_hero_name} имеет {win_rate:.2f}% винрейта против {enemy_hero_name}"
                        win_rate_texts.append(text)

                        # Подсчитываем общую вероятность победы
                        if win_rate >= 50:
                            overall_light_score += 1
                        else:
                            overall_light_score += 0

                except requests.RequestException as e:
                    print(f"Ошибка при запросе для героев {light_hero_id} против {enemy_hero_id}: {e}")

        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)

        for text in win_rate_texts:
            self.results_text.insert(tk.END, f"{text}\n")

        # Вычисляем общую вероятность победы для команды 'light'
        total_matchups = len(self.selected_hero_ids[self.selected_team]) * len(self.selected_hero_ids[enemy_team])
        overall_probability_light = (overall_light_score / total_matchups) * 100
        self.results_text.insert(tk.END,
                                 f"\nОбщая вероятность победы: {overall_probability_light:.2f}%")
        self.results_text.config(state=tk.DISABLED)


