# --------------------------------------------------
# Name        : pypiplot.py
# Author      : E.Taskesen
# Contact     : erdogant@gmail.com
# github      : https://github.com/erdogant/pypiplot
# Licence     : See licences
# --------------------------------------------------

from d3heatmap import d3heatmap as d3
import pypistats
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import argparse
import pandas as pd
import numpy as np
import os


# %%
class pypiplot:
    """Class pypiplot."""

    def __init__(self, username, category=['with_mirrors', 'without_mirrors'], sep=';', savepath=None, verbose=3):
        """Initialize pypiplot.

        Parameters
        ----------
        username : String
            Github user account name.
        category : list, optional
            Downloads is counted for one or both of these categories ['with_mirrors', 'without_mirrors'].
        sep : str, (Default: ';')
            Seperator to store data in csv file.
        savepath : String, (Default: None)
            Storage of the csv files containing download statistics.
        verbose : int, (Default: 3)
            Verbosity message.

        Returns
        -------
        None.

        """
        self.username = username
        self.repo_link = 'https://api.github.com/users/' + username + '/repos'
        self.sep = sep
        self.category = category
        self.curpath = os.path.dirname(os.path.abspath(__file__))
        # self.curpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        if savepath is None:
            self.savepath = os.path.join(self.curpath, 'data')
        else:
            self.savepath = savepath
        self.verbose=verbose

    def update(self, repo=None):
        """Update repo download file(s).

        Description
        -----------
        Update the local stored file with daily downloads for the specified repos.

        Parameters
        ----------
        repo : list of Strings, (Default: None)
            None : Take all available pypi repos for the username.

        Returns
        -------
        None.

        """
        if (repo is not None) and ('str' in str(type(repo))):
            repo = [repo]
        # Extract all repos
        repos = self._get_repo_names_from_git()
        if (repo is not None):
            repos = repo
            if not np.any(np.isin(repos, repo)):
                raise ValueError('[pypiplot] >Error: repos [%s] does not exists or is private.' %(repo))

        if self.verbose>=3: print('[pypiplot] >Start updating..')
        for repo in repos:
            try:
                if self.verbose>=3: print('[pypiplot] >[%s]' %(repo))
                status = True
                df = pypistats.overall(repo, total=True, format="pandas")
                df.dropna(inplace=True)
                df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
                df = df.sort_values("date")
                df.reset_index(drop=True, inplace=True)
                del df['percent']

                # Merge with any on disk
                pathname = os.path.join(self.savepath, repo + '.csv')
                if os.path.isfile(pathname):
                    # Read repo from disk
                    df_disk = read_repo_counts_from_disk(pathname, self.sep)
                    # Merge with latest counts
                    df, status = add_new_counts_to_repo(df, df_disk, repo, verbose=self.verbose)
                # Write to disk
                if status:
                    if self.verbose>=3: print('[pypiplot] >Write to disk..')
                    df.to_csv(pathname, index=False, sep=self.sep)
            except:
                if self.verbose>=1: print('[pypiplot] >Skip [%s] coz not exists on Pypi.' %(repo))

    def stats(self, repo=None):
        """Compute statistics for the specified repo(s).

        Description
        -----------
        Compute and summarize statistics for the libraries.

        Parameters
        ----------
        repo : list of Strings, (Default: None)
            None : Take all available pypi repos for the username.

        Returns
        -------
        dict.
            * data : Download statistics for the repo(s).
            * heatmap : DataFrame containing (summarized) data statistics.
            * repos : Number of repos.
            * n_libraries : Number of libraries processed.

        """
        # Retrieve all repos for the username
        status, repos, filenames, pathnames = self._get_repos()

        if (repo is not None) and ('str' in str(type(repo))):
            repo = [repo]

        # Check whether specific repo exists.
        if repo is not None:
            Iloc = np.isin(repos, repo)
            if not np.any(Iloc): raise ValueError('[pypiplot] >Error: repos [%s] does not exists or is private. Tip: Run the .update() first.' %(repo))
            # repos = [repo]
            repos = repos[Iloc]
            filenames = filenames[Iloc]
            pathnames = pathnames[Iloc]

        if not status:
            if self.verbose>=3: print('[pypiplot] >No repos could be retrieved from git nor disk <return>')
            return None

        out = pd.DataFrame()
        for repo, pathname in zip(repos, pathnames):
            df = read_repo_counts_from_disk(pathname, self.sep)

            # Take desired categories
            Iloc = np.isin(df['category'], self.category)
            df = df.loc[Iloc, :]

            # Group by date
            df = df.groupby("date").sum().sort_values("date")
            df.reset_index(drop=False, inplace=True)

            dftmp = df.groupby("date").sum()
            dftmp.rename(columns={'downloads' : repo}, inplace=True)
            out = pd.concat([out, dftmp], axis=0)

        out.fillna(value=0, inplace=True)
        out.reset_index(drop=False, inplace=True)
        out = out.groupby("date").sum()

        # Make heatmap
        heatmap = _compute_history_heatmap(out, verbose=self.verbose)

        self.results = {}
        self.results['data'] = out
        self.results['heatmap'] = heatmap
        self.results['n_libraries'] = out.shape[1]
        self.results['repos'] = repos
        return self.results

    def _get_repo_names_from_git(self):
        # Extract repos for user
        if self.verbose>=3: print('[pypiplot] >Extracting repo names for [%s]..' %(self.username))
        r = requests.get(self.repo_link)
        data = r.json()

        # Extract the repo names
        repos = []
        for rep in data:
            # full_names.insert(0, rep['full_name'])
            repos.insert(0, rep['name'])
        if self.verbose>=3: print('[pypiplot] >[%.0d] repos found for [%s]' %(len(repos), self.username))
        # Return
        return np.array(repos)

    def _get_repos(self):
        status = True
        # Retrieve all downloads from disk
        repos, filenames, pathnames = get_files_on_disk(self.savepath, verbose=self.verbose)
        # Update and retrieve if needed
        if len(repos)==0:
            if self.verbose>=3: print('[pypiplot] >No files found on disk. Lets update first!')
            # Update all repos
            self.update()
            # Retrieve all downloads from disk
            repos, filenames, pathnames = get_files_on_disk(self.savepath, verbose=0)
            if len(repos)==0:
                status = False
        # Return
        return status, repos, filenames, pathnames

    def plot_year(self, title=None, description=None, path='d3heatmap.html', vmin=10, vmax=None, cmap='interpolateGreens', visible=True, overwrite=False):
        """Plot heatmap across all repos.

        Description
        -----------
        Plot heatmap of all the repos combined with weeks vs day-name

        Parameters
        ----------
        title : String, (Default: None)
            Title of the heatmap.
        description : String, (Default: None)
            Description of the heatmap.
        path : String, (Default: 'd3heatmap.html'.)
            Full pathname or filename to store the file. If None is used, the system tempdir is used.
        vmin : int, (Default: 25)
            Minimum color: Used for colorscheme.
            None: Take the minimum value in the matrix.
        vmax : int, (Default: None)
            Minimum color: Used for colorscheme.
            None: Take the maximum value in the matrix.
        cmap : String, (default: 'interpolateInferno').
            The colormap scheme. This can be found at: https://github.com/d3/d3-scale-chromatic.
        visible : Bool, (default: True).
            Open the browser.

        Returns
        -------
        None.

        """
        if description is None:
            if self.results['n_libraries']>1:
                description = '%.0d Total Pypi downloads across %.0d libraries' %(self.results['heatmap'].sum().sum(), self.results['n_libraries'])
            else:
                description = '%.0d Total Pypi downloads for %s' %(self.results['heatmap'].sum().sum(), self.results['repos'][0])

        if title is None:
            title = ''
        # Make heatmap with d3js.
        d3.matrix(self.results['heatmap'], fontsize=9, title=title, description=description, path=path, width=700, height=200, cmap=cmap, vmin=vmin, vmax=vmax, stroke='black', showfig=visible)

    def plot(self, title=None, description=None, path='d3_heatmap_repos.html', vmin=10, vmax=None, width=700, height=None, cmap='interpolateGreens'):
        """Plot heatmap across all repos.

        Description
        -----------
        Plot heatmap of all the repos combined with weeks vs day-name

        Parameters
        ----------
        title : String, (Default: None)
            Title of the heatmap.
        description : String, (Default: None)
            Description of the heatmap.
        path : String, (Default: 'd3_heatmap_repos.html'.)
            Full pathname or filename to store the file. If None is used, the system tempdir is used.
        vmin : int, (Default: 25)
            Minimum color: Used for colorscheme.
            None: Take the minimum value in the matrix.
        vmax : int, (Default: None)
            Minimum color: Used for colorscheme.
            None: Take the maximum value in the matrix.
        cmap : String, (default: 'interpolateInferno').
            The colormap scheme. This can be found at: https://github.com/d3/d3-scale-chromatic
        width : int, (default: 700).
            Width of the window.
        height : int, (default: None).
            None: Determine based on number of repos.

        Returns
        -------
        None.

        """
        heatmap = pd.DataFrame()
        cols = self.results['data'].columns.values
        for col in cols:
            heatmap[col] = _compute_history_heatmap(pd.DataFrame(self.results['data'][col])).sum(axis=0)

        if title is None:
            title = ''
        if description is None:
            if self.results['n_libraries']>1:
                description = '%.0d Pypi downloads last year across %.0d libraries' %(self.results['heatmap'].sum().sum(), self.results['n_libraries'])
            else:
                description = '%.0d Pypi downloads last year for %s' %(self.results['heatmap'].sum().sum(), self.results['repos'][0])
        if height is None:
            height = np.maximum(np.minimum(40 * heatmap.shape[1], 550), 200)

        # Make heatmap with d3js.
        d3.matrix(heatmap.T, fontsize=9, title=title, description=description, path=path, width=700, height=height, cmap=cmap, vmin=vmin, vmax=vmax, stroke='black')

        # fig, ax = plt.subplots(figsize=(10, 2))
        # out.plot()

        # df['weeknr'] = df['date'].dt.week
        # df['cumsum'] = df['downloads'].cumsum()
        # ax.plot(df['weeknr'].values, df['cumsum'].values, label=repo)
        # ax.plot(df['weeknr'].values, df['downloads'].values, label=repo)

        # ax.legend()
        # ax.grid(True)

        # data = pypistats.overall("pillow", total=True, format="pandas")
        # df = df.groupby("category").get_group("without_mirrors").sort_values("date")
        # df = df.groupby("category").get_group("without_mirrors").sort_values("date")

        # chart = df.plot(x="date", y="downloads", figsize=(10, 2))
        # chart = df.plot(x="date", y="downloads", figsize=(10, 2))
        # chart.figure.show()
        # chart.figure.savefig("overall.png")  # alternatively
        pass

