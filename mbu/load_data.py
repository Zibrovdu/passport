import calendar
from datetime import date, timedelta

import pandas as pd
from sqlalchemy import create_engine
import mbu.load_cfg as lc

engine = create_engine(f'{lc.db_dialect}://{lc.db_username}:{lc.db_password}@{lc.db_host}:{lc.db_port}/{lc.db_name}')

current_month = date.today().month
current_day = date.today().day
current_year = date.today().year
current_week = date.today().isocalendar()[1]

end_day = (date.today() - timedelta(days=7)).day
end_month = (date.today() - timedelta(days=7)).month
end_year = (date.today() - timedelta(days=7)).year


def LoadEtspData():
    df = pd.read_sql('''select * from etsp_data''', con=engine)
    df.timedelta = pd.to_timedelta(df.timedelta)

    return df


def LoadSueData():
    df = pd.read_sql('''select * from sue_data''', con=engine)
    df.timedelta = pd.to_timedelta(df.timedelta)

    return df


def LoadOspData():
    df = pd.read_sql('''select * from osp_data''', con=engine)
    df.timedelta = pd.to_timedelta(df.timedelta)

    return df


def TopUser(df):
    top_user_df = df[(df.unit != '19. Отдел сопровождения пользователей') & (df.unit != 'ЦОКР') & (
            df.user != 'Кондрашова Ирина Сергеевна')]
    top_user_df = pd.DataFrame(top_user_df.groupby('user')['count_task'].sum().sort_values(ascending=False).head()
                               .reset_index()).rename(columns={'user': 'Пользователь', 'count_task': 'Обращения'})
    return top_user_df


def LoadIncident(df):
    incident_df = df[(df.status == 'Проблема') | (df.status == 'Массовый инцидент')]
    incident_df.columns = ['Дата обращения', 'Тип', 'Номер', 'Описание', 'Плановое время', 'Фактическое время',
                           'Пользователь', 'timedelta', 'Отдел', 'Дата', 'finish_date', 'month_open',
                           'month_solved', 'week_open', 'week_solved', 'count_task']
    return incident_df


def NoIncidents():
    no_incidents_df = pd.DataFrame({'Дата': '-', 'Тип': 'Аварийных инциндентов нет', 'Номер': '-', 'Описание': '-',
                                    'Плановое время': '-', 'Фактическое время': '-', 'Пользователь': '-',
                                    'timedelta': '-', 'Отдел': '-', 'start_date': '-', 'finish_date': '-',
                                    'month_open': '-', 'month_solved': '-', 'week_open': '-',
                                    'week_solved': '-', 'count_task': '-'}, index=[0])

    return no_incidents_df


def GetTimeData(df):
    delta_4h, delta_8h, delta_24h, delta_5d = timedelta(hours=4), timedelta(hours=8), timedelta(hours=24), \
                                              timedelta(days=5)

    time_dict = {'до 4-х часов': df[df['timedelta'] <= delta_4h].count_task.sum(),
                 'от 4-х до 8-ми часов': df[(df.timedelta <= delta_8h) & (df.timedelta > delta_4h)].count_task.sum(),
                 'от 8-ми до 24-х часов': df[(df.timedelta <= delta_24h) & (df.timedelta > delta_8h)].count_task.sum(),
                 'от 1-го до 5-ти дней': df[(df.timedelta <= delta_5d) & (df.timedelta > delta_24h)].count_task.sum(),
                 'свыше 5-ти дней': df[df.timedelta > delta_5d].count_task.sum()}
    df1 = pd.DataFrame.from_dict(time_dict, orient='index')

    list_mean_time = [df[df.timedelta <= delta_4h].timedelta.mean(),
                      df[(df.timedelta <= delta_8h) & (df.timedelta > delta_4h)].timedelta.mean(),
                      df[(df.timedelta <= delta_24h) & (df.timedelta > delta_8h)].timedelta.mean(),
                      df[(df.timedelta <= delta_5d) & (df.timedelta > delta_24h)].timedelta.mean(),
                      df[df.timedelta > delta_5d].timedelta.mean()]
    df1.reset_index(inplace=True)
    df1.rename(columns={'index': 'time_task', 0: 'count_task'}, inplace=True)

    df1['persent_task'] = 0
    df1['mean_time'] = 0
    for num in range(len(df1)):
        df1.loc[num, ['persent_task']] = df1.loc[num, ['count_task']].iloc[0] / df1['count_task'].sum()
        df1.loc[num, ['mean_time']] = list_mean_time[num]

    return df1


