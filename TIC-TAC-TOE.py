import tkinter as tk
from tkinter import messagebox
import psycopg2
import json


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Крестики-Нолики")
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.connection = self.connect_to_db()
        self.create_start_screen()

    def connect_to_db(self):
        try:
            # Подключение к базе данных PostgreSQL
            conn = psycopg2.connect(
                dbname="tic-tac-toe",
                user="postgres",  # Укажите имя пользователя
                password="",  # Укажите пароль
                host="localhost",  # Укажите хост (например, localhost)
                port="2006"  # Укажите порт (по умолчанию 5432)
            )
            print("Соединение с базой данных успешно!")
            return conn
        except Exception as e:
            print("Ошибка подключения к базе данных:", e)
            return None

    def register_user(self, username):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (username)
                    VALUES (%s)
                    RETURNING user_id;
                    """,
                    (username,)
                )
                user_id = cursor.fetchone()[0]
                self.connection.commit()
                print(f"Пользователь {username} зарегистрирован с ID {user_id}")
                return user_id
        except Exception as e:
            print("Ошибка регистрации пользователя:", e)
            return None

    def save_game_result(self, player_x_id, player_o_id, winner, moves):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO games (player_x, player_o, winner, moves)
                    VALUES (%s, %s, %s, %s)
                    RETURNING game_id, start_time;
                    """,
                    (player_x_id, player_o_id, winner, json.dumps(moves))
                )
                game_id, start_time = cursor.fetchone()
                self.connection.commit()
                print(f"Игра {game_id} сохранена, началась в {start_time}.")
                return game_id
        except Exception as e:
            print("Ошибка сохранения результата игры:", e)

    def update_statistics(self, user_id, result):
        try:
            with self.connection.cursor() as cursor:
                # Проверим, есть ли уже запись о статистике для этого пользователя
                cursor.execute(
                    """
                    SELECT * FROM statistics WHERE user_id = %s;
                    """,
                    (user_id,)
                )
                stat = cursor.fetchone()

                # Если записи нет, создаём её
                if not stat:
                    cursor.execute(
                        """
                        INSERT INTO statistics (user_id, games_played, games_won, games_drawn, games_lost)
                        VALUES (%s, 0, 0, 0, 0);
                        """,
                        (user_id,)
                    )
                    self.connection.commit()

                # Обновляем статистику в зависимости от результата игры
                if result == "X":
                    cursor.execute(
                        """
                        UPDATE statistics
                        SET games_played = games_played + 1, games_won = games_won + 1
                        WHERE user_id = %s;
                        """,
                        (user_id,)
                    )
                elif result == "O":
                    cursor.execute(
                        """
                        UPDATE statistics
                        SET games_played = games_played + 1, games_lost = games_lost + 1
                        WHERE user_id = %s;
                        """,
                        (user_id,)
                    )
                elif result == "Draw":
                    cursor.execute(
                        """
                        UPDATE statistics
                        SET games_played = games_played + 1, games_drawn = games_drawn + 1
                        WHERE user_id = %s;
                        """,
                        (user_id,)
                    )
                self.connection.commit()
        except Exception as e:
            print("Ошибка обновления статистики:", e)

    def create_start_screen(self):
        self.start_window = tk.Toplevel(self.root)
        self.start_window.title("Введите имя игрока")
        self.start_window.geometry("300x150")

        self.name_label = tk.Label(self.start_window, text="Имя игрока:", font=("Arial", 12))
        self.name_label.pack(pady=10)

        self.name_entry = tk.Entry(self.start_window, font=("Arial", 14))
        self.name_entry.pack(pady=10)

        self.start_button = tk.Button(self.start_window, text="Начать игру", font=("Arial", 14),
                                      command=self.start_game)
        self.start_button.pack(pady=10)

    def start_game(self):
        self.player_name = self.name_entry.get()
        self.start_window.destroy()  # Закрыть окно ввода имени
        self.player_id = self.register_user(self.player_name)
        if not self.player_id:
            messagebox.showerror("Ошибка", "Не удалось зарегистрировать пользователя!")
            return
        self.create_widgets()

    def create_widgets(self):
        self.reset_button = tk.Button(self.root, text="Играть снова", height=2, font=("Arial", 14),
                                      command=self.reset_game)
        self.reset_button.grid(row=3, column=0, columnspan=3, pady=20)
        self.reset_button.grid_forget()  # Скрыть кнопку при старте игры

        for row in range(3):
            for col in range(3):
                button = tk.Button(self.root, text=" ", width=10, height=3, font=("Arial", 20),
                                   command=lambda r=row, c=col: self.on_click(r, c))
                button.grid(row=row, column=col)
                self.buttons[row][col] = button

    def on_click(self, row, col):
        if self.board[row][col] == " " and self.current_player == "X":
            self.board[row][col] = self.current_player
            self.buttons[row][col].config(text=self.current_player)
            if self.check_winner(self.current_player):
                self.show_winner(self.current_player)
            else:
                if self.check_draw():
                    self.show_draw()
                else:
                    self.current_player = "O"
                    self.ai_move()

    def ai_move(self):
        best_move = self.best_move()
        if best_move:
            row, col = best_move
            self.board[row][col] = "O"
            self.buttons[row][col].config(text="O")
            if self.check_winner("O"):
                self.show_winner("O")
            else:
                if self.check_draw():
                    self.show_draw()
                else:
                    self.current_player = "X"

    def best_move(self):
        best_val = -float('inf')
        move = None
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == " ":
                    self.board[row][col] = "O"
                    move_val = self.minimax(self.board, 0, False, -float('inf'), float('inf'))
                    self.board[row][col] = " "
                    if move_val > best_val:
                        best_val = move_val
                        move = (row, col)
        return move

    def minimax(self, board, depth, is_maximizing, alpha, beta):
        if self.check_winner("O"):
            return 10 - depth
        if self.check_winner("X"):
            return depth - 10
        if all(cell != " " for row in board for cell in row):
            return 0

        if is_maximizing:
            max_eval = -float('inf')
            for row in range(3):
                for col in range(3):
                    if board[row][col] == " ":
                        board[row][col] = "O"
                        eval = self.minimax(board, depth + 1, False, alpha, beta)
                        board[row][col] = " "
                        max_eval = max(max_eval, eval)
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break
            return max_eval
        else:
            min_eval = float('inf')
            for row in range(3):
                for col in range(3):
                    if board[row][col] == " ":
                        board[row][col] = "X"
                        eval = self.minimax(board, depth + 1, True, alpha, beta)
                        board[row][col] = " "
                        min_eval = min(min_eval, eval)
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break
            return min_eval

    def check_winner(self, player):
        for row in self.board:
            if all(s == player for s in row):
                return True
        for col in range(3):
            if all(self.board[row][col] == player for row in range(3)):
                return True
        if all(self.board[i][i] == player for i in range(3)) or all(self.board[i][2 - i] == player for i in range(3)):
            return True
        return False

    def check_draw(self):
        return all(cell != " " for row in self.board for cell in row)

    def show_winner(self, winner):
        self.save_game_result(self.player_id, self.player_id, winner, self.board)
        self.update_statistics(self.player_id, winner)
        messagebox.showinfo("Игра завершена", f"Победил {winner}!")
        self.reset_button.grid()

    def show_draw(self):
        self.save_game_result(self.player_id, self.player_id, "Draw", self.board)
        self.update_statistics(self.player_id, "Draw")
        messagebox.showinfo("Игра завершена", "Ничья!")
        self.reset_button.grid()

    def reset_game(self):
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(text=" ")
        self.reset_button.grid_forget()


if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
