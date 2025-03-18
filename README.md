<h1 style='color: white; background: linear-gradient(to bottom, #f54242 50%, #048206 50%); padding: 5rem 0; text-align: center;'>Привет, <b style='font-size: 25px; color: white;'>чанда!</b></h1> 

## Вакансии  

Например: чтобы вставить вакансии к которым есть требование ТОЛЬКО РОССИЯ -> редактируй файл `2.российские вакансии.txt`, который находится в папке `data/vacancies`  
  
Чтобы добавить новую вакансию, например в **Россию** (остальные по аналогии):    
1. открыть файл в `data/vacancies` под названием `2.российские вакансии.txt`  
2. добавить запятую  или начать с новой строки  
3. Вставить название вакансии в формате "должность @ название компании" Например:('UX/UI Designer @ Leroy Merlin')  
4. готово    
  
## Компании  
Если нужно добавить название компании, то нужен файл, находящийся в `data/companies`, там в любой файл с соответствующим названием с таким же порядком действий как выше добавлять названия компаний.  
  
  
## Города  
Хотим добавить город , то нужен файл, находящийся в `data/cities`, там в любой файл с соответствующим названием с таким же порядком действий как выше добавлять названия компаний.

## Как запустить
На винде вводишь в powershell такую команду:
```shell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
На UNIX:
```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```
или 
```shell
wget -qO- https://astral.sh/uv/install.sh | sh
```

Потом пишешь:
```shell
uv run
```

Всё.
