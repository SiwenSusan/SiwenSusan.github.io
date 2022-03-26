import dash
from dash import html
import plotly.graph_objects as go
from dash import dcc, dash_table
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
from analyze import run_model as rm


# run models and get training and testing data outputs
train, test = rm.concat()

# clean date columns
train['date'] = 2022000 + train.dt
train['date'] = pd.to_datetime(train['date'], format='%Y%m%d')
train['date'] = train['date'].dt.date

test['date'] = 2022000 + test.dt
test['date'] = pd.to_datetime(test['date'], format='%Y%m%d')
test['date'] = test['date'].dt.date

df = rm.get_top_3_sectors(test)

app = dash.Dash()

all_options = {
    'linear': ['All Sectors', 'Industrials' , 'Health Care', 'Information Technology',
    'Communication Services' , 'Consumer Staples', 'Consumer Discretionary',
    'Utilities', 'Financials', 'Materials', 'Real Estate', 'Energy'],
    'logitistic': ['All Sectors'],
    'KNN': ['All Sectors'],
    'SVM': ['All Sectors']
}

tabs_styles = {
    'height': '44px'
}

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

app.layout = html.Div([
        html.Div([
            html.H1("Can Moods on Twitter Predict Stock Price Movements?")
                ], 
            style = {'padding' : '10px' , 'backgroundColor' : '#3aaab2'}),

        html.Div([
            html.Label("Choose a topic "),
            dcc.Dropdown(id = 'topic_dropdown',
            options = [
                {'label':'US-China Relations', 'value':'china' },
                {'label': 'COVID-19', 'value':'covid'},
                ],
            value = 'covid')], style = {'padding': '5px', 'width': '20%', 'display': 'inline-block'} ),

        html.Div([
            html.Label("Choose a model "),
            dcc.Dropdown(id = 'model_dropdown',
            options = [
                {'label':'Linear Regression', 'value':'linear' },
                {'label': 'Logistic Regression', 'value':'logistic'},
                {'label': 'KNN', 'value':'KNN'},
                {'label': 'SVM', 'value':'SVM'},
                ],
            value = 'linear')], style = {'padding': '5px', 'width': '20%', 'display': 'inline-block'} ),

        html.Div([
            html.Label("Choose a sector "),
            dcc.Dropdown(id='sector_dropdown', options=[])], 
            style = {'padding': '5px', 'width': "20%", 'display': 'inline-block'}),

        html.H3('Testing the model', style = {'padding': '3px'}),
        dcc.Graph(id = 'bar_plot'),

        html.H3('Model fit for the training data', style = {'padding': '3px'}),
        dcc.Graph(id = 'training_plot'),

        html.H1("Accuracy of each classifier per sector — Top 3", 
            style={'textAlign': 'center', 'color': '#7FDBFF'}),
        dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]),

        dcc.Tabs(id="tabs-styled-with-inline", value='tab-1', children=[
            dcc.Tab(label='About', value='About', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='The Tweet Data', value='The Tweet Data', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='The Stock Data', value='The Stock Data', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='The Output', value='The Output', style=tab_style, selected_style=tab_selected_style),
        ], style=tabs_styles),

    html.Div(id='tabs-content-inline')
])
    
@app.callback(
    Output('sector_dropdown', 'options'),
    Input('model_dropdown', 'value')
)
def set_sector_options(model):
    return [{'label': c, 'value': c} for c in all_options[model]]

@app.callback(
    Output('sector_dropdown', 'value'),
    Input('sector_dropdown', 'options'))
def set_sector_value(available_options):
    return available_options[0]['value']


@app.callback(Output('bar_plot', 'figure'),
            [Input('topic_dropdown', 'value'),
            Input('model_dropdown', 'value'),
            Input('sector_dropdown', 'value')])

def graph_update(topic, model_value, sector_value):
    '''
    Update first graph (for test data output)

    Inputs:
        topic (str): 'covid' or 'china'
        model_value (str): 'linear', 'logistic', 'KNN', or 'SVM'
        sector_value (str): one of the 11 sectors or 'All Sectors'
            for entire S&P 500 Index
    Returns:
        fig: graph
    '''
    if model_value == 'linear':
        df1 = test[(test['topic'] == topic) & (test['sector'] == sector_value) & (test['model'] == model_value)]
        fig = go.Figure(go.Scatter(x = df1['date'], y = df1['actual'], 
                        name = 'Actual price using {} model'.format(model_value),
                        line = {'color': 'firebrick', 'width': 4}))

        fig.add_trace(go.Scatter(x = df1['date'], y = df1['predicted'],
                        name = 'Predicted price {} model'.format(model_value),
                        line = {'color': 'blue', 'width': 2, 'dash': 'dash'}))
        
        fig.update_layout(title = 'Actual vs. Predicted for {}'.format(sector_value),
                        xaxis_title = 'Date',
                        yaxis_title = 'Price ($)'
                        )
    else:
        df1 = test[(test['topic'] == topic) & (test['model'] == model_value)]
        df1['accurate'] = np.where(df1['predicted'] == df1['actual'], 1, 0)
        df2 = pd.DataFrame()
        df2['accuracy'] = df1.groupby('sector')['accurate'].mean()
        df2.reset_index(inplace = True)

        fig = go.Figure(go.Bar(x = df2['sector'], y = df2['accuracy']
                        ))
        fig.update_layout(title = 'Accuracy rate using the {} model'.format(model_value),
                        xaxis_title = 'Sector',
                        yaxis_title = 'Accuracy rate (%)'
                        )

    return fig


