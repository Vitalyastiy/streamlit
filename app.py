#%%
# streamlit run app.py   source venv/bin/activate
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go


# Конфигурация страницы
st.set_page_config(layout='wide')

# Устанавливаем стиль для графиков и увеличиваем шрифт
#plt.style.use('dark_background')
plt.style.use('default')
plt.rcParams.update({'font.size': 30})  # Устанавливаем размер шрифта по умолчанию

@st.cache_data
def load_data():
    df = pd.read_csv('Моё в работе (Jira) 2025-07-16T21_01_51+0300.csv')
    
    # Преобразование дат
    df['Создано'] = pd.to_datetime(df['Создано'].str.strip(), format='%d.%m.%Y %H:%M')
    df['Дата решения'] = pd.to_datetime(df['Дата решения'].str.strip(), format='%d.%m.%Y %H:%M')
    
    # Заполнение пропущенных значений в Story Points
    df['Пользовательское поле (Story Points)'] = df['Пользовательское поле (Story Points)'].fillna(0).astype(int)
    
    return df

# Загрузка данных
df = load_data()

# Список исполнителей
executors = ['flerinvs', 'mikhaelyanta', 'nikishinpa', 'furletovaav', 'balitskayaav', 'iankevichri', 'filippovds']

# Создаем лидерборд
st.markdown("## 🏆 Лидерборд исполнителей")

# Фильтрация по дате
st.sidebar.markdown("### Фильтрация по дате закрытия задачи")
start_date = st.sidebar.date_input('Начальная дата закрытия', pd.to_datetime('2025-01-01').date())
end_date = st.sidebar.date_input('Конечная дата закрытия', df['Дата решения'].max().date())

# Фильтрация по исполнителям
st.sidebar.markdown("### Фильтрация по исполнителям")
selected_executors = st.sidebar.multiselect(
    'Выберите исполнителей',
    executors,
    default=executors
)

# Фильтрация по статусам
st.sidebar.markdown("### Фильтрация по статусам")
statuses = df['Статус'].unique()
selected_status = st.sidebar.multiselect(
    'Выберите статусы',
    statuses,
    default=statuses
)

# Применение фильтров к данным
filtered_df = df[
    (df['Исполнитель'].isin(selected_executors)) &
    (df['Статус'].isin(selected_status)) &
    (df['Дата решения'] >= pd.to_datetime(start_date)) &
    (df['Дата решения'] <= pd.to_datetime(end_date))
]

# Экспорт данных nikishinpa в Excel с детализацией
nikishinpa_data = df[
    (df['Исполнитель'] == 'nikishinpa') & 
    (df['Статус'] == 'Готово') & 
    (df['Дата решения'] >= pd.to_datetime(start_date)) & 
    (df['Дата решения'] <= pd.to_datetime(end_date))
].sort_values('Дата решения')

# Выбираем нужные колонки для выгрузки
columns_to_export = [
    'Ключ проблемы',
    'Идентификатор проблемы',
    'Статус',
    'Исполнитель',
    'Создатель',
    'Создано',
    'Дата решения',
    'Пользовательское поле (Story Points)',
    'Спринт',
    'Тема',
    'Метки'
]

# Сохраняем в Excel с выбранными колонками
nikishinpa_data[columns_to_export].to_excel('nikishinpa_tasks_detailed.xlsx', index=False)
st.markdown("### Данные экспортированы в файл nikishinpa_tasks_detailed.xlsx")

# Создаем DataFrame для лидерборда на основе всех данных
leaderboard_data = []
for executor in executors:
    executor_data = df[df['Исполнитель'] == executor]
    total_tasks = len(executor_data)
    total_sp = executor_data['Пользовательское поле (Story Points)'].sum()
    completed_tasks = len(executor_data[executor_data['Статус'] == 'Готово'])
    completed_sp = executor_data[executor_data['Статус'] == 'Готово']['Пользовательское поле (Story Points)'].sum()
    
    # Подсчет задач за выбранный период
    period_completed_tasks = len(executor_data[
        (executor_data['Статус'] == 'Готово') & 
        (executor_data['Дата решения'] >= pd.to_datetime(start_date)) & 
        (executor_data['Дата решения'] <= pd.to_datetime(end_date))
    ])
    
    leaderboard_data.append({
        'Исполнитель': executor,
        'Всего задач': total_tasks,
        'Выполнено задач': completed_tasks,
        'Выполнено за период': period_completed_tasks,
        'Всего SP': total_sp,
        'Выполнено SP': completed_sp,
        'Эффективность (%)': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    })

leaderboard_df = pd.DataFrame(leaderboard_data)
leaderboard_df = leaderboard_df.sort_values('Выполнено SP', ascending=False)

# Отображаем лидерборд в виде таблицы
st.dataframe(
    leaderboard_df.style.background_gradient(cmap='YlGnBu', subset=['Выполнено SP', 'Эффективность (%)', 'Выполнено за период']),
    use_container_width=True
)

# Группировка и агрегация данных по исполнителям и статусам
# Создаем отдельные датасеты для закрытых и открытых задач
closed_tasks = filtered_df[filtered_df['Статус'].isin(['Готово', 'Закрыт'])]
open_tasks = df[~df['Статус'].isin(['Готово', 'Закрыт'])]

