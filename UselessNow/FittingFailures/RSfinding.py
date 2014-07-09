import matplotlib.pyplot as plt


def plot_rs_histogram(redshifts, rs_numbers, title):
    """
    Very sketchy at best. Don't trust this function.
    :param image:
    :return:
    """





    fig = plt.figure(figsize=(8, 5))
    histo_ax = fig.add_subplot(1, 1, 1)
    histo_ax.bar(redshifts, rs_numbers, width=0.01)
    histo_ax.set_title(title)
    histo_ax.set_xlabel("Redshift")
    histo_ax.set_ylabel("Galaxies in Red Sequence")

    return fig