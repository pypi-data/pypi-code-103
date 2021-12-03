
import shap, numpy as np, re
from shap.explainers import *
from shap.explainers.other import *
from ._utils import raise_dataobject as rd
from collections.abc import Iterable
import copy
import matplotlib.pyplot as plt
plt.rcParams["figure.dpi"] = 600

flags = dict(
    sk=1,
    xgb=1,
    cat=1,
    lgb=1,
    inte=1,
    
    )

EXPLAINER = [
    Tree,
    GPUTree,
    Linear,
    Permutation,
    Partition,
    Sampling,
    Additive,
    Exact,
    Maple,
    TreeGain,
    TreeMaple,
    LimeTabular,
    Coefficent,
    Random, 
    ]

try:
    # expliciluy require this experimetal feature if using sklearn.ensembkle.Hist*
    from sklearn.experimental import enable_hist_gradient_boosting  # noqa
    from sklearn.neighbors import KNeighborsRegressor, RadiusNeighborsRegressor
    from sklearn.svm import SVR
    from sklearn.dummy import DummyRegressor
    from sklearn.ensemble import AdaBoostRegressor, BaggingRegressor, \
        ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor, \
        StackingRegressor, VotingRegressor, HistGradientBoostingRegressor
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.linear_model import PassiveAggressiveRegressor, SGDRegressor, LinearRegression, Lasso, ElasticNet
    from sklearn.neural_network import MLPRegressor
    from sklearn.tree import DecisionTreeRegressor, ExtraTreeRegressor
    from sklearn.neighbors import KNeighborsClassifier, RadiusNeighborsClassifier
    from sklearn.svm import SVC
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import AdaBoostClassifier, BaggingClassifier, \
        ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier, \
        StackingClassifier, VotingClassifier, HistGradientBoostingClassifier
    from sklearn.gaussian_process import GaussianProcessClassifier
    from sklearn.linear_model import LogisticRegression, PassiveAggressiveClassifier, \
        RidgeClassifier, SGDClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
except:
    flags["sk"] = 0


try:
    from catboost import CatBoostRegressor
    from catboost import CatBoostClassifier
except:
    flags["cat"] = 0

try:
    from interpret.glassbox import ExplainableBoostingRegressor
    from interpret.glassbox import ExplainableBoostingClassifier
except:
    flags["inte"] = 0

try:
    from lightgbm import LGBMRegressor
    from lightgbm import LGBMClassifier
except:
    flags["lgb"] = 0

try:
    from xgboost import XGBRegressor
    from xgboost import XGBClassifier
except:
    flags["xgb"] = 0

permutation_list = []
permutation_list_clf = []
permutation_list_reg = []
tree_list = []
linear_list = []
additive_list = []
if flags["sk"] == 1:
    permutation_list += [
        KNeighborsClassifier, 
        KNeighborsRegressor, 
        SVC, SVR, 
        DummyClassifier, 
        DummyRegressor,
        AdaBoostClassifier, 
        AdaBoostRegressor, 
        BaggingClassifier, 
        BaggingRegressor, 
        MLPClassifier, 
        MLPRegressor, 
        ]
    permutation_list_clf += [
        KNeighborsClassifier, 
        SVC,  
        DummyClassifier, 
        AdaBoostClassifier, 
        BaggingClassifier, 
        MLPClassifier, 
        ]
    permutation_list_reg += [
        KNeighborsRegressor, 
        SVR, 
        DummyRegressor,
        AdaBoostRegressor, 
        BaggingRegressor, 
        MLPRegressor, 
        ]
    tree_list += [
        ExtraTreeClassifier, 
        ExtraTreeRegressor, 
        GradientBoostingClassifier, 
        GradientBoostingRegressor, 
        RandomForestRegressor, 
        RandomForestClassifier, 
        HistGradientBoostingClassifier, 
        HistGradientBoostingRegressor, 
        DecisionTreeClassifier, 
        DecisionTreeRegressor,
        ExtraTreesClassifier,
        ExtraTreesRegressor
        ]
    linear_list += [
        LinearRegression,
        LogisticRegression, 
        PassiveAggressiveClassifier, 
        PassiveAggressiveRegressor, 
        RidgeClassifier, 
        SGDClassifier, 
        SGDRegressor,
        Lasso,
        ElasticNet
        ]
