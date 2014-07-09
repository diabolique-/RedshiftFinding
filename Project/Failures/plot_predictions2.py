from get_model_predictions import get_model_predictions


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

    # Just going to plot points for now
    for z in predictions:
        color_mag_ax.scatter(predictions[z][filter_idx[1]],  # magnitude on x axis
                             predictions[z][filter_idx[0]] - predictions[z][filter_idx[1]])  # color on y axis

    # return the axes and figure
    return fig, color_mag_ax
