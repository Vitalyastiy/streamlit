#%%
#streamlit run app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('dark_background')  # Устанавливаем стиль для графиков

# Загрузка данных из CSV файла
df = pd.read_csv('Jira 2024-07-30T22_11_01+0300.csv')

# Преобразование столбцов 'Обновлено' и 'Создано' в формат datetime
df['Обновлено'] = pd.to_datetime(df['Обновленo'], dayfirst=True)
df['Создано'] = pd.to_datetime(df['Создано'], dayfirst=True)

# Преобразование Story Points в int и заполнение NaN
df['Пользовательское поле (Story Points)'] = df['Пользовательское поле (Story Points)'].fillna(0).astype(int)

# Создание столбца 'Время выполнения'
df['Время выполнения'] = (df['Обновлено'] - df['Создано']).dt.days

# Фильтры в боковой панели
st.sidebar.markdown("## Фильтры")
executors = df['Исполнитель'].unique().tolist()
statuses = df['Статус'].unique().tolist()
selected_executors = st.sidebar.multiselect('Выберите исполнителей', executors, default=executors)
selected_status = st.sidebar.multiselect('Выберите статус задачи', statuses, default=statuses)
st.sidebar.markdown("### Фильтрация по дате")
start_date = st.sidebar.date_input('Начальная дата', df['Создано'].min().date())
end_date = st.sidebar.date_input('Конечная дата', df['Создано'].max().date())

# Применение фильтров к данным
filtered_df = df[
    (df['Исполнитель'].isin(selected_executors)) &
    (df['Статус'].isin(selected_status)) &
    (df['Создано'] >= pd.to_datetime(start_date)) &
    (df['Создано'] <= pd.to_datetime(end_date))
]

# Группировка и агрегация данных по месяцам и исполнителям
pivot_df = filtered_df.groupby([filtered_df['Обновлено'].dt.to_period('M'), 'Исполнитель'])['Пользовательское поле (Story Points)'].sum().unstack()

# Заголовок приложения
st.markdown("<h1 style='font-size: 30px;'>Динамика производительности команды BI</h1>", unsafe_allow_html=True)

# Создание блока метрик (KPI)
col1, col2, col3, col4 = st.columns(4)
total_tasks = filtered_df.shape[0]
completed_tasks = filtered_df[filtered_df['Статус'] == 'Готово'].shape[0]
total_story_points = filtered_df['Пользовательское поле (Story Points)'].sum()
average_completion_time = (filtered_df['Обновлено'] - filtered_df['Создано']).mean()
average_completion_time_str = str(average_completion_time).split('.')[0]

col1.metric("Общее количество задач", total_tasks)
col2.metric("Выполненные задачи", completed_tasks)
col3.metric("Всего Story Points", total_story_points)
col4.metric("Среднее время выполнения", average_completion_time_str)

# Функция для создания и отображения графиков
def create_plot(fig, ax, title):
    ax.set_title(title)
    st.pyplot(fig, use_container_width=True)

# Определение размера для графиков
fig_size = (15, 9)

# График выполнения задач по месяцам и исполнителям
fig1, ax1 = plt.subplots(figsize=fig_size)
pivot_df.plot(kind='barh', stacked=True, ax=ax1)
create_plot(fig1, ax1, 'График выполнения задач по месяцам и исполнителям')

# График количества задач по статусам
fig2, ax2 = plt.subplots(figsize=fig_size)
filtered_df['Статус'].value_counts().plot(kind='bar', ax=ax2)
create_plot(fig2, ax2, 'График количества задач по статусам')

# График количества задач по исполнителям
fig3, ax3 = plt.subplots(figsize=fig_size)
filtered_df['Исполнитель'].value_counts().plot(kind='bar', ax=ax3)
create_plot(fig3, ax3, 'График количества задач по исполнителям')

# График количества задач по создателям
fig4, ax4 = plt.subplots(figsize=fig_size)
filtered_df['Создатель'].value_counts().plot(kind='bar', ax=ax4)
create_plot(fig4, ax4, 'График количества задач по создателям')

# График распределения Story Points по исполнителям
fig5, ax5 = plt.subplots(figsize=fig_size)
sns.boxplot(x='Исполнитель', y='Пользовательское поле (Story Points)', data=filtered_df, ax=ax5)
create_plot(fig5, ax5, 'Распределение Story Points по исполнителям')

# График распределения времени выполнения задач
fig6, ax6 = plt.subplots(figsize=fig_size)
sns.histplot(filtered_df['Время выполнения'], bins=20, kde=True, ax=ax6)
create_plot(fig6, ax6, 'Распределение времени выполнения задач')

# Отображение таблицы с фильтрованными данными
st.markdown("## Таблица фильтрованных данных")
st.dataframe(filtered_df)



# %%
# Введение
# Данная документация описывает приложение для анализа динамики производительности команды на основе данных Jira. Приложение разработано с использованием библиотеки Streamlit для создания интерактивных веб-приложений на языке Python.

# Установка
# Установите необходимые зависимости:

# pip install streamlit pandas numpy matplotlib seaborn
# Скачайте и подготовьте данные в формате CSV для загрузки в приложение.

# Запуск приложения
# Сохраните ваш CSV файл с данными Jira в корневой папке проекта.

# Запустите приложение командой:

# streamlit run app.py
# После запуска приложение будет доступно по адресу http://localhost:8501.

# Использование приложения
# 1. Главная страница
# На главной странице отображаются основные метрики производительности команды и графики.

# 2. KPI-блоки
# На этой странице отображаются ключевые показатели производительности:

# Общее количество задач
# Выполненные задачи
# Всего Story Points
# Среднее время выполнения задач
# 3. Графики
# В разделе "Графики" представлены:

# График выполнения задач по месяцам и исполнителям
# График количества задач по статусам
# График количества задач по исполнителям
# График количества задач по создателям
# 4. Фильтрация данных
# Вы можете фильтровать данные по:

# Исполнителю
# Статусу задачи
# Дате создания задачи
# 5. Дополнительные графики
# Предоставляются дополнительные визуализации:

# Распределение Story Points по исполнителям
# Распределение времени выполнения задач
# Разработка и поддержка
# Автор: [Ваше имя]
# Версия: 1.0
# Дата последнего обновления: [дата]

# %%
