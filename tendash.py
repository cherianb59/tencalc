import dash
from dash import dcc, html, Input, Output ,dash_table
import dash_daq as daq
import dash_bootstrap_components as dbc
import tensim
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flask import Flask

server = Flask(__name__)
server.secret_key ='test'

app = dash.Dash(name = __name__, server = server, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server 
app.title = "Child Support Formula"
app.layout = dbc.Container(
    children=[
      header,
      dbc.Row( [ intro ])   ,
      dbc.Row( [ match_probability ])   ,      
      dbc.Row( [ match_inputs, par_a_inputs ,par_b_inputs, ])   ,
      dbc.Row( [ liability_chart ])   ,

    ]
)

header = html.Div(
        children=[
        html.P(children="👶", className="header-emoji"),
                html.H1(
                    children="Tennis Simulator", className="header-title"
                ),
                html.P(
                    children="Tennis simulator",
                    className="header-description",
                ),
        ],
        className="header",
      )
intro = dbc.Col(
      children=[ html.Div(id='introduction-container',
      children=[html.P(children="Enter the details of each of the players, player a will start serving"),]
      ), ]
      ,
      )
      
match_probability = dbc.Col(
      children=[ html.P(html.Div(id='match_probability-container')), ]
      ,
      )

def slider_range(min,max,step=1):
  sr = list(range(min,max+1,step))
  if sr[-1] != max: sr[-1] = max
  return(sr)

def make_tooltip(id,text):
    return dbc.Tooltip(
        text,
        target=id 
        ,placement="top")
  
match_inputs = dbc.Col(
      children=[
          
          html.Div(
              children=[
                  html.Div(children="Number of sets", className="menu-title"),
                  dcc.Slider(id="num_set_i", min=3,max=5,value=3,step=2,tooltip={"placement": "bottom", "always_visible": False},),
#TODO add sets
#TODO make player b serve first
              ]
          ),
        ],
      )
      
player_a_inputs = dbc.Col(
      children=[        
          html.Div(
              children=[
                  html.Div(children="Baseline probability of winning a point", className="menu-title",id="a_base_p_tt"),make_tooltip(id="a_base_p_tt",text="Baseline probability of winning a point"), dcc.Slider(id="a_base_p_i", min=0,max=1,value=0.5,tooltip={"placement": "bottom", "always_visible": False},),
                  html.Div(children="Point streak probability modifier", className="menu-title",id="a_point_streak_tt"),make_tooltip(id="a_point_streak_tt",text="Point streak probability modifier"), dcc.Slider(id="a_point_streak_i", min=-1,max=1,value=0,step=0.01,marks={ m: str(m) for m in slider_range(-1,1,0.2) },tooltip={"placement": "bottom", "always_visible": False},),                  
              ]
          ),
        ],
      )

player_b_inputs = dbc.Col(
      children=[        
          html.Div(
              children=[
                  html.Div(children="Baseline probability of winning a point", className="menu-title",id="b_base_p_tt"),make_tooltip(id="b_base_p_tt",text="Baseline probability of winning a point"), dcc.Slider(id="b_base_p_i", min=0,max=1,value=0.5,tooltip={"placement": "bottom", "always_visible": False},),
                  html.Div(children="Point streak probability modifier", className="menu-title",id="b_point_streak_tt"),make_tooltip(id="b_point_streak_tt",text="Point streak probability modifier"), dcc.Slider(id="b_point_streak_i", min=-1,max=1,value=0,step=0.01,marks={ m: str(m) for m in slider_range(-1,1,0.2) },tooltip={"placement": "bottom", "always_visible": False},),                  
              ]
          ),
        ],
      )
                
set_hist = html.Div(
            children=dcc.Graph(id="set-hist-chart", ),
            className="card",
        )
              

##TODO there should be an easier way to do this.
@app.callback(
    [Output('match_probability-container', 'children'),Output("set-distribution", "figure")],
    [dict(
    num_set = Input('num_set_i', 'value'),
    a_base_p = Input('a_base_p_i', 'value'),
    a_point_streak = Input('a_point_streak_i', 'value'),
    b_base_p = Input('b_base_p_i', 'value'),
    b_point_streak = Input('b_point_streak_i', 'value'),
    )
    ]
)
def simulate_matches(num_set , a_base_p , a_point_streak ,  b_base_p ,  b_point_streak ):
           
    # number of iterations
    sims = 100
    
    #iterate through matches
    results = []
    #numpy vectoristion is not much faster
    for i,income in enumerate(range(0,sims)):

      match = Match(1, i , player_profiles = [default_player_profile,rf_player_profile])
      match.run_match()
      results.append(match.result)
      del match              
    
    #
    match_statement = "Player A won {} out of {} matches ({}%)".format([sum(results),sims,float(sum(results))/sims])
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add traces (lines)
    fig.add_trace(
        go.Scatter(x=incomes, y=marginal, name="Marginal change in entitlement"),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(x=incomes, y=entitlements, # replace with your own data source
        name="Entitlement"), secondary_y=False,
    )
        
    fig.update_layout(
    template="simple_white",
    margin=dict(l=0, r=0, t=50, b=0),

    )
    # Add figure title
    fig.update_layout(title_text="Your pre-tax income vs how much you are entitled to")

    # Set x-axis title
    fig.update_xaxes(title_text="Your pre-tax income",tickprefix = '$', tickformat = ',.0f')

    # Set y-axes titles   
    fig.update_yaxes(title_text="How much the other parent owes you", tickprefix = '$', tickformat = ',.0f',secondary_y=False)
    
    fig.update_yaxes(title_text="", secondary_y=True)
    fig.update_yaxes(tickformat=",.0%", secondary_y=True)
    #fig.update_layout(yaxis_tickprefix = '$', yaxis_tickformat = ',.0f', secondary_y=True)
    
    fig.update_layout(
    legend=dict(
        x=0.7,
        y=0.9,
        bgcolor="rgba(0,0,0,0)",
        traceorder="normal",
        font=dict(
            family="sans-serif",
            size=12,
            color="black"
        ),
    )
  )

  )

    return([matches_statement,fig])

if __name__ == "__main__":
    app.run_server(debug=True,host='0.0.0.0', port=5000)