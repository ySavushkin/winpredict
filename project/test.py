import requests
import random
import tkinter as tk

from project.predictwin_funcs import PredictWinFuncs
from project.predictwin_ui import AppUI


class PredictorTest:
    def __init__(self):
        self.base_url = "https://api.opendota.com/api"
        self.heroes = self.fetch_heroes()

    def fetch_heroes(self):
        response = requests.get(f"{self.base_url}/heroes")
        response.raise_for_status()
        heroes_data = response.json()
        return {hero['id']: hero['localized_name'] for hero in heroes_data}

    def fetch_random_matches(self, num_matches=10):
        response = requests.get(f"{self.base_url}/publicMatches")
        response.raise_for_status()
        matches = response.json()
        return random.sample(matches, num_matches)

    def analyze_match(self, match, predictor):
        # Парсим героев из radiant_team и dire_team
        light_hero_ids = match.get('radiant_team', [])
        dark_hero_ids = match.get('dire_team', [])

        if len(light_hero_ids) != 5 or len(dark_hero_ids) != 5:
            print("Неполный состав команд. Пропуск матча.")
            return None, 0  # Возвращаем None и 0, если состав команд неполный

        predictor.selected_hero_ids['light'] = light_hero_ids
        predictor.selected_hero_ids['dark'] = dark_hero_ids
        predictor.selected_team = 'light'
        print(dark_hero_ids)

        win_rate_texts = []
        overall_light_score = 0

        enemy_team = 'dark' if predictor.selected_team == 'light' else 'light'
        enemy_hero_ids = predictor.selected_hero_ids[enemy_team]

        for light_hero_id in light_hero_ids:
            try:
                response = requests.get(f"{predictor.base_url}/heroes/{light_hero_id}/matchups")
                print(f"https://api.opendota.com/api/heroes/{light_hero_id}/matchups")
                response.raise_for_status()
                matchups_data = response.json()

                for dark_hero_id in dark_hero_ids:
                    matchup = next((m for m in matchups_data if m["hero_id"] == dark_hero_id), None)

                    if matchup:
                        win_rate = (matchup["wins"] / matchup["games_played"]) * 100
                        light_hero_name = predictor.heroes.get(light_hero_id, "Unknown")
                        enemy_hero_name = predictor.heroes.get(dark_hero_id, "Unknown")

                        text = f"{light_hero_name} имеет {win_rate:.2f}% винрейта против {enemy_hero_name}"
                        win_rate_texts.append(text)

                        if win_rate >= 50:
                            overall_light_score += 1

            except requests.RequestException as e:
                print(f"Ошибка при запросе для героя {light_hero_id}: {e}")

        predictor.results_text.config(state=tk.NORMAL)
        predictor.results_text.delete(1.0, tk.END)

        for text in win_rate_texts:
            predictor.results_text.insert(tk.END, f"{text}\n")

        total_matchups = len(predictor.selected_hero_ids['light']) * len(enemy_hero_ids)
        overall_probability_light = (overall_light_score / total_matchups) * 100
        predictor.results_text.insert(tk.END, f"\nОбщая вероятность победы: {overall_probability_light:.2f}%")
        # print(f"\nОбщая вероятность победы cил света: {overall_probability_light:.2f}%")
        predictor.results_text.config(state=tk.DISABLED)

        actual_winner = "light" if match.get('radiant_win', False) else "dark"

        print(f"\nОбщая вероятность победы сил света: {overall_probability_light:.2f}%")

        def get_hero_name(hero_id, predictor):
            # Возвращаем имя героя из словаря или ищем в API
            if hero_id in predictor.heroes:
                return predictor.heroes[hero_id]
            else:
                try:
                    # Запрашиваем всех героев сразу
                    response = requests.get(f"{predictor.base_url}/heroes")
                    response.raise_for_status()
                    heroes_data = response.json()

                    # Ищем нужного героя по ID в полученном списке
                    hero_data = next((hero for hero in heroes_data if hero['id'] == hero_id), None)

                    if hero_data and 'localized_name' in hero_data:
                        localized_name = hero_data['localized_name']
                        predictor.heroes[hero_id] = localized_name
                        return localized_name
                    else:
                        return f"Unknown({hero_id})"

                except requests.RequestException as e:
                    print(f"Ошибка при получении имени героя {hero_id}: {e}")
                    return f"Unknown({hero_id})"

        # Пример использования в выводе
        print(f"Герои Силы Света: {[get_hero_name(hero, predictor) for hero in light_hero_ids]}")
        print(f"Герои Силы Тьмы: {[get_hero_name(hero, predictor) for hero in dark_hero_ids]}")

        print(f"Фактический победитель: {'Сила Света' if actual_winner == 'light' else 'Сила Тьмы'}")
        print("-" * 50)

        return actual_winner, overall_light_score  # Возвращаем их

    def run_test(self, predictor, num_matches=10):
        matches = self.fetch_random_matches(num_matches)
        correct_predictions = 0

        for match in matches:
            actual_winner, overall_light_score = self.analyze_match(match, predictor)

            predictor_text = predictor.results_text.get("1.0", "end")
            predicted_winner = "light" if "Общая вероятность победы" in predictor_text else "dark"

            if actual_winner == predicted_winner:
                correct_predictions += 1

        print(f"Точность предсказаний: {correct_predictions / overall_light_score * 100:.2f}%")


# Пример использования
if __name__ == "__main__":
    test = PredictorTest()

    root = tk.Tk()
    ui = AppUI  # Здесь подставьте ваш UI, если требуется
    predictor = PredictWinFuncs(root, ui)

    predictor.create_hero_selection_window()

    test.run_test(predictor, num_matches=10)
