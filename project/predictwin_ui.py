import tkinter as tk
from predictwin_funcs import PredictWinFuncs


class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hero Picker")

        # Скрываем основное окно до выбора команды
        self.root.withdraw()

        self.hero_picker = PredictWinFuncs(self.root, self)

        # Начальное окно для выбора команды
        self.show_team_selection_window()

    def show_team_selection_window(self):
        window_width = 200
        window_height = 200
        self.team_window = tk.Toplevel(self.root)
        self.team_window.title("Выбор команды")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)

        self.team_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        label = tk.Label(self.team_window, text="Выбери свою команду:")
        label.pack(padx=10, pady=10)

        self.team_choice = tk.StringVar(value="light")

        light_team_radio = tk.Radiobutton(self.team_window, text="Сила Света", variable=self.team_choice, value="light")
        light_team_radio.pack(padx=10, pady=5)

        dark_team_radio = tk.Radiobutton(self.team_window, text="Сила Тьмы", variable=self.team_choice, value="dark")
        dark_team_radio.pack(padx=10, pady=5)

        confirm_button = tk.Button(self.team_window, text="Подтвердить", command=self.confirm_team_selection)
        confirm_button.pack(padx=10, pady=20)

    def confirm_team_selection(self):
        self.hero_picker.selected_team = self.team_choice.get()
        self.team_window.destroy()  # Закрываем окно выбора команды
        self.hero_picker.create_hero_selection_window()


if __name__ == "__main__":

    root = tk.Tk()
    app_ui = AppUI(root)
    root.mainloop()
