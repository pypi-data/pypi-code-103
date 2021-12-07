import seaborn as sns
import matplotlib.pyplot as plt

from . import xproblem, xpd


def plot_feature_importances(folds, title=''):
    df = xproblem.calc_feature_importances(folds, flat=True)
    if df is None:
        return

    fis = df.groupby('feature_name')['feature_importance'].mean()
    df = xpd.x_sort_on_lookup(df, 'feature_name', fis, ascending=True)
    sns.catplot(data=df, y='feature_name', x='feature_importance')
    plt.xlim([0, None])
    if title:
        plt.title(title)

    plt.tight_layout()
    plt.show()

    return
