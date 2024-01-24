import psycopg2
from dotenv import load_dotenv
import os
from src.from_sql import DBManager
from src.from_api import get_employer_vacancies
from src.interface import table_print, data_base_menu, what_doing

load_dotenv()
key = os.getenv('key')
data_base_name = os.getenv('db')
# базово выбранные компании
base_company_list = [('X5 Digital', '4716984'), ('МегаФон', '3127'), ('БКК Коломенский', '2166'),
                     ('Группа ЛСР', '3344'), ('Совкомбанк Страхование', '1111067'), ('Татнефть-АЗС-Запад', '2413989'),
                     ('ЛУКОЙЛ', '907345'), ('Газпром нефть', '39305'), ('СБЕР', '3529'), ('Яндекс', '1740')]
employers_list = []
vacancy_list = []

if __name__ == '__main__':

    print("Здравствуйте, данная программа получает информацию о вакансиях выбранных компаний, размещенных на hh.ru.\n"
          "сохраняет её в базу данных и позволит удобно работать с ней.")
    while True:
        user_input_1 = input("\t\t\t\t\t1 - Работа с базой данных из базового набора компаний(10).\n\t\t\t\t\t"
                             "2 - Работа с базой данных выбранных компаний.\n\t\t\t\t\t"
                             "3 - Выход\n>>>")
        if user_input_1 == "1":
            # работаем с готовой базой данных
            db_object = DBManager('vacancies_test', 'employers_test', base_company_list)
            if db_object.check_table():
                print("Добро пожаловать в базу данных вакансий следующих компаний:\n")
                table_print(db_object.list_of_employers, ['Компания', 'id_компании'])
                # работаем с готовой базой данных
                data_base_menu(db_object)
            else:
                print("Необходима загрузка базы данных")
                db_object.drop_tables()
                db_object.create_db_tables()
                for company in db_object.list_of_employers:
                    print(company)
                    vacancy_list = get_employer_vacancies(company[1])
                    print(len(vacancy_list))
                    connection = psycopg2.connect(host="localhost", database=data_base_name, user="postgres",
                                                  password=key)
                    try:
                        db_object.fill_db((company[0], int(company[1])), vacancy_list)
                    except psycopg2.errors.UniqueViolation:
                        print("Данный работодатель уже загружен")
                        continue

        elif user_input_1 == "2":
            db_user = DBManager('vacancies', 'employers', [])
            while True:
                user_check = input("\t\t\t\t\t1 - Последняя удачная выборка\n\t\t\t\t\t"
                                   "2 - Выбрать работодателей и создать базу\n\t\t\t\t\t"
                                   "3 - Перейти в предыдущее меню\n>>>")
                if user_check == "1":
                    if db_user.check_table():
                        db_user.list_of_employers = db_user.reading_data_from_tables()
                        print("Добро пожаловать в базу данных вакансий следующих компаний:\n")
                        table_print(db_user.list_of_employers, ['Компания', 'id_компании'])
                        # работаем с готовой базой данных
                        data_base_menu(db_user)
                    else:
                        print("Необходима загрузка базы данных")

                elif user_check == "2":
                    # Переход в меню выбора компаний
                    employers_list = what_doing()
                    if len(employers_list) > 0:
                        print("Выбраны следующие компании - ")
                        table_print(employers_list, ['Компания', 'id_компании'])
                        db_user.list_of_employers = employers_list
                        db_user.drop_tables()
                        db_user.create_db_tables()
                        for company in db_user.list_of_employers:
                            print(company)
                            vacancy_list = get_employer_vacancies(company[1])
                            print(len(vacancy_list))
                            connection = psycopg2.connect(host="localhost", database=data_base_name, user="postgres",
                                                          password=key)
                            try:
                                db_user.fill_db((company[0], int(company[1])), vacancy_list)
                            except psycopg2.errors.UniqueViolation:
                                print("Данный работодатель уже загружен")
                                continue
                        data_base_menu(db_user)
                    else:
                        print("Ничего не выбрали")
                elif user_check == "3":
                    break
                else:
                    print("Выберете номер соответствующего пункта и нажмите Enter")

        elif user_input_1 == "3":
            print("До свиданья")
            break
        else:
            print("Выберете номер соответствующего пункта и нажмите Enter")