# %%
def _compute_history_heatmap(df, duration=360, nr_days=7, verbose=3):
    df = df.sum(axis=1).copy()
    datetimeformat='%Y-%m-%d'

    if verbose>=3: print('[pypiplot] >Computing heatmap across the last %.0d days.' %(duration))

    # Make sure the duration is tops 365 from now
    extend_days = datetime.now() - timedelta(duration)
    dates_start = pd.to_datetime(pd.date_range(start=extend_days, end=df.index[0]).strftime(datetimeformat), format=datetimeformat)
    df_start = pd.DataFrame(np.zeros((len(dates_start), 1)), dtype=int, index=dates_start)

    # Fill the gap between now and the latest point of the date in the data
    dates_end = pd.to_datetime(pd.date_range(start=df.index[-1] + timedelta(1), end=datetime.now()).strftime(datetimeformat), format=datetimeformat)
    df_end = pd.DataFrame(np.zeros((len(dates_end), 1)), dtype=int, index=dates_end)

    # dataframe containing 365 days of data
    df_365 = pd.concat([df_start, df, df_end], axis=0)

    # To make sure we can break the dataframe into columns of 7 days, we need to extend a bit more.
    extend_days = float(nr_days - np.mod(df_365.shape[0], nr_days))
    start = df_365.index[0] - timedelta(extend_days)
    dates_start = pd.to_datetime(pd.date_range(start=start, end=df_365.index[0] - timedelta(1)).strftime(datetimeformat), format=datetimeformat)
    df_start = pd.DataFrame(np.zeros((len(dates_start), 1)), dtype=int, index=dates_start)

    # Final
    df_fin = pd.concat([df_start, df_365], axis=0)
    df_values = df_fin.values.reshape((-1, nr_days))

    # Column names
    colnames = df_fin.index.isocalendar().week.astype(str).values
    
    # colnames = pd.Int64Index(idx.isocalendar().week
    colnames = colnames.reshape((-1, nr_days))[:, -1]
    rownames = df_fin.index.day_name().values.reshape((-1, nr_days))[0, :]
    rownames = np.array(list(map(lambda x: x[0:3], rownames))).astype('O')

    # Flip matrix up down to make sure that sunday is on top
    rownames=rownames[::-1]
    df_values = np.flipud(df_values.T)

    # Output
    df_heatmap = pd.DataFrame(columns=colnames, data=df_values, index=rownames)

    return df_heatmap

