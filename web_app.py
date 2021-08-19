import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import dash_table
from dash.dependencies import Input, Output
import config

hist_engine = create_engine("mysql+mysqlconnector://{user}:{pw}@{host}/{db}".format(user=config.user, pw=config.passwd, host=config.host, db=config.ETL_db_name))
anal_engine = create_engine("mysql+mysqlconnector://{user}:{pw}@{host}/{db}".format(user=config.user, pw=config.passwd, host=config.host, db=config.anal_db_name))

const_table_list = pd.read_sql("SHOW TABLES;", con=hist_engine)
constList= const_table_list[const_table_list.columns].squeeze()
anal_table_list = pd.read_sql("SHOW TABLES;", con=anal_engine)
analList= anal_table_list[anal_table_list.columns].squeeze()

displayType = [config.ETL_db_name, config.anal_db_name]


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Constituents and Analytics Dashboard'

app.layout = html.Div([
    html.Div(
            style={'padding': 30}
    ),
    html.H1(
            children='Constituents and Analytics Dashboard',
            style={
                'textAlign': 'center'
            }
    ),
    html.Label("Please choose between Historical or Analytical Database:",style={'fontSize':20, 'textAlign':'left'}),
    dcc.Dropdown(
        id='hist-anal',
        options=[{'label':i, 'value':i} for i in displayType],
        clearable=False
    ),
    html.Div(
            style={'padding': 30}
    ),
    html.Label("Please choose a table from the list:",style={'fontSize':20, 'textAlign':'left'}),
    dcc.Dropdown(
        id='constituents-names',
        options=[],
        clearable=False
    ),
    html.Div(
            style={'padding': 30}
    ),
    dash_table.DataTable(
        id='select-table',
        columns=[],
        data=[],
        style_as_list_view=True,
        style_header={
            'backgroundColor': 'white',
            'fontSize':15,
            'fontWeight': 'bold'},
        style_cell={                # ensure adequate header width when text is shorter than cell's text
            'minWidth': 95, 'maxWidth': 95, 'width': 80
        },
        style_cell_conditional=[    # align text columns to left. By default they are aligned to right
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['country', 'iso_alpha3']
        ],
        style_data={                # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto'
        }
    )
])



@app.callback(Output('constituents-names','options'),
              Input('hist-anal','value'))
def update_display_types(selected_type):
    if selected_type is None:
        return dash.no_update
    if selected_type == config.ETL_db_name:
        dropdown_list = [{'label':i, 'value':i} for i in constList]
    else:
        dropdown_list = [{'label':i, 'value':i} for i in analList]
    return dropdown_list



@app.callback(Output('select-table','columns'),
              Output('select-table','data'),
              Input('hist-anal','value'),
               Input('constituents-names','value'))
def update_tables(selected_type, selected_table):
    if selected_table is None:
        return dash.no_update
    else:
        if selected_type == config.ETL_db_name:
            try:
                table_data = pd.read_sql("select * from `" + str(selected_table) + "`;", con=hist_engine)
            except sqlalchemy.exc.ProgrammingError:
                table_data = pd.read_sql("select * from `" + str(selected_table) + "`;", con=anal_engine)
        else:
            try:
                table_data = pd.read_sql("select * from `" + str(selected_table) + "`;", con=anal_engine)
            except sqlalchemy.exc.ProgrammingError:
                table_data = pd.read_sql("select * from `" + str(selected_table) + "`;", con=hist_engine)

        column_layout = [{"name": i, "id": i} for i in table_data.columns]
        return column_layout, table_data.to_dict('records')


if __name__ == '__main__':
    app.run_server(port=8050,host='0.0.0.0')
