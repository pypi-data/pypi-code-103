"""
Run OrcaNet functionalities from command line.

"""
import warnings
import argparse
from orcanet import version

# imports involving tf moved inside functions for speed up


def train(directory, list_file=None, config_file=None, model_file=None, to_epoch=None):
    from orcanet.core import Organizer
    from orcanet.model_builder import ModelBuilder
    from orcanet.misc import find_file

    orga = Organizer(directory, list_file, config_file, tf_log_level=1)

    if orga.io.get_latest_epoch() is None:
        # Start of training
        print("Building new model")
        if model_file is None:
            model_file = find_file(directory, "model.toml")
        model = ModelBuilder(model_file).build(orga, verbose=False)
    else:
        model = None

    return orga.train_and_validate(model=model, to_epoch=to_epoch)


def _add_parser_train(subparsers):
    parser = subparsers.add_parser(
        "train",
        description="Train and validate a model.",
    )
    _add_common_args(parser)
    parser.add_argument(
        "--model_file",
        type=str,
        help="Path to toml model file. Will be used to build a model at "
        "the start of the training. Not needed to resume training. "
        "Default: Look for a file called 'model.toml' in the "
        "given OrcaNet directory.",
        default=None,
    )
    parser.add_argument(
        "--to_epoch",
        type=int,
        help="Train up to and including this epoch. Default: Train forever.",
        default=None,
    )
    parser.set_defaults(func=train)


def predict(directory, list_file=None, config_file=None, epoch=None, fileno=None):
    from orcanet.core import Organizer

    orga = Organizer(directory, list_file, config_file, tf_log_level=1)
    return orga.predict(epoch=epoch, fileno=fileno)[0]


def _add_paser_predict(subparsers):
    parser = subparsers.add_parser(
        "predict",
        description="Load a trained model and save its prediction on "
        "the predictions files to h5.",
    )
    _add_common_args(parser)
    parser.add_argument(
        "--epoch", type=int, help="Epoch of model to load. Default: best", default=None
    )
    parser.add_argument(
        "--fileno",
        type=int,
        help="Fileno of model to load. Default: best",
        default=None,
    )
    parser.set_defaults(func=predict)


def inference(directory, list_file=None, config_file=None, epoch=None, fileno=None):
    from orcanet.core import Organizer

    orga = Organizer(directory, list_file, config_file, tf_log_level=1)
    return orga.inference(epoch=epoch, fileno=fileno)


def _add_parser_inference(subparsers):
    parser = subparsers.add_parser(
        "inference",
        description="Load a trained model and save its prediction on the "
        "inference files to h5.",
    )
    _add_common_args(parser)
    parser.add_argument(
        "--epoch",
        type=int,
        help="Epoch of model to load. Default: best",
        default=None,
    )
    parser.add_argument(
        "--fileno",
        type=int,
        help="Fileno of model to load. Default: best",
        default=None,
    )
    parser.set_defaults(func=inference)


def inference_on_file(
    input_file,
    output_file=None,
    config_file=None,
    saved_model=None,
    directory=None,
    epoch=None,
    fileno=None,
):
    from orcanet.core import Organizer

    if directory is None and saved_model is None:
        raise ValueError("Either directory or saved_model is required!")
    elif directory is not None and saved_model is not None:
        warnings.warn("Warning: Ignoring given directory since saved_model was given.")
        directory = None

    if directory is not None:
        orga = Organizer(directory, config_file=config_file)
    else:
        orga = Organizer(".", config_file=config_file, discover_tomls=False)

    return orga.inference_on_file(
        input_file,
        output_file=output_file,
        saved_model=saved_model,
        epoch=epoch,
        fileno=fileno,
    )


def _add_parser_inf_on_file(subparsers):
    parser = subparsers.add_parser(
        "inference_on_file",
        description="Load a trained model and save its prediction on the given input "
        "file to the given output file.\n"
        "Useful for sharing a fully trained model, since the usual "
        "orcanet directory structure is not necessarily required.\n Can either load "
        "a saved model from a given path, or use the usual orcanet "
        "directory method of loading the best model of a training. ",
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to a DL file (i.e. output of OrcaSong) on which the inference should be done on.",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        help="Save output to an h5 file with this name. Default: auto-generate "
        "name and save in same directory as the input file.",
        default=None,
    )
    parser.add_argument(
        "--config_file",
        type=str,
        help="Path to toml config file. Default: None.",
        default=None,
    )
    parser.add_argument(
        "--saved_model",
        type=str,
        help="Optional path to a saved model, which will be used instead of "
        "loading the one with the given epoch/fileno. ",
        default=None,
    )
    parser.add_argument(
        "--directory",
        type=str,
        help="Path to an OrcaNet directory. Only relevant if saved_model is not given.",
        default=None,
    )
    parser.add_argument(
        "--epoch",
        type=int,
        help="Epoch of a model to load from the directory. Only relevant if saved_model is not given. "
        "Default: lowest val loss.",
        default=None,
    )
    parser.add_argument(
        "--fileno",
        type=int,
        help="File number of a model to load from the directory. Only relevant if saved_model is not given. "
        "Default: lowest val loss.",
        default=None,
    )
    parser.set_defaults(func=inference_on_file)


def _add_common_args(prsr):
    prsr.add_argument(
        "directory",
        help="Path to OrcaNet directory.",
    )
    prsr.add_argument(
        "--list_file",
        type=str,
        help="Path to toml list file. Default: Look for a file called "
        "'list.toml' in the given OrcaNet directory.",
        default=None,
    )
    prsr.add_argument(
        "--config_file",
        type=str,
        help="Path to toml config file. Default: Look for a file called "
        "'config.toml' in the given OrcaNet directory.",
        default=None,
    )


def _add_parser_summarize(subparsers):
    import orcanet.utilities.summarize_training as summarize_training

    parent_parser = summarize_training.get_parser()
    parser = subparsers.add_parser(
        "summarize",
        description=parent_parser.description,
        formatter_class=argparse.RawTextHelpFormatter,
        parents=[parent_parser],
        add_help=False,
    )
    parser.set_defaults(func=summarize_training.summarize)


def main():
    parser = argparse.ArgumentParser(
        prog="orcanet",
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=version)

    subparsers = parser.add_subparsers()
    _add_parser_train(subparsers)
    _add_paser_predict(subparsers)
    _add_parser_inference(subparsers)
    _add_parser_inf_on_file(subparsers)
    _add_parser_summarize(subparsers)

    kwargs = vars(parser.parse_args())
    func = kwargs.pop("func")
    func(**kwargs)
