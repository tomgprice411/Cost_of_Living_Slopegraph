import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots



#import datafile
df = pd.read_csv("cost_of_living.csv")


################################
#### Create Graph Variables ####
################################

MARGIN = {"t": 30, "r": 400, "b": 90, "l": 40}
LINE_COLOUR = "#798286" #"#A6ACAF"
PRIMARY_COLOUR = "#076b78" #"#1F618D"
FONT_COLOR = "#6d7578"
FONT_SIZE = 18
TITLE_COLOUR = "#303436"
TITLE_SIZE = 22
PLOTBG_COLOUR = "#c9cdcf"  #"white"
SECONDARY_COLOUR = "#0cbdd4" #"#3498DB"
WIDTH_SINGLE = 1280
HEIGHT_SINGLE = 720

############################
#### Transform the Data ####
############################

#we will only compare London and New York, so filter on these values
df = df.loc[(df["city"].isin(["London", "New York"])) & (df["country"].isin(["United States", "United Kingdom"]))].copy()


#currently the variables x1 to x55 are columns, so we need to transform the data set so we have variable name and price as the two columns
df_2 = df.melt(id_vars = ["city"], value_vars = ["x{}".format(i) for i in range(1, 56)], value_name = "price", var_name = "item")

#filter on just the variables that I want to keep 
# check this link to find out the actual name of each variable https://www.kaggle.com/datasets/mvieira101/global-cost-of-living?select=cost-of-living.csv
df_2 = df_2.loc[df_2["item"].isin(["x1", "x3", "x4", "x5", "x6", "x7"
                                # "x9", "x10", "x11", "x13", "x14", "x15", "x16", "x20", "x23", "x24", "x25", "x26", 
                                # "x36", "x38", "x39", "x40", "x41", 
                                # "x44", "x45", "x46", "x47", 
                                # "x48", "x49", "x50", "x51"
                                ])].copy()

#rename the the variables to their actual item name (found in above link)
df_2["item"] = df_2["item"].map(dict(
                x1 = "Meal (Inexpensive Restaurant)", x3 = "Meal (McDonalds)", x4 = "Domestic Beer", x5 = "Imported Beer", x6 = "Cappuccino" , x7 = "Coke", #restaurant items
                # x9 = "Milk", x10 = "Bread", x11 = "Rice", x13 = "Cheese", x14 = "Chicken Fillets", x15 = "Beef", x16 = "Apples", x20 = "Potatoes", x23 = "Water", x24 = "Wine", x25 = "Domestic Beer", x26 = "Imported Beer", #supermarket items
                # x36 = "Bills", x38 = "Internet", x39 = "Gym", x40 = "Tennis Court Rental", x41 = "Cinema", #House costs
                # x44 = "Jeans", x45 = "Dress", x46 = "Nike Trainers", x47 = "Leather Shoes", # clothing
                # x48 = "Apartment (1 bed) City Centre", x49 = "Apartment (1 bed) Outside City Centre", x50 = "Apartment (3 bed) City Centre", x51 = "Apartment (3 bed) Outside City Centre" #rent
                ))

# we want to highlight the meal and beer items because we'll add commentary on these later on
df_2["colour"] = LINE_COLOUR
df_2.loc[df_2["item"] == "Meal (Inexpensive Restaurant)", "colour"] = PRIMARY_COLOUR
df_2.loc[df_2["item"] == "Imported Beer", "colour"] = SECONDARY_COLOUR

df_2["line_size"] = 2
df_2.loc[df_2["item"].isin(["Meal (Inexpensive Restaurant)", "Imported Beer"]), "line_size"] = 4

df_2["marker_size"] = 2
df_2.loc[df_2["item"].isin(["Meal (Inexpensive Restaurant)", "Imported Beer"]), "marker_size"] = 12

### create a dataframe to hold the price variances between London and New York, these will be used for the annotations in the slopegraph
df_annotations = df_2.pivot(index = ["item", "colour"], columns = "city", values = "price").reset_index()
df_annotations["Var"] = (df_annotations["London"] - df_annotations["New York"]) / df_annotations["New York"]

