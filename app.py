#%%
#streamlit run app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Конфигурация страницы
st.set_page_config(layout='wide')

# Устанавливаем стиль для графиков и увеличиваем шрифт
#plt.style.use('dark_background')
plt.style.use('default')
plt.rcParams.update({'font.size': 30})  # Устанавливаем размер шрифта по умолчанию

# Загрузка данных из CSV файла
df = pd.read_csv('Моё в работе (Jira) 2024-08-29T13_51_55+0300.csv')

# Преобразование столбцов 'Обновлено' и 'Создано' в формат datetime
df['Обновлено'] = pd.to_datetime(df['Обновленo'], dayfirst=True)
df['Создано'] = pd.to_datetime(df['Создано'], dayfirst=True)

# Преобразование Story Points в int и заполнение NaN
df['Пользовательское поле (Story Points)'] = df['Пользовательское поле (Story Points)'].fillna(0).astype(int)

# Создание столбца 'Время выполнения'
df['Время выполнения'] = (df['Обновлено'] - df['Создано']).dt.days

# Фильтры в боковой панели
st.sidebar.markdown("## Фильтры")
executors = ['flerinvs', 'mikhaelyanta', 'nikishinpa', 'furletovaav', 'klekovkinve', 'balitskayaav']
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
col1, col2, col3, col4, col5 = st.columns(5)

# Задач незакрытых
total_tasks = df.query('~`Статус`.str.contains("Cancel|Закрыт|Готово")').shape[0]
# Производительность
total_story_points = filtered_df.query('`Статус`.str.contains("Готово") & `Спринт`.str.contains("BI")').groupby('Спринт').size().mean().round()
# velocity
completed_tasks = filtered_df.query('`Статус`.str.contains("Готово|Закрыт") & `Спринт`.str.contains("BI")').groupby('Спринт')['Пользовательское поле (Story Points)'].sum().mean().round()
# lead time
average_completion_time = (filtered_df.query('`Статус`.str.contains("Готово") & `Спринт`.str.contains("BI")')['Обновлено'] - filtered_df.query('`Статус`.str.contains("Готово") & `Спринт`.str.contains("BI")')['Создано']).mean()
average_completion_time_str = str(average_completion_time).split('.')[0]


teh =(round((df.query('~`Статус`.str.contains("Cancel|Закрыт|Готово") & `Пользовательское поле (Epic Link)`.str.contains("ANL-2690|ANL-2271|ANL-2150|ANL-2239") ').shape[0] / df.query('~`Статус`.str.contains("Cancel|Закрыт|Готово")').shape[0]) , 2))


col1.metric("Открытых задач ANL", total_tasks)
col2.metric("Задач в неделю, в сред.", total_story_points)
col3.metric("Velocity", completed_tasks)
col4.metric("Lead Time", average_completion_time_str)
col5.metric("Коэффициент техдолга", teh)

# Функция для создания и отображения графиков
def create_plot(fig, ax, title):
    ax.set_title(title, fontsize=20)  # Увеличиваем шрифт заголовка графика
    ax.tick_params(axis='x', labelsize=14)  # Увеличиваем шрифт подписей оси X
    ax.tick_params(axis='y', labelsize=14)  # Увеличиваем шрифт подписей оси Y
    ax.set_xlabel(ax.get_xlabel(), fontsize=16)  # Увеличиваем шрифт метки оси X
    ax.set_ylabel(ax.get_ylabel(), fontsize=16)  # Увеличиваем шрифт метки оси Y
    st.pyplot(fig, use_container_width=True)

# Определение размера для графиков
fig_size = (25, 15)

# Динамика по заведенным задачам, накопительно
fig5, ax5  = plt.subplots(figsize=fig_size)
dynamic_counts = df.query('~Статус.str.contains("Cancel|Закрыт|Готово")').groupby([df['Создано'].dt.to_period('M')])['Идентификатор проблемы'].size()
cumulative_counts = dynamic_counts.cumsum()
cumulative_counts.plot(kind='line', ax=ax5, color='red')


# График количества задач по статусам
fig2, ax2 = plt.subplots(figsize=fig_size)
filtered_df.query('`Статус`.str.contains("Готово") & `Спринт`.str.contains("BI") & `Обновлено` >= "2024-01-01"').groupby([df['Обновлено'].dt.to_period('W')])['Спринт'].size().plot(kind='bar', ax=ax2)



