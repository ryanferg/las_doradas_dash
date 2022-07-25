import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, ctx, State
import pandas as pd
import plotly.graph_objects as go
import os
import json


cur_dir = os.path.dirname(__file__)

passDF = pd.read_csv(os.path.join(cur_dir, "passDF.csv"))
passDF["text_str"] = passDF.apply(
    lambda x: f"xT = {x.xT_str}<br>{x.match_name}<br>{x.timestamp}<extra></extra>",
    axis=1,
)
gameDF = pd.read_csv(os.path.join(cur_dir, "gameDF.csv"))

player_aggDF = (
    passDF.groupby(["player_id", "position_id", "player_name"])
    .xT.agg(["mean", "sum"])
    .reset_index()
    .rename(columns={"mean": "mean_xt", "sum": "sum_xt", "player_id": "value"})
    .sort_values("sum_xt", ascending=False)
)
player_aggDF["label"] = (
    player_aggDF.player_name
    + player_aggDF.sum_xt.apply(lambda x: f" sum_xt = {x:.2f}")
    + player_aggDF.mean_xt.apply(lambda x: f" mu_xt = {x:.2f}")
)

all_agg_player_options = player_aggDF[["label", "value"]].to_dict(orient="records")

player_options = (
    passDF[["player_id", "player_name"]]
    .drop_duplicates()
    .rename(columns={"player_id": "value", "player_name": "label"})
    .to_dict(orient="records")
)

position_options = (
    passDF[["position_id", "position"]]
    .drop_duplicates()
    .rename(columns={"position_id": "value", "position": "label"})
    .to_dict(orient="records")
)

game_options = (
    gameDF[["match_id", "match_name"]]
    .drop_duplicates()
    .rename(columns={"match_id": "value", "match_name": "label"})
    .to_dict(orient="records")
)

team_options = (
    pd.concat(
        (
            gameDF[["home_team_id", "home_team_name"]].rename(
                columns={"home_team_id": "value", "home_team_name": "label"}
            ),
            gameDF[["away_team_id", "away_team_name"]].rename(
                columns={"away_team_id": "value", "away_team_name": "label"}
            ),
        ),
        axis=0,
    )
    .drop_duplicates()
    .to_dict(orient="records")
)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

position_dropdown = dcc.Dropdown(
    id="position_search_drop", options=position_options, placeholder="select position"
)

position_dropdown2 = dcc.Dropdown(
    id="position_search_drop2", options=position_options, placeholder="select position"
)

team_dropdown = dcc.Dropdown(
    id="team_search_drop", options=team_options, placeholder="select team"
)
game_dropdown = dcc.Dropdown(
    id="game_search_drop", options=game_options, placeholder="select game"
)
player_dropdown = dcc.Dropdown(
    id="player_search_drop", options=player_options, placeholder="select player"
)

player_dropdown2 = dcc.Dropdown(
    id="player_search_drop2",
    options=all_agg_player_options,
    placeholder="select player",
)
player_filter_chunk = dbc.Col(
    [
        dbc.Row([dbc.Col(team_dropdown), dbc.Col(position_dropdown)]),
        dbc.Row([dbc.Col(game_dropdown), dbc.Col(player_dropdown)]),
    ]
)

position_filter_chunk = dbc.Col(
    [
        dbc.Row(dbc.Col(position_dropdown2)),
        dbc.Row(dbc.Col(player_dropdown2)),
    ]
)

filter_tab = dbc.Col(
    dbc.Tabs(
        [
            dbc.Tab(
                children=player_filter_chunk, label="By Player", tab_id="by_player_tab"
            ),
            dbc.Tab(
                children=position_filter_chunk, label="By Pos", tab_id="by_pos_tab"
            ),
        ],
        id="tabs",
    )
)

button_chunk = dbc.Col(
    [
        dbc.Row(dbc.Button("Clear", id="clear_butt")),
        dbc.Row(dbc.Button("Plot", id="plot_butt", disabled=True, color="success")),
    ],
    width={"size": 2, "order": "last"},
    align="end",
)


