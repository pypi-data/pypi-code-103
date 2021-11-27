from fenics import plot as backend_plot
import os
import re

try:
    import matplotlib.pyplot as plt
except:
    pass

# Just use `debug(locals(), globals())` to drop into an interactive Python interpreter.
def debug(locals, globals, msg="(InteractiveConsole)"):
    import code

    code.interact(
        local=dict(globals, **locals),
        banner="\n" + msg,
        exitmsg="(Exiting InteractiveConsole)\n",
    )


## add_bool_arg() adds a boolean argument to the given argparse parser.
def add_bool_arg(parser, name, default=False, help=""):
    group = parser.add_mutually_exclusive_group(required=False)
    if default:
        group.add_argument("--no-" + name, dest=name, action="store_false", help=help)
    else:
        group.add_argument("--" + name, dest=name, action="store_true", help=help)
    parser.set_defaults(**{name: default})


## plot() plots the given function, adds a legend for the color gradient, and adds a new figure
#  so that subsequent plot() calls don't overwrite this plot. Pass newfig=False if you don't
#  want it to create a new figure afterwards.
FIGURE_SAVE_DIR = False
SHOW_FIGURES = True


def plot(u, **kwargs):
    newfig = kwargs.pop("newfig", True)
    show = kwargs.pop("noshow", SHOW_FIGURES)
    try:
        if hasattr(u, "shape") and (
            len(u.shape) == 2 or (len(u.shape) == 3 and u.shape[2] in (3, 4))
        ):
            # Plot matrix.
            f = plt.imshow(u, **kwargs)
        else:
            f = backend_plot(u, **kwargs)
        try:
            plt.colorbar(f)
        except:
            pass
        saveplot()
        if not show:
            plt.close()
        if newfig:
            plt.figure()
        return f
    except Exception as e:
        print("Warning: couldn't plot stuff:", e)


def saveplot(filename=None, **kwargs):
    savedir = kwargs.pop("savedir", FIGURE_SAVE_DIR)
    if savedir:
        fig = plt.gcf()
        os.makedirs(savedir, exist_ok=True)

        # Remove dots from filename so that matplotlib doesn't interpret it as image format.
        if filename is None:
            filename = fig.gca().get_title()
        filename = re.sub(r"\.", "_", filename)
        fig.savefig(savedir + "/" + filename)


## showplot() closes the current plot (unless you pass closefig=False) and then calls plt.show()
def showplot(closefig=True):
    try:
        if closefig:
            plt.close()
        plt.show()
    except Exception as e:
        print("Warning: couldn't show plot:", e)


def print_dir(o, private=False):
    d = dir(o)
    if not private:
        d = filter(lambda s: not s.startswith("_"), d)
    print("\n".join(d))
