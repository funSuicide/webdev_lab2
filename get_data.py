import json
import requests
from bs4 import BeautifulSoup


def get_data():
    data = {"groups": [], "staff": []}

    for i in range(1, 6):
        url = f"https://ssau.ru/rasp/faculty/492430598?course={i}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        groups = soup.select(".group-catalog__groups > a")
        for group in groups:
            group_id = ''.join(filter(str.isdigit, group.get("href")))
            data["groups"].append({"group_number": group.text, "link": f"/rasp?groupId={group_id}"})

    for i in range(1, 120):
        url = f"https://ssau.ru/staff?page={i}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        staff = soup.select(".list-group-item > a")
        for person in staff:
            person_id = ''.join(filter(str.isdigit, person.get("href")))
            data["staff"].append({"person_name": person.text, "link": f"/rasp?staffId={person_id}"})

    with open("data.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False)


def main():
    get_data()


if __name__ == "__main__":
    main()