def GetTimePeriods(etsp_df, sue_df, osp_df):
    start_weeks_list = [etsp_df.reg_date.min().week, sue_df.reg_date.min().week, osp_df.reg_date.min().week]
    end_weeks_list = [etsp_df.reg_date.max().week, sue_df.reg_date.max().week, osp_df.reg_date.max().week]

    start_month_list = [etsp_df.reg_date.min().month, sue_df.reg_date.min().month, osp_df.reg_date.min().month]
    end_month_list = [etsp_df.reg_date.max().month, sue_df.reg_date.max().month, osp_df.reg_date.max().month]

    start_year_list = [etsp_df.reg_date.min().year, sue_df.reg_date.min().year, osp_df.reg_date.min().year]
    end_year_list = [etsp_df.reg_date.max().year, sue_df.reg_date.max().year, osp_df.reg_date.max().year]

    return dict(week=[min(start_weeks_list), max(end_weeks_list)], month=[min(start_month_list), max(end_month_list)],
                year=[min(start_year_list), max(end_year_list)])


def GetIntent(df):
    pd.options.mode.chained_assignment = None

    df['Описание'] = df['Описание'].fillna('missed value')
    df['Описание'] = df['Описание'].apply(lambda x: str(x).lower())

    temp_df = pd.DataFrame(columns=['num', 'text', 'intent'])
    for i in range(len(df)):
        temp_df.loc[i] = i, df['Описание'].loc[i], ''

    conf = {
        'intents': {
            "1С ЭБ": ['эб', 'элбюджету', 'элбюджета', 'эб', 'элбюджета', ' 1с ', ' 1c ', 'базу 1с ', ' систему 1с ',
                      ' 1c ', 'электронным бюджетом', 'не заходит в 1с', '1с,', 'в 1с, ', '1с:предприятие', '1с:п',
                      '1 c ', '1с-облако', 'электронный бюджет', '-1с', 'эл.бюджет', '1с.', 'в 1с.', '1с в', ' с 1с',
                      'эл.бюджет', ' работает 1 с ', 'базе 1 с', 'бюджету', 'электронный', 'бюджет'],
            'ЛанДокс': ['lan docs', 'ландокс', 'лан докс', 'landocs', 'лаандокс'],
            'ЗКВС': ['звкс', 'зквс', 'vdi', 'getmobit', ' закрытый контур', 'контур'],
            'Электронная почта': ['почта ', 'аутлук', 'сбросить', 'пароль от почты', 'пароль от пя', ' входом почту',
                                  'сменить пароль', 'пароля от уз', 'действия пароля', ' востановить пароль',
                                  'изменить пароль', 'обновить пароль', 'нового правила', 'настроить почту',
                                  'почта работает', 'работает почт', 'outlook', 'почтой', 'правила почты',
                                  'правило почты', 'аутлук', 'настройка почты', 'подключение почты ', 'почты',
                                  'работает аутлук', 'почтовый ящик', 'почтового ящика', 'оутлук', 'настройка почты ',
                                  'отправляется письмо ', 'сменить пароль'],
            'настройка ЭП': [' эп ', 'эцп', 'эцпп', 'эцп', 'эцп', 'эцпп', 'эцп ', 'новую эп', 'настроить криптопро',
                             'криптопро', ' лицензию крипто', 'криптоарм', 'крипто арм ', 'эцпп'],
            'не работают базы (ПУиОТ)': ['пуиот', 'пу и от'],
            'установка 1С «Тонкий Клиент»': ['тонкий', 'клиент', 'тонкие', 'клиенты', 'tionix', 'thinclient',
                                             ' тонкий клиент', 'документы печать'],
            'установка банк-клиент': ['банк-клиент'],
            'не работает СУЭ ФК': ['суэ фк', 'суэ'],
            'Доступ': ['доступ ', 'доступа ', 'могу войти', 'войти', 'зайти на диск', 'не могу зайти',
                       'ошибки при входе', 'не дает зацти', 'получается зайти', 'не дает зайти',
                       'предоставить логин и пароль', 'сетевых', 'папок', 'диске', 'ресурсу', 'ресурс', 'сетевой',
                       'папке', 'папку', 'общий', 'диск', 'сетевую папку', 'сетевая папка', 'сетевым папкам',
                       'работает интернет', 'интернетом', ' доступ сайт', 'wi fi', 'настройка доступа',
                       'доступа интернет', ' доступ сайту', 'wifi', 'нету интернета', 'доступ порталу', 'работает сайт',
                       'подключения интернету', ' портала'],
            'Органайзер': ['органайзер', 'БГУ ', ' ЗКГУ ', 'модуль бухгалтерия', 'ошибка крипто провайдера ',
                           'не установлено расширение'],
            'ПУР': ['пур', 'п у р'],
            'ПУИО': ['пуио', 'пу и о'],
            'ПУОТ': ['пуот', 'пу о т '],
            'не подписывается документ': ['не может подписать', 'подписью', 'возможности подписать',
                                          'ошибка при подписании', 'документ не удается', 'подписать документ',
                                          'подписывает документ', 'подписать документы', 'jinn', 'client', 'стороннее',
                                          ' cisco ', ' jinn ', ' справкибк', ' справки бк', ' впн клиента ', ' cisco ',
                                          ' jinn ', ' справкибк', ' справки бк', ' впн клиента '],
            'Настройка печати': ['пинкод ', ' pin ', 'инкод ', ' пин ', 'код доступа', 'пин-код', 'печаль',
                                 'пикод печати', 'код использования', 'принтеры', 'настройка печати', 'печатается файл',
                                 'доступ принтеру', 'настроить печать', 'документов печать', 'подключить принтер',
                                 'печати ', 'печатью ', 'пароль печати'],
            'Замена РМ': ['тонер', 'мало', 'картридж', 'картриджа', 'пурпурный', 'замяло бумагу', 'зажевывает',
                          'зажевал'],
            'Работа с техникой': ['вкл пк', ' монитор ', ' спящего ', ' режима ', ' включается ', 'завис пк',
                                  ' сломался', 'мышки', 'клавиатура ', ' мышь ', ' kvm ', ' свитч ', ' переключатель ',
                                  'switch', ' nd телефон '],
            'Перемещение рабочих мест': ['переноса', 'переноса рабоч', 'перенос мест', 'перенести рабочее',
                                         'переместить с', 'переместить сотрудника', 'перенос ', ' пересадить '],
            'скуд': ['скуд', 'замок'],
            'консультант +': ['консультант +', 'консультантплюс', 'консультант+', ' консультант', 'консультанте плюс '],
            'Новый сотрудник': ['полная', 'первичная', 'сотруднику', 'организовать', 'рабочее', 'полная', 'организация',
                                'нового', 'организация рабоч', 'создать учетную запись'],
        }
    }

    for item, value in conf['intents'].items():
        for i in value:
            mask = temp_df['text'].str.contains(i)
            temp_df.loc[mask, 'intent'] = item

    df3 = temp_df[temp_df.loc[:, 'intent'] == '1С ЭБ']
    mask = df3['text'].str.contains('работает')
    df3.loc[mask, 'intent'] = 'не работает (1С ЭБ)'

    df4 = temp_df[temp_df['intent'] == 'ЛанДокс']
    mask = df4['text'].str.contains('настроить ')
    df4.loc[mask, 'intent'] = 'настроить ЛанДокс'

    df5 = temp_df[temp_df['intent'] == 'ЗКВС']
    mask = df5['text'].str.contains('работает', 'установка')
    df5.loc[mask, 'intent'] = 'установка (не работает) ЗКВС'

    total_df = df3.append(df5[df5.intent == 'установка (не работает) ЗКВС'])

    df5 = df5[df5.intent == 'ЗКВС']

    df6 = df5.append(df4)

    mask = df6['text'].str.contains('настроить ')
    df6.loc[mask, 'intent'] = 'настроить (ЛанДокс, ЗКВС)'

    total_df = total_df.append(df6[df6.intent == 'настроить (ЛанДокс, ЗКВС)'])
    total_df = total_df.append(df6[df6.intent == 'ЛанДокс'])

    df7 = df6[df6.intent == 'ЗКВС'].append(temp_df[temp_df['intent'] == 'Электронная почта'])

    mask = df7['text'].str.contains('сброс', 'парол')
    df7.loc[mask, 'intent'] = 'сброс пароля (почта, ЗКВС)'

    total_df = total_df.append(df7)

    total_df = total_df.append(temp_df[temp_df['intent'] == 'ПУИО'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'ПУР'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'ПУОТ'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'Органайзер'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'Доступ'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'не работает СУЭ ФК'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'настройка ЭП'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'не работают базы (ПУиОТ)'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'не подписывается документ'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'установка 1С «Тонкий Клиент»'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'консультант +'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'Новый сотрудник'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'Настройка печати'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'Работа с техникой'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'Замена РМ'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'скуд'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'Перемещение рабочих мест'])

    temp_df1 = temp_df.drop(list(total_df.num), axis=0)
    temp_df1.intent = 'Прочие обращения'
    total_df = total_df.append(temp_df1)

    df.reset_index(inplace=True)
    df.rename(columns={'index': 'num'}, inplace=True)
    merged_df = df.merge(total_df[['num', 'intent']], on='num', how='left')
    merged_df.drop('num', axis=1, inplace=True)
    df.drop('num', axis=1, inplace=True)

    del temp_df, df3, df4, df5, df6, df7, total_df, temp_df1

    return merged_df