# %%
def get_files_on_disk(curpath, verbose=3):
    if verbose>=3: print('[pypiplot] >Retrieve files from disk..')
    filenames = np.array(os.listdir(curpath))
    filesplit = np.array(list(map(os.path.splitext, filenames)))
    repos = filesplit[:, 0]
    Iloc = filesplit[:, 1]=='.csv'

    filenames = filenames[Iloc]
    repos = repos[Iloc]
    # Make full path
    pathnames = np.array(list(map(lambda x: os.path.join(curpath, x), filenames)))
    return repos, filenames, pathnames 

def read_repo_counts_from_disk(pathname, sep):
    df_disk = pd.read_csv(pathname, sep=sep)
    df_disk['date'] = pd.to_datetime(df_disk['date'], format='%Y-%m-%d')
    return df_disk

def add_new_counts_to_repo(df, df_disk, repo, verbose=3):
    STATUS = False
    count_before = df_disk.shape[0]
    df = pd.concat([df, df_disk], axis=0)
    df.drop_duplicates(inplace=True)
    df = df.sort_values("date")
    df.reset_index(drop=True, inplace=True)

    count_after = df.shape[0]
    if count_after>count_before:
        STATUS=True
        if verbose>=3: print('[pypiplot] >[%s] updated.' %(repo))

    return df, STATUS


# %% Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("github", type=str, help="github account name")
    parser.add_argument("-u", "--username", type=str, help="username github.")
    parser.add_argument("-l", "--library", type=str, help="library name(s).")
    parser.add_argument("-p", "--path", type=str, help="path name to store plot.")
    parser.add_argument("-v", "--vmin", type=str, help="minimu value of the figure.")
    args = parser.parse_args()
    print('[pypiplot] >Booting up: username: [%s], Libraries: [%s]' %(args.username, args.library))
    # Initialize library
    pp = pypiplot(username=args.username)
    # Update
    pp.update(repo=args.library)
    # Get the statistics
    pp.stats()
    # Store
    pp.plot_year(path=args.path, vmin=float(args.vmin))
