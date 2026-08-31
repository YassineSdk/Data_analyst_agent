import pandas as pd 
import plotly.express as px
from plotly.subplots import make_subplots 
from models import PlotState, AllPlots


TEMPLATE = "simple_white"


#plots

def create_barchart(df:pd.DataFrame,plot:PlotState):
    return px.bar(
        df,
        x=plot.x,
        y=plot.y,
        color=plot.color,
        title=plot.title,
        template=TEMPLATE
    )

def create_line(df:pd.DataFrame,plot:PlotState):
    return px.line(
        df,
        x=plot.x,
        y=plot.y,
        color=plot.color,
        title=plot.title,
        template=TEMPLATE
    )

def create_pie(df:pd.DataFrame,plot:PlotState):
    return px.bar(
        df,
        x=plot.x,
        y=plot.y,
        color=plot.color,
        title=plot.title,
        template=TEMPLATE
    )

PLOT_REGISTRY = {
    "bar":create_barchart,
    "line":create_line,
    "pie":create_pie
}


def Get_Plots(state) -> list:
    """
    Generate Plotly figures from the requested plot configurations.

    The function converts the executor result into a DataFrame,
    retrieves the requested plots, and maps each plot type to its
    corresponding plotting function through PLOT_REGISTRY.
    """

    execution = state["execution"]
    allplots = state["allplots"]

    df = pd.DataFrame(
        execution.result,
        columns=execution.columns
    )

    figures = []

    for plot in allplots.plots:

        plot_function = PLOT_REGISTRY.get(plot.plottype)

        if plot_function is None:
            raise ValueError(
                f"Unsupported plot type: {plot.plottype}"
            )

        fig = plot_function(df, plot)

        figures.append(fig)

    return figures