def CountMeanTime(filtered_df):
    duration = filtered_df['timedelta'].mean()
    count_tasks = filtered_df['count_task'].sum()

    # преобразование в дни, часы, минуты и секунды
    days, seconds = duration.days, duration.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    avg_time = days, hours, minutes, seconds

    if count_tasks == 0:
        avg_time = '-'
    elif avg_time[0] == 0:
        avg_time = f'{avg_time[1]} час. {avg_time[2]} мин.'
    else:
        avg_time = f'{avg_time[0]} дн. {avg_time[1]} час. {avg_time[2]} мин.'

    return avg_time


def LoadInfSystemsData():
    df = pd.read_excel(r'mbu/assets/dostup.xlsx', sheet_name='Лист5', index_col=0)
    df.drop('Номер отдела', axis=1, inplace=True)

    return df


def GetPeriod(year, week, output_format='n'):
    """
    Синтаксис:
    GetPeriod(
            year,
            week,
            output_format='n')

    Описание:
    Функция принимает на вход год и номер недели. Возвращает список или строку содержащие начальную и конечную
    даты недели

    Параметры
    ----------
    year:
        год
    week:
        номер недели
    output_format: string, default 'n'
        Определяет формат вывода данных. Допустимые значения:
        'n' - строка вида 'ДД-ММ-ГГГГ - ДД-ММ-ГГГГ'
        's' - список вида ['ГГГГ-ММ-ДД', 'ГГГГ-ММ-ДД']
        При указании другого параметра вернется список ['1900-01-01', '1900-01-01']

    Returns
    -------
    string or list of strings
    """
    first_year_day = date(year, 1, 1)
    if first_year_day.weekday() > 3:
        first_week_day = first_year_day + timedelta(7 - first_year_day.weekday())
    else:
        first_week_day = first_year_day - timedelta(first_year_day.weekday())

    dlt_start = timedelta(days=(week - 1) * 7)
    dlt_end = timedelta(days=(((week - 1) * 7) + 6))

    start_day_of_week = first_week_day + dlt_start
    end_day_of_week = first_week_day + dlt_end

    if output_format == 'n':
        period = ' - '.join([start_day_of_week.strftime("%d-%m-%Y"), end_day_of_week.strftime("%d-%m-%Y")])
    elif output_format == 's':
        period = [start_day_of_week.strftime("%Y-%m-%d"), end_day_of_week.strftime("%Y-%m-%d")]
    else:
        period = ['1900-01-01', '1900-01-01']

    return period


