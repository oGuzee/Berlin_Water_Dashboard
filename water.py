import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import json
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go

app = dash.Dash()

app.scripts.config.serve_locally = True

# DFs
results = pd.read_csv('water_quality/result.csv', sep=';')
results = results.drop(['summary', 'wiki'], axis=1)
survey = pd.read_csv('water_quality/survey_how_often.csv', sep=';')
danger = pd.read_csv('water_quality/danger.csv',sep=";")
html_table = pd.read_csv('water_quality/html_table.csv',sep=';')#

# Markdown
markdown_datatable = '''
### Interactive datatable to look up for your own!
'''
markdown_htmltable = '''
### Important toxic chemicals in berlin water!
'''
markdown_survey = '''
### How often do you drink water from the tap?
'''

markdown_question = '''
### Questions of customer: 
1. Wasserwerk with the hardest/least hard water
2. pH levels per Wasserwerk

Contamination:
3. Wasserwerk with highest/lowest Nitrate concentration
4. What is the concentration of highly toxic chemicals per Wasserwerk?
5. Is any of the Wasserwerks affected by agriculture? (Nitrogen and phosphorus are the key indicators)
''' 
# Function to process dataframe to html table
def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )



app.layout = html.Div([
    dcc.Markdown('''# Water Quality'''),
    html.Label('by Oguzhan Uyar'),
    html.Label('Customer: Andrey Shabalov'),
    html.Label('06.12.18'),
    
    dcc.Markdown(markdown_question),
    
    # Markdown survey
    dcc.Markdown(markdown_survey),
    # Surver Plot
    dcc.Graph(
        id='survey-graph',
        figure={
            'data': [
                {
                    'x' : ['several times a day', 'every day / almost every day', 'sometimes', 'rarely', 'never'],
                    'y': [42.8, 23.5, 19.6, 7.2, 6.9],
                    'type' : 'bar',
                    'name' : 'survey',
                }
            ],
            'layout': {
                'title': 'Survey'
            }
        }
    ),
    # Markdown html table
    dcc.Markdown(markdown_htmltable),
    generate_table(html_table),
    # Scatter Plot Dangerous
    dcc.Graph(
        id='dangerous',
        figure={
            'data': [
                go.Scatter(
                    x=danger[danger['name'] == i]['threshold'],
                    y=danger[danger['name'] == i]['measured'],
                    text=danger[danger['name'] == i]['wiki'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        #'color': [120, 125, 130, 135, 140, 145],
                        #'showscale' : True,
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                        
                    },
                    showlegend=False,                    
                    name = i,
                    hoverlabel={
                        'namelength':-1
                    },
                    hoverinfo="x + y + text + name"
                ) for i in danger.name
            ],
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': 'threshold'},
                yaxis={'type': 'log', 'title': 'measured'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                #legend=dict(orientation="h"),
                hovermode='closest'
            )
        }
    ),
    # Markdown Data Tale
    dcc.Markdown(markdown_datatable),

    # Interactive Data Table
    dt.DataTable(
        rows=results.to_dict('records'),

        # optional - sets the order of columns
        # columns=sorted(results.columns),

        row_selectable=False,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable'
    ),
    # Responding Graphs
    html.Div(id='selected-indexes'),
    #html.Div(id='selected-indexes'),
    dcc.Graph(
        id='graph'
    )
], className="container")

# Data table interactiveness
@app.callback(
    Output('datatable', 'selected_row_indices'),
    [Input('graph', 'clickData')],
    [State('datatable', 'selected_row_indices')])
def update_selected_row_indices(clickData, selected_row_indices):
    if clickData:
        for point in clickData['points']:
            if point['pointNumber'] in selected_row_indices:
                selected_row_indices.remove(point['pointNumber'])
            else:
                selected_row_indices.append(point['pointNumber'])
    return selected_row_indices

# Bar chart interactiveness
@app.callback(
    Output('graph', 'figure'),
    [Input('datatable', 'rows'),
     Input('datatable', 'selected_row_indices')])
def update_figure(rows, selected_row_indices):
    dff = pd.DataFrame(rows)
    fig = plotly.tools.make_subplots(
        rows=2, cols=1,
        subplot_titles=('Berlin Water',),
        shared_xaxes=True)
    marker = {'color': ['#0074D9']*len(dff)}
    for i in (selected_row_indices or []):
        marker['color'][i] = '#FF851B'
    fig.append_trace(go.Bar(
        x=dff['location'],
        y=dff['measured'],
        text=dff['name'],
        name='measured',
        marker={'color': ['#0074D9']*len(dff)}
    ), 1, 1)
    fig.append_trace(go.Bar(
        x=dff['location'],
        y=dff['threshold'],
        text=dff['name'],
        name='threshold',
        marker={'color': ['#c50a0a']*len(dff)}
    ), 1, 1)
    fig['layout']['showlegend'] = False
    fig['layout']['height'] = 800
    fig['layout']['margin'] = {
        'l': 40,
        'r': 10,
        't': 60,
        'b': 200
    }
    return fig

# HTML stylesheet
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

if __name__ == '__main__':
    app.run_server(debug=True)