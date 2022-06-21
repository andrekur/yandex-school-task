# yandex-school-task
## Установка
```
git clone https://github.com/andrekur/yandex-school-task.git
mkdir ./yandex-school-task/migration/versions
cd yandex-school-task/_CD
mv env.example .env
sudo docker-compose build
sudo docker-compose up
```
после проверьте адресс localhost:80/docs
## Ссылки в продукте

Тип запроса | адрес | описание 
:-----:| :--------: | :---: 
GET |/docs  | документация по проекту 
POST |/imports | добавление данных 
GET |/delete/{item_uuid} | удаление продукта/категории (связанные элементы будут удалены)
GET |/node/{item_uuid} | получить товар/категорию (включая связанные элементы, порядком ниже)
GET |/sales | query_params: date Товары цена которых была изменена за полуинтервал [date - 24 hour; date)


## Этого нет, но должно быть в проекте

- Асинхронность в Fast Api (если async то все, иначе смысла нет)
- Асинхронность в БД(Tortoise, ormar)
- Блокировки в БД при записи во избежания конфликтов
- Логи и обработка ошибок(HTTP status_code > 500)
- Кастомные ошибки(при валидации)
- Больше тестов
- CI/CD, Git Action
- PEP8 не во всем проекте (на самом деле это очень критично)

Задание было интересным, узнал много нового)
Сервис был написан за 26 рабочик часов, очень торопился(поздно узнал о школе), тк хочу попасть на основной трек
