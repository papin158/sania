import re, pathlib, typing, itertools
from base64 import b64encode

company_finder = re.compile(r'[\n\r,]+')


def get_txt_data(*paths: pathlib.Path, generator=typing.Generator[pathlib.Path, None, None]) -> list:
    companies = []
    for path in itertools.chain(paths, generator):
        with open(path.absolute(), 'r', encoding='utf-8') as file:
            companies += [[company.strip() for company in company_finder.split(file.read().strip())]]
    return companies


def set_intercept_request(login, password):
    def intercept_request(request):
        request.headers['Authorization'] = f"Basic {b64encode(f'{login}:{password}'.encode()).decode()}"
    return intercept_request