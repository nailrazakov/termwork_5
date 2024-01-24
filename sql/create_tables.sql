CREATE DATABASE base_hh_vacancies

-- SQL-команды для создания таблиц
CREATE TABLE employers_test
(
	employer_id serial PRIMARY KEY,
	employer_name varchar(64) NOT NULL,
	external_id varchar(20) UNIQUE NOT NULL
);
CREATE TABLE vacancies_test
(
	vacancy_id serial PRIMARY KEY,
	vacancy_name varchar(128) NOT NULL,
	vacancy_url varchar(64),
	salary_from int NOT NULL,
	salary_to int NOT NULL,
	external_id varchar(20) NOT NULL,
	employer_id varchar(20) REFERENCES employers_test(external_id)
);