import numpy as np
import matplotlib.pyplot as plt

men_means = (163268, 133705, 29563)
women_means = (187049, 153421, 33628)

ind = np.arange(len(men_means))  # the x locations for the groups
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(ind - width/2, men_means, width, color='SkyBlue', label='01/01/2019')
rects2 = ax.bar(ind + width/2, women_means, width, color='IndianRed', label='02/01/2019')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Number of Messages')
ax.set_title('BGP Messages - DECIX Route Collector')
ax.set_xticks(ind)
ax.set_xticklabels(('Total', 'Announcement', 'Withdrawn'))
ax.legend()


def autolabel(rects, xpos='center'):
    """
    Attach a text label above each bar in *rects*, displaying its height.

    *xpos* indicates which side to place the text w.r.t. the center of
    the bar. It can be one of the following {'center', 'right', 'left'}.
    """

    xpos = xpos.lower()  # normalize the case of the parameter
    ha = {'center': 'center', 'right': 'left', 'left': 'right'}
    offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}  # x_txt = x + w*off

    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()*offset[xpos], 1.01*height,
                '{}'.format(height), ha=ha[xpos], va='bottom')


autolabel(rects1, "left")
autolabel(rects2, "right")

plt.show()
