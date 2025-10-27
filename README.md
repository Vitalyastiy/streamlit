# Jira Task Analytics Dashboard

Streamlit приложение для анализа задач из Jira с визуализацией данных и лидербордом исполнителей.

## 🚀 Как запустить проект

### 1. Активация виртуального окружения
```bash
source venv/bin/activate
```

### 2. Установка зависимостей
```bash
pip install streamlit pandas matplotlib seaborn numpy plotly openpyxl watchdog
```

### 3. Запуск приложения
```bash
streamlit run app.py
```

Приложение будет доступно по адресу: http://localhost:8501

## 📊 Функциональность

- **Лидерборд исполнителей** - рейтинг по количеству выполненных задач и Story Points
- **Фильтрация данных** - по датам, исполнителям и статусам задач
- **Визуализация** - тепловые карты, графики распределения задач
- **Экспорт данных** - выгрузка результатов в Excel файлы
- **Анализ эффективности** - статистика по выполнению задач

## 📁 Структура проекта

- `app.py` - основное приложение Streamlit
- `requirements.txt` - зависимости Python
- `venv/` - виртуальное окружение
- CSV файлы с данными из Jira

## 🌐 Онлайн версии

- https://legendary-umbrella-qrvv69rj5r9f4vw6-8501.app.github.dev/
- https://vitalyastiy-streamlit-app-fc4mou.streamlit.app/
