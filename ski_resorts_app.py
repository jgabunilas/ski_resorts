from dash import Dash, dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template

import plotly.express as px
import pandas as pd
import numpy as np

# URL to apply bootstrap themes to dcc components
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.css"

# Load the figure template to apply themes to figures
load_figure_template("CERULEAN")

# Initiate application. External stylesheets must be called in order for the bootstrap grid layout to function
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CERULEAN, dbc_css],
    #     meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

# Import the dataframe and assign four new columns that, for each country, ranks the resorts by elevation, price, slope, and snow cannon count
# Modified to read .xlsx files. Requires openpyxl
resorts = (
    pd.read_excel("resorts.xlsx").assign(
        country_elevation_rank=lambda x: x.groupby("Country", as_index=False)[
            "Highest point"
        ].rank(ascending=False),
        country_price_rank=lambda x: x.groupby("Country", as_index=False)["Price"].rank(
            ascending=False
        ),
        country_slope_rank=lambda x: x.groupby("Country", as_index=False)[
            "Total slopes"
        ].rank(ascending=False),
        country_cannon_rank=lambda x: x.groupby("Country", as_index=False)[
            "Snow cannons"
        ].rank(ascending=False),
    )
    # Rename the columns to be more human-readable
    .rename(
        columns={
            "country_elevation_rank": "Elevation Rank",
            "country_price_rank": "Lift Ticket Price Rank",
            "country_cannon_rank": "Cannon Count Rank",
            "country_slope_rank": "Slope Count Rank",
        }
    )
)

