# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['zenml',
 'zenml.artifact_stores',
 'zenml.artifacts',
 'zenml.cli',
 'zenml.config',
 'zenml.core',
 'zenml.integrations',
 'zenml.integrations.airflow',
 'zenml.integrations.airflow.orchestrators',
 'zenml.integrations.beam',
 'zenml.integrations.beam.materializers',
 'zenml.integrations.beam.orchestrators',
 'zenml.integrations.dash',
 'zenml.integrations.dash.visualizers',
 'zenml.integrations.facets',
 'zenml.integrations.facets.visualizers',
 'zenml.integrations.gcp',
 'zenml.integrations.gcp.artifact_stores',
 'zenml.integrations.gcp.io',
 'zenml.integrations.gcp.metadata_stores',
 'zenml.integrations.graphviz',
 'zenml.integrations.graphviz.visualizers',
 'zenml.integrations.plotly',
 'zenml.integrations.plotly.visualizers',
 'zenml.integrations.pytorch',
 'zenml.integrations.pytorch.materializers',
 'zenml.integrations.pytorch_lightning',
 'zenml.integrations.pytorch_lightning.materializers',
 'zenml.integrations.sklearn',
 'zenml.integrations.sklearn.materializers',
 'zenml.integrations.tensorflow',
 'zenml.integrations.tensorflow.materializers',
 'zenml.integrations.tensorflow.steps',
 'zenml.io',
 'zenml.materializers',
 'zenml.metadata',
 'zenml.orchestrators',
 'zenml.orchestrators.local',
 'zenml.pipelines',
 'zenml.post_execution',
 'zenml.stacks',
 'zenml.steps',
 'zenml.steps.step_interfaces',
 'zenml.utils',
 'zenml.visualizers']

package_data = \
{'': ['*']}

install_requires = \
['analytics-python>=1.4.0,<2.0.0',
 'apache-beam>=2.30.0,<3.0.0',
 'click>=8.0.1,<9.0.0',
 'distro>=1.6.0,<2.0.0',
 'gitpython>=3.1.18,<4.0.0',
 'ml-pipelines-sdk>=1.3.0,<2.0.0',
 'pandas>=1.1.5,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'pyyaml>=5.4.1,<6.0.0',
 'tabulate>=0.8.9,<0.9.0']

entry_points = \
{'console_scripts': ['zenml = zenml.cli.cli:cli']}

