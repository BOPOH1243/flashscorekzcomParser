# csv_exporter.py
import csv


def export_to_csv(data, filename="corners_stats.csv"):
    """
    Сохраняет список словарей в CSV в формате:
    <название команды>,<средний тотал угловых>,<средний индивидуальный тотал>,<средний тотал соперников>
    """
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # заголовки
        writer.writerow([
            "team",
            "avg_total_corners",
            "avg_team_corners",
            "avg_opponent_corners"
        ])
        # строки с данными
        for row in data:
            writer.writerow([
                row["team"],
                round(row["avg_total_corners"], 2),
                round(row["avg_team_corners"], 2),
                round(row["avg_opponent_corners"], 2),
            ])