# Create the layout for the application
app.layout = dbc.Container(
    [
        dcc.Tabs(
            id="tabs",
            children=[
                # Create the first tab which will hold the map
                dcc.Tab(
                    id="maptab",
                    label="Resort Finder",
                    children=[
                        html.Br(),
                        dbc.Row(html.H2(id="title")),
                        html.Br(),
                        dbc.Row(),
                        dbc.Row(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    children=[
                                        dbc.Card(
                                            children=[
                                                dcc.Markdown(
                                                    """
                            #### **Instructions**
                            **Use this application to find the perfect ski resort for you!**
                            **Select from the options below, then use the map on the right to find ski resorts that fit your selections. This map is global, so zoom out and explore!**                           
                            """,
                                                    className="dbc",
                                                ),
                                            ]
                                        ),
                                        html.Br(),
                                        dbc.Card(
                                            [
                                                dcc.Markdown(
                                                    """**Select Your Lift Ticket Price Limit in $USD**"""
                                                ),
                                                html.Br(),
                                                dcc.Slider(
                                                    id="price-select",
                                                    min=0,
                                                    max=150,
                                                    step=25,
                                                    value=150,
                                                    className="dbc",
                                                ),
                                            ]
                                        ),
                                        #                         dcc.RadioItems(
                                        #                             id="nightski",
                                        #                             options=["Has Night Skiing", "Does Not Have Night Skiing"],
                                        #                             value="Has Night Skiing",
                                        #                         ),
                                        html.Br(),
                                        dbc.Card(
                                            [
                                                dcc.Markdown(
                                                    """**Select Your Resort Options**"""
                                                ),
                                                dcc.Checklist(
                                                    id="resort-options",
                                                    options=[
                                                        # We will use the exact names of the columns as values for the checklist, as this will make the dataframe filtering logic much easier to handle below
                                                        {
                                                            "label": "Has Snow Park",
                                                            "value": "Snowparks",
                                                        },
                                                        {
                                                            "label": "Has Night Skiing",
                                                            "value": "Nightskiing",
                                                        },
                                                        {
                                                            "label": "Has Summer Skiing",
                                                            "value": "Summer skiing",
                                                        },
                                                    ],
                                                    value=[],
                                                    className="dbc",
                                                ),
                                            ]
                                        ),
                                        html.Br(),
                                        #                         html.H6(
                                        #                             "Instructions: Select from the options above, then use the map on the right to find ski resorts that fit your selections. This map is global, so zoom out and explore!",
                                        #                             style={"font-weight": "bold"},
                                        #                         ),
                                    ],
                                    width=3,
                                ),
                                #                 html.H2(id="debugging"),
                                dbc.Col(
                                    dcc.Graph(id="resort-map", responsive=False),
                                    width=9,
                                ),
                            ]
                        ),
                        dbc.Row(
                            "Disclaimer: This application should not be used to plan an actual ski vacation. Its sole purpose is to illustrate the use of the Plotly and Dash libraries. The underlying data may contain many inaccuracies.",
                            style={"text-align": "center", "color": "red"},
                        ),
                    ],
                    className="dbc",
                ),
                dcc.Tab(
                    label="Resort Rankings",
                    children=[
                        html.Br(),
                        dbc.Row(html.H2(id="title2")),
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    children=[
                                        dbc.Card(
                                            [
                                                dcc.Markdown(
                                                    """
                                                    #### **Instructions**  
                                                    Select a Continent, Country, and Metric for which to rank ski resorts. Then hover over the bar graph to see the rankings of resorts.
                                                    """,
                                                    className="dbc",
                                                ),
                                            ]
                                        ),
                                        html.Br(),
                                        # Continent selector
                                        dcc.Markdown("""Select a Continent"""),
                                        dcc.Dropdown(
                                            id="continent-select",
                                            options=resorts["Continent"].unique(),
                                            value="Europe",
                                            className="dbc",
                                        ),
                                        html.Br(),
                                        html.Br(),
                                        # Country selector
                                        dbc.Row(
                                            dcc.Markdown(
                                                """Select a Country""",
                                                className="dbc",
                                            )
                                        ),
                                        dbc.Row(
                                            dcc.Dropdown(
                                                id="country-options",
                                                value="Austria",
                                                className="dbc",
                                            ),
                                        ),
                                        html.Br(),
                                        html.Br(),
                                        # Metric selector
                                        dbc.Row(
                                            dcc.Markdown(
                                                """Select a Metric""",
                                                className="dbc",
                                            )
                                        ),
                                        dbc.Row(
                                            # For the metrics dropdown, the options will be the numeric columns of the dataframe, except for the first column where the rows are arbitrarily numbered
                                            dcc.Dropdown(
                                                id="metric-select",
                                                options=resorts.select_dtypes(
                                                    "number"
                                                ).columns[1:],
                                                value="Price",
                                                className="dbc",
                                            )
                                        ),
                                    ],
                                    width=3,
                                ),
                                dbc.Col(dbc.Row(dcc.Graph(id="resort-graph")), width=6),
                                dbc.Col(
                                    children=[
                                        dbc.Card(
                                            children=[
                                                dcc.Markdown(
                                                    """
                                            #### **Resort Report Card**  
                                            Mouse over the bar graph to see resort rankings.
                                            """,
                                                    className="dbc",
                                                ),
                                                dbc.Card(
                                                    dbc.Row(html.H5(id="resort-name")),
                                                ),
                                                dbc.Card(
                                                    children=[
                                                        dbc.Row(
                                                            html.P(id="elevation-rank")
                                                        ),
                                                    ]
                                                ),
                                                dbc.Card(
                                                    dbc.Row(html.P(id="price-rank")),
                                                ),
                                                dbc.Card(
                                                    dbc.Row(html.P(id="slope-rank")),
                                                ),
                                                dbc.Card(
                                                    dbc.Row(html.P(id="cannon-rank")),
                                                ),
                                            ]
                                        ),
                                        html.Br(),
                                        dbc.Card(
                                            dcc.Markdown(
                                                """
                                                #### **Ranking Guide**  
                                                **Elevation**: Rank 1 has the lowest elevation.  
                                                **Lift Ticket Price**: Rank 1 has the lowest price.  
                                                **Slope Count**: Rank 1 has the smallest number of slopes.  
                                                **Cannon Count**: Rank 1 has the smallest number of snow cannons.  
                                                
                                                """,
                                                className="dbc",
                                            )
                                        ),
                                    ],
                                    width=3,
                                ),
                            ]
                        ),
                        dbc.Row(
                            "Disclaimer: This application should not be used to plan an actual ski vacation. Its sole purpose is to illustrate the use of the Plotly and Dash libraries. The underlying data may contain many inaccuracies.",
                            style={"text-align": "center", "color": "red"},
                        ),
                    ],
                    className="dbc",
                ),
            ],
            className="dbc",
        )
    ]
)