@app.callback(Output('tabs-content-inline', 'children'),
              Input('tabs-styled-with-inline', 'value'))
def render_content(tab):
    '''
    Render content for each tab based on user

    Input: tab

    Returns: content of each tab
    '''
    if tab == 'About':
        return html.Div([
            html.H3("""
            Stock prices are influenced by the public attitude towards 
            the market. Psychological research shows that emotions play a significant role 
            in human decision-making. Similarly, behavioral finance research shows
            that financial decisions are influenced by people's emotions and moods. """),

            html.H3('''
            Twitter is a popular place for users to express their moods and sentiments 
            towards a variety of topics. We look into how the polarity of sentiments in 
            tweets is related to the daily movements of stock prices!
            ''')
        ])
    elif tab == 'The Tweet Data':
        return html.Div([
                    html.H3('''
                        Tweets were collected from the Twitter Developer API. 
                        We gathered tweets related to COVID-19 and 
                        US-China Relations from February 14, 2022 to 
                        March 15, 2022. 
                        '''),
                    html.H3(
                        'The query keywords used to collect tweets are as follows: '),
                    html.H3('''
                        COVID-19: covid19, covid, covid-19, vaccine, vaccination, omicron,
                        booster, mask, mandate, lockdown, death rate, travel restriction,
                        total infections, breakthrough infections, social distancing,
                        quarantine, isolation, pandemic, & shutdown. '''),
                    html.H3(
                        'US-China Relations: Trump, Biden, trade war, Xi Jinping, Eileen Gu, '
                        'Taiwan, Hong Kong, CCP, TikTok, Huawei, tariffs, human rights, '
                        'Xinjiang, Zhao Lijian, & Ned Price.'
            ), 
        ])
    elif tab == 'The Stock Data':
        return html.Div([
            html.H3('''
                We collected stock data from all S&P 500 companies and grouped the data 
                into 11 different sectors: Information Technology, Health Care, Consumer 
                Discretionary, Financials, Communication Services, Industrials, Consumer Staples, 
                Energy, Real Estate, Materials, and Utilities.
            '''
            )
        ])
    elif tab == 'The Output':
        return html.Div([
            html.H3('''
            You can check out the differences for both testing and
            training data through the various dropdown menus. 
            For both topics, you may select
            a model to see the accuracy of the prediction using average Twitter
            sentiments on stock market movement. 
            If you choose linear regression, you can choose a sector.
            For all other models, we show the accuracy of the models with all sectors
            on one plot.
            '''
            )
        ])

@app.callback(Output('training_plot', 'figure'),
            [Input('topic_dropdown', 'value'),
            Input('model_dropdown', 'value'),
            Input('sector_dropdown', 'value')])

def graph_update_tr(topic, model_value, sector_value):
    '''
    Update second graph (for training data output)

    Inputs:
        topic (str): 'covid' or 'china'
        model_value (str): 'linear', 'logistic', 'KNN', or 'SVM'
        sector_value (str): one of the 11 sectors or 'All Sectors'
            for entire S&P 500 Index
    Returns:
        fig1: graph
    '''
    if model_value == 'linear':
        tr1 = train[(train['topic'] == topic) & (train['sector'] == sector_value) & (train['model'] == model_value)]
        fig1 = go.Figure(go.Scatter(x = tr1['date'], y = tr1['true_y'], 
                        name = 'Actual price using the {} model'.format(model_value),
                        line = {'color': 'firebrick', 'width': 4}))

        fig1.add_trace(go.Scatter(x = tr1['date'], y = tr1['fitted_y'],
                        name = 'Fitted price {} model'.format(model_value),
                        line = {'color': 'blue', 'width': 2, 'dash': 'dash'}))
        
        fig1.update_layout(title = 'Actual vs. Fitted for {}'.format(sector_value),
                        xaxis_title = 'Date',
                        yaxis_title = 'Price ($)'
                        )
    else:
        tr1 = train[(train['topic'] == topic) & (train['model'] == model_value)]
        tr1['accurate'] = np.where(tr1['fitted_y'] == tr1['true_y'], 1, 0)
        tr2 = pd.DataFrame()
        tr2['accuracy'] = tr1.groupby('sector')['accurate'].mean()
        tr2.reset_index(inplace = True)

        fig1 = go.Figure(go.Bar(x = tr2['sector'], y = tr2['accuracy']
                        ))
        fig1.update_layout(title = 'Training accuracy rate using {} model'.format(model_value),
                        xaxis_title = 'Sector',
                        yaxis_title = 'Accuracy rate (%)'
                        )

    return fig1

if __name__ == '__main__': 
    app.run_server()
