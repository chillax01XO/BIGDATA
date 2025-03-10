from typing import List


def tic_tac_toe_checker(board: List[List[str]]) -> str:

    size = 3
    win_lines = []

    # Проверка строк и столбцов
    for i in range(size):
        win_lines.append(board[i])  # Строка
        win_lines.append([board[j][i] for j in range(size)])  # Столбец

    # Проверка диагоналей
    win_lines.append([board[i][i] for i in range(size)])
    win_lines.append([board[i][size - 1 - i] for i in range(size)])

    # Ищем победителя
    for line in win_lines:
        if all(cell == "x" for cell in line):
            return "Победа -> X"
        if all(cell == "o" for cell in line):
            return "Победа -> O"

    # Проверяем, есть ли пустые клетки
    if any("-" in row for row in board):
        return "Игра незакончена! "

    return "Ничья"

# Игровое поле
board =  [["o", "o", "x"],
          ["x", "x", "o"],
          ["o", "o", "x"]]


print(tic_tac_toe_checker(board))