# the price of a McDonals and an imported beer in NY are both $10, so the y positions of the annotations will need to be adjusted so they don't overlap
df_annotations["NY_ypos"] = df_annotations["New York"]
df_annotations.loc[df_annotations["item"] == "Imported Beer", "NY_ypos"] = 9.5
df_annotations.loc[df_annotations["item"] == "Meal (McDonalds)", "NY_ypos"] = 10.5






#########################
### Create Slopegraph ###
#########################


#create an empty graph object called fig
fig = go.Figure()

#add a line on the scatter plot for each item
for item in df_2["item"].unique():
    df_plot = df_2.loc[df_2["item"] == item].copy()
    fig.add_trace(go.Scatter(x = df_plot["city"], y = df_plot["price"], 
                            marker = dict(color = df_plot["colour"].iloc[0], size = df_plot["marker_size"].iloc[0]),
                            line = dict(width = df_plot["line_size"].iloc[0])
                            ))

#customise the layout of the scatter plot
fig.update_layout(plot_bgcolor = PLOTBG_COLOUR, 
                    paper_bgcolor = PLOTBG_COLOUR,
                    showlegend = False,
                    margin = MARGIN,
                    font = dict(color = FONT_COLOR, size = FONT_SIZE),
                    yaxis = dict(visible = False, range = [0,30]),
                    xaxis = dict(gridcolor = PLOTBG_COLOUR)
                    )

#add annotations to the scatter plot
for item, lon_price, ny_price, var, y_pos, colour in zip(df_annotations["item"], df_annotations["London"], df_annotations["New York"], df_annotations["Var"], df_annotations["NY_ypos"], df_annotations["colour"]):
    fig.add_annotation(text = "  {}: ${:.2f} ({:.0%})".format(item, lon_price, var),
                        xref = "x",
                        yref = "y",
                        x = "London",
                        y = lon_price,
                        align = "left",
                        xanchor = "left",
                        showarrow = False,
                        font = dict(color = colour))

    fig.add_annotation(text = "${:.2f}  ".format(ny_price),
                        xref = "x",
                        yref = "y",
                        x = "New York",
                        y = y_pos,
                        align = "right",
                        xanchor = "right",
                        showarrow = False,
                        font = dict(color = colour))

# the original x axis line extends across the graph, but I want the it to only go between the labels New York and London
#so I've added it in manually
fig.add_shape(type = "line",
                x0 = "New York",
                x1 = "London",
                y0 = 0.1,
                y1 = 0.1,
                line = dict(color = LINE_COLOUR)
                )


#add the title
fig.add_annotation(text = "Restaurant Prices are Cheaper in London than New York Across All Items",
                    xref = "paper",
                    yref = "paper",
                    x = -0.005,
                    y = 1,
                    align = "left",
                    xanchor = "left",
                    showarrow = False,
                    font = dict(color = TITLE_COLOUR, size = TITLE_SIZE))


#add some commentary about what the graph is showing
fig.add_annotation(text = 'The biggest difference in absolute <br>price is from having an inexpensive <br>restauarant meal. <b><span style = "color: '+ PRIMARY_COLOUR +'">London is ' + '&#36;' + "7 <br>cheaper at " + '&#36;' + "18</span></b>.", 
                    xref = "paper",
                    yref = "y",
                    x = 1.03,
                    y = 18.4,
                    align = "left",
                    xanchor = "left",
                    yanchor = "top",
                    showarrow = False)

fig.add_annotation(text = 'The largest difference in price <br>percentage at restaurants is from <br>imported beer. <b><span style = "color: '+ SECONDARY_COLOUR +'">London is 40% <br>cheaper at ' + '&#36;' + "6</b></span>.", 
                    xref = "paper",
                    yref = "y",
                    x = 1.03,
                    y = 6.4,
                    align = "left",
                    xanchor = "left",
                    yanchor = "top",
                    showarrow = False)

# add creator and data source info
fig.add_annotation(text = 'Created by: Tom Price <br>Data source: "Cost of Living" dataset on Kaggle', 
                    xref = "paper",
                    yref = "paper",
                    x = -0.005,
                    y = -0.13,
                    align = "left",
                    xanchor = "left",
                    yanchor = "bottom",
                    showarrow = False,
                    font = dict(size = FONT_SIZE - 4))



fig.write_image("slopegraph.png", scale = 1, width = WIDTH_SINGLE, height = HEIGHT_SINGLE)