center = c_x, c_y = 60, 40
field_shapes = [
    dict(type="rect", x0=0, y0=0, x1=120, y1=80, layer="below"),
    dict(type="rect", x0=0, y0=18, x1=18, y1=62, layer="below"),
    dict(type="rect", x0=102, y0=18, x1=120, y1=62, layer="below"),
    dict(type="rect", x0=0, y0=30, x1=6, y1=50, layer="below"),
    dict(type="rect", x0=114, y0=30, x1=120, y1=50, layer="below"),
    dict(type="rect", x0=-2, y0=35, x1=0, y1=44, layer="below"),
    dict(type="rect", x0=120, y0=35, x1=122, y1=44, layer="below"),
    dict(type="circle", x0=50, y0=30, x1=70, y1=50, layer="below"),
    dict(type="line", x0=60, y0=0, x1=60, y1=80, layer="below"),
    dict(type="path", path="M 18,32 C 25,35 25,45 18,48", layer="below"),
    dict(type="path", path="M 102,32 C 95,35 95,45 102,48", layer="below"),
]

xaxis = go.layout.XAxis(range=[-5, 125], showgrid=False, zeroline=False)
yaxis = go.layout.YAxis(
    range=[85, -5], showgrid=False, zeroline=False, scaleanchor="x", scaleratio=1
)
margin = go.layout.Margin(l=0, r=0, b=3, t=50, pad=10)
layout = go.Layout(
    shapes=field_shapes, xaxis=xaxis, yaxis=yaxis, margin=margin, width=900, height=600
)

fig = go.Figure(layout=layout)

plot_body = dbc.Col(
    html.Div(
        [
            dcc.Graph(
                id="figure",
                figure=fig,
                config=dict(fillFrame=True),
                style={"width": "90vh"},
            )
        ],
    ),
    width={"size": 9, "offset": 1, "order": "last"},
)


plot_settings_accord = dbc.Accordion(
    [
        dbc.AccordionItem(
            dbc.Row(
                [
                    dbc.Label("XT range"),
                    dcc.RangeSlider(
                        -0.25, 0.25, 0.05, value=[-0.25, 0.25], id="xt_range"
                    ),
                ]
            ),
            title="Plot Settings",
        )
    ],
    start_collapsed=True,
    flush=True,
)


modal_360 = dbc.Modal(
    [dbc.ModalTitle(id="modal_head"), dbc.ModalBody("hithere", id="modal_body")],
    id="modal_360",
    size="xl",
    is_open=False,
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                filter_tab,
                button_chunk,
            ]
        ),
        dbc.Row(plot_settings_accord),
        dbc.Row(plot_body),
        modal_360,
    ]
)


