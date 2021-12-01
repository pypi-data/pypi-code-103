'''
 Do not remove this alias file

 Its only purpose is to provide backwards compatibility
 for users of the Builder classes, which have been moved to components.datasets

'''
import warnings

warnings.warn("DatasetBuilder and DatasetLocationBuilder have now moved, you can still use them here, but "
              "please update your imports as below, as they will deprecated in the future (1.20). Change from:\n\n"
              "from dli.client.builders import DatasetLocationBuilder \n"
              "to \n"
              "from dli.components.dataset import DatasetLocationBuilder"
              "\n"
              "\n"
              "from dli.client.builders import DatasetBuilder \n"
              "to \n"
              "from dli.components.dataset import DatasetBuilder\n\n"
              )
from dli.components.dataset import DatasetLocationBuilder
from dli.components.dataset import DatasetBuilder