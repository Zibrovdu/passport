import requests
import pandas as pd
import mbu.load_cfg as cfg
import mbu.log_writer as lw


def get_site_info(start_date, end_date):
    headers = {'Authorization': 'OAuth ' + cfg.token}
    sources_sites = {
        'metrics': 'ym:s:visits,ym:s:users,ym:s:pageviews,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds',
        'dimensions': 'ym:s:date,ym:s:startURLPathLevel1,ym:s:startURLPathLevel2,ym:s:startURLPathLevel3,'
                      'ym:s:startURLPathLevel4,ym:s:startURL',
        'date1': start_date,
        'date2': end_date,
        'accuracy': 'full',
        'ids': 23871871,
        'limit': 10000,
        'filters': "ym:s:startURLPathLevel1=='https://mbufk.roskazna.gov.ru/'"
    }

    response = requests.get('https://api-metrika.yandex.net/stat/v1/data', params=sources_sites, headers=headers)
    lw.log_writer(f"server response code {response.status_code}")

    metrika_data = response.json()
    lw.log_writer(f"Data load successfully, total row loaded: {metrika_data['total_rows']}")

    if response.status_code != 200 or metrika_data['total_rows'] == 0:
        metrika_df = pd.DataFrame(
            columns=['date', 'startURL', 'Level1', 'Level2', 'Level3', 'Level4', 'visits', 'users', 'pageviews',
                     'bounceRate', 'pageDepth', 'avgVisitDurationSeconds'])
        metrika_df.loc[0] = '-', '-', '-', '-', '-', 0, 0, 0, 0, 0, 0, 0

    else:
        list_of_dicts = []
        dimensions_list = metrika_data['query']['dimensions']
        metrics_list = metrika_data['query']['metrics']
        for data_item in metrika_data['data']:
            metrics_dict = {}
            for i, dimension in enumerate(data_item['dimensions']):
                metrics_dict[dimensions_list[i]] = dimension['name']
            for i, metric in enumerate(data_item['metrics']):
                metrics_dict[metrics_list[i]] = metric
            list_of_dicts.append(metrics_dict)

        metrika_df = pd.DataFrame(list_of_dicts)
        metrika_df.columns = ['date', 'startURL', 'Level1', 'Level2', 'Level3', 'Level4', 'visits', 'users',
                              'pageviews', 'bounceRate', 'pageDepth', 'avgVisitDurationSeconds']

    return metrika_df


def get_data_visits_graph(metrika_df):
    metrika_df.columns = ('date', 'level1', 'level2', 'level3', 'level4',
                          'startURL', 'visits', 'users', 'pageviews', 'bounceRate', 'pageDepth',
                          'avgVisitDurationSeconds')

    metrika_df = metrika_df
    metrika_df['level4'] = metrika_df['level4'].fillna('')
    for col in ['visits', 'users', 'pageviews']:
        metrika_df[col] = metrika_df[col].astype(int)

    molod_sovet_df = pd.DataFrame(
        metrika_df[metrika_df['level4'].str.contains('molodezhnyy-sovet')].groupby(['level4'], as_index=False)[
            ['visits', 'users', 'pageviews', 'bounceRate', 'pageDepth', 'avgVisitDurationSeconds']].sum().rename(
            columns={'level4': 'level2'}))
    metrika_df = pd.DataFrame(metrika_df.groupby(['level2'], as_index=False)[
                                  ['visits', 'users', 'pageviews', 'bounceRate', 'pageDepth',
                                   'avgVisitDurationSeconds']].sum())
    metrika_df = metrika_df.append(molod_sovet_df).reset_index()
    metrika_df.drop('index', axis=1, inplace=True)

    names_dict = {'molodezhnyy-sovet/': 'Молодежный совет', 'elektronnyy-byudzhet/': 'Электронный бюджет',
                  'o-kaznachejstve/': 'О Межрегиональном бухгалтерском УФК', 'inaya-deyatelnost/': 'Иная деятельность',
                  'dokumenty/': 'Документы', 'gis/': 'Информационные системы',
                  'novosti-i-soobshheniya/': 'Новости и сообщения',
                  'poisk/': 'Поиск', 'priem-obrashhenij/': 'Прием обращений'}

    for search_str, name in names_dict.items():
        mask = metrika_df[metrika_df['level2'].str.contains(search_str)].index
        metrika_df.loc[mask, 'level2'] = name

    site_sections = ['Электронный бюджет', 'О Межрегиональном бухгалтерском УФК', 'Иная деятельность', 'Документы',
                     'Прием обращений']
    mask = metrika_df['level2'].isin(site_sections)
    metrika_df = metrika_df.loc[mask].sort_values('visits', ascending=True)

    return metrika_df
