import requests
import pandas as pd
import load_cfg as cfg
import log_writer as lw


def get_site_info(start_date, end_date):
    headers = {'Authorization': 'OAuth ' + cfg.token}
    sources_sites = {
        'metrics': 'ym:s:visits,ym:s:users,ym:s:pageviews,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds',
        'dimensions': 'ym:s:startURL,ym:s:startURLPathLevel1,ym:s:startURLPathLevel2,ym:s:startURLPathLevel3,'
                      'ym:s:startURLPathLevel4',
        'date1': start_date,
        'date2': end_date,
        'ids': 23871871,
        'filters': "ALL(ym:s:startURL=='https://mbufk.roskazna.gov.ru/')"
    }

    response = requests.get('https://api-metrika.yandex.net/stat/v1/data', params=sources_sites, headers=headers)
    lw.log_writer(f"server response code {response.status_code}")

    metrika_data = response.json()

    if response.status_code != 200 or metrika_data['total_rows'] == 0:
        metrika_df = pd.DataFrame(columns=['startURL', 'Level1', 'Level2', 'Level3', 'Level4', 'visits', 'users',
                                           'pageviews', 'bounceRate', 'pageDepth', 'avgVisitDurationSeconds'])
        metrika_df.loc[0] = '-', '-', '-', '-', 0, 0, 0, 0, 0, 0, 0

    else:
        list_of_dicts = []
        dimensions_list = metrika_data['query']['dimensions']
        metrics_list = metrika_data['query']['metrics']
        for data_item in metrika_data['data']:
            d = {}
            for i, dimension in enumerate(data_item['dimensions']):
                d[dimensions_list[i]] = dimension['name']
            for i, metric in enumerate(data_item['metrics']):
                d[metrics_list[i]] = metric
            list_of_dicts.append(d)

        metrika_df = pd.DataFrame(list_of_dicts)
        metrika_df.columns = ['startURL', 'Level1', 'Level2', 'Level3', 'Level4', 'visits', 'users', 'pageviews',
                              'bounceRate', 'pageDepth', 'avgVisitDurationSeconds']

    return metrika_df
