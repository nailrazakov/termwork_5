import requests


def get_employer_vacancies(id_company: str) -> list:
    """Получает список вакансий с необходимыми данными по id компании"""
    vacancies_list = []
    for page in range(10):
        url = "https://api.hh.ru/vacancies?employer_id=" + id_company  # ссылка для работы с Api конкретной компании
        headers = {
            "User-Agent": "User Agent",  # HH requires User-Agent or HH-User-Agen
        }
        params = {
            "page": page,
            "per_page": 100,
            "period": 10
        }
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            vacancies = data.get("items", [])
            for vacancy in vacancies:
                vacancy_id = vacancy.get("id")
                vacancy_title = vacancy.get("name")
                vacancy_url = vacancy.get("alternate_url")
                # company_name = vacancy.get("employer", {}).get("name")
                # published_iso = vacancy.get("published_at")
                # published = isodate.parse_datetime(published_iso)
                # responsibility = vacancy.get('snippet', {}).get('responsibility')
                try:
                    if vacancy.get("salary", {}).get("from") != None:
                        salary_from = vacancy.get("salary", {}).get("from")
                    else:
                        salary_from = 0
                except AttributeError:
                    salary_from = 0
                try:
                    if vacancy.get("salary", {}).get("to") != None:
                        salary_to = vacancy.get("salary", {}).get("to")
                    else:
                        salary_to = 0
                except AttributeError:
                    salary_to = 0
                if salary_to < salary_from:
                    salary_to = salary_from
                vacancies_list.append((vacancy_title, vacancy_url, salary_from, salary_to, vacancy_id, id_company))
        else:
            print(f"Request failed with status code: {response.status_code}")
    return vacancies_list


def get_employer_id(user_company_name: str) -> dict or None:
    """Поиск id компании"""
    name_found = 0  # Переменная для подсчета найденного точного соответствия запроса и результата поиска
    similar_name_found = 0  # Переменная для подсчета найденного НЕ точного соответствия запроса и результата поиска
    similar_company_found = []  # Список найденных компаний НЕ точного соответствия запроса
    url = "https://api.hh.ru/employers"  # ссылка для работы с Api по поиску и просмотру вакансий
    headers = {
        "User-Agent": "User Agent",  # HH requires User-Agent or HH-User-Agen
    }
    params = {
        "text": user_company_name,
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        rows = data.get("items", [])
        for row in rows:
            if row.get('name') == user_company_name:
                company_id_f = row.get("id")
                company_name_f = row.get("name")
                company_open_vacancies_f = row.get('open_vacancies')
                name_found += 1
            else:
                if int(row.get('open_vacancies')) > 10:
                    company_name = row.get("name")
                    company_id = row.get("id")
                    count_vacancy = row.get('open_vacancies')
                    similar_name_found += 1
                    similar_company_found.append((company_name, company_id, int(count_vacancy)))
                    continue
        # обработка результатов поиска
        if name_found == 1 and similar_name_found == 1:
            print(f"Найдена компания:\nНазвание компании - {company_name_f}, id компании - {company_id_f}, "
                  f"Открытые вакансии - {company_open_vacancies_f}")
            print("Есть еще компания с похожим именем")
            print(f"{company_name} - количество вакансий - {count_vacancy}")
            return {"main": (company_name_f, company_id_f), "alternative": (company_name, company_id)}
        elif name_found == 0 and similar_name_found == 1:
            print("Есть еще компания с похожим именем")
            print(f"{company_name} - количество вакансий - {count_vacancy}")
            return {"main": (company_name, company_id), "alternative": (company_name, company_id)}
        elif name_found == 1 and similar_name_found == 0:
            print(f"Найдена компания:\nНазвание компании - {company_name_f}, id компании - {company_id_f}, "
                  f"Открытые вакансии - {company_open_vacancies_f}")
            return {"main": (company_name_f, company_id_f), "alternative": (company_name_f, company_id_f)}
        elif name_found == 0 and similar_name_found > 1:
            sorted_data_list = sorted(similar_company_found, key=lambda x: x[2], reverse=True)
            print(f"Не найдено точного соответствия\nВот две с большим количеством открытых вакансий\n"
                  f"{sorted_data_list[0][0]} - количество вакансий {sorted_data_list[0][2]}\n"
                  f"{sorted_data_list[1][0]} - количество вакансий {sorted_data_list[1][2]}")
            return {"main": (sorted_data_list[0][0], sorted_data_list[0][1]),
                    "alternative": (sorted_data_list[1][0], sorted_data_list[1][1])}
        elif name_found == 1 and similar_name_found > 1:
            print(f"Найдена компания:\nНазвание компании - {company_name_f}, id компании - {company_id_f}, "
                  f"Открытые вакансии - {company_open_vacancies_f}")
            print("Есть еще компания с похожим именем")
            sorted_data_list = sorted(similar_company_found, key=lambda x: x[2], reverse=True)
            print(f"С наибольшим количеством вакансий\n"
                  f"{sorted_data_list[0][0]} - количество вакансий {sorted_data_list[0][2]}\n")
            return {"main": (company_name_f, company_id_f),
                    "alternative": (sorted_data_list[0][0], sorted_data_list[0][1])}
        else:
            print('Не найдено компаний с открытыми вакансиями > 10')
            return None
    else:
        print(f"Request failed with status code: {response.status_code}")
