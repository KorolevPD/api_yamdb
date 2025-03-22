# Yamdb

## Описание
Yamdb - это сервис для создания и хранения базы данных различных произведений (фильмов, сериалов, книг и т.д).
Данный сервис поддерживает авторизацию пользователей, систему отзывов и комментариев.
Также в сервисе предусмотрен импорт ваших данных из CSV-файла.

## Установка

Для того чтобы развернуть проект на локальной машине, выполните следующие шаги:
1. **Клонируйте репозиторий:**
```
git clone https://github.com/KorolevPD/api_yamdb.git
```

2. **Cоздайте и активируйте виртуальное окружение:**
Windows:
```
python -m venv venv
source venv/Scripts/activate
```
Linux/macOS:
```
python3 -m venv venv
source venv/bin/activate
```

3. **Обновите систему управления пакетами pip:**
Windows:
```
python -m pip install --upgrade pip
```
Linux/macOS:
```
python3 -m pip install --upgrade pip
```

4. **Установите зависимости из файла requirements.txt:**
```
pip install -r requirements.txt
```

5. **Выполните миграции:**
Windows:
```
python manage.py makemigrations
python manage.py migrate
```
Linux/macOS:
```
python3 manage.py makemigrations
python3 manage.py migrate
```

6. **Запустите проект:**
Windows:
```
python manage.py runserver
```
Linux/macOS:
```
python3 manage.py runserver
```

## Регистрация
Для регистрации нового пользователя необходимо отправить POST-запрос с параметрами email и username на эндпоинт "/api/v1/auth/signup/":
```
POST /api/v1/auth/signup/
Content-Type:  application/json
{
  "username": "NewUser",
  "email": "your_mail@email.com"
}
```

После чего на почту нового пользователя придет сообщение с кодом подверждения. Далле необходимо отправить код подтверждения на эндпоинт "/api/v1/auth/token/" с параметрами username и confirmation_code, чтобы получить JWT токен:
```
POST /api/v1/auth/token/
Content-Type:  application/json
{
  "username": "NewUser",
  "confirmation_code": "123456"
}
```

## Примеры запросов к API
### **Получение списка категорий:**

Запрос:
```
GET /api/v1/categories/
```
Ответ:
```
{
"count": 2,
"next": None,
"previous": None,
"results": [
    {
      "name": "Фильмы",
      "slug": "movie"
    },
    {
      "name": "Сериалы",
      "slug": "Series"
    }
  ]
}
```

### **Создание жанра:**

Запрос:
```
POST /api/v1/genres/
Authorization:  Bearer <ваш JWT-токен>
Content-Type:  application/json
{
  "name": "Ужасы",
  "slug": "horror"
}
```
Ответ:
```
{
  "name": "Ужасы",
  "slug": "horror"
}
```

### **Получение информации о своем профиле:**

Запрос:
```
GET /api/v1/users/me/
Authorization:  Bearer <ваш JWT-токен>
Content-Type:  application/json
```
Ответ:
```
{
  "username": "YourUser",
  "email": "user@example.com",
  "first_name": "Ivan",
  "last_name": "Ivanov",
  "bio": "Your bio text",
  "role": "user"
}
```

**Более подробная документация API находится по адресу /redoc/**
>>>>>>> 38c575a8dc5e69798fb525737d8e0309423fde41
