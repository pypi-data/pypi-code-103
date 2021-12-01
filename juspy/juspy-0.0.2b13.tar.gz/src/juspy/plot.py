import pandas as pd
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

#default theme
plt.style.use('ggplot')
sns.set(context='notebook', style='darkgrid', palette='colorblind', font='sans-serif', font_scale=1, rc=None)
matplotlib.rcParams['figure.figsize'] =[8,8]
matplotlib.rcParams.update({'font.size': 15})
matplotlib.rcParams['font.family'] = 'sans-serif'


def confusion_matrix(cf_matrix, cmap_color="Blues"):
    group_names = ['True Neg','False Pos','False Neg','True Pos']

    group_counts = ["{0:0.0f}".format(value) for value in
                    cf_matrix.flatten()]

    group_percentages = ["{0:.2%}".format(value) for value in
                         cf_matrix.flatten()/np.sum(cf_matrix)]

    labels = [f"{v1}\n{v2}\n{v3}" for v1, v2, v3 in
              zip(group_names,group_counts,group_percentages)]

    labels = np.asarray(labels).reshape(cf_matrix.shape[0],cf_matrix.shape[1])

    sns.heatmap(cf_matrix/np.sum(cf_matrix), annot=labels,
                fmt='', cmap=cmap_color)

def piechart(data=None, plot_title=' '):
    if data is None:
        train = pd.read_csv('https://raw.githubusercontent.com/juspreet51/ml_templates/main/datasets/regression/black_friday/black_friday_train.csv')
        train.dtypes.value_counts().plot.pie(explode=[0.1,0.1,0.1],autopct='%1.2f%%',shadow=True)
        plt.title('type of our data')
    else:
        data.value_counts().plot.pie()
        plt.title(plot_title + " Distribution")