@app.callback(
    Output("position_search_drop", "options"),
    Output("position_search_drop", "value"),
    Output("team_search_drop", "options"),
    Output("team_search_drop", "value"),
    Output("game_search_drop", "options"),
    Output("game_search_drop", "value"),
    Output("player_search_drop", "options"),
    Output("player_search_drop", "value"),
    Output("plot_butt", "disabled"),
    Output("position_search_drop2", "options"),
    Output("position_search_drop2", "value"),
    Output("player_search_drop2", "options"),
    Output("player_search_drop2", "value"),
    [
        Input("player_search_drop", "value"),
        Input("game_search_drop", "value"),
        Input("position_search_drop", "value"),
        Input("team_search_drop", "value"),
        Input("clear_butt", "n_clicks"),
        Input("player_search_drop2", "value"),
        Input("position_search_drop2", "value"),
        State("tabs", "active_tab"),
    ],
    prevent_initial_call=True,
)
def setup_options_filter(
    player_id,
    game_id,
    position_id,
    team_id,
    clear_butt,
    player_id2,
    position_id2,
    active_tab,
):
    print((str(ctx.triggered[0]) + ", " + str(ctx.triggered_id)))
    pos_opts = dash.no_update
    pos_value = dash.no_update
    team_opts = dash.no_update
    team_value = dash.no_update
    game_opts = dash.no_update
    game_value = dash.no_update
    player_opts = dash.no_update
    player_value = dash.no_update
    plot_butt_disabled = dash.no_update
    pos_opts2 = dash.no_update
    pos_value2 = dash.no_update
    player_opts2 = dash.no_update
    player_value2 = dash.no_update

    if active_tab == "by_player_tab":
        bool_idx = passDF.player_id > 0
        if player_id is not None:
            bool_idx = bool_idx & (passDF.player_id == player_id)
        if position_id is not None:
            bool_idx = bool_idx & (passDF.position_id == position_id)
        if game_id is not None:
            bool_idx = bool_idx & (passDF.match_id == game_id)
        if team_id is not None:
            bool_idx = bool_idx & (passDF.team_id == team_id)
        player_games = passDF.loc[bool_idx, "match_id"].unique()
        game_opts = list(filter(lambda x: x.get("value") in player_games, game_options))
        player_opts = (
            passDF.loc[bool_idx, ["player_id", "player_name"]]
            .drop_duplicates()
            .rename(columns={"player_id": "value", "player_name": "label"})
            .to_dict(orient="records")
        )
        all_pos = passDF.loc[bool_idx, "position_id"].unique()
        pos_opts = list(filter(lambda x: x.get("value") in all_pos, position_options))
        team_opts = list(
            filter(
                lambda x: x.get("value") in passDF.loc[bool_idx, "team_id"].unique(),
                team_options,
            )
        )
        if len(game_opts) == 1:
            game_value = game_opts[0].get("value")
        else:
            game_value = None
        if len(player_opts) == 1:
            player_value = player_opts[0].get("value")
        else:
            player_value = None
        if len(pos_opts) == 1:
            pos_value = pos_opts[0].get("value")
        else:
            pos_value = None
        if len(team_opts) == 1:
            team_value = team_opts[0].get("value")
        else:
            team_value = None
        pos_opts2 = position_options
        pos_value2 = None
        player_opts2 = all_agg_player_options
        player_value2 = None
    if active_tab == "by_pos_tab":
        bool_idx = player_aggDF.value > 0
        if player_id2 is not None:
            bool_idx = bool_idx & (player_aggDF.value == player_id2)
        if position_id2:
            bool_idx = bool_idx & (player_aggDF.position_id == position_id2)
        if ctx.triggered_id != "clear_butt":
            pos_opts2 = list(
                filter(
                    lambda x: x.get("value")
                    in player_aggDF.loc[bool_idx, "position_id"].unique(),
                    position_options,
                )
            )
            if len(pos_opts2) == 1:
                pos_value2 = pos_opts2[0].get("value")
            player_opts2 = player_aggDF.loc[bool_idx, ["value", "label"]].to_dict(
                orient="records"
            )
            if len(player_opts2) == 1:
                player_value2 = player_opts2[0].get("value")

    if ctx.triggered_id == "clear_butt":
        pos_opts = position_options
        pos_value = None
        team_opts = team_options
        team_value = None
        game_opts = game_options
        game_value = None
        player_opts = player_options
        player_value = None
        pos_opts2 = pos_opts
        pos_value2 = None
        player_opts2 = all_agg_player_options
        player_value2 = None
    if (player_value is not None) | (player_value2 is not None):
        plot_butt_disabled = False
    else:
        plot_butt_disabled = True
    return (
        pos_opts,
        pos_value,
        team_opts,
        team_value,
        game_opts,
        game_value,
        player_opts,
        player_value,
        plot_butt_disabled,
        pos_opts2,
        pos_value2,
        player_opts2,
        player_value2,
    )


