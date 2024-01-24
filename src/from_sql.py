import psycopg2
from dotenv import load_dotenv
import os


class DBManager:
    def __init__(self, vacancy_table, employers_table, list_of_employers):  # инициализируем с названиями таблиц
        self.vacancy_table = str(vacancy_table)
        self.employers_table = str(employers_table)
        self.list_of_employers = list_of_employers
        self.key = os.getenv('key')
        self.data_base_name = os.getenv('db')

    def db_request(self, query):
        """
        Создает запросы в базу данных
        """
        conn = psycopg2.connect(host="localhost", database=self.data_base_name, user="postgres", password=self.key)
        try:
            with conn:
                # после закрытия контекстного меню connection делает commit нужно закрывать
                # create cursor
                with conn.cursor() as curs:
                    # после закрытия контекстного меню cursor закрывается
                    # execute query
                    curs.execute(query)
                    rows = curs.fetchall()
                    return rows

        # except Exception:
        #     print("Ошибка!!!")
        finally:
            conn.close()

    def get_companies_and_vacancies_count(self):
        """
        Получает список всех компаний и количество вакансий у каждой компании.
        """
        return self.db_request(f'SELECT e.employer_name, count(*) as quantity_vacancy FROM {self.vacancy_table} as '
                               f'v JOIN {self.employers_table} as e ON e.external_id=v.employer_id GROUP BY '
                               f'employer_name')

    def get_all_vacancies(self):
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию.
        """
        return self.db_request(f'SELECT e.employer_name, v.vacancy_name, '
                               f'CONCAT (\'от \', salary_from, \' - \', \'до \', salary_to), vacancy_url '
                               f'FROM {self.vacancy_table} as v '
                               f'JOIN {self.employers_table} as e ON e.external_id=v.employer_id')

    def get_avg_salary(self):
        """
        Получает среднюю зарплату по вакансиям.
        """
        return self.db_request(f'SELECT ROUND(AVG(salary_from), 2), ROUND(AVG(salary_to), 2) '
                               f'FROM {self.vacancy_table}')

    def get_vacancies_with_higher_salary(self):
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
        """
        return self.db_request(f'SELECT vacancy_name, salary_from, salary_to, vacancy_url '
                               f'FROM {self.vacancy_table} '
                               f'WHERE salary_to > (SELECT AVG(salary_to) FROM {self.vacancy_table}) ')

    def get_vacancies_with_keyword(self, word):
        """
        Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python.
        Регистр-независимый.
        """
        query_with_word = (f"SELECT vacancy_name, salary_to, vacancy_url FROM {self.vacancy_table} "
                           f"WHERE vacancy_name ILIKE \'%{word}%\'")
        return self.db_request(query_with_word)

    def fill_db(self, employer, vacancy_list):
        print("загрузка данных")
        conn = psycopg2.connect(host="localhost", database=self.data_base_name, user="postgres", password=self.key)
        try:
            with conn:
                with conn.cursor() as curs:
                    curs.execute(f'INSERT INTO {self.employers_table} (employer_name, external_id) VALUES (%s, %s)',
                                 employer)
                    for i in range(len(vacancy_list)):
                        curs.execute(f"INSERT INTO {self.vacancy_table} (vacancy_name, vacancy_url, salary_from,"
                                     "salary_to, external_id, employer_id) VALUES (%s, %s, %s, %s, %s, %s)",
                                     vacancy_list[i])
            print("Данные загружены")
        finally:
            conn.close()

    def check_table(self):
        """Проверяет доступна ли такая база данных, заполнены ли таблицы"""
        checking = True
        try:
            conn = psycopg2.connect(host="localhost", database=self.data_base_name, user="postgres", password=self.key)
        except psycopg2.OperationalError:
            print(f"Ошибка: 'psycopg2.OperationalError' \nБаза данных с именем "
                  f"{self.data_base_name} не найдена!!!")
            checking = False
        else:
            try:
                with conn:
                    # после закрытия контекстного меню connection делает commit нужно закрывать
                    # create cursor
                    with conn.cursor() as curs:
                        # после закрытия контекстного меню cursor закрывается
                        # execute query
                        for table in (self.vacancy_table, self.employers_table):
                            # проверка наличия таблиц
                            try:
                                curs.execute(f"SELECT COUNT(*) FROM {table}")
                                rows = curs.fetchall()
                                if rows[0] == (0,):
                                    print(f"{table} - Таблица пустая")
                                    checking = False
                                else:
                                    checking = True
                            except psycopg2.errors.UndefinedTable:
                                print(f"Соединение с базой данных успешно\nВ базе данных таблицы c именем {table} "
                                      f"не существует")
                                checking = False
                                break
            finally:
                conn.close()
                return checking

    def create_db_tables(self) -> None:
        """Функция для создания таблиц в заранее созданной базе данных"""
        conn = psycopg2.connect(host="localhost", database=self.data_base_name, user="postgres", password=self.key)
        try:
            with conn:
                with conn.cursor() as curs:
                    # таблица Работодатели
                    curs.execute(f'CREATE TABLE {self.employers_table}'
                                 '('
                                 'employer_id serial PRIMARY KEY, '
                                 'employer_name varchar(64) NOT NULL, '
                                 'external_id varchar(20) UNIQUE NOT NULL'
                                 ');')
                    # таблица Вакансии
                    curs.execute(f'CREATE TABLE {self.vacancy_table}'
                                 '('
                                 'vacancy_id serial PRIMARY KEY, '
                                 'vacancy_name varchar(128) NOT NULL, '
                                 'vacancy_url varchar(64), '
                                 'salary_from int NOT NULL, '
                                 'salary_to int NOT NULL, '
                                 'external_id varchar(20) NOT NULL, '
                                 f'employer_id varchar(20) REFERENCES {self.employers_table}(external_id)'
                                 ');')
        except psycopg2.errors.DuplicateTable:
            print('Такие таблицы существуют')
        finally:
            conn.close()

    def drop_tables(self):
        conn = psycopg2.connect(host="localhost", database=self.data_base_name, user="postgres", password=self.key)
        try:
            with conn:
                with conn.cursor() as curs:
                    curs.execute(f'drop table if exists {self.vacancy_table};')
                    curs.execute(f'drop table if exists {self.employers_table};')
        finally:
            conn.close()

    def reading_data_from_tables(self):
        return self.db_request(f'select employer_name, external_id from {self.employers_table}')
