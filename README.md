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

Тип запроса | Адрес | Описание 
:-----:| :-------------: | :---: 
GET |/docs  | документация по проекту 
POST |/imports | добавление данных 
GET |/delete/{item_uuid} | удаление продукта/категории (связанные элементы будут удалены)
GET |/node/{item_uuid} | получить товар/категорию (включая связанные элементы, порядком ниже)
GET |/sales | query_params: date Товары цена которых была изменена за полуинтервал [date - 24 hour; date)

Сервис был написан за 26 рабочик часов
