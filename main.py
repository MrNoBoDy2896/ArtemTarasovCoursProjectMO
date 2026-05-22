import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

from create_db import get_user, add_user, get_all_users, delete_user
from optimization_core import (set_parameters, get_parameters,
                               set_optimization_method, optimize_with_method,
                               get_available_methods)
from plot_2d import plot_contour
from plot_3d import plot_3d_surface


class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Авторизация - Оптимизация теплообменника")
        self.window.geometry("400x500")
        self.window.resizable(False, False)

        self.center_window()

        self.setup_ui()

    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        title_label = tk.Label(self.window, text="🔐 АВТОРИЗАЦИЯ",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=30)

        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Имя пользователя:", font=("Arial", 11)).pack(anchor=tk.W, pady=(10, 5))
        self.username_entry = ttk.Entry(frame, font=("Arial", 11), width=30)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="Пароль:", font=("Arial", 11)).pack(anchor=tk.W, pady=(10, 5))
        self.password_entry = ttk.Entry(frame, font=("Arial", 11), width=30, show="•")
        self.password_entry.pack(fill=tk.X, pady=(0, 20))

        login_btn = ttk.Button(frame, text="ВОЙТИ", command=self.login)
        login_btn.pack(fill=tk.X, pady=10)

        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.login())

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Предупреждение", "Введите имя пользователя и пароль")
            return

        user = get_user(username, password)
        if user:
            self.window.destroy()
            app = MainApplication(username, user[3])
            app.run()
        else:
            messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")

    def run(self):
        self.window.mainloop()


