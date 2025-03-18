import typing
from pathlib import Path
from config.scripts import get_txt_data


data_folder = Path('./data')

companies_folder = data_folder / 'companies'
vacancies_folder = data_folder / 'vacancies'
cities_folder    = data_folder / 'cities'

__companies:list[list] = get_txt_data(
    generator=companies_folder.glob('*.txt')
)

__vacancies:list[list] = get_txt_data(
    generator=vacancies_folder.glob('*.txt')
)

__cities:list[list] = get_txt_data(
    generator=cities_folder.glob('*.txt')
)

foreign_companies, russian_companies                    = __companies
foreign_vacancies, russian_vacancies, spec_vacancies    = __vacancies
foreign_cities, russian_cities                          = __cities

class Data(typing.NamedTuple):
    companies: list[str]
    vacancies: list[str]
    cities: list[str]

russia          = Data(russian_companies, russian_vacancies, russian_cities)
other_countries = Data(foreign_companies, foreign_vacancies, foreign_cities)

