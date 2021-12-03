import os
import sys
import json
from pathlib import Path


try:
        import importlib.resources as pkg_resources
except ImportError:
        # Try backported to PY<37 `importlib_resources`.
            import importlib_resources as pkg_resources

config_file = "config.json"


def get_config_data():
    providers = []
    datasets = []
    providersRequiredFields = set()
    datasetsRequiredFields = set()

    with pkg_resources.open_text("ystafdb.data", config_file) as json_file:
        data = json.load(json_file)
        for provider in data['providers']:
            providers.append(provider)
            for dataset in provider['datasets']:
                dataset['provider'] = provider['provider']
                datasets.append(dataset)
        for requiredField in data['providers_required_fields']:
            providersRequiredFields.add(requiredField)
        for requiredField in data['datasets_required_fields']:
            datasetsRequiredFields.add(requiredField)

    # Each provider must have all required fields
    providerNames = []
    for provider in providers:
        providerKeys = set([key for key in provider])
        if not providersRequiredFields.issubset(providerKeys):
            exit("{} is a required field for providers, but have not been supplied for all providers\n"
                 "Check config.json and try again\n"
                 "Exiting".format(', '.join(list(providersRequiredFields - providerKeys))))

        # All provider names must be distinct
        if provider['provider'] in providerNames:
            exit("All providers must have different names, but the provider {} "
                 "is used multiple times".format(provider['provider']))
        else:
            providerNames.append(provider['provider'])

        # All datasets from the same provider must have distinct names
        datasetNames = []
        for dataset in provider['datasets']:
            if dataset['name'] in datasetNames:
                exit("All datasets for the same provider must have different names, but the name {} "
                     "is used for multiple datasets".format(dataset['name']))
            else:
                datasetNames.append(dataset['name'])

    # Each dataset must have all required fields
    for dataset in datasets:
        datasetKeys = set([key for key in dataset])
        if not datasetsRequiredFields.issubset(datasetKeys):
            exit("{} is a required field for datasets, but have not been supplied for all datasets\n"
                 "Check config.json and try again\n"
                 "Exiting".format(', '.join(list(datasetsRequiredFields - datasetKeys))))


    # Each dataset must have a provider
    providersSetA = set([dataset['provider'] for dataset in datasets])
    providersSetB = set([provider['provider'] for provider in providers])

    if not providersSetA.issubset(providersSetB):
        exit("{} has not been listed as a dataset provider\n"
             "Add The provider to the config.json or remove datasets using the provider\n"
             "Exiting".format(', '.join(list(providersSetA - providersSetB))))

    # Format dataset fields
    providers = format_providers(providers)
    datasets = format_datasets(datasets)

    return providers, datasets


def get_repo_name():
    with pkg_resources.open_text("ystafdb.data", config_file) as json_file:
        data = json.load(json_file)
        git_repo_name = data["git_repo_name"]

    return git_repo_name


def does_provider_dataset_combi_exist(prov, data):
    _, datasets = get_config_data()
    for dataset in datasets:
        if dataset['name'] == data.lower().replace(' ', '_') and dataset['provider'] == prov.lower().replace(' ', '_'):
            return dataset
    return None


def format_datasets(datasets):
    formattedDatasets = []
    for i, dataset in enumerate(datasets):
        newDataset = dataset.copy()
        newDataset['original_name'] = dataset['name']
        newDataset['provider'] = dataset['provider'].lower().replace(' ', '_')
        newDataset['version'] = dataset['version'].replace('.', '_')
        newDataset['update_date'] = dataset['update_date'].replace('.', '-').replace('/', '-')
        newDataset['name'] = dataset['name'].lower().replace('.', '_').replace('/', '_')
        newDataset['id'] = str(i)
        formattedDatasets.append(newDataset)

    return formattedDatasets


def format_providers(providers):
    formattedProviders = []
    for i, provider in enumerate(providers):
        newProvider = provider.copy()
        newProvider['name'] = provider['provider']
        newProvider['provider'] = provider['provider'].lower().replace(' ', '_')
        newProvider['id'] = str(i)
        formattedProviders.append(newProvider)

    return formattedProviders