@app.callback(
    # Outputs for the title and resort map
    Output("title", "children"),
    Output("resort-map", "figure"),
    #     Output("debugging", "children"),
    # Inputs from the Slider and the checklist elements
    Input("price-select", "value"),
    Input("resort-options", "value"),
    #     Input("nightski", "value"),
)
def global_resortmap(price, options):
    # Define the dataframe. First, we will pre-filter the dataframe so that only Price values that are lower than the selected slider price are considered
    df = resorts.loc[resorts["Price"] < price]

    # This logic filters the dataframe based on the options selected from the checklist
    # If all three options are selected, filter the dataframe so that results that have all three options are included as "Yes"
    if len(options) == 3:
        df = df.loc[
            (df["Nightskiing"] == "Yes")
            & (df["Snowparks"] == "Yes")
            & (df["Summer skiing"] == "Yes")
        ]
    # If two options are selected, filter the dataframe so that the two selected options are "Yes" for the included resorts. The included resorts may or may not have the unselected option.
    elif len(options) == 2:
        df = df.loc[(df[options[0]] == "Yes") & (df[options[1]] == "Yes")]
    # If only one option is selected, filter the dataframe so that the selected option is a "Yes" for the included resorts. The included resorts may or may not have the unselected options.
    elif len(options) == 1:
        df = df.loc[df[options[0]] == "Yes"]
    # If no options are selected, the dataframe will not be filtered any further and all resorts fitting the selected price limit will be included.

    # Construct the density_mapbox figure
    fig = px.density_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        z="Total slopes",
        center={"lat": 44.5, "lon": -103.5},
        mapbox_style="open-street-map",
        zoom=3.5,
        color_continuous_scale="Plotly3",
        hover_data=["Resort", "Price", "Snowparks", "Nightskiing", "Summer skiing"],
        width=1000,
        height=800,
    )

    # Create the dynamic title that will be passed back to the title element
    title = (
        f"Ski Resorts by Total Slopes with a Lift Ticket Price of Less Than ${price}"
    )
    return title, fig


# Callback function for selecting the countries available from the selected continent
@app.callback(
    Output("country-options", "options"),
    # Inputs from the Slider and the checklist elements
    Input("continent-select", "value"),
)
def continent_filter(continent):
    return resorts[resorts["Continent"] == continent]["Country"].unique()


# Callback function to create the bar graph based on the country and metric selections
@app.callback(
    Output("title2", "children"),
    Output("resort-graph", "figure"),
    Input("country-options", "value"),
    Input("metric-select", "value"),
)
def graph_generator(country, metric):
    if not country or not metric:
        raise PreventUpdate
    # Filter the dataframe to include only the data for the selection country, then sort the values on the selected metric. Finally, take only the top 10 values
    sorted_data = resorts[resorts["Country"] == country].sort_values(
        by=metric, ascending=False
    )[0:10]

    fig = px.bar(
        sorted_data,
        x="Resort",
        y=metric,
        height=750,
        # In addition to building the graph, we also want to pass the Resort name as custom_data back to the output. This will allow us to "select" the resort name when we hover over that resort's data in our bar graph
        custom_data=["Resort"],
    )
    title = f"Top {len(sorted_data)} Resort(s) in {country} by {metric}"
    return title, fig


# Callback function to modify the report card. We will pass in the hoverData from the resort graph (resort name in this case) and return the rankings for that resort.
@app.callback(
    Output("resort-name", "children"),
    Output("elevation-rank", "children"),
    Output("price-rank", "children"),
    Output("slope-rank", "children"),
    Output("cannon-rank", "children"),
    Input("resort-graph", "hoverData"),
)
def report_card(hoverData):
    if not hoverData:
        raise PreventUpdate
    # We need to access the resort name from the hoverData that was passed in. It's a standard json object.
    resort_name = hoverData["points"][0]["customdata"][0]
    # After obtaining the resort name, we can use that to pull the various ranks from the dataframe
    elev_rank = resorts.loc[resorts["Resort"] == resort_name]["Elevation Rank"].item()
    price_rank = resorts.loc[resorts["Resort"] == resort_name][
        "Lift Ticket Price Rank"
    ].item()
    slope_rank = resorts.loc[resorts["Resort"] == resort_name][
        "Slope Count Rank"
    ].item()
    cannon_rank = resorts.loc[resorts["Resort"] == resort_name][
        "Cannon Count Rank"
    ].item()
    resort_text = f"Resort Name: {resort_name}"
    elev_text = f"Elevation Rank: {elev_rank}"
    price_text = f"Lift Ticket Price Rank: {elev_rank}"
    slope_text = f"Slope Count Rank: {slope_rank}"
    cannon_text = f"Cannon Count Rank: {cannon_rank}"

    return resort_text, elev_text, price_text, slope_text, cannon_text


if __name__ == "__main__":
    app.run_server()
#     app.run_server(port=2381, jupyter_mode="external", debug=True)
