import dash_core_components as dcc
import dash_html_components as html
import calendar
import datetime as dt
import dash_table

import dash_daq as daq
import mbu.load_data as ld
import mbu.site_info as si
import mbu.figures as pf

etsp_df = ld.LoadEtspData()
etsp_top_user_df = ld.TopUser(etsp_df)

sue_df = ld.LoadSueData()
sue_top_user_df = ld.TopUser(sue_df)

osp_df = ld.LoadOspData()
inf_systems_data = ld.LoadInfSystemsData()

sue_incidents_df = ld.LoadIncident(sue_df)

periods = ld.GetTimePeriods(etsp_df, sue_df, osp_df)

start_week, start_month, start_year = periods['week'][0], periods['month'][0], periods['year'][0]
finish_week, finish_month, finish_year = periods['week'][1], periods['month'][1], periods['year'][1]

date1 = ld.GetPeriod(ld.current_year, ld.current_week, 's')[0]
date2 = ld.GetPeriod(ld.current_year, ld.current_week, 's')[1]
metrika_df = si.get_site_info(date1, date2)

tab_selected_style = dict(backgroundColor='#ebecf1', fontWeight='bold')

choice_type = [dict(label='Неделя', value='w'),
               dict(label='Месяц', value='m'),
               dict(label='Произвольный период', value='p')]

d_month = ld.GetMonths(start_month, start_year, finish_month, finish_year)

d_week = ld.GetWeeks(start_week, start_year, finish_week, finish_year)

projects_df = ld.load_projects()
projects_names = [{"label": i[0], "value": i[1]} for i in projects_df[['name', 'id']].values]
projects_statuses = [{"label": i, "value": i} for i in projects_df['status'].unique()]
projects_persents = [{"label": ''.join([str(i * 10), '%']), "value": i / 10} for i in range(1, 11, 1)]

