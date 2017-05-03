# Copyright (C) 2015-2017 DLR
#
# All rights reserved. This program and the accompanying materials are made
# available under the terms of the Eclipse Public License v1.0 which
# accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
# Franz Steinmetz <franz.steinmetz@dlr.de>
# Sebastian Brunner <sebastian.brunner@dlr.de>

from gtkmvc import ModelMT
from rafcon.utils.vividict import Vividict
from rafcon.core.library_manager import LibraryManager

from rafcon.utils import log
logger = log.get_logger(__name__)


class LibraryManagerModel(ModelMT):
    """This model class manages a library manager

    The model class is part of the MVC architecture. It holds the data to be shown (in this case a library manager).

    :param library_manager: The library_manager to be managed
     """

    library_manager = None

    __observables__ = ("library_manager",)

    def __init__(self, library_manager, meta=None):
        """Constructor
        """

        ModelMT.__init__(self)  # pass columns as separate parameters

        assert isinstance(library_manager, LibraryManager)

        self.library_manager = library_manager

        if isinstance(meta, Vividict):
            self.meta = meta
        else:
            self.meta = Vividict()

        # this class is an observer of its own properties:
        self.register_observer(self)