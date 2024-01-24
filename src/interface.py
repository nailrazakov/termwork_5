# from db_part import DBManager
from src.from_api import get_employer_id
from prettytable import PrettyTable


def what_doing():
    """
    Меню создания списка компаний
    """
    list_of_companies = []
    dict_of_query = {}
    while True:
        print("\nВведите название компании. \nВведите выход - для сохранения списка и выхода.")
        user_input = input("\n>>>")
        if user_input == "выход":
            return list_of_companies
        try:
            dict_of_query = get_employer_id(user_input)
            print(dict_of_query)
            if dict_of_query is not None:
                while True:
                    print("Выберете возможные действия")
                    user_input = input(f"\t\t\t\t\t1 - Добавить компанию в список\n\t\t\t\t\t2 - Выбрать альтернативную\n"
                                       f"\t\t\t\t\t3 - Ввести другую компанию\n\t\t\t\t\t4 - Сохранить список\n>>>")
                    if user_input == "1":
                        list_of_companies.append(dict_of_query["main"])
                        break
                    elif user_input == "2":
                        list_of_companies.append(dict_of_query["alternative"])
                        break
                    elif user_input == "3":
                        break
                    elif user_input == "4":
                        return list_of_companies
                    else:
                        print("Выберете номер соответствующего пункта и нажмите Enter")
            else:
                print('Такой компании не найдено. Попробуйте ещё раз!')
                continue
        except:
            print('Такой компании не найдено. Попробуйте ещё раз')
            break


def data_base_menu(db_request):
    # меню работы с базой данных
    while True:
        print("Выберете возможные действия")
        user_input = input(f"\t\t\t\t\t1 - получить список всех компаний и количество вакансий у каждой компании"
                           f"\n\t\t\t\t\t2 - получить список всех вакансий с указанием названия компании, "
                           f"названия вакансии и зарплаты и ссылки на вакансию."
                           f"\n\t\t\t\t\t3 - получить среднюю зарплату по вакансиям."
                           f"\n\t\t\t\t\t4 - получить список всех вакансий, у которых зарплата выше средней"
                           f"\n\t\t\t\t\t5 - получить список всех вакансий, в названии которых содержатся "
                           f"переданные в метод слова, например python."
                           f"\n\t\t\t\t\t6 - выход в предыдущее меню\n>>>")
        if user_input == "1":
            print("Список компаний")
            company_list = db_request.get_companies_and_vacancies_count()
            colum_names = ['Название компании', 'Количество вакансий']
            table_print(company_list, colum_names)
        elif user_input == "2":
            print("Список вакансий")
            colum_names = ['Названия компании', 'Название вакансии', 'Зарплата', 'Ссылка на вакансию']
            vacancy_list = db_request.get_all_vacancies()
            table_print(vacancy_list, colum_names)
        elif user_input == "3":
            print("Средняя зарплата по вакансиям")
            avg = db_request.get_avg_salary()
            colum_names = ['Среднее значение зарплаты от по всем вакансиям',
                           'Среднее значение зарплаты до по всем вакансиям']
            table_print(avg, colum_names)
        elif user_input == "4":
            print("Список всех вакансий, у которых зарплата выше средней ")
            upper_salary = db_request.get_vacancies_with_higher_salary()
            colum_names = ['Название вакансии', 'Зарплата от', 'Зарплата до', 'Ссылка на вакансию']
            table_print(upper_salary, colum_names)
        elif user_input == "5":
            key_word = input("Введите ключевое слово\n>>>")
            like = db_request.get_vacancies_with_keyword(key_word)
            colum_names = ['Название вакансии', 'Зарплата до', 'Ссылка на вакансию']
            table_print(like, colum_names)
        elif user_input == "6":
            break
        else:
            print("Выберете номер соответствующего пункта и нажмите Enter")


def table_print(data, column_list):
    """Вывод запросов из базы данных в красивой форме"""
    x = PrettyTable()
    x.field_names = column_list  # дописать форму
    data_1 = []
    try:
        for row in data:
            row_list = list(row)
            x.add_row(row_list)
        print(x)
    except TypeError:
        print(f"'Данные для таблицы {column_list} не получены', данные - {data}")


if __name__ == "__main__":
    print(what_doing())
