#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Allows you to orchestrate a batch of tasks.
"""

import time


__pdoc__ = {"Map.__iter__": True}


class Map:
    """
    Computes a function using arguments from each of the iterables.

    Example
    -------
    >>> from raisin import map_main
    >>> foo = lambda x: x**2
    >>> with map_main.Map(foo, [0, 1, 2, 3]) as m:
    ...     list(m)
    ...
    [0, 1, 4, 9]
    >>>
    """
    def __init__(self, target, *iterables, func_kwargs={}, **kwargs):
        """
        ** Recupere les attributs **
        ----------------------------

        Parameters
        ----------
        target : callable
            This is the function that is evaluated for different arguments.
        *iterables : iterable
            These are the different parameters that will allow the function
            to be evaluated. Each process will be evaluated for each element of these iterables. 
            Stops when the shortest iterable is exhausted.
            Without parallelization, this is equivalent to ``[target(*args) for args in zip(*iterables)]``.
        func_kwargs : dict
            Allows to pass constant arguments. each key is the name of
            the parameter and with each name of the parameter, this
            dictionary is used to associate this value with it. 
        parallelization_rate : int
            * This is the level of parallelization used. There are 5 possible levels:
                * 0 => No parallelization at all.
                    * The only use is to be able to do statistics.
                    * Is a little bit equivalent to ``[target(*args, **func_kwargs) for args in zip(*iterables)]``.
                    * This is the most reliable option and the least crowded.
                * 1 => Do a 'fake' parallelization with fake python
                    threads like the ``threading`` module would. In the case
                    where the tasks do not consume CPU resources but are waiting
                    for an event, it is this level of parallelization which
                    has a good chance of being the most efficient.
                * 2 => Parallelize the different tasks on the different physical
                    cores of the machine. It is the same level of
                    parallelization as that proposed by ``multiprocessing`` module.
                    If the granularity of the tasks is relatively low or
                    the size of the data is large, it is probably this
                    rate of parallelization which is the best.
                * 3 => Parallelize not only on the different hearts of the machine
                    but will also explore the other machines present on the local network.
                    * Nessecite to have installed 'raisin'. There must be a server listening on the local machine.
                    * If 'raisin' is not installed, falls back on a multiprocessing parallelization.
                    * Other machines on the local network must be listening,
                        otherwise this method will be slower than method 2.
                * 4 (default value) => The biggest parallelization among all. It allows you to
                    explore resources through a cluster that can extend all over the world. 
                    * The constraints are the same as for method number 3.
                    * Only for security aspects, the set-up can be a little more complicated.
                    * Although we have done a lot of effort to make everything as secure as possible,
                        this option makes your computer a little more vulnerable to cyber attacks. 
        force : boolean, optional
            If 'False' (default value), see if the calculation has already been performed.
            If so, the result is returned directly. On the other hand, if 'True',
            the calculation is actually done whatever the situation.
        timeout : number, optional
            The maximum total time expresed in second allowed before raises a TimeoutError exception.
            The default value is one month = ``3600*24*31 s``.
        task_timeout : number, optional
            The maximum time for each tasks expresed in second allowed
            before raises a TimeoutError exception.
            The default value is one day = ``3600*24 s``.
        save : boolean, optional
            If 'True' (default value), save the results if there is room
            and it is worth it. It is worth it if the compute is long
            enough and the result is small enough. If false, do not
            try to save anything.
        keep_order : boolean, optional
            If 'True' (default value), the order of the results is kept. Otherwise,
            the results are processed as soon as they arrive, which avoids
            the buffer memory and little allows to work in more tight flow. 
        """
        assert hasattr(target, "__call__"), \
            f"'target' has to be a function, not a {type(target).__name__}."
        assert all(hasattr(iterable, "__iter__") for iterable in iterables), \
            "All the arguments must be iterable, it is not the case."
        assert isinstance(func_kwargs, dict), \
            f"'func_kwargs' has to be a dictionary, not a {type(func_kwargs).__name__}."
        assert all(isinstance(key, str) for key in func_kwargs.keys()), \
            "All 'func_kwargs' keys must be a string."
        parallelization_rate = kwargs.get("parallelization_rate", 4)
        assert isinstance(parallelization_rate, int), \
            f"'parallelization_rate' has to be an integer, not a {type(parallelization_rate).__name__}."
        assert parallelization_rate in {0, 1, 2, 3, 4}, ("The parallelization_rate value"
            f"can only be 0, 1, 2, 3 or 4. It is {parallelization_rate}.")
        force = kwargs.get("force", False)
        assert isinstance(force, bool), \
            f"'force' has to be a boolean, not a {type(force).__name__}."
        timeout = kwargs.get("timeout", 2678400)
        assert isinstance(timeout, (int, float)), \
            f"'timeout' has to be an integer, not a {type(timeout).__name__}."
        assert timeout > 0, f"The timeout must be strictely positive. Not {timeout}."
        task_timeout = kwargs.get("task_timeout", 86400)
        assert isinstance(task_timeout, (int, float)), \
            f"'task_timeout' has to be an integer, not a {type(task_timeout).__name__}."
        assert task_timeout > 0, f"The task timeout must be strictely positive. Not {task_timeout}."
        save = kwargs.get("save", True)
        assert isinstance(save, bool), \
             f"'save' has to be a boolean, not a {type(save).__name__}."
        keep_order = kwargs.get("keep_order", True)
        assert isinstance(keep_order, bool), \
            f"'keep_order' has to be a boolean, not a {type(keep_order).__name__}."

        self.target = target
        self.iterables = iterables
        self.func_kwargs = func_kwargs

        self.parallelization_rate = parallelization_rate
        self.force = force
        self.timeout = timeout
        self.task_timeout = task_timeout
        self.save = save
        self.keep_order = keep_order

        # Variables d'etat.
        self._is_started = False # True quand 'self.start' est lance.
        self._finished = False # True quand tous les resultats con recuperes.
        self._starting_date = None # Date du premier appel de la methode 'self.start' (float).
        self._tasks = None # Les taches ou generateur de taches.

    def get(self):
        """
        ** Get the results and stats. **

        Notes
        -----
        All the fields are not necessarily present.

        Returns
        -------
        dict
            * Contains general information and also specific information.
            The fields are as follows:
                * 'total_time' : The total time elapsed between the
                    call of the 'start' method and the moment when
                    all the results are retrieved.
                * 'transfer_time' : The total sum for each task of
                    the time spent serializing the data and passing it through.
                * 'task_time' : The time actually spent by each process.
                    This time does not take into account all the data
                    formatting and transfer operations.
                * 'flo' : Estimation of the number of floating-point operations.
                    This estimate makes it possible to have an idea of the
                    quantity of resources which were necessary to carry out
                    the entirety of the calculation.
                * 'energy' : Estimate of the energy (in joules (w/s))
                    which was necessary for this calculation. Takes into
                    account the energy consumed by each task and the
                    energy consumed by the internet to send the packets.
                * 'results' : list contains a dictionary for each result:
                    * 'value' : The value of the result.
                    * 'error' : None or the excepption if an exception occured.
                    * 'hash' : The signing of this result.
                    * 'host' : The machine on which the calculation was performed.
                    * 'cpu_time' : Le temps cpu reelement ecoule par cette tache.
        """
        self.start()

        if self.parallelization_rate == 0:
            from raisin.calculation.task import Task
            results = [Task(self.target, task_timeout=self.task_timeout)(*args, **self.func_kwargs)
                for args in zip(*self.iterables)]
            self._finished = True
            return {
                "results": results,
                "total_time": time.time() - self._starting_date,
                "transfer_time": 0,
            }
        
        raise NotImplementedError

    def start(self):
        """
        ** Start the thread's activity. **
        ----------------------------------

        Notes
        -----
        * This method can only take effect once.
        * Its explicit call by the user is optional.
        Indeed, it is recalled by the ``Map.get`` and ``Map.__iter__``.
        """
        if self._finished:
            raise RuntimeError("This computation cluster has already been "
                "launched and the results have already been recovered. "
                "You can only apply it once.")
        
        if self._is_started:
            return

        self._is_started = True
        self._starting_date = time.time()
        
        if self.parallelization_rate == 0:
            return
        elif self.parallelization_rate == 1:
            raise NotImplementedError
        elif self.parallelization_rate == 2:
            raise NotImplementedError
        elif self.parallelization_rate == 3:
            raise NotImplementedError
        elif self.parallelization_rate == 4:
            raise NotImplementedError

    
    def manage_server(self):
        """
        Boucle qui permet de gérer le dérouler du calcul dans le graphe
        Doit être exécuter dans un thread.
        """
        # Tant que calculs pas finis
            # On recupère le graphe en interogeant le serveur
            # On met à jour le graphe via le task_manager
            # On pousse les modification

        raise NotImplementedError()

    def __iter__(self):
        """
        ** Retrieve the results without stats. **
        -----------------------------------------

        Yields
        ------
        object
            The result of each task.

        Raises
        ------
        TimeoutError
            if the critical time is reached.
        """
        self.start()

        if self.parallelization_rate == 0:
            from raisin.tools import timeout_decorator
            yield from (
                timeout_decorator(self.task_timeout)(self.target)(
                    *args, **self.func_kwargs
                    )
                for args in zip(*self.iterables)
                )

        else:
            raise NotImplementedError

        self._finished = True

    def __repr__(self):
        """
        Representation de l'objet.
        """
        return "<Map(target=%s)>" % repr(self.target)

