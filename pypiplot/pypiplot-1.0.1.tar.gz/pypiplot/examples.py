# %%
# import pypiplot
# print(pypiplot.__version__)

from pypiplot import pypiplot
# print(dir(pypiplot))

# %% Plot
# Init
pp = pypiplot(username='erdogant', savepath='D://REPOS/pypiplot/repo_data/')
# Get download statistics
results = pp.stats()

# Store svg on github.io
path = 'D://REPOS/erdogant.github.io/docs/imagesc/pypi/pypi_heatmap.html'
pp.plot_year(path=path, vmin=700)
# Store all repo info in github.io
path = 'D://REPOS/erdogant.github.io/docs/imagesc/pypi/pypi_heatmap_repos.html'
pp.plot(path=path, vmin=100)


# %%
pp = pypiplot(username='erdogant')

pp.stats(repo='distfit')
pp.plot_year()
pp.plot(vmin=25)

# %% Update all
pp = pypiplot(username='erdogant', savepath='D://REPOS/pypiplot/repo_data/')
pp.update()

# %% Update single repo
pp.update(repo=['bnlearn'])
pp.update(repo='bnlearn')

results = pp.stats(repo=['df2onehot','pca'])
results = pp.stats(repo='df2onehot')

# %% Get some stats
results = pp.stats(repo=['df2onehot','pca','bnlearn','ismember','thompson'])

# %%
pp = pypiplot(username='erdogant')

pp.stats(repo='distfit')
pp.plot_year()
pp.plot(vmin=25)

pp.stats(repo='worldmap')
pp.plot_year()

pp.stats(repo='hnet')
pp.plot_year()

pp.stats(repo='ismember')
pp.plot_year()

pp.stats(repo='flameplot')
pp.plot_year()

pp.stats(repo='pca')
pp.plot_year()

pp.stats(repo=['df2onehot','pca','bnlearn','ismember','thompson'])
pp.plot_year(vmin=100)
pp.plot(vmin=25)

# %% Plot bnlearn
results = pp.stats(repo='bnlearn')
pp.plot_year()

# %%
pp.update()
results = pp.stats()
pp.plot_year(vmin=700)
pp.plot(vmin=25)

# %% Plot
# Init
pp = pypiplot(username='erdogant', savepath='D://REPOS/pypiplot/repo_data/')
# Get download statistics
results = pp.stats()

# Store svg on github.io
path = 'D://REPOS/erdogant.github.io/docs/imagesc/pypi/pypi_heatmap.html'
pp.plot_year(path=path, vmin=700)
# Store all repo info in github.io
path = 'D://REPOS/erdogant.github.io/docs/imagesc/pypi/pypi_heatmap_repos.html'
pp.plot(path=path, vmin=100)

# %%
results['data'].cumsum().plot()