@app.callback(
    Output("modal_360", "is_open"),
    Output("modal_body", "children"),
    Output("modal_head", "children"),
    Input("figure", "clickData"),
    prevent_initial_call=True,
)
def make_modal(clickData):
    print(clickData)
    if not clickData:
        return False, None
    sel_id = clickData["points"][0]["customdata"]
    dat360 = json.loads(
        passDF.loc[passDF.id == sel_id, "freeze_frame"]
        .values[0]
        .replace("'", '"')
        .replace("True", "true")
        .replace("False", "false")
    )
    selDF = passDF.loc[passDF.id == sel_id]
    df360 = pd.DataFrame(dat360)
    df360["location_x"] = df360.location.apply(lambda x: x[0])
    df360["location_y"] = df360.location.apply(lambda x: x[-1])
    df360 = df360.loc[df360.actor == False]
    if (
        selDF.team_id.values[0]
        == gameDF.loc[
            gameDF.match_id == selDF.match_id.values[0], "home_team_id"
        ].values[0]
    ):
        same_team = gameDF.loc[
            gameDF.match_id == selDF.match_id.values[0], "home_team_name"
        ].values[0]
        other_team = gameDF.loc[
            gameDF.match_id == selDF.match_id.values[0], "away_team_name"
        ].values[0]
    else:
        other_team = gameDF.loc[
            gameDF.match_id == selDF.match_id.values[0], "home_team_name"
        ].values[0]
        same_team = gameDF.loc[
            gameDF.match_id == selDF.match_id.values[0], "away_team_name"
        ].values[0]
    fig = go.Figure(layout=layout)
    arrow_list = [
        dict(
            x=x_end,
            y=y_end,
            xref="x",
            yref="y",
            text="",
            showarrow=True,
            axref="x",
            ayref="y",
            ax=x_start,
            ay=y_start,
            arrowhead=3,
            arrowwidth=1.5,
        )
        for x_start, y_start, x_end, y_end in selDF[
            ["location_x", "location_y", "end_location_x", "end_location_y"]
        ].values
    ]
    fig.add_trace(
        go.Scatter(
            x=selDF.location_x,
            y=selDF.location_y,
            text=selDF.text_str,
            customdata=selDF.id,
            hovertemplate="%{text}<extra></extra>",
            mode="markers",
            name=selDF.player_name.values[0],
            marker_size=10,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df360.loc[df360.teammate == False].location_x,
            y=df360.loc[df360.teammate == False].location_y,
            marker_color="red",
            mode="markers",
            name=other_team,
            marker_size=10,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df360.loc[df360.teammate == True].location_x,
            y=df360.loc[df360.teammate == True].location_y,
            marker_color="green",
            mode="markers",
            name=same_team,
            marker_size=10,
        )
    )
    fig.update_layout(annotations=arrow_list)
    return (
        True,
        dcc.Graph(figure=fig),
        f"{selDF.player_name.values[0]} in {selDF.match_name.values[0]} at {selDF.timestamp.values[0]}",
    )


@app.callback(
    Output("figure", "figure"),
    [
        Input("plot_butt", "n_clicks"),
        Input("clear_butt", "n_clicks"),
        State("player_search_drop", "value"),
        State("game_search_drop", "value"),
        State("position_search_drop", "value"),
        State("team_search_drop", "value"),
        State("tabs", "active_tab"),
        State("player_search_drop2", "value"),
        Input("xt_range", "value"),
    ],
    prevent_initial_call=True,
)
def output_plot(
    button_click,
    clear_click,
    player_id,
    game_id,
    position_id,
    team_id,
    active_tab,
    player_id2,
    xt_range,
):
    if (player_id is None) & (player_id2 is None):
        return dash.no_update
    if active_tab == "by_player_tab":
        bool_idx = passDF.player_id > 0
        if player_id is not None:
            bool_idx = bool_idx & (passDF.player_id == player_id)
        if position_id is not None:
            bool_idx = bool_idx & (passDF.position_id == position_id)
        if game_id is not None:
            bool_idx = bool_idx & (passDF.match_id == game_id)
        if team_id is not None:
            bool_idx = bool_idx & (passDF.team_id == team_id)
    else:
        bool_idx = passDF.player_id == player_id2
    fig = go.Figure(layout=layout)
    if (ctx.triggered_id == "plot_butt") | (ctx.triggered_id == "xt_range"):
        range_bool = passDF.xT.between(*xt_range)
        selDF = passDF.loc[bool_idx & range_bool].dropna(subset=["end_location_x"])
        arrow_list = [
            dict(
                x=x_end,
                y=y_end,
                xref="x",
                yref="y",
                text="",
                showarrow=True,
                axref="x",
                ayref="y",
                ax=x_start,
                ay=y_start,
                arrowhead=3,
                arrowwidth=1.5,
            )
            for x_start, y_start, x_end, y_end in selDF[
                ["location_x", "location_y", "end_location_x", "end_location_y"]
            ].values
        ]
        fig.add_trace(
            go.Scatter(
                x=selDF.location_x,
                y=selDF.location_y,
                text=selDF.text_str,
                customdata=selDF.id,
                hovertemplate="%{text}<extra></extra>",
                mode="markers",
                marker_size=10,
            )
        )
        fig.update_layout(annotations=arrow_list)
    else:
        fig = go.Figure(layout=layout)
    return fig


if __name__ == "__main__":
    app.run(port=8118, debug=True, dev_tools_hot_reload=False)