layout = html.Div([
    html.Div([
        html.H2('Отдел сопровождения пользователей'),
        html.Img(src="assets/logo.png")
    ], className="banner"),
    html.Div([
        html.Div([
            html.Div([html.Div([html.Label("Выберите период: ")], className='wrapper-dropdown-4')], className='bblock'),
            html.Div([html.Div([dcc.Dropdown(id='choice_type',
                                             options=choice_type,
                                             searchable=False,
                                             clearable=False,
                                             optionHeight=50,
                                             value='w',
                                             disabled=False)
                                ], className='wrapper-dropdown-3', style=dict(width='295px', display='block'))],
                     className='bblock'),  # choice period dropdown
            html.Div([html.Div([dcc.Dropdown(id='month_choice',
                                             options=d_month,
                                             searchable=False,
                                             clearable=False,
                                             value=finish_month,
                                             disabled=False
                                             )], className='wrapper-dropdown-3', style=dict(width='190px'))],
                     className='bblock'), ]),  # Month_choice dropdown
        html.Div([html.Div([dcc.Dropdown(id='week_choice',
                                         options=d_week,
                                         searchable=False,
                                         clearable=False,
                                         value=finish_week,
                                         style=dict(width='100%', heigth='60px'),
                                         disabled=False
                                         )], className='wrapper-dropdown-3', style=dict(width='420px'))],
                 className='bblock'),  # Week_choice dropdown
        html.Div([html.Div([dcc.DatePickerRange(id='period_choice',
                                                display_format='DD-MM-YYYY',
                                                min_date_allowed=dt.date(start_year, start_month, 1),
                                                max_date_allowed=dt.date(finish_year, finish_month,
                                                                         calendar.monthrange(finish_year,
                                                                                             finish_month)[1]),
                                                start_date=dt.date(ld.end_year, ld.end_month, ld.end_day),
                                                end_date=dt.date(ld.current_year, ld.current_month, ld.current_day),
                                                updatemode='bothdates',
                                                style=dict(background='#b1d5fa'),
                                                clearable=False
                                                # with_portal=True
                                                )])], className='bblock',
                 style=dict(heigth='45px')),  # Period_choice range picker
    ], style=dict(background='#b1d5fa')),
    html.Div([
        html.Div([
            dcc.Tabs(id='choice_period', value='weeks', children=[
                dcc.Tab(label='Работа с пользователями', value='weeks', children=[
                    html.Div([
                        html.Div([html.Table([
                            html.Tr([
                                html.Td([html.Label('Количество обращений'), ]),
                                html.Td(html.Label('Количество пользователей')),
                                html.Td('Среднее время решения', colSpan=3)
                            ]),
                            html.Tr([
                                html.Td(id='tasks', rowSpan=2, style={'fontSize': '2em'}),
                                html.Td(id='users', rowSpan=2, style={'font-size': '2.2em'}),
                                html.Td('ЕЦП'),
                                html.Td('СУЭ'),
                                html.Td('ОСП')
                            ]),
                            html.Tr([
                                html.Td(id='etsp-time'),
                                html.Td(id='sue-time'),
                                html.Td(id='osp-time')
                            ]),
                            html.Tr([
                            ]),
                            html.Tr([
                            ]),
                        ])], className='line_block', style=dict(width='60%')),  # table_1
                        html.Div([html.Label('Аварийные инциденты'),
                                  dash_table.DataTable(id='sue_avaria',
                                                       columns=[{"name": i, "id": i} for i in sue_incidents_df.columns
                                                                if
                                                                i == 'Тип' or i == 'Номер' or
                                                                i == 'Описание' or i == 'Дата'],
                                                       sort_action="native",
                                                       style_table={'height': '150px', 'overflowY': 'auto'},
                                                       fixed_rows={'headers': True},
                                                       style_as_list_view=True,
                                                       cell_selectable=False,
                                                       style_data=dict(width='20%'),
                                                       css=[{'selector': '.dash-spreadsheet td div',
                                                             'rule': '''
                                                                line-height: 10px;
                                                                max-height: 20px; min-height: 20px; height: 20px;
                                                                display: block;
                                                                overflow-y: hidden;
                                                           '''}],
                                                       tooltip_data=[{
                                                           column: {'value': str(value), 'type': 'markdown'}
                                                           for column, value in row.items()
                                                       } for row in sue_incidents_df.to_dict('records')],
                                                       tooltip_duration=None,
                                                       style_cell=dict(textAlign='center',
                                                                       overflow='hidden',
                                                                       textOverflow='ellipsis',
                                                                       maxWidth=0))], className='line_block',
                                 style=dict(width='32%')),
                    ]),
                    html.Hr(),
                    html.Div([
                        html.Div([dcc.Graph(id='users_figure')], className='line_block', style=dict(width='46%')),
                        html.Div([dcc.Graph(id='support_figure')], className='line_block', style=dict(width='46%')),
                    ]),
                    html.Br(),
                    html.Div([html.H3('ТОП-5 пользователей')],
                             style={'color': '#222780', 'font-type': 'bold'}),
                    html.Div([
                        html.Div([html.H4('ЕЦП')], className='line_block', style=dict(width='46%')),  # html div
                        html.Div([html.H4('СУЭ')], className='line_block', style=dict(width='46%')),  # html div
                    ]),
                    html.Div([
                        html.Div([
                            dash_table.DataTable(id='table_top_etsp',
                                                 columns=[{"name": i, "id": i} for i in etsp_top_user_df.columns],
                                                 sort_action="native",
                                                 style_as_list_view=True,
                                                 cell_selectable=False,
                                                 style_data={'width': '50px', 'font-size': ' 1.3em'},
                                                 style_cell=dict(textAlign='center'),
                                                 style_cell_conditional=[
                                                     {'if': {'column_id': 'Пользователь'},
                                                      'textAlign': 'left'}]
                                                 )], className='line_block', style=dict(width='46%')),
                        html.Div([
                            dash_table.DataTable(id='table_top_sue',
                                                 columns=[{"name": i, "id": i} for i in sue_top_user_df.columns],
                                                 sort_action="native",
                                                 style_as_list_view=True,
                                                 cell_selectable=False,
                                                 style_data={'width': '50px', 'font-size': ' 1.3em'},
                                                 style_cell=dict(textAlign='center'),
                                                 style_cell_conditional=[
                                                     {'if': {'column_id': 'Пользователь'},
                                                      'textAlign': 'left'}]
                                                 )], className='line_block', style=dict(width='46%')),
                    ]),
                ], selected_style=tab_selected_style),  # tab user
                dcc.Tab(label='Информационные системы', value='months', children=[
                    html.Br(),
                    html.Div([
                        html.Table([
                            html.Tr([
                                html.Td([html.Label('Подключено сотрудников МБУ ФК к ГИИС "Электронный бюджет"')]),
                            ]),
                            html.Tr([
                                html.Td([daq.LEDDisplay(id='total_tasks', value=254, color='#222780',
                                                        backgroundColor='#e8edff', )], rowSpan=2),
                            ]),

                        ], className='table_budget')
                    ], style=dict(height='165px')),
                    html.Div([
                        daq.BooleanSwitch(
                            id='leg_show',
                            label="Легенда",
                            labelPosition="top",
                            color='#1959d1',
                            on=False
                        ),
                    ], style=dict(width='15%')),
                    html.Div([dcc.Graph(id='inf_systems')], style=dict(background='#ebecf1'))
                ], selected_style=tab_selected_style),  # tab tech
                dcc.Tab(label='Сайт', value='s', children=[
                    html.Br(),
                    html.Div([dash_table.DataTable(id='site_stat',
                                                   columns=[{"name": i, "id": i} for i in ['Визиты', 'Посетители',
                                                                                           'Просмотры', 'Отказы',
                                                                                           'Глубина просмотра',
                                                                                           'Время на сайте']],
                                                   style_table={'height': '150px'},
                                                   # fixed_rows={'headers': True},
                                                   style_as_list_view=True,
                                                   cell_selectable=False,
                                                   tooltip_data=[
                                                       {
                                                           'Визиты': 'Суммарное количество визитов.',
                                                           'Посетители': 'Количество уникальных посетителей.',
                                                           'Просмотры': 'Число просмотров страниц на сайте за '
                                                                        'выбранный период.',
                                                           'Отказы': 'Доля визитов, в рамках которых состоялся лишь '
                                                                     'один просмотр страницы, продолжавшийся менее 15'
                                                                     ' секунд.',
                                                           'Глубина просмотра': 'Количество страниц, просмотренных '
                                                                                'посетителем во время визита.',
                                                           'Время на сайте': 'Средняя продолжительность визита в '
                                                                             'минутах и секундах. '
                                                       }],
                                                   tooltip_duration=None,
                                                   style_cell=dict(textAlign='center',
                                                                   overflow='hidden',
                                                                   textOverflow='ellipsis',
                                                                   maxWidth=0))],
                             style=dict(width='90%', padding='0 5%', fontSize='2em')),
                    html.Div([html.H3('Рейтинг посещаемости разделов сайта за 2020 год', style=dict(padding='20px'))]),
                    html.Div([dcc.Graph(id='site_top_fig')]),
                    html.Div([dcc.Graph(id='site_top_fig2', figure=pf.fig_site_top2)]),
                    html.Div([dcc.Graph(id='site_top_fig3', figure=pf.fig_site_top3)]),
                ], selected_style=tab_selected_style),  # tab site
                dcc.Tab(label='Проекты', value='pr', children=[
                    html.Br(),
                    html.Div([
                        dcc.Dropdown(id='projects_name',
                                     options=projects_names,
                                     value='1',
                                     style=dict(width='99%', margin='0 auto')),
                        html.Br(),
                        html.H4(id='project_name'),
                        html.Br(),
                        html.Div([
                            html.H5('Исполнители:  '),
                        ], style=dict(float='left', width='14.6%')),
                        html.Div([
                            html.H6(id='executor', style=dict()),
                        ], style=dict(float='left', width='45%')),
                        html.Div([
                            html.H5('Процент выполнения:  ')
                        ], style=dict(float='left', width='23.5%')),
                        html.Div([
                        ], style=dict(float='left', width='3%')),
                        html.Div([
                            # html.H5(id='persent_dd', style=dict(color='green')),
                            dcc.Dropdown(id='persent_dd',
                                         options=projects_persents,
                                         clearable=False,
                                         searchable=False,
                                         disabled=True, style=dict(float='left', width='100%'))
                        ], style=dict(display='inline-block', marginRight='20px', verticalAlign='top', width='13.7%')),

                    ]),

                    html.Br(),
                    html.Div([
                        html.Div([
                            html.H5('Статус проекта:  ', style=dict(width='250px'))], style=dict(display='inline-block',
                                                                                                 marginRight='20px',
                                                                                                 verticalAlign='top')),
                        html.Div([
                            dcc.Dropdown(id='status',
                                         options=projects_statuses,
                                         clearable=False,
                                         searchable=False,
                                         multi=False,
                                         disabled=True,
                                         style=dict(width='320px'))
                        ], style=dict(display='inline-block', marginRight='20px', verticalAlign='top')),
                    ], style=dict(float='right')),
                    html.Br(),
                    html.Div([
                        html.H5('Описание проекта:'),
                    ], style=dict(width='200px')),
                    html.Div([
                        dcc.Textarea(id='project_decsr', style={'width': '100%', 'height': 300})
                    ]),
                    html.Div(style=dict(backgroundColor='#ebecf1', height='300', border='1px solid black'))
                ], selected_style=tab_selected_style),  # tab projects
            ], colors=dict(border='#ebecf1', primary='#222780', background='#33ccff')),  # main tabs end
            html.Div(id='tabs_content')
        ])  # html.div 2
    ], style=dict(background='#ebecf1'))  # html.div 1
])  # app layout end