# Объединяем датасеты
combined_df = pd.concat([closed_tasks, open_tasks])

# Группируем по исполнителям и статусам
executor_task_counts = combined_df.groupby(['Исполнитель', 'Статус']).size().unstack(fill_value=0)

# Создаем тепловую карту с plotly для количества задач
fig = px.imshow(
    executor_task_counts,
    labels=dict(x="Статус", y="Исполнитель", color="Количество задач"),
    x=executor_task_counts.columns,
    y=executor_task_counts.index,
    color_continuous_scale='YlGnBu',
    aspect="auto"
)

# Добавляем текст с значениями и процентами
for i, row in enumerate(executor_task_counts.index):
    row_total = executor_task_counts.loc[row].sum()
    for j, col in enumerate(executor_task_counts.columns):
        value = executor_task_counts.iloc[i, j]
        percentage = (value / row_total * 100) if row_total > 0 else 0
        fig.add_annotation(
            x=col,
            y=row,
            text=f"{value}<br>({percentage:.1f}%)",
            showarrow=False,
            font=dict(color="black" if value < executor_task_counts.values.max()/2 else "white")
        )

fig.update_layout(
    title='Распределение задач по исполнителям и статусам',
    height=500,
    width=800
)

st.plotly_chart(fig, use_container_width=True)

# Создаем тепловую карту с plotly для сторипоинтов
executor_task_counts2 = combined_df.groupby(['Исполнитель', 'Статус'])['Пользовательское поле (Story Points)'].sum().unstack(fill_value=0)

fig2 = px.imshow(
    executor_task_counts2,
    labels=dict(x="Статус", y="Исполнитель", color="Количество Story Points"),
    x=executor_task_counts2.columns,
    y=executor_task_counts2.index,
    color_continuous_scale='YlGnBu',
    aspect="auto"
)

# Добавляем текст с значениями и процентами
for i, row in enumerate(executor_task_counts2.index):
    row_total = executor_task_counts2.loc[row].sum()
    for j, col in enumerate(executor_task_counts2.columns):
        value = executor_task_counts2.iloc[i, j]
        percentage = (value / row_total * 100) if row_total > 0 else 0
        fig2.add_annotation(
            x=col,
            y=row,
            text=f"{int(value)}<br>({percentage:.1f}%)",
            showarrow=False,
            font=dict(color="black" if value < executor_task_counts2.values.max()/2 else "white")
        )

fig2.update_layout(
    title='Распределение Story Points по исполнителям и статусам',
    height=500,
    width=800
)

st.plotly_chart(fig2, use_container_width=True)

# Определение размера для графиков
fig_size = (12, 6)

# График распределения задач по исполнителям
fig3, ax3 = plt.subplots(figsize=fig_size)
task_counts = df.groupby('Исполнитель')['Идентификатор проблемы'].count()
task_counts.plot(kind='bar', ax=ax3)
ax3.set_title('Распределение задач по исполнителям')
ax3.set_xlabel('Исполнитель')
ax3.set_ylabel('Количество задач')
plt.xticks(rotation=45)
st.pyplot(fig3)

# График распределения Story Points по исполнителям
fig4, ax4 = plt.subplots(figsize=fig_size)
sp_counts = df.groupby('Исполнитель')['Пользовательское поле (Story Points)'].sum()
sp_counts.plot(kind='bar', ax=ax4)
ax4.set_title('Распределение Story Points по исполнителям')
ax4.set_xlabel('Исполнитель')
ax4.set_ylabel('Story Points')
plt.xticks(rotation=45)
st.pyplot(fig4)

# Динамика по заведенным задачам, накопительно
fig5, ax5  = plt.subplots(figsize=fig_size)
# Используем ту же логику фильтрации, что и для подсчета открытых задач
dynamic_counts = df[~df['Статус'].isin(['Готово', 'Закрыт'])].groupby([df['Создано'].dt.to_period('M')])['Идентификатор проблемы'].size()
cumulative_counts = dynamic_counts.cumsum()
cumulative_counts.plot(kind='line', ax=ax5, color='red')
ax5.set_title('Динамика по открытым задачам в бэклоге, накопительно')
ax5.set_xlabel('Месяц')
ax5.set_ylabel('Количество задач')
ax5.grid(True)
st.pyplot(fig5)

# %%
# Экспорт данных в Excel только если есть данные для экспорта
try:
    if not average_completion_time.empty:
        average_completion_time[['Ключ проблемы', 'Идентификатор проблемы', 'Идентификатор родителя',
           'Статус', 'Создано', 'Обновленo', 'Исполнитель',
           'Пользовательское поле (Story Points)', 'Тема', 'Создатель',
           'Пользовательское поле (First sprint start date)', 'Дата решения',
           'Пользовательское поле (Epic Link)', 'Метки']].to_excel('average_completion_time.xlsx')
        st.success('Данные успешно экспортированы в Excel')
    else:
        st.warning('Нет данных для экспорта в Excel')
except Exception as e:
    st.error(f'Ошибка при экспорте в Excel: {str(e)}')
# %%
