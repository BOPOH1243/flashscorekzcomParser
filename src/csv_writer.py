# csv_writer.py
import csv
from typing import Iterable, Tuple


def save_team_corners_csv(filepath: str, rows: Iterable[Tuple[str, float, float, float]]):
    """
    rows: iterable строк формата (team_name, avg_total, avg_team, avg_opponent)
    Сохраняет CSV в формате:
    <название команды>,<среднее значение тотала угловых>,<среднее индивидуальное для команды>,<среднее индивидуальное для соперника>
    """
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # заголовок (опционально)
        writer.writerow(["team", "avg_total_corners", "avg_team_corners", "avg_opponent_corners"])
        for row in rows:
            writer.writerow([row[0], f"{row[1]:.2f}", f"{row[2]:.2f}", f"{row[3]:.2f}"])
