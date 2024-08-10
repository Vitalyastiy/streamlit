#%%
#streamlit run app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('dark_background')  # Устанавливаем стиль для графиков
# Загрузка данных из CSV файла
df = pd.read_csv('Jira 2024-08-03T18_29_35+0300.csv')


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
col1, col2, col3, col4 = st.columns(4)

# Задач незакрытых
total_tasks = df.query('~`Статус`.str.contains("Cancel|Закрыт|Готово")').shape[0]
# Производительность
total_story_points = filtered_df.query('`Статус`.str.contains("Готово") & `Спринт`.str.contains("BI")').groupby('Спринт').size().mean().round()
# velocity
completed_tasks = filtered_df.query('`Статус`.str.contains("Готово|Закрыт") & `Спринт`.str.contains("BI")').groupby('Спринт')['Пользовательское поле (Story Points)'].sum().mean().round()
# lead time
average_completion_time = (filtered_df.query('`Статус`.str.contains("Готово") & `Спринт`.str.contains("BI")')['Обновлено'] - filtered_df.query('`Статус`.str.contains("Готово") & `Спринт`.str.contains("BI")')['Создано']).mean()
average_completion_time_str = str(average_completion_time).split('.')[0]

col1.metric("Открытых задач ANL", total_tasks)
col2.metric("Задач в неделю в сред.", total_story_points)
col3.metric("Velocity", completed_tasks)
col4.metric("Lead Time", average_completion_time_str)

# Функция для создания и отображения графиков
def create_plot(fig, ax, title):
    ax.set_title(title)
    st.pyplot(fig, use_container_width=True)
# Определение размера для графиков
fig_size = (15, 9)




# Динкамика по заведенным задачам, накопитлеьно
fig5, ax5  = plt.subplots(figsize=fig_size)
# Группируем по дате и статусу, считаем количество
dynamic_counts = df.query('~Статус.str.contains("Cancel|Закрыт|Готово")').groupby([df['Создано'].dt.to_period('M')])['Идентификатор проблемы'].size()
# Группируем по дате и статусу, считаем количество для закрытых задач
cumulative_counts = dynamic_counts.cumsum()
cumulative_counts.plot(kind='line', ax=ax5, color='red')
create_plot(fig5, ax5, 'Динкамика по открытым задачам в бэклоге, накопитлеьно')



# График количества задач по статусам
fig2, ax2 = plt.subplots(figsize=fig_size)
filtered_df.query('`Статус`.str.contains("Готово") & `Спринт`.str.contains("BI") & `Обновлено` >= "2024-01-01"').groupby([df['Обновлено'].dt.to_period('M')])['Спринт'].size().plot(kind='bar', ax=ax2)
create_plot(fig2, ax2, 'Реализованные задачи, по мес.')




# График выполнения задач по месяцам и исполнителям
fig1, ax1 = plt.subplots(figsize=fig_size)
filtered_pivot_df = pivot_df.query('`Обновлено` >= "2024-01-01"')
filtered_pivot_df.plot(kind='bar', stacked=True, ax=ax1)
# Расчет среднего значения Story Points
average_story_points = filtered_pivot_df.sum(axis=1).mean()
# Добавление линии среднего значения
ax1.axhline(average_story_points, color='red', linestyle='--', linewidth=2, label='Среднее значение')
# Настройка легенды
ax1.legend()
create_plot(fig1, ax1, 'Производительность в сторипоинтах накопительно, в месяц')







# График количества задач по создателям
fig4, ax4 = plt.subplots(figsize=fig_size)
filtered_df.query('~`Создатель`.str.contains("flerinvs|mikhaelyanta|nikishinpa|furletovaav|klekovkinve|balitskayaav") & `Спринт`.str.contains("BI")')['Создатель'].sort_values(ascending=True).value_counts().head(15).plot(kind='barh', ax=ax4)
create_plot(fig4, ax4, 'TOP-15 заказчиков BI, чьи задачи были в спринтах')
# График распределения Story Points по исполнителям



# График распределения времени выполнения задач
fig6, ax6 = plt.subplots(figsize=fig_size)
sns.histplot(filtered_df.query('`Создатель`.str.contains("flerinvs|mikhaelyanta|nikishinpa|furletovaav|klekovkinve|balitskayaav") & `Спринт`.str.contains("BI")')['Время выполнения'], bins=10, kde=True, ax=ax6)
create_plot(fig6, ax6, 'Распределение времени выполнения задач')






# График количества задач по исполнителям
fig3, ax3 = plt.subplots(figsize=fig_size)
filtered_df['Исполнитель'].value_counts().plot(kind='bar', ax=ax3)
create_plot(fig3, ax3, 'График количества задач по исполнителям')






# Отображение таблицы с фильтрованными данными
st.markdown("## Таблица фильтрованных данных")
st.dataframe(filtered_df)




# %%

# %%
filtered_df.query('`Статус`.str.contains("Готово") & `Спринт`.str.contains("BI")').groupby([df['Обновлено'].dt.to_period('M')])['Спринт'].size()
# %%
filtered_df.query('`Статус`.str.contains("Готово") & `Спринт`.str.contains("BI")').groupby('Спринт').size()

# %%