class MainApplication:
    def __init__(self, username, role):
        self.username = username
        self.role = role
        self.T1_opt = None
        self.T2_opt = None
        self.cost_opt = None
        self.params = get_parameters()
        self.current_variant = 2

        self.root = tk.Tk()
        self.root.title(
            f"Оптимизация теплообменника - {username} ({'Администратор' if role == 'admin' else 'Пользователь'})")
        self.root.geometry("1200x900")

        self.center_window()

        self.setup_menu()
        self.setup_ui()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def open_methods_help(self):
        MethodsHelpWindow(self.root)

    def open_about(self):
        about_text = """
        Программа оптимизации теплообменника

        Версия: 1.0
        Разработано для решения задачи минимизации затрат 
        на изготовление теплообменника.

        Функционал:
        • Выбор метода оптимизации (SLSQP, дифференциальная эволюция, имитация отжига)
        • Настройка параметров целевой функции
        • 2D и 3D визуализация результатов
        • Управление пользователями (для администратора)
        """
        messagebox.showinfo("О программе", about_text)

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выйти", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        if self.role == 'admin':
            admin_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Администрирование", menu=admin_menu)
            admin_menu.add_command(label="Управление пользователями", command=self.open_user_management)
            admin_menu.add_command(label="Параметры задачи", command=self.open_task_settings)
            admin_menu.add_separator()
            admin_menu.add_command(label="Выбор варианта (11-17)", command=self.open_variant_selection)

        methods_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Метод оптимизации", menu=methods_menu)

        available_methods = get_available_methods()
        current_method = self.params.get('optimization_method', 'SLSQP')

        for method in available_methods:
            methods_menu.add_command(
                label=f"{'✓ ' if method == current_method else '  '}{method}",
                command=lambda m=method: self.change_optimization_method(m)
            )

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О методах оптимизации", command=self.open_methods_help)
        help_menu.add_separator()
        help_menu.add_command(label="О программе", command=self.open_about)

    def change_optimization_method(self, method):
        set_optimization_method(method)
        self.params = get_parameters()
        self.L_opt = None
        self.S_opt = None
        self.cost_opt = None
        messagebox.showinfo("Успех", f"Метод оптимизации изменен на: {method}")
        self.setup_menu()

    def setup_ui(self):
        info_frame = ttk.Frame(self.root, padding="10")
        info_frame.pack(fill=tk.X)

        ttk.Label(info_frame, text=f"Пользователь: {self.username}", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(info_frame, text=f"Роль: {'Администратор' if self.role == 'admin' else 'Пользователь'}",
                  font=("Arial", 10)).pack(side=tk.LEFT, padx=(20, 0))

        current_method = self.params.get('optimization_method', 'SLSQP')
        ttk.Label(info_frame, text=f"Метод: {current_method}",
                  font=("Arial", 10), foreground="blue").pack(side=tk.LEFT, padx=(20, 0))

        if self.role == 'admin' and self.current_variant:
            ttk.Label(info_frame, text=f"Вариант: {self.current_variant}",
                      font=("Arial", 10), foreground="green").pack(side=tk.LEFT, padx=(20, 0))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_task_tab()
        self.create_plots_tab()

    def open_variant_selection(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Выбор варианта")
        dialog.geometry("400x450")
        dialog.resizable(False, False)

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (450 // 2)
        dialog.geometry(f'400x450+{x}+{y}')

        ttk.Label(dialog, text="Выбор варианта задачи",
                  font=("Arial", 14, "bold")).pack(pady=20)

        ttk.Label(dialog, text="Доступные варианты:",
                  font=("Arial", 11)).pack()

        variants_info = tk.Text(dialog, height=8, width=40, font=("Arial", 10))
        variants_info.pack(pady=10, padx=20)
        variants_info.insert(tk.END, "Вариант 1: ❌ Недостаточно данных\n")
        variants_info.insert(tk.END, "Вариант 2: ✅ Полные данные (работает)\n")
        variants_info.insert(tk.END, "Вариант 3: ❌ Недостаточно данных\n")
        variants_info.insert(tk.END, "Вариант 4: ❌ Недостаточно данных\n")
        variants_info.insert(tk.END, "Вариант 5: ❌ Недостаточно данных\n")
        variants_info.insert(tk.END, "Вариант 6: ❌ Недостаточно данных\n")
        variants_info.insert(tk.END, "Вариант 7: ❌ Недостаточно данных")
        variants_info.config(state=tk.DISABLED)

        ttk.Label(dialog, text="Введите номер варианта (1-7):",
                  font=("Arial", 10)).pack(pady=(10, 5))

        variant_var = tk.StringVar(value=str(self.current_variant))
        variant_spinbox = ttk.Spinbox(dialog, from_=1, to=7, textvariable=variant_var,
                                      width=10, font=("Arial", 11))
        variant_spinbox.pack(pady=5)

        def apply_variant():
            try:
                variant = int(variant_var.get())
                if 1 <= variant <= 7:
                    if variant == 2:
                        self.current_variant = variant
                        messagebox.showinfo("Успех", ...)
                        dialog.destroy()
                        self.update_variant_display()
                        self.setup_menu()
                    else:
                        messagebox.showwarning("Недостаточно данных",
                                               f"Вариант {variant}:\n\n"
                                               "❌ Недостаточно данных для выполнения расчета.\n\n"
                                               "Пожалуйста, выберите вариант 2 для полноценной работы.\n\n"
                                               "Доступные данные:\n"
                                               "• Параметры теплообменника: только для варианта 2\n"
                                               "• Граничные условия: только для варианта 2\n"
                                               "• Исходные данные: только для варианта 2")
                else:
                    messagebox.showwarning("Ошибка", "Введите число от 1 до 7")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число")

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Применить", command=apply_variant,  width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy,  width=15).pack(side=tk.LEFT, padx=10)

    def update_variant_display(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label) and "Вариант:" in str(child.cget("text")):
                        child.destroy()

                if self.role == 'admin':
                    ttk.Label(widget, text=f"Вариант: {self.current_variant}",
                              font=("Arial", 10), foreground="green").pack(side=tk.LEFT, padx=(20, 0))
                break

        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == "Описание задачи":
                self.notebook.forget(tab_id)
                break

        self.create_task_tab()

    def create_task_tab(self):
        task_frame = ttk.Frame(self.notebook)
        self.notebook.add(task_frame, text="Описание задачи")

        text_widget = tk.Text(task_frame, wrap=tk.WORD, font=("Arial", 11), padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True)

        params = get_parameters()

        # Добавляем информацию о выбранном варианте
        variant_info = ""
        if self.role == 'admin':
            if self.current_variant == 2:
                variant_info = "\n✅ ВЫБРАН РАБОЧИЙ ВАРИАНТ 2 - все данные доступны\n"
            else:
                variant_info = f"\n⚠️ ВЫБРАН ВАРИАНТ {self.current_variant} - недостаточно данных для расчета\n"

        description = f"""
        ФОРМАЛИЗОВАННОЕ ОПИСАНИЕ ЗАДАЧИ ОПТИМИЗАЦИИ ТЕПЛООБМЕННИКА
        ===========================================================
        {variant_info}
        Целевая функция:
        C(L, S) = {params['price_per_kg']} * [ {params['alpha']} * (L - S)² + {params['beta']} * (1/{params['T1']}) * (S + L - {params['gamma']} * {params['T2']})² ]

        где:
        • L - длина теплообменника (м)
        • S - ширина теплообменника (м)
        • C - затраты на изготовление (у.е.)

        Текущие параметры:
        • alpha = {params['alpha']}
        • beta = {params['beta']}
        • gamma = {params['gamma']}
        • H = {params['T1']}
        • N = {params['T2']}
        • price_per_kg = {params['price_per_kg']}
        • Метод оптимизации: {params.get('optimization_method', 'SLSQP')}

        Ограничения:
        • 1 ≤ L ≤ 15 (длина в допустимых пределах)
        • 1 ≤ S ≤ 12 (ширина в допустимых пределах)
        • L + S ≥ 12 (минимальный периметр)

        Физический смысл:
        Задача заключается в минимизации затрат на изготовление теплообменника 
        при соблюдении геометрических ограничений. Целевая функция учитывает 
        квадратичное отклонение от оптимального соотношения сторон и 
        ограничение по минимальному периметру.

        Математическая запись:

        min L,S  {params['price_per_kg']}[{params['alpha']}(L - S)² + {params['beta']}(S + L - {params['gamma']}*{params['T2']})²/{params['T1']}]

        при условиях:
        L ∈ [1, 15]
        S ∈ [1, 12]
        L + S ≥ 12
        """

        # Если выбран не вариант 2, добавляем предупреждение
        if self.role == 'admin' and self.current_variant != 2:
            description += f"""

            ⚠️ ⚠️ ⚠️ ПРЕДУПРЕЖДЕНИЕ ⚠️ ⚠️ ⚠️

            Выбран вариант {self.current_variant}.

            Для этого варианта отсутствуют необходимые данные для выполнения 
            оптимизационного расчета.

            Пожалуйста, выберите вариант 2 для получения корректных результатов.
            """

        text_widget.insert(tk.END, description)
        text_widget.config(state=tk.DISABLED)

    def create_plots_tab(self):
        plots_frame = ttk.Frame(self.notebook)
        self.notebook.add(plots_frame, text="Графики и результаты")

        control_frame = ttk.Frame(plots_frame, padding="10")
        control_frame.pack(fill=tk.X)

        ttk.Button(control_frame, text="📊 ПОСТРОИТЬ ГРАФИКИ",
                   command=self.build_plots).pack(side=tk.LEFT, padx=5)

        self.results_frame = ttk.LabelFrame(plots_frame, text="Результаты оптимизации", padding="10")
        self.results_frame.pack(fill=tk.X, padx=10, pady=5)

        self.results_text = tk.Text(self.results_frame, height=6, font=("Arial", 10))
        self.results_text.pack(fill=tk.X)
        self.results_text.config(state=tk.DISABLED)

        self.graphs_frame = ttk.Frame(plots_frame)
        self.graphs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def build_plots(self):
        if self.role == 'admin' and self.current_variant != 2:
            messagebox.showwarning(
                "Недостаточно данных",
                f"Вариант {self.current_variant}:\n\n"
                "❌ Невозможно выполнить оптимизационный расчет.\n\n"
                "Причина: отсутствуют необходимые исходные данные.\n\n"
                "Решение: выберите вариант 2 в меню 'Администрирование → Выбор варианта'"
            )
            return

        try:
            x0 = [8, 6]

            # Используем выбранный метод оптимизации
            method = self.params.get('optimization_method', 'SLSQP')

            from optimization_core import optimize_with_method
            result = optimize_with_method(method, x0)

            if result is not None and result.success:
                self.L_opt, self.S_opt = result.x
                self.cost_opt = result.fun

                for widget in self.graphs_frame.winfo_children():
                    widget.destroy()

                plot_notebook = ttk.Notebook(self.graphs_frame)
                plot_notebook.pack(fill=tk.BOTH, expand=True)

                frame_2d = ttk.Frame(plot_notebook)
                plot_notebook.add(frame_2d, text="2D Контурный график")
                self.create_2d_plot(frame_2d)

                frame_3d = ttk.Frame(plot_notebook)
                plot_notebook.add(frame_3d, text="3D Поверхность")
                self.create_3d_plot(frame_3d)

                self.update_results()
                messagebox.showinfo("Успех",
                                    f"Оптимизация выполнена!\n\n"
                                    f"Использованный метод: {method}\n"
                                    f"Количество итераций: {result.nit if hasattr(result, 'nit') else 'N/A'}")
            else:
                error_msg = "Не удалось найти оптимальное решение"
                if result is not None and hasattr(result, 'message'):
                    error_msg += f"\n\nСообщение: {result.message}"
                messagebox.showerror("Ошибка", error_msg)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении графиков: {str(e)}")

    def create_2d_plot(self, parent):
        fig = plot_contour(self.L_opt, self.S_opt)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_3d_plot(self, parent):
        fig = plot_3d_surface(self.L_opt, self.S_opt)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_results(self):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)

        method = self.params.get('optimization_method', 'SLSQP')

        results = f"""
        Метод оптимизации: {method}
        Оптимальная длина L: {self.L_opt:.2f} м
        Оптимальная ширина S: {self.S_opt:.2f} м
        Минимальные затраты: {self.cost_opt:.2f} у.е.
        Сумма L+S: {self.L_opt + self.S_opt:.2f} м

        Проверка ограничений:
        • L ≥ 1: {'✓ выполнено' if self.L_opt >= 1 else '✗ не выполнено'}
        • L ≤ 15: {'✓ выполнено' if self.L_opt <= 15 else '✗ не выполнено'}
        • S ≥ 1: {'✓ выполнено' if self.S_opt >= 1 else '✗ не выполнено'}
        • S ≤ 12: {'✓ выполнено' if self.S_opt <= 12 else '✗ не выполнено'}
        • L + S ≥ 12: {'✓ выполнено' if self.L_opt + self.S_opt >= 12 else '✗ не выполнено'}
        """

        self.results_text.insert(tk.END, results)
        self.results_text.config(state=tk.DISABLED)

    def open_user_management(self):
        UserManagementWindow(self.root)

    def open_task_settings(self):
        TaskSettingsWindow(self.root, self)

    def logout(self):
        if messagebox.askyesno("Подтверждение", "Вы действительно хотите выйти?"):
            self.root.destroy()
            login = LoginWindow()
            login.run()

    def run(self):
        self.root.mainloop()


class UserManagementWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Управление пользователями")
        self.window.geometry("600x500")
        self.window.resizable(False, False)

        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        list_frame = ttk.LabelFrame(self.window, text="Список пользователей", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('ID', 'Username', 'Role', 'Created At')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = ttk.Frame(self.window, padding="10")
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="➕ Добавить", command=self.add_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Удалить", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_users).pack(side=tk.LEFT, padx=5)

    def load_users(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        users = get_all_users()
        for user in users:
            self.tree.insert('', tk.END, values=user)

    def add_user(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Добавление пользователя")
        dialog.geometry("300x250")
        dialog.resizable(False, False)

        ttk.Label(dialog, text="Имя пользователя:").pack(pady=(20, 5))
        username_entry = ttk.Entry(dialog, width=30)
        username_entry.pack()

        ttk.Label(dialog, text="Пароль:").pack(pady=(10, 5))
        password_entry = ttk.Entry(dialog, width=30, show="•")
        password_entry.pack()

        ttk.Label(dialog, text="Роль:").pack(pady=(10, 5))
        role_var = tk.StringVar(value="user")
        role_combo = ttk.Combobox(dialog, textvariable=role_var, values=["user", "admin"], state="readonly")
        role_combo.pack()

        def save():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            role = role_var.get()

            if username and password:
                if add_user(username, password, role):
                    messagebox.showinfo("Успех", f"Пользователь {username} добавлен")
                    dialog.destroy()
                    self.load_users()
                else:
                    messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует")
            else:
                messagebox.showwarning("Предупреждение", "Заполните все поля")

        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=20)

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления")
            return

        user_id = self.tree.item(selected[0])['values'][0]
        username = self.tree.item(selected[0])['values'][1]

        if messagebox.askyesno("Подтверждение", f"Удалить пользователя {username}?"):
            if delete_user(user_id):
                messagebox.showinfo("Успех", "Пользователь удален")
                self.load_users()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить пользователя")


class TaskSettingsWindow:
    def __init__(self, parent, main_app):
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("Параметры задачи оптимизации")
        self.window.geometry("500x450")
        self.window.resizable(False, False)

        self.params = get_parameters()

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="РЕДАКТИРОВАНИЕ ПАРАМЕТРОВ ЦЕЛЕВОЙ ФУНКЦИИ",
                  font=("Arial", 12, "bold")).pack(pady=(0, 20))

        param_frame = ttk.LabelFrame(main_frame, text="Параметры", padding="15")
        param_frame.pack(fill=tk.BOTH, expand=True)

        row1 = ttk.Frame(param_frame)
        row1.pack(fill=tk.X, pady=5)
        ttk.Label(row1, text="alpha (коэффициент разности сторон):", width=30, anchor=tk.W).pack(side=tk.LEFT)
        self.alpha_var = tk.StringVar(value=str(self.params['alpha']))
        ttk.Entry(row1, textvariable=self.alpha_var, width=15).pack(side=tk.RIGHT)

        row2 = ttk.Frame(param_frame)
        row2.pack(fill=tk.X, pady=5)
        ttk.Label(row2, text="beta (коэффициент периметра):", width=30, anchor=tk.W).pack(side=tk.LEFT)
        self.beta_var = tk.StringVar(value=str(self.params['beta']))
        ttk.Entry(row2, textvariable=self.beta_var, width=15).pack(side=tk.RIGHT)

        row3 = ttk.Frame(param_frame)
        row3.pack(fill=tk.X, pady=5)
        ttk.Label(row3, text="gamma (коэффициент N):", width=30, anchor=tk.W).pack(side=tk.LEFT)
        self.gamma_var = tk.StringVar(value=str(self.params['gamma']))
        ttk.Entry(row3, textvariable=self.gamma_var, width=15).pack(side=tk.RIGHT)

        row4 = ttk.Frame(param_frame)
        row4.pack(fill=tk.X, pady=5)
        ttk.Label(row4, text="T1 (**************):", width=30, anchor=tk.W).pack(side=tk.LEFT)
        self.T1_var = tk.StringVar(value=str(self.params['T1']))
        ttk.Entry(row4, textvariable=self.T1_var, width=15).pack(side=tk.RIGHT)

        row5 = ttk.Frame(param_frame)
        row5.pack(fill=tk.X, pady=5)
        ttk.Label(row5, text="T2 (*************):", width=30, anchor=tk.W).pack(side=tk.LEFT)
        self.T2_var = tk.StringVar(value=str(self.params['T2']))
        ttk.Entry(row5, textvariable=self.T2_var, width=15).pack(side=tk.RIGHT)
        
        row51 = ttk.Frame(param_frame)
        row51.pack(fill=tk.X, pady=5)
        ttk.Label(row5, text="P1 (************):", width=30, anchor=tk.W).pack(side=tk.LEFT)
        self.p1_var = tk.StringVar(value=str(self.params['p1']))
        ttk.Entry(row5, textvariable=self.T2_var, width=15).pack(side=tk.RIGHT)

        row52 = ttk.Frame(param_frame)
        row52.pack(fill=tk.X, pady=5)
        ttk.Label(row5, text="P2 (************):", width=30, anchor=tk.W).pack(side=tk.LEFT)
        self.p2_var = tk.StringVar(value=str(self.params['p2']))
        ttk.Entry(row5, textvariable=self.T2_var, width=15).pack(side=tk.RIGHT)
        
        

        row6 = ttk.Frame(param_frame)
        row6.pack(fill=tk.X, pady=5)
        ttk.Label(row6, text="price_per_kg (стоимость 1 кг):", width=30, anchor=tk.W).pack(side=tk.LEFT)
        self.price_var = tk.StringVar(value=str(self.params['price_per_kg']))
        ttk.Entry(row6, textvariable=self.price_var, width=15).pack(side=tk.RIGHT)

        ttk.Label(param_frame, text="Ограничения (фиксированы):", font=("Arial", 9, "bold")).pack(anchor=tk.W,
                                                                                                  pady=(15, 5))
        ttk.Label(param_frame, text="• 1 ≤ L ≤ 15\n• 1 ≤ S ≤ 12\n• L + S ≥ 12 *********************", justify=tk.LEFT).pack(anchor=tk.W)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(btn_frame, text="💾 Сохранить", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✖ Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="↺ Сбросить", command=self.reset_settings).pack(side=tk.RIGHT, padx=5)

    def save_settings(self):
        try:
            alpha = float(self.alpha_var.get())
            beta = float(self.beta_var.get())
            gamma = float(self.gamma_var.get())
            T1 = float(self.T1_var.get())
            T2 = float(self.T2_var.get())
            p1 = float(self.p1_var.get())
            p2 =float(self.p2_var.get())
            price = float(self.price_var.get())

            set_parameters(alpha, beta, gamma, T1, T2, p1, p2, price)

            self.main_app.params = get_parameters()

            for tab_id in self.main_app.notebook.tabs():
                if self.main_app.notebook.tab(tab_id, "text") == "Описание задачи":
                    self.main_app.notebook.forget(tab_id)
                    break

            self.main_app.create_task_tab()

            self.main_app.L_opt = None
            self.main_app.S_opt = None
            self.main_app.cost_opt = None

            messagebox.showinfo("Успех", "Параметры успешно сохранены в settings.txt")
            self.window.destroy()

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")

    def reset_settings(self):
        default = {
            'alpha': 1.0,
            'beta': 1.0,
            'gamma': 1.0,
            'T1': 9,
            'T2': 10,
            'price_per_kg': 100
        }

        self.alpha_var.set(str(default['alpha']))
        self.beta_var.set(str(default['beta']))
        self.gamma_var.set(str(default['gamma']))
        self.T1_var.set(str(default['T1']))
        self.T2_var.set(str(default['T2']))
        self.p1_var.set(str(default['p1']))
        self.p2_var.set(str(default['p2']))
        self.price_var.set(str(default['price_per_kg']))


class MethodsHelpWindow:

    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Справка - Методы оптимизации")
        self.window.geometry("650x550")
        self.window.resizable(True, True)

        # Центрирование окна
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.window.winfo_screenheight() // 2) - (550 // 2)
        self.window.geometry(f'650x550+{x}+{y}')

        self.setup_ui()

    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        title_label = tk.Label(main_frame, text="📚 МЕТОДЫ ОПТИМИЗАЦИИ",
                               font=("Arial", 14, "bold"), fg="#2c3e50")
        title_label.pack(pady=(0, 15))

        # Текстовое поле с прокруткой
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Arial", 10),
                                   yscrollcommand=scrollbar.set, padx=15, pady=15)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_widget.yview)

        # Вставка описаний методов
        self.insert_methods_description()

        # Кнопка закрытия
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))

        ttk.Button(btn_frame, text="Закрыть", command=self.window.destroy).pack()

    def insert_methods_description(self):
        descriptions = """ *******************************
══════════════════════════════════════════════════════════════

1. SLSQP (Sequential Least Squares Programming)
──────────────────────────────────────────────────────────────
Тип метода: Градиентный / Последовательное квадратичное программирование

Принцип работы:
• Использует информацию о производных (градиенте) целевой функции
• На каждой итерации решает задачу квадратичного программирования
• Последовательно улучшает решение, двигаясь в направлении антиградиента

Особенности:
✓ Быстрая сходимость для гладких функций
✓ Точно соблюдает ограничения
✗ Требует вычисления производных (используется численное дифференцирование)
✗ Может застревать в локальных минимумах

Когда использовать: Для гладких, выпуклых или почти выпуклых функций, 
когда важна скорость вычислений.

══════════════════════════════════════════════════════════════

2. Дифференциальная эволюция (Differential Evolution)
──────────────────────────────────────────────────────────────
Тип метода: Эволюционный / Генетический алгоритм

Принцип работы:
• Создается популяция потенциальных решений
• На каждом поколении:
  - Выбираются случайные особи для "мутации"
  - Создаются новые решения путем комбинации существующих
  - Лучшие решения переходят в следующее поколение

Особенности:
✓ Не требует вычисления производных
✓ Хорошо находит глобальный минимум
✓ Устойчив к "оврагам" и разрывам функции
✗ Медленнее градиентных методов
✗ Требует настройки параметров (размер популяции, коэффициент мутации)

Когда использовать: Для многоэкстремальных задач, когда важно найти 
глобальный оптимум, а не локальный.

════════════════════════════════════════════════════════════

3. Имитация отжига (Simulated Annealing / Dual Annealing)
────────────────────────────────────────────────────────────
Тип метода: Метаэвристический / Вероятностный

Принцип работы:
• Имитирует процесс отжига металлов при закалке
• На начальных этапах может принимать ухудшающие решения (высокая "температура")
• Со временем "температура" снижается, и алгоритм становится более консервативным
• Dual Annealing использует два этапа: глобальный и локальный поиск

Особенности:
✓ Находит глобальный оптимум с высокой вероятностью
✓ Не требует производных
✓ Хорош для сложных ландшафтов
✗ Медленный (много вычислений целевой функции)
✗ Зависит от выбора начальной температуры и графика охлаждения

Когда использовать: Для сложных, сильно изрезанных функций, когда 
дифференциальная эволюция работает медленно.

══════════════════════════════════════════════════════════════

СРАВНИТЕЛЬНАЯ ТАБЛИЦА
──────────────────────────────────────────────────────────────
▶ СКОРОСТЬ (от самой быстрой к самой медленной):
    1. SLSQP — ⚡⚡⚡ (очень быстро)
    2. Дифференциальная эволюция — ⚡⚡ (средне)
    3. Имитация отжига — ⚡ (медленно)

▶ ГЛОБАЛЬНЫЙ ПОИСК (способность находить глобальный минимум):
    • SLSQP — ⭐ (только локальный поиск)
    • Дифференциальная эволюция — ⭐⭐⭐ (отлично)
    • Имитация отжига — ⭐⭐⭐ (отлично)

▶ ТОЧНОСТЬ РЕШЕНИЯ:
    • SLSQP — ⭐⭐⭐ (высокая точность)
    • Дифференциальная эволюция — ⭐⭐ (средняя)
    • Имитация отжига — ⭐⭐ (средняя)

▶ РАБОТА С ЗАШУМЛЕННЫМИ ФУНКЦИЯМИ:
    • SLSQP — ❌ (плохо)
    • Дифференциальная эволюция — ✅ (хорошо)
    • Имитация отжига — ✅ (хорошо)

▶ НЕОБХОДИМОСТЬ В ПРОИЗВОДНЫХ:
    • SLSQP — ✅ (требует, использует численное дифференцирование)
    • Дифференциальная эволюция — ❌ (не требует)
    • Имитация отжига — ❌ (не требует)

РЕКОМЕНДАЦИИ ПО ВЫБОРУ
─────────────────────────────────────────────────────────────
• Для быстрой оценки → используйте SLSQP
• Если функция имеет множество локальных минимумов → используйте 
  Дифференциальную эволюцию
• Для сложных, разрывных функций → используйте Имитацию отжига
• Если результат SLSQP вызывает сомнения → проверьте другим методом

════════════════════════════════════════════════════════════
        """

        self.text_widget.insert(tk.END, descriptions)
        self.text_widget.config(state=tk.DISABLED)

def main():
    if not os.path.exists('users.db'):
        import create_db
        create_db.create_database()

    login = LoginWindow()
    login.run()


if __name__ == "__main__":
    main()