def GetMonthPeriod(year, month_num):
    """
    Функция принимает на вход год и номер месяца. Возвращает списко содержащий первую и последнюю даты месяца
    в виде строки формата 'ГГГГ-ММ-ДД'
    """
    num_days = calendar.monthrange(year, month_num)[1]

    start_date = f'{year}-0{month_num}-01'
    end_date = f'{year}-0{month_num}-{num_days}'

    return [start_date, end_date]


def GetWeeks(start_week, start_year, finish_week, finish_year):
    """
    Функция принимает на вход период в виде 4-х параметров (номер недели и год начала, номер недели и год окончания.
    Возвращает список словарей содержащих информацию о номере недели, её периоде, и номере недели для последующей
    загрузки в компонент dcc.Dropdown.
    """
    last_week_of_start_year = date(start_year, 12, 31).isocalendar()[1]

    start_period = [{"label": f'Неделя {i} ({GetPeriod(start_year, i)})',
                     "value": i} for i in range(start_week, last_week_of_start_year + 1)]
    end_period = [{"label": f'Неделя {i} ({GetPeriod(finish_year, i)})', "value": i} for i in range(1, finish_week + 1)]

    for item in end_period:
        start_period.append(item)
    start_period.reverse()

    return start_period


def GetPeriodMonth(year, month):
    """
    Функция принимает на вход номер месяца и год. Взоращает строку 'Месяц год'
    """
    months = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
              'Ноябрь', 'Декабрь']
    period = ' '.join([str(months[month]), str(year)])

    return period


