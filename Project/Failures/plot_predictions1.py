from get_model_predictions import get_model_predictions
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib.collections as coll


def plot_predictions(fig, color_mag_ax, filters):
    # first need to get the model's predictions
    predictions = get_model_predictions()

    # Need filter info to tell what filters to use here
    if filters == "r":
        filter_idx = [0, 2]
    elif filters == "i":
        filter_idx = [1, 3]
    elif filters == "[3.6]":
        filter_idx = [3, 4]
    else:
        filter_idx = 0

    # # Make a colormap
    # my_cmap = colors.LinearSegmentedColormap.from_list('mycolors',['blue','red'])
    # sm = plt.cm.ScalarMappable(cmap=my_cmap, norm=plt.normalize(vmin=0, vmax=1))
    # # fake up the array of the scalar mappable. Urgh...
    # sm._A = []
    # plt.colorbar(sm)

    # Make x pair, for long horizontal line
    x = [-100, 100]

    # Initialize empty list for storing lines
    lines = []

    # zip things together to make a list passable to LineCollection
    for z in predictions:
        color = predictions[z][filter_idx[0]]-predictions[z][filter_idx[1]]
        y = [color, color] # Will be a horizontal line, which is what I want
        lines.append(zip(x, y))


    # plot these lines on the CMD
    #for z in predictions:
        # color_mag_ax.axhline(y=(predictions[z][filter_idx[0]]-predictions[z][filter_idx[1]]), linestyle="-",
        #                             linewidth=.5)

    z_lines = coll.LineCollection(lines)
    #z_lines.set_array(x)
    color_mag_ax.add_collection(z_lines)
    # fig = plt.gcf()
    #axcb = fig.colorbar(z_lines)


    # return the axes and figure
    return fig, color_mag_ax