if flags["xgb"] == 1:
    tree_list += [
        XGBClassifier, 
        XGBRegressor
        ]
if flags["lgb"] == 1:
    tree_list += [
        LGBMClassifier, 
        LGBMRegressor
        ]
if flags["inte"] == 1:
    additive_list += [
        ExplainableBoostingClassifier, 
        ExplainableBoostingRegressor
        ]
if flags["cat"] == 1:
    tree_list += [
        CatBoostClassifier, 
        CatBoostRegressor
        ]


class Shap:
    
    def __init__(self):
        self.model = None
    
    def fit(self, model, dataobject, explainer="auto", feature_names=None, shap_kwargs=dict(), model_kwargs=dict()):
        rd(dataobject)
        self.model = model
        X = dataobject.X
        Y = dataobject.Y
        self.X = X
        self.Y = Y
        if explainer in EXPLAINER:
            Explainer = explainer
        else:
            Explainer = self.select_explainer()
        
        if feature_names is None:
        #     self.feature_names = np.array(range(X.shape[1]))
        # else:
            self.feature_names = dataobject.Xnames
        
        if Explainer != Linear:
            shap_kwargs.update(dict(feature_names=self.feature_names))
        if Explainer in tree_list:
            shap_kwargs.update(dict(feature_perturbation="tree_path_dependent"))
        
        try:
            if model == SVC:
                model_kwargs.update(dict(probability=True))
        except:
            pass
        
        # try:
        #     if model == CatBoostClassifier or model == CatBoostRegressor:
        #         self.explainer = Explainer(model(**model_kwargs).fit(X, Y), **shap_kwargs)
        # except:
        #     pass
        if model in permutation_list_reg:
            self.explainer = Explainer(model(**model_kwargs).fit(X, Y).predict, X, **shap_kwargs)
        elif model in permutation_list_clf:
            model = model(**model_kwargs).fit(X, Y)
            f = lambda x: model.predict_proba(x)[:,1]
            med = np.median(X, axis=0).reshape((1, X.shape[1]))
            self.explainer = Explainer(f, med, **shap_kwargs)
        elif model == CatBoostClassifier or model == CatBoostRegressor:
            self.explainer = Explainer(model(**model_kwargs).fit(X, Y), **shap_kwargs)
        else:
            self.explainer = Explainer(model(**model_kwargs).fit(X, Y), X, **shap_kwargs)
        if model in [RandomForestRegressor, RandomForestClassifier]:
            self.shap_values = self.explainer(X, check_additivity=False)
        else:
            self.shap_values = self.explainer(X)
        self.feature_importance = self.shap_values.abs.mean(0).values
        if len(self.feature_importance.shape) > 1: self.feature_importance = self.feature_importance[:, 0]
        self.feature_shap = np.array(sorted(enumerate(self.feature_importance), key=lambda x: x[1], reverse=True))
        self.feature_importance = self.feature_shap[:, 1]
        self.feature_index = self.feature_order = self.feature_shap[:, 0].astype(int)
        return self

    def transform(self, dataobject, max_f=None):
        rd(dataobject)
        if max_f is None:
            max_f = dataobject.X.shape[1]
        else:
            max_f = max_f - 1
        mask = self.feature_shap[:max_f+1, 0].astype(int)
        dataobject.X = dataobject.X[:, mask]
        dataobject.Xnames = dataobject.Xnames[mask]
        return dataobject

    def fit_transform(self, algo, dataobject, max_f=None):
        self.fit(algo, dataobject)
        return self.transform(dataobject, max_f)
    
    def select_explainer(self):
        
        if self.model in permutation_list:
            if self.X.shape[0] < 100 and self.X.shape[1] < 20:
                Explainer = Exact
            else:
                Explainer = Permutation
        elif self.model in linear_list:
            Explainer = Linear
        elif self.model in tree_list:
            Explainer = Tree
        elif self.model in additive_list:
            Explainer = Additive
        else:
            raise ValueError("No model matches with shap explainers")
        return Explainer
    
    @property
    def bar_data(self):
        return self.feature_names[self.feature_index], self.feature_importance
    
    @property
    def beeswarm_data(self):
        values = self.shap_values.values
        def _data():
            for i in self.feature_index:
                yield (self.feature_names[i], values[:, i], )
        return _data()
    
    def bar(self, max_display=10, xlabel="SHAP values", bar_color="#d62728", show=True, title=None):
        features = np.array(self.shap_values.data).reshape(-1, )[self.feature_order]
        feature_names = np.array(self.feature_names).reshape(-1, )[self.feature_order]
        values = np.array(self.feature_importance).reshape(-1, )
        feature_order = np.array(self.feature_order)
        
        if max_display is None:
            max_display = len(feature_names)
        num_features = min(max_display, len(values))
        max_display = min(max_display, num_features)
        
        orig_inds = [[i] for i in range(len(values))]
        orig_values = values.copy()
        
        feature_inds = feature_order[:max_display]
        y_pos = np.arange(len(feature_inds), 0, -1)
        feature_names_new = []
        for pos,inds in enumerate(orig_inds):
            if len(inds) == 1:
                feature_names_new.append(feature_names[inds[0]])
        feature_names = feature_names_new
        if num_features < len(values):
            num_cut = np.sum([len(orig_inds[feature_order[i]]) for i in range(num_features-1, len(values))])
            values[num_features-1] = np.sum([values[i] for i in range(num_features-1, len(values))], 0)
        
        yticklabels = []
        for i in range(len(feature_inds)):
            yticklabels.append(feature_names[i])
        if num_features < len(values):
            yticklabels[-1] = "Sum of %d other features" % num_cut
        
        fig, ax = plt.subplots(1, figsize=(8, max_display * 0.5 + 1.5))
        negative_values_present = np.sum(values[feature_order[:num_features]] < 0) > 0
        
        if negative_values_present:
            pl.axvline(0, 0, 1, color="#000000", linestyle="-", linewidth=1, zorder=1)
        
        bar_width = 0.7
        ypos_offset = - (( - 1 / 2) * bar_width + bar_width / 2)
        ax.barh(
            y_pos + ypos_offset, values[:max_display],
            bar_width, align='center',
            # color=[colors.blue_rgb if values[i, feature_inds[j]] <= 0 else colors.red_rgb for j in range(len(y_pos))],
            color = [ bar_color ],
            hatch=None,
            # edgecolor=(1,1,1,0.8)
        )
        
        xlen = ax.get_xlim()[1] - ax.get_xlim()[0]
        bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        width = bbox.width
        bbox_to_xscale = xlen/width
        
        ypos_offset = - ((0 - 1 / 2) * bar_width + bar_width / 2)
        for j in range(len(y_pos)):
            if values[j] < 0:
                ax.text(
                    values[j] - (5/72)*bbox_to_xscale, y_pos[j] + ypos_offset, self.format_value(values[j], '%+0.02f'),
                    horizontalalignment='right', verticalalignment='center', 
                    # color=colors.blue_rgb,
                    fontsize=12
                )
            else:
                ax.text(
                    values[j] + (5/72)*bbox_to_xscale, y_pos[j] + ypos_offset, self.format_value(values[j], '%+0.02f'),
                    horizontalalignment='left', verticalalignment='center', 
                    # color=colors.red_rgb,
                    fontsize=12
                )
        
        for i in range(num_features):
            ax.axhline(i+1, color="#888888", lw=0.5, dashes=(1, 5), zorder=-1)
            
        if features is not None:
            features = list(features)
            for i in range(len(features)):
                try:
                    if round(features[i]) == features[i]:
                        features[i] = int(features[i])
                except:
                    pass
        
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('none')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        if negative_values_present:
            ax.spines['left'].set_visible(False)
        ax.tick_params('x', labelsize=11)
        
        xmin,xmax = ax.get_xlim()
        ymin,ymax = ax.get_ylim()
        
        if negative_values_present:
            ax.set_xlim(xmin - (xmax-xmin)*0.05, xmax + (xmax-xmin)*0.05)
        else:
            ax.set_xlim(xmin, xmax + (xmax-xmin)*0.05)
        
        ax.set_xlabel(xlabel, fontsize=13)
        
        ax.set_yticks(list(y_pos))
        ax.set_yticklabels(yticklabels, fontsize=13)
        
        if show:
            plt.show()
    
    def format_value(self, s, format_str):
        """ Strips trailing zeros and uses a unicode minus sign.
        """
    
        if not issubclass(type(s), str):
            s = format_str % s
        s = re.sub(r'\.?0+$', '', s)
        if s[0] == "-":
            s = u"\u2212" + s[1:]
        return s
    
    def beeswarm(self, max_display=5, alpha=1, color_bar=True, color_bar_label="Feature value", xlabel="Shap Value", axis_color="#333333",show=True):
        values = self.shap_values.values.copy()
        features = self.shap_values.data
        feature_names = self.feature_names
        feature_order = self.feature_order
        
        if max_display is None:
            max_display = len(feature_names)
        num_features = min(max_display, len(feature_names))
        
        orig_inds = [[i] for i in range(len(feature_names))]
        orig_values = values.copy()
        
        feature_inds = feature_order[:max_display]
        y_pos = np.arange(len(feature_inds), 0, -1)
        feature_names_new = []
        for pos,inds in enumerate(orig_inds):
            if len(inds) == 1:
                feature_names_new.append(feature_names[inds[0]])
        feature_names = feature_names_new
        if num_features < len(values[0]):
            num_cut = np.sum([len(orig_inds[feature_order[i]]) for i in range(num_features-1, len(values[0]))])
            values[:,feature_order[num_features-1]] = np.sum([values[:,feature_order[i]] for i in range(num_features-1, len(values[0]))], 0)
        
        yticklabels = [feature_names[i] for i in feature_inds]
        if num_features < len(values[0]):
            yticklabels[-1] = "Sum of %d other features" % num_cut
        
        fig, ax = plt.subplots(1, figsize=(8, min(len(feature_order), max_display) * 0.4 + 1.5))
        ax.axvline(x=0, color="#999999", zorder=1)
        
        for pos, i in enumerate(reversed(feature_inds)):
            ax.axhline(y=pos, color="#cccccc", lw=0.5, dashes=(1, 5), zorder=-1)
            shaps = values[:, i]
            fvalues = None if features is None else features[:, i]
            # from sklearn.utils import check_random_state
            # rng = check_random_state(20210525)
            # inds = rng.permutation(len(shaps))
            inds = np.arange(len(shaps))
            np.random.shuffle(inds)
            if fvalues is not None:
                fvalues = fvalues[inds]
            shaps = shaps[inds]
            colored_feature = True
            try:
                fvalues = np.array(fvalues, dtype=np.float64)  # make sure this can be numeric
            except:
                colored_feature = False
            N = len(shaps)
            nbins = 100
            quant = np.round(nbins * (shaps - np.min(shaps)) / (np.max(shaps) - np.min(shaps) + 1e-8))
            inds = np.argsort(quant + np.random.randn(N) * 1e-6)
            layer = 0
            last_bin = -1
            ys = np.zeros(N)
            for ind in inds:
                if quant[ind] != last_bin:
                    layer = 0
                ys[ind] = np.ceil(layer / 2) * ((layer % 2) * 2 - 1)
                layer += 1
                last_bin = quant[ind]
            ys *= 0.9 * (0.4 / np.max(ys + 1))
            
            from shap.plots import colors
            color = colors.red_blue
            if features is not None:
                vmin = np.nanpercentile(fvalues, 5)
                vmax = np.nanpercentile(fvalues, 95)
                if vmin == vmax:
                    vmin = np.nanpercentile(fvalues, 1)
                    vmax = np.nanpercentile(fvalues, 99)
                    if vmin == vmax:
                        vmin = np.min(fvalues)
                        vmax = np.max(fvalues)
                if vmin > vmax:
                    vmin = vmax
                assert features.shape[0] == len(shaps), "Feature and SHAP matrices must have the same number of rows!"
                nan_mask = np.isnan(fvalues)
                ax.scatter(shaps[nan_mask], pos + ys[nan_mask], color="#777777", vmin=vmin, 
                           vmax=vmax, s=16, alpha=alpha, linewidth=0, zorder=3, rasterized=len(shaps) > 500)
                
                cvals = fvalues[np.invert(nan_mask)].astype(np.float64)
                cvals_imp = cvals.copy()
                cvals_imp[np.isnan(cvals)] = (vmin + vmax) / 2.0
                cvals[cvals_imp > vmax] = vmax
                cvals[cvals_imp < vmin] = vmin
                ax.scatter(shaps[np.invert(nan_mask)], pos + ys[np.invert(nan_mask)], 
                           cmap=color, vmin=vmin, vmax=vmax, s=16, c=cvals, alpha=alpha, 
                           linewidth=0, zorder=3, rasterized=len(shaps) > 500)
            else:
                ax.scatter(shaps, pos + ys, s=16, alpha=alpha, linewidth=0, zorder=3, 
                           color = color if colored_feature else "#777777", rasterized=len(shaps) > 500)
        
        if color_bar and features is not None:
            import matplotlib.cm as cm
            m = cm.ScalarMappable(cmap=color)
            m.set_array([0, 1])
            cb = plt.colorbar(m, ticks=[0, 1], aspect=1000)
            cb.set_ticklabels(["Low", "High"])
            cb.set_label(color_bar_label, size=12, labelpad=0)
            cb.ax.tick_params(labelsize=11, length=0)
            cb.set_alpha(1)
            cb.outline.set_visible(False)
            bbox = cb.ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
            cb.ax.set_aspect((bbox.height - 0.9) * 20)
            
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('none')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.tick_params(color=axis_color, labelcolor=axis_color)
        ax.set_yticks(range(len(feature_inds)))
        ax.set_yticklabels(reversed(yticklabels), fontsize=13)
        ax.tick_params('y', length=20, width=0.5, which='major')
        ax.tick_params('x', labelsize=11)
        ax.set_ylim(-1, len(feature_inds))
        ax.set_xlabel(xlabel, fontsize=13)
        if show:
            plt.show()
    
    # def bar(self, max_display=10, xlabel="SHAP values", textcolor=None, barcolor=None):
    #     from shap.plots import colors
    #     from shap.utils._general import format_value
    #     import seaborn as sns; sns.set()
                
    #     if isinstance(textcolor, Iterable) and not isinstance(textcolor, str):
    #         textcolor = textcolor
    #     elif isinstance(textcolor, str):
    #         textcolor = [textcolor, textcolor]
    #     else:
    #         textcolor = [colors.blue_rgb, colors.red_rgb]
    #     if isinstance(barcolor, Iterable) and not isinstance(barcolor, str):
    #         barcolor = barcolor
    #     elif isinstance(barcolor, str):
    #         barcolor = [barcolor, barcolor]
    #     else:
    #         barcolor = [colors.blue_rgb, colors.red_rgb]
        
    #     values = self.shap_values.abs.mean(0).values
    #     feature_names = copy.deepcopy(self.feature_names)
    #     show_features_index = self.feature_index[:max_display]
    #     values[show_features_index[-1]] = values[self.feature_index[max_display:]].sum()
    #     num_cut = len(self.feature_index) - max_display + 1
    #     # feature_names[show_features_index[-1]] = f"Sum of {num_cut} other features"
    #     show_values = values[show_features_index]
    #     if len(show_values.shape) > 1: show_values = show_values[:, 0]
    #     show_features = feature_names[show_features_index].tolist()
    #     if num_cut > 0:
    #         show_features[-1] = f"Sum of {num_cut} other features"
    #     if max_display > len(show_features_index):
    #         max_display = len(show_features_index)
    #     y_pos = np.arange(max_display, 0, -1)
    #     y_ticklabels = np.array(show_features)
        
    #     fig, ax = plt.subplots(1, figsize=(8, max_display * 0.5 + 1.5))
        
    #     negative_values_present = np.sum(show_values < 0) > 0
    #     if negative_values_present:
    #         ax.axvline(0, 0, 1, color="#000000", linestyle="-", linewidth=1, zorder=1)
        
    #     bar_width = 0.7
    #     ax.barh(
    #         y_pos, show_values,
    #         bar_width, align='center',
    #         color=[barcolor[0] if show_values[j] <= 0 else barcolor[1] for j in range(len(y_pos))],
    #         edgecolor=(1,1,1,0.8)
    #     )
        
    #     xlen = ax.get_xlim()[1] - ax.get_xlim()[0]
    #     bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    #     width = bbox.width
    #     bbox_to_xscale = xlen/width

    #     for j in range(len(y_pos)):
    #         if show_values[j] < 0:
    #             ax.text(
    #                 show_values[j] - (5/72)*bbox_to_xscale, y_pos[j], format_value(show_values[j], '%+0.02f'),
    #                 horizontalalignment='right', verticalalignment='center', color=textcolor[0],
    #                 fontsize=12
    #             )
    #         else:
    #             ax.text(
    #                 show_values[j] + (5/72)*bbox_to_xscale, y_pos[j], format_value(show_values[j], '%+0.02f'),
    #                 horizontalalignment='left', verticalalignment='center', color=textcolor[1],
    #                 fontsize=12
    #             )
        
    #     for i in range(max_display):
    #         ax.axhline(i+1, color="#888888", lw=0.5, dashes=(1, 5), zorder=-1)
        
    #     ax.xaxis.set_ticks_position('bottom')
    #     ax.yaxis.set_ticks_position('none')
    #     ax.spines['right'].set_visible(False)
    #     ax.spines['top'].set_visible(False)
    #     if negative_values_present:
    #         ax.spines['left'].set_visible(False)
    #     ax.tick_params('x', labelsize=11)
        
    #     xmin,xmax = ax.get_xlim()
    #     ymin,ymax = ax.get_ylim()
        
    #     if negative_values_present:
    #         ax.set_xlim(xmin - (xmax-xmin)*0.05, xmax + (xmax-xmin)*0.05)
    #     else:
    #         ax.set_xlim(xmin, xmax + (xmax-xmin)*0.05)
        
    #     ax.set_xlabel(xlabel, fontsize=13)
        
    #     ax.set_yticks(list(y_pos))
    #     ax.set_yticklabels(y_ticklabels.tolist(), fontsize=13)
        
    #     return fig, ax

    # def beeswarm(self, max_display=10, color=None, plot_size="auto", alpha=1, color_bar=True, color_bar_label="Feature value", axis_color="#333333", xlabel="SHAP value"):
    #     from shap.plots import colors
    #     from shap.plots._utils import convert_color
    #     from shap.utils import safe_isinstance
    #     shap_exp = self.shap_values
    #     base_values = shap_exp.base_values
    #     values = shap_exp.values
    #     features = shap_exp.data
    #     feature_names = shap_exp.feature_names
    #     order = self.feature_index
    #     if color is None:
    #         if features is not None:
    #             color = colors.red_blue
    #         else:
    #             color = colors.blue_rgb
    #     color = convert_color(color)
        
    #     num_features = values.shape[1]
    #     if max_display is None:
    #         max_display = len(feature_names)
    #     num_features = min(max_display, len(feature_names))
    #     orig_inds = [[i] for i in range(len(feature_names))]
    #     orig_values = values.copy()
        
    #     feature_inds = self.feature_order[:max_display]
    #     y_pos = np.arange(len(feature_inds), 0, -1)
        
    #     feature_names_new = []
    #     for pos,inds in enumerate(orig_inds):
    #         if len(inds) == 1:
    #             feature_names_new.append(feature_names[inds[0]])
    #         elif len(inds) <= 2:
    #             feature_names_new.append(" + ".join([feature_names[i] for i in inds]))
    #         else:
    #             max_ind = np.argmax(np.abs(orig_values).mean(0)[inds])
    #             feature_names_new.append(feature_names[inds[max_ind]] + " + %d other features" % (len(inds)-1))
    #     feature_names = feature_names_new
        
    #     if num_features < len(values[0]):
    #         num_cut = np.sum([len(orig_inds[self.feature_order[i]]) for i in range(num_features-1, len(values[0]))])
    #         values[:, self.feature_order[num_features-1]] = np.sum([values[:, self.feature_order[i]] for i in range(num_features-1, len(values[0]))], 0)
    #     yticklabels = [feature_names[i] for i in feature_inds]
    #     if num_features < len(values[0]):
    #         yticklabels[-1] = "Sum of %d other features" % num_cut
        
    #     row_height = 0.4
    #     fig, ax = plt.subplots(1)
    #     if plot_size == "auto":
    #         fig.set_size_inches(8, min(len(self.feature_order), max_display) * row_height + 1.5)
    #     elif type(plot_size) in (list, tuple):
    #         fig.set_size_inches(plot_size[0], plot_size[1])
    #     elif plot_size is not None:
    #         fig.set_size_inches(8, min(len(self.feature_order), max_display) * plot_size + 1.5)
    #     ax.axvline(x=0, color="#999999", zorder=-1)
        
    #     # make the beeswarm dots
    #     for pos, i in enumerate(reversed(feature_inds)):
    #         ax.axhline(y=pos, color="#cccccc", lw=0.5, dashes=(1, 5), zorder=-1)
    #         shaps = values[:, i]
    #         fvalues = None if features is None else features[:, i]
    #         inds = np.arange(len(shaps))
    #         np.random.shuffle(inds)
    #         if fvalues is not None:
    #             fvalues = fvalues[inds]
    #         shaps = shaps[inds]
    #         colored_feature = True
    #         try:
    #             fvalues = np.array(fvalues, dtype=np.float64)  # make sure this can be numeric
    #         except:
    #             colored_feature = False
    #         N = len(shaps)
    #         # hspacing = (np.max(shaps) - np.min(shaps)) / 200
    #         # curr_bin = []
    #         nbins = 100
    #         quant = np.round(nbins * (shaps - np.min(shaps)) / (np.max(shaps) - np.min(shaps) + 1e-8))
    #         inds = np.argsort(quant + np.random.randn(N) * 1e-6)
    #         layer = 0
    #         last_bin = -1
    #         ys = np.zeros(N)
    #         for ind in inds:
    #             if quant[ind] != last_bin:
    #                 layer = 0
    #             ys[ind] = np.ceil(layer / 2) * ((layer % 2) * 2 - 1)
    #             layer += 1
    #             last_bin = quant[ind]
    #         ys *= 0.9 * (row_height / np.max(ys + 1))
    
    #         if safe_isinstance(color, "matplotlib.colors.Colormap") and features is not None and colored_feature:
    #             # trim the color range, but prevent the color range from collapsing
    #             vmin = np.nanpercentile(fvalues, 5)
    #             vmax = np.nanpercentile(fvalues, 95)
    #             if vmin == vmax:
    #                 vmin = np.nanpercentile(fvalues, 1)
    #                 vmax = np.nanpercentile(fvalues, 99)
    #                 if vmin == vmax:
    #                     vmin = np.min(fvalues)
    #                     vmax = np.max(fvalues)
    #             if vmin > vmax: # fixes rare numerical precision issues
    #                 vmin = vmax
    
    #             assert features.shape[0] == len(shaps), "Feature and SHAP matrices must have the same number of rows!"
    
    #             # plot the nan fvalues in the interaction feature as grey
    #             nan_mask = np.isnan(fvalues)
    #             ax.scatter(shaps[nan_mask], pos + ys[nan_mask], color="#777777", vmin=vmin,
    #                         vmax=vmax, s=16, alpha=alpha, linewidth=0,
    #                         zorder=3, rasterized=len(shaps) > 500)
    
    #             # plot the non-nan fvalues colored by the trimmed feature value
    #             cvals = fvalues[np.invert(nan_mask)].astype(np.float64)
    #             cvals_imp = cvals.copy()
    #             cvals_imp[np.isnan(cvals)] = (vmin + vmax) / 2.0
    #             cvals[cvals_imp > vmax] = vmax
    #             cvals[cvals_imp < vmin] = vmin
    #             ax.scatter(shaps[np.invert(nan_mask)], pos + ys[np.invert(nan_mask)],
    #                         cmap=color, vmin=vmin, vmax=vmax, s=16,
    #                         c=cvals, alpha=alpha, linewidth=0,
    #                         zorder=3, rasterized=len(shaps) > 500)
    #         else:
    
    #             ax.scatter(shaps, pos + ys, s=16, alpha=alpha, linewidth=0, zorder=3,
    #                         color=color if colored_feature else "#777777", rasterized=len(shaps) > 500)
    #     # draw the color bar
    #     if safe_isinstance(color, "matplotlib.colors.Colormap") and color_bar and features is not None:
    #         import matplotlib.cm as cm
    #         m = cm.ScalarMappable(cmap=color)
    #         m.set_array([0, 1])
    #         cb = plt.colorbar(m, ticks=[0, 1], aspect=1000)
    #         cb.set_ticklabels(["Low", "High"])
    #         cb.set_label(color_bar_label, size=12, labelpad=0)
    #         cb.ax.tick_params(labelsize=11, length=0)
    #         cb.set_alpha(1)
    #         cb.outline.set_visible(False)
    #         bbox = cb.ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    #         cb.ax.set_aspect((bbox.height - 0.9) * 20)
    #     ax.xaxis.set_ticks_position('bottom')
    #     ax.yaxis.set_ticks_position('none')
    #     ax.spines['right'].set_visible(False)
    #     ax.spines['top'].set_visible(False)
    #     ax.spines['left'].set_visible(False)
    #     ax.tick_params(color=axis_color, labelcolor=axis_color)
    #     ax.set_yticks(range(len(feature_inds)))
    #     ax.set_yticklabels(reversed(yticklabels), fontsize=13)
    #     ax.tick_params('y', length=20, width=0.5, which='major')
    #     ax.tick_params('x', labelsize=11)
    #     ax.set_ylim(-1, len(feature_inds))
    #     ax.set_xlabel(xlabel, fontsize=13)
    #     return fig, ax

if __name__ == "__main__":
    from sklearn.datasets import load_boston, load_breast_cancer
    X, Y = load_breast_cancer(return_X_y=True); X=X[:50, :5]; Y=Y[:50]
    algo = SVC
    s = Shap().fit(algo, X, Y, feature_names=load_breast_cancer().feature_names, model_kwargs=dict())
    # s.feature_importance
    # s.feature_shap
    # s.feature_index
    # shap.plots.bar(s.shap_values)
    # s.bar(max_display=20)
    # s.shap_values
    # model = algo().fit(X, Y)
    # explainer = Tree(model)
    # explainer(X)
    
    # shap.plots.beeswarm(s.shap_values)
    # s.bar(max_display=20)
    # s.beeswarm()