setup_kwargs = {
    'name': 'zenml',
    'version': '0.5.4',
    'description': 'ZenML: Write production-ready ML code.',
    'long_description': '<div align="center">\n\n<img src="https://zenml.io/assets/social/github.svg">\n\n<p align="center">\n  <a href="https://zenml.io">Website</a> •\n  <a href="https://docs.zenml.io">Docs</a> •\n  <a href="https://zenml.io/roadmap">Roadmap</a> •\n  <a href="https://zenml.io/discussion">Vote For Features</a> •\n  <a href="https://zenml.io/slack-invite/">Join Slack</a>\n  <a href="https://zenml.io/newsletter/">Newsletter</a>\n</p>\n\n[![PyPI - ZenML Version](https://img.shields.io/pypi/v/zenml.svg?label=pip&logo=PyPI&logoColor=white)](https://pypi.org/project/zenml/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/zenml)](https://pypi.org/project/zenml/)\n[![PyPI Status](https://pepy.tech/badge/zenml)](https://pepy.tech/project/zenml)\n![GitHub](https://img.shields.io/github/license/zenml-io/zenml)\n[![Codecov](https://codecov.io/gh/zenml-io/zenml/branch/main/graph/badge.svg)](https://codecov.io/gh/zenml-io/zenml)\n[![Interrogate](docs/interrogate.svg)](https://interrogate.readthedocs.io/en/latest/)\n![Main Workflow Tests](https://github.com/zenml-io/zenml/actions/workflows/main.yml/badge.svg)\n\n</div>\n\n<div align="center"> Join our\n<a href="https://zenml.io/slack-invite" target="_blank">\n    <img width="25" src="https://cdn3.iconfinder.com/data/icons/logos-and-brands-adobe/512/306_Slack-512.png" alt="Slack"/>\n<b>Slack Community</b> </a> and become part of the ZenML family\n</div>\n<div align="center"> Give us a \n    <img width="25" src="https://cdn.iconscout.com/icon/free/png-256/github-153-675523.png" alt="Slack"/>\n<b>GitHub star</b> to show your love\n</div>\n<div align="center"> \n    <b>NEW: </b> <a href="https://zenml.io/discussion" target="_blank"><img width="25" src="https://cdn1.iconfinder.com/data/icons/social-17/48/like-512.png" alt="Vote"/><b> Vote</b></a> on the next ZenML features \n</div>\n\n## What is ZenML?\n\n\nBefore: Sam struggles to productionalize ML |  After: Sam finds Zen in her MLOps with ZenML\n:-------------------------:|:-------------------------:\n![Sam is frustrated](docs/readme/sam_frustrated.jpg)  |  ![Sam is happy](docs/readme/sam_zen_mode.jpg)\n\n\n\n**ZenML** is an extensible, open-source MLOps framework to create production-ready machine learning pipelines. It has a simple, flexible syntax,\nis cloud and tool agnostic, and has interfaces/abstractions that are catered towards ML workflows.\n\nAt its core, ZenML pipelines execute ML-specific workflows from sourcing data to splitting, preprocessing, training, all the way to the evaluation of\nresults and even serving. There are many built-in batteries as things progress in ML development. ZenML is not here to replace the great tools that\nsolve these individual problems. Rather, it integrates natively with many popular ML tooling, and gives standard abstraction to write your workflows.\n\n## Why do I need it?\n\n_**Ichi Wa Zen, Zen Wa Ichi.**_\n\nWe built ZenML because we could not find an easy framework that translates the patterns observed in the research phase with Jupyter notebooks into a production-ready ML environment.\nZenML follows the paradigm of [`Pipelines As Experiments` (PaE)](https://docs.zenml.io/why-zenml), meaning ZenML pipelines are designed to be written early on the development lifecycle, where the users can explore their\npipelines as they develop towards production.\n\nBy using ZenML at the early stages of development, you get the following features:\n\n- **Reproducibility** of training and inference workflows.\n- Managing ML **metadata**, including versioning data, code, and models.\n- Getting an **overview** of your ML development, with a reliable link between training and deployment.\n- Maintaining **comparability** between ML models.\n- **Scaling** ML training/inference to large datasets.\n- Retaining code **quality** alongside development velocity.\n- **Reusing** code/data and reducing waste.\n- Keeping up with the **ML tooling landscape** with standard abstractions and interfaces.\n\n## Who is it for?\n\nZenML is built for ML practitioners who are ramping up their ML workflows towards production.\nIt is created for data science / machine learning teams that are engaged in not only training models, but also putting them out in production. Production can mean many things, but examples would be:\n\n- If you are using a model to generate analysis periodically for any business process.\n- If you are using models as a software service to serve predictions and are consistently improving the model over time.\n- If you are trying to understand patterns using machine learning for any business process.\n\nIn all of the above, there will be team that is engaged with creating, deploying, managing and improving the entire process. You always want the best results, the best models, and the most robust and reliable results. This is where ZenML can help.\nIn terms of user persona, ZenML is created for producers of the models. This role is classically known as \'data scientist\' in the industry and can range from research-minded individuals to more engineering-driven people. The goal of ZenML is to enable these practitioners to own their models until deployment and beyond.\n\n## Roadmap and Community\n\nZenML is being built in public. The [roadmap](https://zenml.io/roadmap) is a regularly updated source of truth for the ZenML community to understand where the product is going in the short, medium, and long term.\n\nZenML is managed by a [core team](https://zenml.io/team) of developers that are responsible for making key decisions and incorporating feedback from the community. The team oversee\'s feedback via various channels, but you can directly influence the roadmap as follows:\n\n- Vote on your most wanted feature on the [Discussion board](https://zenml.io/discussion).\n- Create a [Feature Request](https://github.com/zenml-io/zenml/issues/new/choose) in the [GitHub board](https://github.com/zenml-io/zenml/issues).\n- Start a thread in the [Slack channel](https://zenml.io/slack-invite).\n\n## Quickstart\n\nThe quickest way to get started is to create a simple pipeline.\n\n#### Step 0: Installation\n\nZenML is available for easy installation into your environment via PyPI:\n\n```bash\npip install zenml\n```\n\nAlternatively, if you’re feeling brave, feel free to install the bleeding edge:\n**NOTE:** Do so on your own risk, no guarantees given!\n\n```bash\npip install git+https://github.com/zenml-io/zenml.git@main --upgrade\n```\n\n#### Step 1: Initialize a ZenML repo from within a git repo\n\n```bash\ngit init\nzenml init\n```\n\n#### Step 2: Assemble, run, and evaluate your pipeline locally\n\n```python\nimport numpy as np\nimport tensorflow as tf\n\nfrom zenml.pipelines import pipeline\nfrom zenml.steps import step\nfrom zenml.steps.step_output import Output\n\n\n@step\ndef importer() -> Output(\n    X_train=np.ndarray, y_train=np.ndarray, X_test=np.ndarray, y_test=np.ndarray\n):\n    """Download the MNIST data store it as numpy arrays."""\n    (X_train, y_train), (X_test, y_test) = tf.keras.datasets.mnist.load_data()\n    return X_train, y_train, X_test, y_test\n\n\n@step\ndef trainer(\n    X_train: np.ndarray,\n    y_train: np.ndarray,\n) -> tf.keras.Model:\n    """A simple Keras Model to train on the data."""\n    model = tf.keras.Sequential()\n    model.add(tf.keras.layers.Flatten(input_shape=(28, 28)))\n    model.add(tf.keras.layers.Dense(10))\n\n    model.compile(\n        optimizer=tf.keras.optimizers.Adam(0.001),\n        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),\n        metrics=["accuracy"],\n    )\n\n    model.fit(X_train, y_train)\n\n    # write model\n    return model\n\n\n@step\ndef evaluator(\n    X_test: np.ndarray,\n    y_test: np.ndarray,\n    model: tf.keras.Model,\n) -> float:\n    """Calculate the accuracy on the test set"""\n    test_acc = model.evaluate(X_test, y_test, verbose=2)\n    return test_acc\n\n\n@pipeline\ndef mnist_pipeline(\n    importer,\n    trainer,\n    evaluator,\n):\n    """Links all the steps together in a pipeline"""\n    X_train, y_train, X_test, y_test = importer()\n    model = trainer(X_train=X_train, y_train=y_train)\n    evaluator(X_test=X_test, y_test=y_test, model=model)\n\npipeline = mnist_pipeline(\n    importer=importer(),\n    trainer=trainer(),\n    evaluator=evaluator(),\n)\npipeline.run()\n```\n\n## Leverage powerful integrations\nOnce code is organized into a ZenML pipeline, you can supercharge your ML development with powerful integrations and\non multiple [MLOps stacks](https://docs.zenml.io/core-concepts).\n\n### View statistics\n\n```python\n# See statistics of train and eval [COMING SOON]\nfrom zenml.core.repo import Repository\nfrom zenml.integrations.facets.visualizers.facet_statistics_visualizer import (\n  FacetStatisticsVisualizer,\n)\n\nrepo = Repository()\npipe = repo.get_pipelines()[-1]\nimporter_outputs = pipe.runs[-1].get_step(name="importer")\nFacetStatisticsVisualizer().visualize(importer_outputs)\n```\n\n![Boston Housing Dataset Statistics Visualization](docs/book/.gitbook/assets/statistics_boston_housing.png)\n\n### Use Caching across (Pipelines As) Experiments\n\nZenML makes sure for every pipeline you can trust that:\n\n✅ Code is versioned   \n✅ Data is versioned  \n✅ Models are versioned  \n✅ Configurations are versioned\n\nYou can utilize caching to help iterate quickly through ML experiments.\n\n\n### Work locally but switch seamlessly to the cloud\n\nSwitching from local experiments to cloud-based pipelines doesn\'t need to be complex.\n\n```\n[COMING SOON]\n```\n\n![Development and production stack](docs/book/.gitbook/assets/stacks.png)\n\n\n\n\n### Automatically detect schema\n\n```python\n[COMING SOON]\n```\n\n![Automatic schema dection](docs/schema.png)\n\n\n### Evaluate the model using built-in evaluators\n\n```python\n[COMING SOON]\n```\n\n\n![ZenML built-in pipeline comparison](docs/tensorboard_inline.png)\n\n\n### Compare training pipelines\n\n```python\n[COMING SOON]\n```\n\n![ZenML built-in pipeline comparison](docs/compare.png)\n\n### Distribute preprocessing to the cloud\n\nLeverage distributed compute powered by [Apache Beam](https://beam.apache.org/):\n\n```python\n[COMING SOON]\n```\n\n![ZenML distributed processing](docs/zenml_distribute.png)\n\n\n### Deploy models automatically\n\nAutomatically deploy each model with powerful Deployment integrations like [Ray](https://docs.ray.io/en/latest/serve/index.html).\n\n```python\n[COMING SOON]\n```\n\nThe best part is that ZenML is extensible easily, and can be molded to your use-case. You can create your own custom logic or create a PR and contribute to the ZenML community, so that everyone can benefit.\n\n## Release 0.5.0 and what lies ahead\n\nThe current release is bare bones (as it is a complete rewrite).\nWe are missing some basic features which used to be part of ZenML 0.3.8 (the previous release):\n\n- Standard interfaces for `TrainingPipeline`.\n- Individual step interfaces like `PreprocessorStep`, `TrainerStep`, `DeployerStep` etc. need to be rewritten from within the new paradigm. They should\n  be included in the non-RC version of this release.\n- A proper production setup with an orchestrator like Airflow.\n- A post-execution workflow to analyze and inspect pipeline runs.\n- The concept of `Backends` will evolve into a simple mechanism of transitioning individual steps into different runners.\n- Support for `KubernetesOrchestrator`, `KubeflowOrchestrator`, `GCPOrchestrator` and `AWSOrchestrator` are also planned.\n- Dependency management including Docker support is planned.\n\nHowever, bare with us: Adding those features back in should be relatively faster as we now have a solid foundation to build on. Look out for the next email!\n\n## Contributing\n\nWe would love to receive your contributions! Check our [Contributing Guide](CONTRIBUTING.md) for more details on how best to contribute.\n\n<br>\n\n![Repobeats analytics image](https://repobeats.axiom.co/api/embed/635c57b743efe649cadceba6a2e6a956663f96dd.svg "Repobeats analytics image")\n\n## Copyright\n\nZenML is distributed under the terms of the Apache License Version 2.0. A complete version of the license is available in the [LICENSE.md](LICENSE.md) in this repository.\n\nAny contribution made to this project will be licensed under the Apache License Version 2.0.\n\n## Credit\n\nZenML is built on the shoulders of giants: we leverage, and would like to give credit to, existing open-source libraries like [TFX](https://github.com/tensorflow/tfx/). The goal of our framework is neither to replace these libraries, nor to diminish their usage. ZenML is simply an opinionated, higher-level interface with the focus being purely on easy-of-use and coherent intuitive design.\nYou can read more about why we actually started building ZenML at our [blog](https://blog.zenml.io/why-zenml/).\n',
    'author': 'ZenML GmbH',
    'author_email': 'info@zenml.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://zenml.io',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<3.9',
}


setup(**setup_kwargs)
