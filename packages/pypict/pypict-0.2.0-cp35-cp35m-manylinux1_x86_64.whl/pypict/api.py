from pypict import capi


class Task(object):
    def __init__(self, seed=None):
        self.handle = capi.createTask()
        self._model = _Model(seed)
        capi.setRootModel(self.handle, self._model.handle)

    def __del__(self):
        if self.handle != 0:
            capi.deleteTask(self.handle)

    @property
    def model(self):
        return self._model

    def add_exclusion(self, items):
        capi.addExclusion(self.handle, tuple(items))

    def add_seed(self, items):
        capi.addSeed(self.handle, tuple(items))

    def generate(self):
        capi.generate(self.handle)
        return _ResultSet(self)

    def get_total_parameter_count(self):
        return capi.getTotalParameterCount(self.handle)


class _Model(object):
    def __init__(self, seed=None):
        if seed is None:
            seed = capi.DEFAULT_RANDOM_SEED
        self.handle = capi.createModel(seed)
        self._owned = True

    def __del__(self):
        if self.handle != 0 and self._owned:
            capi.deleteModel(self.handle)

    def add_parameter(
            self, count, order=capi.PAIRWISE_GENERATION, weights=None):
        if weights is not None:
            weights = tuple(weights)
        return capi.addParameter(self.handle, count, order, weights)

    def attach_child_model(self, order, seed=None):
        if seed is None:
            seed = capi.DEFAULT_RANDOM_SEED
        childModel = _Model(seed)
        capi.attachChildModel(self.handle, childModel.handle, order)
        childModel._owned = False
        return childModel


class _ResultSet(object):
    def __init__(self, task):
        self._task = task

    def __iter__(self):
        capi.resetResultFetching(self._task.handle)
        buf = capi.allocateResultBuffer(self._task.handle)
        try:
            while True:
                remaining = capi.getNextResultRow(self._task.handle, buf)
                if remaining == 0:
                    break
                yield list(buf)
        finally:
            capi.freeResultBuffer(buf)
