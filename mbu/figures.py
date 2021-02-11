
import plotly.graph_objects as go
import mbu.load_data as ld

site_top_df = ld.load_data_site()

el_b_df = ld.load_data_eb()

fig_site_top3 = go.Figure(data=[go.Pie(labels=el_b_df['site_page'], values=el_b_df['Глубина просмотра'], hole=.3)])
fig_site_top3.update_layout(title_text='Глубина просмотра раздела "Электронный бюджет"',
                            autosize=True,
                            piecolorway=['#26205b', '#3257af', '#c8abd5', '#f9c5d8', '#b83e74', '#8d0837', '#9456ef'],
                            paper_bgcolor='#ebecf1',
                            plot_bgcolor='#ebecf1')

colors_site_top = ['#003b32', '#40817a', '#afbaa3', '#d0d0b8', '#037c87', '#7cbdc9']


site_top_df.sort_values('Визиты', inplace=True)
site_label1 = site_top_df.sort_values('Посетители', ascending=False).reset_index().drop('index', axis=1)

labels = list(site_label1['Название'].head(5))
labels.append("Остальные")
values = list(site_label1['Посетители'].head(5))
values.append(site_label1.loc[5:14]['Посетители'].sum())

colors_site = ['#ba83c4', '#fca3b5', '#b1d1ed', '#fcf3b5', '#efc67c', '#82bcc7']

fig_site_top2 = go.Figure(data=[go.Pie(labels=labels,
                                       values=values,
                                       marker_colors=colors_site,
                                       hole=.2)])

fig_site_top2.update_layout(title_text="Посетители", paper_bgcolor='#ebecf1', plot_bgcolor='#ebecf1')