# Расположить два графика в одном ряду
col1, col2 = st.columns(2)
with col1:
    ax2.axhline(total_story_points, color='red', linestyle='--', linewidth=2, label='Среднее значение')
    ax2.legend(fontsize=16)
    create_plot(fig5, ax5, 'Динамика по открытым задачам в бэклоге, накопительно')
with col2:
    create_plot(fig2, ax2, 'Динамика выполеннных задач, понедельно')




# График количества задач по создателям
fig4, ax4 = plt.subplots(figsize=fig_size)
filtered_df.query('~`Создатель`.str.contains("flerinvs|mikhaelyanta|nikishinpa|furletovaav|klekovkinve|balitskayaav") & `Спринт`.str.contains("BI")')['Создатель'].sort_values(ascending=True).value_counts().head(15).plot(kind='barh', ax=ax4)
#create_plot(fig4, ax4, 'TOP-15 заказчиков BI, чьи задачи были в спринтах')

# График распределения времени выполнения задач
fig6, ax6 = plt.subplots(figsize=fig_size)
sns.histplot(filtered_df.query('`Создатель`.str.contains("flerinvs|mikhaelyanta|nikishinpa|furletovaav|klekovkinve|balitskayaav") & `Спринт`.str.contains("BI")')['Время выполнения'], bins=10, kde=True, ax=ax6)
#create_plot(fig6, ax6, 'Распределение времени выполнения задач')


# Создание двух колонок для графиков
col1, col2 = st.columns(2)

# График количества задач по создателям
with col1:
    fig4, ax4 = plt.subplots(figsize=fig_size)
    filtered_df.query('~`Создатель`.str.contains("flerinvs|mikhaelyanta|nikishinpa|furletovaav|klekovkinve|balitskayaav") & `Спринт`.str.contains("BI")')['Создатель'].sort_values(ascending=True).value_counts().head(15).plot(kind='barh', ax=ax4)
    create_plot(fig4, ax4, 'TOP-15 заказчиков BI, чьи задачи были в спринтах')

# График распределения времени выполнения задач
with col2:
    fig6, ax6 = plt.subplots(figsize=fig_size)
    sns.histplot(filtered_df.query('`Создатель`.str.contains("flerinvs|mikhaelyanta|nikishinpa|furletovaav|klekovkinve|balitskayaav") & `Спринт`.str.contains("BI")')['Время выполнения'], bins=10, kde=True, ax=ax6)
    create_plot(fig6, ax6, 'Распределение времени выполнения задач')


# Создание двух колонок для графиков
col1, col2 = st.columns(2)

# График выполнения задач по месяцам и исполнителям
with col1:
    fig1, ax1 = plt.subplots(figsize=fig_size)
    filtered_pivot_df = pivot_df.query('`Обновлено` >= "2024-01-01"')
    filtered_pivot_df.plot(kind='bar', stacked=True, ax=ax1)
    average_story_points = filtered_pivot_df.sum(axis=1).mean()
    ax1.axhline(average_story_points, color='red', linestyle='--', linewidth=2, label='Среднее значение')
    ax1.legend(fontsize=16)
    create_plot(fig1, ax1, 'Производительность в сторипоинтах накопительно, в месяц')

# График количества задач по исполнителям
with col2:
    fig3, ax3 = plt.subplots(figsize=fig_size)
    filtered_df.query('`Исполнитель`.str.contains("flerinvs|mikhaelyanta|nikishinpa|furletovaav|klekovkinve|balitskayaav") & `Спринт`.str.contains("BI")')['Исполнитель'].value_counts().plot(kind='barh', ax=ax3)
    create_plot(fig3, ax3, 'График количества задач по исполнителям')




# Группировка данных по исполнителям и статусам
executor_task_counts = filtered_df.query('~`Статус`.str.contains("Сделать")').groupby(['Исполнитель', 'Статус']).size().unstack(fill_value=0)

# График с тепловой картой
fig7, ax7 = plt.subplots(figsize=(25, 15))
sns.heatmap(executor_task_counts, annot=True, fmt="d",cmap='coolwarm', ax=ax7)
create_plot(fig7, ax7, 'Распределение задач по исполнителям и статусам')


# Отображение таблицы с фильтрованными данными
st.markdown("## Таблица фильтрованных данных")
st.dataframe(filtered_df)



# %%
