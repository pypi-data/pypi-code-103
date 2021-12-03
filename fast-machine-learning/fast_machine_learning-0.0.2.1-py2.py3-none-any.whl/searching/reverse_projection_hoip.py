import numpy as np, pandas as pd
from shap.plots.colors import red_blue
import matplotlib.pyplot as plt, os
plt.rcParams["figure.dpi"] = 300
from hyperopt import fmin, hp, tpe, STATUS_OK
from ..descriptors import HOIP
from ..data import DataObject
from pynput import keyboard
import sys



class ReverseProjectionHOIP(object):

    def __init__(self, decomposer, scaler, max_try=10, rounds=200, verbose=False, early_stop_rounds=150, early_stop_loss=9999, early_stop_dst=0.1):
        self.max_try = max_try
        self.rounds = rounds
        self.verbose = verbose
        self.early_stop_rounds = early_stop_rounds
        self.early_stop_loss = early_stop_loss
        self.early_stop_dst = early_stop_dst

        self.total_trials = []
        self.total_metrics = []

        if hasattr(decomposer, "__call__"):
            self.decomposer = decomposer()
        else:
            self.decomposer = decomposer

        if hasattr(scaler, "__call__"):
            self.scaler = scaler()
        else:
            self.scaler = scaler

        try:
            decomposer.transform
            decomposer.fit
            scaler.transform
            scaler.fit
        except AttributeError as e:
            print(e)

    def fit(self,
            votingmodel,
            formular_info,
            feature_names,
            expected_value=None,
            expected_range=None,
            criterion=0.05,
            site_counts=[2,2,2],
            ratio_digit=3,
            scatter_X=None,
            scatter_Y=None,
            dump_file_path=None,
            scatter_point_size=8,
            annotate=False,
            rect=None,
            hint=True,
            clicked_scatter_plot=dict(),
            searched_scatter_plot=dict(),
            rect_plot=dict(),
            plot_params=dict()
            ):

        if not hasattr(self.scaler, "mean_"):
            if scatter_X is None:
                raise Exception("scaler is not fitted, transfer fitting data to scatter_X")
            else:
                self.scaler.fit(scatter_X)

        scaled_X = self.scaler.transform(scatter_X)

        if not self.decomposer.n_components:
            if scatter_X is None:
                raise Exception("scaler is not fitted, transfer fitting data to scatter_X and scatter_Y")
            else:
                self.decomposer.fit(scaled_X)

        decomposed_X = self.decomposer.transform(scaled_X)

        if expected_value is not None and isinstance(expected_value, (int, float, )):
            self.expected_value = expected_value
            self.check_range = False
        elif expected_range is not None and len(expected_range) == 2:
            self.expected_value = (max(expected_range) + min(expected_range)) / 2
            self.check_range = (max(expected_range) - min(expected_range)) / 2

        self.scaled_X = scaled_X
        self.decomposed_X = decomposed_X
        self.scatter_Y = scatter_Y
        self.criterion = criterion
        self.scatter_X = scatter_X
        self.votingmodel = votingmodel
        self.formular_info = formular_info
        self.site_counts = site_counts
        self.feature_names = feature_names
        self.ratio_digit = ratio_digit
        self.dump_file_path = dump_file_path
        self.annotate = annotate
        self.rect = rect
        self.hint = hint

        default_clicked_scatter_plot = dict(
            c="red", s=10, linewidths=0.2, marker="*",
        )
        for i, j in clicked_scatter_plot.items():
            default_clicked_scatter_plot[i] = j

        default_searched_scatter_plot = dict(
            c="black", s=10, linewidths=0.2, marker="*",
        )
        for i, j in searched_scatter_plot.items():
            default_searched_scatter_plot[i] = j

        default_rect_plot = dict(
            linewidth = 1.5, edgecolor = "pink", facecolor = "none", linestyle = "--"
            )


        fig, ax, X_in_criterion = self.scatter(scatter_point_size=scatter_point_size, **plot_params)

        if self.rect is None:
            pass
        else:
            if self.rect == "auto":
                rect_xy = (X_in_criterion[:, 0].min(), X_in_criterion[:, 1].min())
                rect_height = X_in_criterion[:, 1].max() - X_in_criterion[:, 1].min()
                rect_width = X_in_criterion[:, 0].max() - X_in_criterion[:, 0].min()
            elif len(self.rect) == 3:
                rect_xy = self.rect[0]
                rect_width = self.rect[1]
                rect_height = self.rect[2]
            rect = plt.Rectangle(rect_xy, rect_width, rect_height, **default_rect_plot)
            ax.add_patch(rect)

        def on_press(key):
            if key == keyboard.Key.esc:
                sys.exit()
                plt.close()
                return False
            else:
                pass

        def get_vk(key):
            if isinstance(key, keyboard.Key):
                return key.value.vk
            elif isinstance(key, keyboard._win32.KeyCode):
                return key.vk
            else:
                return None

        def win32_event_filter(msg, data):
            if data.vkCode != get_vk(keyboard.Key.esc):
                listener.suppress_event()

        listener = keyboard.Listener(on_press=on_press, win32_event_filter=win32_event_filter)
        # listener.start()

        while True:

            self.total_trials = []
            self.total_metrics = []

            point = plt.ginput(1, timeout=-1)
            if point is None or len(point) == 0:
                break
            else:
                point = point[0]

            print(f"clicked point: {point[0], point[1]}")

            ax.scatter(point[0], point[1], **default_clicked_scatter_plot)
            fig.canvas.draw()

            new_pt = self.search(point)
            if new_pt is not None:
                print(f"searched point: {new_pt[0], new_pt[1]}, prediction: {self.best_metrics[0]}")
                ax.scatter(new_pt[0], new_pt[1], **default_searched_scatter_plot)

                if self.annotate:
                    ax.annotate("", xy=(new_pt[0], new_pt[1]), xytext=(point[0], point[1]), arrowprops=dict(arrowstyle="->", ls="--", lw=0.5, ec="#4B0082"))

                fig.canvas.draw()


            # if plt.waitforbuttonpress():
            #     break
        return self

    def scatter(self,
                xlabel="PCA 1",
                ylabel="PCA 2",
                title="Reverse Projection",
                xlim=None,
                ylim=None,
                scatter_point_size=8,
                edgecolor="yellow",
                linewidths=0.5
                ):
        fig, ax = plt.subplots()
        p = ax.scatter(self.decomposed_X[:, 0], self.decomposed_X[:, 1],
                       c=self.scatter_Y, cmap=red_blue, alpha=1, s=scatter_point_size)
        cb = plt.colorbar(p, ax=ax)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if self.hint:
            title += "\n press ESC to exit (hint=False to close this hint)"
        ax.set_title(title)
        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)

        X_in_criterion = self.decomposed_X[np.abs(self.scatter_Y - self.expected_value) < self.criterion]

        ax.scatter(
            X_in_criterion[:, 0], X_in_criterion[:, 1],
            marker="o", s=scatter_point_size, c="",
            edgecolor=[edgecolor], linewidths=linewidths,
        )

        return fig, ax, X_in_criterion

    def search(self, point):

        space = {}

        for site, site_info, site_count in zip(["A", "B", "C"], self.formular_info, self.site_counts):
            atom_info = {}
            ratio_info = {}
            if site == "C":
                max_ratio = 2.999
            else:
                max_ratio = 0.999
            for site_i in range(1, site_count + 1):
                atom_name = f"{site.lower()}{site_i}"
                ratio_name = f"r{atom_name}"
                atom_info.update({
                    atom_name: hp.choice(atom_name, site_info)
                })
                ratio_info.update({
                    ratio_name: hp.uniform(ratio_name, 0.001, max_ratio)
                })
            space[site] = {
                "atoms": atom_info,
                "ratios": ratio_info,
            }

        self.space = space

        for i in range(self.max_try):
            metrics, trials = self._search(point)
            if len(metrics) > 0:
                self.total_metrics.append(metrics)
                self.total_trials.append(trials)
                self.total_metrics_ = np.concatenate(self.total_metrics, axis=0)
                self.total_trials_ = np.concatenate(self.total_trials, axis=0)
                self.best_index = np.argmin(self.total_metrics_[:, -1])
                self.best_metrics = self.total_metrics_[self.best_index]
                self.best_trials = self.total_trials_[self.best_index]
                if (self.best_metrics[0] - self.expected_value) < self.criterion:
                    if self.best_metrics[-1] < self.early_stop_dst:
                        break
        if len(self.total_metrics) == 0:
            print("No result searched")
            return None
        return self.decomposer.transform(self.scaler.transform(self.best_trials[2:].reshape(1, -1)))[0, :2]

    def _search(self, point):

        if self.dump_file_path:
            if os.path.exists(self.dump_file_path):
                with open(self.dump_file_path, "r") as f:
                    existed_formulars = pd.read_csv(self.dump_file_path).index.values.tolist()
            else:
                with open(self.dump_file_path, "w") as f:
                    f.writelines(f"formular, Prediction, clicked_PCA1, clicked_PCA2, PCA1, PCA2, {', '.join(self.feature_names)}\n")
                    existed_formulars = []

        trials = []
        metrics = []
        def f(params):
            # if self.verbose:
            #     print(params)
            formular = []
            formular_name = ""
            for _, site_info in params.items():
                tmp = {}
                ratio_sum = sum(site_info["ratios"].values())
                for atom, ratio in zip(site_info["atoms"].values(), site_info["ratios"].values()):
                    ratio = ratio / ratio_sum
                    if _ == "C":
                        ratio *= 3
                    ratio = round(ratio, self.ratio_digit)
                    if atom in tmp.keys():
                        tmp[atom] += ratio
                    else:
                        tmp[atom] = ratio
                for atom, ratio in tmp.items():
                    formular_name += atom
                    if ratio != 1:
                        formular_name += str(ratio)
                formular.append(tmp)
            descriptor = HOIP().describe_formular(formular, True).loc[self.feature_names]
            x = descriptor.values.reshape(1, -1)
            x = self.decomposer.transform(self.scaler.transform(x))
            searching_point = x[0, :2]
            dst_error = ((point - searching_point) ** 2).sum()
            data = DataObject(X=descriptor.values.reshape(1, -1), Y=[0],
                              Xnames=descriptor.index.values, Yname=self.votingmodel.trainobjects[0].Yname[0])
            prediction = self.votingmodel.predict(data)[0]
            trials.append(
                [formular_name, prediction] + descriptor.values.tolist()
            )
            error = abs(self.expected_value - prediction) + dst_error
            metrics.append(
                [prediction, error, dst_error]
            )

            if abs(self.expected_value - prediction) < self.criterion:
                if dst_error < self.early_stop_dst:
                    if self.dump_file_path:
                        if formular_name in existed_formulars:
                            pass
                        else:
                            with open(self.dump_file_path, "a") as f:
                                f.writelines(f"{formular_name}, {prediction}, {point[0]}, {point[1]}, {searching_point[0]}, {searching_point[1]}, {', '.join(descriptor.astype(str).tolist())}\n")

            return {"loss": error, "status": STATUS_OK}
        fmin(fn=f, space=self.space, algo=tpe.suggest, max_evals=self.rounds, verbose=self.verbose, early_stop_fn=self.early_stop_fn)
        metrics = np.array(metrics)
        trials = np.array(trials)
        if self.check_range:
            criterion_range = self.check_range + self.criterion
        else:
            criterion_range = self.criterion
        mask = abs(metrics[:, 0] - self.expected_value) < criterion_range
        metrics = metrics[mask]
        trials = trials[mask]
        return metrics, trials

    def early_stop_fn(self, trials, *args, **wargs):
        
        losses = trials.losses()
        
        best_loss = trials.best_trial["result"]["loss"]
        
        stop = False
        
        if len(losses) > self.early_stop_rounds:
            if best_loss > self.early_stop_loss:
                stop = True
        
        return stop, dict(loss=trials.losses()[-1])