# Contributing to Sapphire

## Release Process

1. **Подготовка релиза**

   ```bash
   # Убедитесь, что вы на main ветке
   git checkout main
   git pull origin main

   # Обновите версию в файлах
   # sapphire.py, README.md, CHANGELOG.md

   # Создайте и протестируйте билд
   python setup.py build
   ```

2. **Коммит изменений**

   ```bash
   # Добавьте изменения
   git add .

   # Создайте коммит
   git commit -m "Release vX.X.X"
   ```

3. **Создание тега**

   ```bash
   # Создайте аннотированный тег
   git tag -a vX.X.X -m "Version X.X.X"
   ```

4. **Публикация**

   ```bash
   # Отправьте изменения
   git push origin main

   # Отправьте тег
   git push origin vX.X.X
   ```

## Создание хотфикса

1. **Создание ветки хотфикса**

   ```bash
   git checkout -b hotfix/vX.X.X main
   ```

2. **Внесение исправлений**

   ```bash
   # Внесите необходимые исправления
   git add .
   git commit -m "Fix: описание исправления"
   ```

3. **Слияние и публикация**

   ```bash
   # Вернитесь на main
   git checkout main

   # Слейте изменения
   git merge --no-ff hotfix/vX.X.X

   # Создайте тег
   git tag -a vX.X.X -m "Hotfix vX.X.X"

   # Отправьте изменения
   git push origin main
   git push origin vX.X.X
   ```

## Конвенции коммитов

Используйте следующие префиксы для коммитов:

- `feat:` - новая функциональность
- `fix:` - исправление бага
- `docs:` - изменения в документации
- `style:` - форматирование, отступы и т.д.
- `refactor:` - рефакторинг кода
- `test:` - добавление тестов
- `chore:` - обновление зависимостей и т.д.

Пример:

```
feat: добавлен новый функционал для работы с кошельками
```

## Ветвление

- `main` - основная ветка
- `develop` - ветка разработки
- `feature/*` - ветки для новых функций
- `hotfix/*` - ветки для срочных исправлений
- `release/*` - ветки для подготовки релиза
