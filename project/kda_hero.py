import requests
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from scipy.stats import norm, gamma
import numpy as np
from scipy.optimize import brentq

def fetch_heroes():
    response = requests.get("https://api.opendota.com/api/heroes")
    response.raise_for_status()
    return response.json()

def fetch_matches(hero_id):
    url = f"https://api.opendota.com/api/heroes/{hero_id}/matches"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def analyze_hero():
    selected_hero = hero_combobox.get()
    hero_id = hero_dict[selected_hero]
    matches = fetch_matches(hero_id)

    kdas = []
    outcomes = []
    for match in matches:
        kills = match["kills"]
        deaths = match["deaths"]
        assists = match["assists"]
        win = match["radiant_win"] if match["radiant"] else not match["radiant_win"]

        kda = (kills + assists) / (deaths + 1)
        kdas.append(kda)
        outcomes.append(1 if win else 0)

    plot_kda_distribution(kdas, outcomes)

def plot_kda_distribution(kdas, outcomes):
    kdas = np.array(kdas)
    outcomes = np.array(outcomes)

    plt.figure(figsize=(10, 6))
    bins = np.linspace(min(kdas), max(kdas), 100)

    plt.hist(kdas[outcomes == 1], bins=bins, alpha=0.6, label="Перемоги", color="green", density=True)
    plt.hist(kdas[outcomes == 0], bins=bins, alpha=0.6, label="Поразки", color="red", density=True)

    mean_win, std_win = norm.fit(kdas[outcomes == 1])
    mean_loss, std_loss = norm.fit(kdas[outcomes == 0])

    x = np.linspace(min(kdas), max(kdas), 200)
    pdf_win = norm.pdf(x, mean_win, std_win)
    pdf_loss = norm.pdf(x, mean_loss, std_loss)

    plt.plot(x, pdf_win, "g", label="Норм. розподіл Перемоги")
    plt.plot(x, pdf_loss, "r", label="Норм. розподіл Поразки")

    def intersection_func(x_val):
        return norm.pdf(x_val, mean_win, std_win) - norm.pdf(x_val, mean_loss, std_loss)

    intersection_point = brentq(intersection_func, min(x), max(x))

    plt.axvline(intersection_point, color="purple", linestyle="--", label=f"Порог: {intersection_point:.2f}")

    shape_win, loc_win, scale_win = gamma.fit(kdas[outcomes == 1], floc=0)
    shape_loss, loc_loss, scale_loss = gamma.fit(kdas[outcomes == 0], floc=0)

    pdf_win_gamma = gamma.pdf(x, shape_win, loc=loc_win, scale=scale_win)
    pdf_loss_gamma = gamma.pdf(x, shape_loss, loc=loc_loss, scale=scale_loss)

    plt.plot(x, pdf_win_gamma, "b--", label="Гамма розподіл Перемоги")
    plt.plot(x, pdf_loss_gamma, "b-", label="Гамма розподіл Поразки")

    def gamma_intersection_func(x_val):
        return gamma.pdf(x_val, shape_win, loc=loc_win, scale=scale_win) - gamma.pdf(x_val, shape_loss, loc=loc_loss,
                                                                                     scale=scale_loss)

    try:
        gamma_intersection_point = brentq(gamma_intersection_func, min(x), max(x))
        plt.axvline(gamma_intersection_point, color="orange", linestyle="--",
                    label=f"Гамма поріг: {gamma_intersection_point:.2f}")
    except ValueError as e:
        print(f"Ошибка поиска точки пересечения гамма-распределений: {e}")

    plt.title("Розподіл KDA з нормальним та гамма розподілами")
    plt.xlabel("KDA")
    plt.ylabel("Щільність ймовірності")
    plt.legend()
    plt.grid()

    plt.show()

heroes = fetch_heroes()
hero_dict = {hero["localized_name"]: hero["id"] for hero in heroes}

root = tk.Tk()
root.title("Аналіз KDA за героєм")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

hero_label = tk.Label(frame, text="Оберіть героя:")
hero_label.pack(side="left")

hero_combobox = ttk.Combobox(frame, values=list(hero_dict.keys()), width=30)
hero_combobox.pack(side="left")
hero_combobox.set("Оберіть героя")

analyze_button = tk.Button(frame, text="Аналізувати", command=analyze_hero)
analyze_button.pack(side="left", padx=5)

root.mainloop()