def GetMonths(start_month, start_year, finish_month, finish_year):
    """
    Функция принимает на вход период в виде 4-х параметров (номер месяца и год начала, номер месяца и год окончания.
    Возвращает список словарей содержащих информацию о месяце, годе и номере месяца для последующей загрузки в
    компонент dcc.Dropdown.
    """
    start_period = [{"label": f'{GetPeriodMonth(start_year, i)}', "value": i} for i in range(start_month, 13)]
    end_period = [{"label": f'{GetPeriodMonth(finish_year, i)}', "value": i} for i in range(1, finish_month + 1)]

    for item in end_period:
        start_period.append(item)
    start_period.reverse()

    return start_period


def load_projects():
    df = pd.read_sql("""select * from projects_test""", con=engine)
    return df


def load_data_site():
    df = pd.read_excel(r'mbu/assets/site.xlsx', skiprows=6)
    df['Страница входа, ур. 4'] = df['Страница входа, ур. 4'].fillna('')
    df2 = df[df['Страница входа, ур. 4'].str.contains('molodezhnyy-sovet')][['Страница входа, ур. 4', 'Визиты',
                                                                             'Посетители', 'Просмотры',
                                                                             'Доля новых посетителей']]
    df2 = pd.DataFrame(df2.groupby(['Страница входа, ур. 4'], as_index=False)[['Визиты', 'Посетители', 'Просмотры',
                                                                               'Доля новых посетителей']].sum())
    df2 = df2.rename(columns={'Страница входа, ур. 4': 'Страница входа, ур. 2'})
    df = pd.DataFrame(df.groupby(['Страница входа, ур. 2'], as_index=False)[
                          ['Визиты', 'Посетители', 'Просмотры', 'Доля новых посетителей']].sum())
    df.loc[13, 'Страница входа, ур. 2'] = 'https://mbufk.roskazna.gov.ru/'
    df = df.append(df2).reset_index()
    df.drop('index', axis=1, inplace=True)
    df.loc[8, ['Визиты', 'Посетители', 'Просмотры', 'Доля новых посетителей']] = \
        df.loc[8, ['Визиты', 'Посетители', 'Просмотры', 'Доля новых посетителей']] - \
        df.loc[14, ['Визиты', 'Посетители', 'Просмотры', 'Доля новых посетителей']]

    df2 = pd.read_excel(r'mbu/assets/site.xlsx', sheet_name='перевод', header=None)
    df['Название'] = ''
    for num in range(len(df2)):
        mask = df['Страница входа, ур. 2'].isin(df2.iloc[num])
        df.loc[mask, 'Название'] = df2.iloc[num][1]
    df3 = df[(df['Название'] == 'О Межрегиональном бухгалтерском УФК') | (df['Название'] == 'Новости') |
             (df['Название'] == 'Документы') | (df['Название'] == 'Электронный бюджет') |
             (df['Название'] == 'Иная деятельность') | (df['Название'] == 'Прием обращений')]
    return df3


def load_data_eb():
    df = pd.read_excel(r'mbu/assets/site.xlsx', skiprows=6)
    df = df[df['Страница входа, ур. 2'] == 'https://mbufk.roskazna.gov.ru/elektronnyy-byudzhet/']
    df_eb = df.groupby('Страница входа, ур. 3', as_index=False)['Глубина просмотра'].sum()
    df4 = pd.read_excel(r'mbu/assets/site.xlsx', sheet_name='перевод', skiprows=15, header=None)
    df_eb['site_page'] = ''
    for num in range(len(df4)):
        mask = df_eb['Страница входа, ур. 3'].isin(df4.iloc[num])
        df_eb.loc[mask, 'site_page'] = df4.iloc[num][1]
    return df_eb
