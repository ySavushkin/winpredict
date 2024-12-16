import tkinter as tk
from tkinter import font
from predictwin_funcs import PredictWinFuncs


class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hero Picker")

        # Скрываем основное окно до выбора команды
        self.root.withdraw()

        self.hero_picker = PredictWinFuncs(self.root, self)

        # Настраиваем шрифты
        self.title_font = font.Font(size=14, weight="bold")
        self.label_font = font.Font(size=12)
        self.button_font = font.Font(size=10, weight="bold")

        # Начальное окно для выбора команды
        self.show_team_selection_window()

    def show_team_selection_window(self):
        window_width = 300
        window_height = 300
        self.team_window = tk.Toplevel(self.root)
        self.team_window.title("Выбор команды")
        self.team_window.configure(bg="#2C3E50")  # Темный фон

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)

        self.team_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Заголовок
        label = tk.Label(
            self.team_window,
            text="Выберите свою команду:",
            font=self.title_font,
            bg="#2C3E50",
            fg="#ECF0F1"
        )
        label.pack(pady=(20, 10))

        # Радиокнопки
        self.team_choice = tk.StringVar(value="light")

        light_team_radio = tk.Radiobutton(
            self.team_window,
            text="Сила Света",
            variable=self.team_choice,
            value="light",
            font=self.label_font,
            bg="#2C3E50",
            fg="#ECF0F1",
            activebackground="#34495E",
            activeforeground="#ECF0F1",
            selectcolor="#34495E"
        )
        light_team_radio.pack(pady=5)

        dark_team_radio = tk.Radiobutton(
            self.team_window,
            text="Сила Тьмы",
            variable=self.team_choice,
            value="dark",
            font=self.label_font,
            bg="#2C3E50",
            fg="#ECF0F1",
            activebackground="#34495E",
            activeforeground="#ECF0F1",
            selectcolor="#34495E"
        )
        dark_team_radio.pack(pady=5)

        # Кнопка подтверждения
        confirm_button = tk.Button(
            self.team_window,
            text="Подтвердить",
            font=self.button_font,
            bg="#1ABC9C",
            fg="#FFFFFF",
            activebackground="#16A085",
            activeforeground="#ECF0F1",
            command=self.confirm_team_selection
        )
        confirm_button.pack(pady=20)

    def confirm_team_selection(self):
        self.hero_picker.selected_team = self.team_choice.get()
        self.team_window.destroy()  # Закрываем окно выбора команды
        self.hero_picker.create_hero_selection_window()


if __name__ == "__main__":
    root = tk.Tk()
    app_ui = AppUI(root)
    root.mainloop()
