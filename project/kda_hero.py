import requests
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from scipy.stats import norm
import numpy as np

# Получение списка героев через OpenDota API
def fetch_heroes():
    response = requests.get("https://api.opendota.com/api/heroes")
    response.raise_for_status()
    return response.json()

# Получение матчей для выбранного героя
def fetch_matches(hero_id):
    url = f"https://api.opendota.com/api/heroes/{hero_id}/matches"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Обработчик выбора героя
def analyze_hero():
    selected_hero = hero_combobox.get()
    hero_id = hero_dict[selected_hero]
    matches = fetch_matches(hero_id)

    # Расчет KDA и метки побед/поражений
    kdas = []
    outcomes = []
    for match in matches:
        kills = match["kills"]
        deaths = match["deaths"]
        assists = match["assists"]
        win = match["radiant_win"] if match["radiant"] else not match["radiant_win"]

        kda = (kills + assists) / (deaths + 1)  # Избегаем деления на 0
        kdas.append(kda)
        outcomes.append(1 if win else 0)

    # Построение графика
    plot_kda_distribution(kdas, outcomes)

# Построение графика KDA
def plot_kda_distribution(kdas, outcomes):
    kdas = np.array(kdas)
    outcomes = np.array(outcomes)

    # Гистограммы для побед и поражений
    plt.figure(figsize=(10, 6))
    bins = np.linspace(min(kdas), max(kdas), 200)
    plt.hist(kdas[outcomes == 1], bins=bins, alpha=0.6, label="Победы", color="green", density=True)
    plt.hist(kdas[outcomes == 0], bins=bins, alpha=0.6, label="Поражения", color="red", density=True)

    # Аппроксимация нормальным распределением
    mean_win, std_win = norm.fit(kdas[outcomes == 1])
    mean_loss, std_loss = norm.fit(kdas[outcomes == 0])
    x = np.linspace(min(kdas), max(kdas), 200)
    pdf_win = norm.pdf(x, mean_win, std_win)
    pdf_loss = norm.pdf(x, mean_loss, std_loss)

    plt.plot(x, pdf_win, "g", label=f"Норм. распр. Победы")
    plt.plot(x, pdf_loss, "r", label=f"Норм. распр. Поражения")

    # Нахождение порога KDA
    # Нахождение порога KDA
    def pdf_difference(kda):
        return norm.pdf(kda, mean_win, std_win) - norm.pdf(kda, mean_loss, std_loss)

    from scipy.optimize import brentq

    # Проверка, меняет ли функция знак
    lower_bound = min(kdas) - 1  # Немного расширяем диапазон
    upper_bound = max(kdas) + 1
    try:
        if pdf_difference(lower_bound) * pdf_difference(upper_bound) > 0:
            raise ValueError("Распределения KDA побед и поражений не пересекаются.")

        threshold_kda = brentq(pdf_difference, lower_bound, upper_bound)
        plt.axvline(threshold_kda, color="blue", linestyle="--", label=f"Порог KDA: {threshold_kda:.2f}")
    except ValueError as e:
        print(f"Ошибка: {e}")
        threshold_kda = None

    # Сообщение о пороге
    if threshold_kda is None:
        plt.title("Распределение KDA (порог KDA не найден)")
    else:
        plt.title("Распределение KDA и вероятность поражения")

    plt.xlabel("KDA")
    plt.ylabel("Плотность вероятности")
    plt.title("Распределение KDA и вероятность поражения")
    plt.legend()
    plt.grid()
    plt.show()

# Создание GUI
heroes = fetch_heroes()
hero_dict = {hero["localized_name"]: hero["id"] for hero in heroes}

root = tk.Tk()
root.title("Анализ KDA по герою")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

hero_label = tk.Label(frame, text="Выберите героя:")
hero_label.pack(side="left")

hero_combobox = ttk.Combobox(frame, values=list(hero_dict.keys()), width=30)
hero_combobox.pack(side="left")
hero_combobox.set("Выберите героя")

analyze_button = tk.Button(frame, text="Анализировать", command=analyze_hero)
analyze_button.pack(side="left", padx=5)

root.mainloop()
