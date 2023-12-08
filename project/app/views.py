from django.shortcuts import render
import json
import requests
from bs4 import BeautifulSoup
import re

DEFAULT_URL = 'https://ssau.ru/rasp?groupId=531030143'
TIME_MARKS = ['08:00 - 09:35', '09:45 - 11:20', '11:30 - 13:05', '13:30 - 15:05', '15:15 - 16:50', '17:00 - 18:35']
DEFAULT_PARAM = '6411-100503D'


def get_lists_data():
    data = []
    with open('data.json', 'r', encoding='utf-8') as json_data:
        load_data = json.load(json_data)
    for group in load_data['groups']:
        data.append(group['group_number'])
    for person in load_data['staff']:
        data.append(person['person_name'])
    return data


def get_current_week():
    url = DEFAULT_URL
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    current_week = soup.find('span', class_='h3-text week-nav-current_week')
    current_week = re.findall(r'\d+', current_week.text)[0]
    return int(current_week)


def parse_html(html, student):
    soup = BeautifulSoup(html, 'html.parser')
    schedule_items = soup.find_all('div', class_='schedule__item')
    schedule_data = {0: [], 1: [], 2: [], 3: [], 4: [], 5: []}
    number_day = -1
    schedule_items = schedule_items[7:]
    for item in schedule_items:
        if item.find('div', class_='schedule__lesson lesson-border lesson-border-type-1') or True:
            try:
                if student:
                    subject = item.find('div', class_='schedule__discipline').text.strip()
                    place = item.find('div', class_='schedule__place').text.strip()
                    person = item.find('div', class_='schedule__teacher').text.strip()
                else:
                    subject = item.find('div', class_='body-text schedule__discipline lesson-color lesson-color-type-1'
                                        ).text.strip()
                    place = item.find('div', class_='caption-text schedule__place').text.strip()
                    person = None
                groups = [group.text.strip() for group in item.find_all('a', class_='caption-text schedule__group')]
            except:
                subject = 'None'
                place = 'None'
                person = 'None'
                groups = 'None'
            time_borders = (item.find_all_previous('div', class_='schedule__time')[0].
                            find_all('div', class_='schedule__time-item'))
            left_border = time_borders[0].text.strip()
            right_border = time_borders[1].text.strip()

            if number_day == 5:
                number_day = -1
            number_day += 1

            schedule_data[number_day].append({
                'time': f'{left_border} - {right_border}',
                'subject': subject,
                'place': place,
                'person': person,
                'groups': groups
            })

    return schedule_data


def get_schedule_data(request):
    times = TIME_MARKS
    param = DEFAULT_PARAM
    names = get_lists_data()
    current_week = get_current_week()
    week_shift = int(request.POST.get('week_shift', 0))
    search_url = DEFAULT_URL
    is_group = True
    result_week = current_week + week_shift
    with open('data.json', 'r', encoding='utf-8') as data_json:
        data = json.load(data_json)
    if request.method == 'POST':
        param = request.POST.get('data_query')
        if current_week - week_shift < 0 and week_shift < 0:
            current_week = abs(week_shift)
        for group in data['groups']:
            if param in group['group_number']:
                group_link = group['link']
                search_url = f'https://ssau.ru/{group_link}&selectedWeek={current_week + week_shift}&selectedWeekday=1'
                break
        for teacher in data['staff']:
            if teacher['person_name'].find(param) != -1:
                is_group = False
                teacher_link = teacher['link']
                search_url = f'https://ssau.ru/{teacher_link}&selectedWeek={current_week + week_shift}&selectedWeekday=1'
                break
    response = requests.get(search_url)
    html_code = response.text
    schedule = parse_html(html_code, is_group)
    for day, entries in schedule.items():
        for entry in entries:
            for key, value in entry.items():
                if value == 'None':
                    entry[key] = ''
    return render(request, 'index.html',
                  {'schedule': schedule, 'time_slots': times, 'current_data': param,
                   'current_week': current_week, 'all_data': names, 'result_week': result_week})
