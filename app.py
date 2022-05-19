import argparse
from time import sleep
from typing import Final
import csv

import requests

USER_INFO_TYPE = dict[str, str]

HOST: Final[str] = "ui.mob-edu.ru"
BASE_URL: Final[str] = "https://" + HOST
REFERER_URL: Final[str] = BASE_URL + "/ui/index.html"
AUTH_API_URL: Final[str] = BASE_URL + "/api/authenticate"
BASE_HEADERS: dict[str, str] = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ru-RU,ru;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6",
    "Content-Type": "application/json;charset=UTF-8",
    "Host": HOST,
    "Origin": BASE_URL,
    "Referer": REFERER_URL,
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-platform": "Linux",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
}


def get_users(filename: str, delimiter: str = ",") -> list[USER_INFO_TYPE]:
    with open(filename, newline='') as csvfile:
        users: list[dict[str, str]] = []
        for row in csv.reader(csvfile, delimiter=delimiter):
            users.append({
                "name": row[1],
                "login": row[2].strip(),
                "password": row[3]
            })

        return users


def process(user: USER_INFO_TYPE) -> tuple[str, str]:
    try:
        result = requests.post(
            AUTH_API_URL,
            json={"username": user["login"], "password": user["password"]},
            headers=BASE_HEADERS
        )

        if result.status_code == 403:
            return "Ошибка", "Неправильный Логин/Пароль"

        if result.status_code == 200:
            return "Успешно", ""

        return "Ошибка", result.text

    except Exception as exc:
        return "Ошибка", f"Не удалось выполнить авторизацию: {exc}"


def main(file: str, delimiter: str, delay: float):
    users = get_users(filename=file, delimiter=delimiter)

    ok, fails = 0, 0
    fail_names = []
    for user in users:
        if not user["name"]:
            continue

        status, error = process(user)
        print(f"Вход под пользователем {user['name']:30} СТАТУС: {status:10}")

        if error:
            print(f"\n{'='*60}\n\tОшибка входа под пользователем '{user['name']}'\n\t{error}\n{'='*60}\n")
            fails += 1
            fail_names.append(user["name"])
        else:
            ok += 1

        sleep(delay)

    print(f"\n{'=' * 60}\n\tОбработка завершена\n")
    print(f"\tУСПЕШНО: {ok}")
    print(f"\tОШИБКА: {fails}")

    if fail_names:
        print(f"\tПОЛЬЗОВАТЕЛИ С ОШИБКОЙ:")
        for user in fail_names:
            print(f"\t{user}")

    print(f"\n{'=' * 60}\n\t")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parser')
    parser.add_argument("--file", type=str, dest="file", help="CSV-файл с логинами и паролями")
    parser.add_argument("--delimiter", type=str, dest="delimiter", default=",", help="Разделитель в CSV-файле")
    parser.add_argument("--delay", type=float, dest="delay", default=1.0, help="Задержка между запросами")

    args = parser.parse_args()

    main(file=args.file, delimiter=args.delimiter, delay=args.delay)
