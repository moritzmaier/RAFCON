"""
.. module:: global_variable_manager
   :platform: Unix, Windows
   :synopsis: A module to organize all global variables of the state machine

.. moduleauthor:: Sebastian Brunner

"""

import copy
from gtkmvc import Observable
from threading import Lock
from rafcon.core.id_generator import *

from rafcon.utils import log
from rafcon.utils import type_helpers
logger = log.get_logger(__name__)


class GlobalVariableManager(Observable):
    """A class for organizing all global variables of the state machine

    :ivar __global_variable_dictionary: the dictionary, where all global variables are stored
    :ivar __variable_locks: a dictionary that holds one mutex for each global variable
    :ivar __dictionary_lock: a mutex to prevent that the dictionary is written by two threads simultaneously
    :ivar __access_keys: a dictionary that holds an access key to each locked global variable
    :ivar __variable_references: a dictionary that stores whether a variable can be returned by reference or not
    """

    def __init__(self):
        Observable.__init__(self)
        self.__global_variable_dictionary = {}
        self.__global_variable_type_dictionary = {}
        self.__variable_locks = {}
        self.__dictionary_lock = Lock()
        self.__access_keys = {}
        self.__variable_references = {}

    @Observable.observed
    def set_variable(self, key, value, per_reference=False, access_key=None, data_type=None):
        """Sets a global variable

        :param key: the key of the global variable to be set
        :param value: the new value of the global variable
        :param per_reference: a flag to decide if the variable should be stored per reference or per value
        :param access_key: if the variable was explicitly locked with the  rafcon.state lock_variable
        :raises exceptions.RuntimeError: if a wrong access key is passed
        """
        if self.variable_exist(key):
            if data_type is None:
                data_type = self.__global_variable_type_dictionary[key]
        else:
            if data_type is None:
                data_type = type(None)
        assert isinstance(data_type, type)
        self.check_value_and_type(value, data_type)

        self.__dictionary_lock.acquire()
        unlock = True
        if self.variable_exist(key):
            if self.is_locked(key) and self.__access_keys[key] != access_key:
                self.__dictionary_lock.release()
                raise RuntimeError("Wrong access key for accessing global variable")
            elif self.is_locked(key):
                unlock = False
            else:
                access_key = self.lock_variable(key)
        else:
            self.__variable_locks[key] = Lock()
            access_key = self.lock_variable(key)

        # --- variable locked
        if per_reference:
            self.__global_variable_dictionary[key] = value
            self.__global_variable_type_dictionary[key] = data_type
            self.__variable_references[key] = True
        else:
            self.__global_variable_dictionary[key] = copy.deepcopy(value)
            self.__global_variable_type_dictionary[key] = data_type
            self.__variable_references[key] = False
        # --- release variable

        if unlock:
            self.unlock_variable(key, access_key)
        self.__dictionary_lock.release()
        logger.debug("Global variable '{}' was set to value '{}' with type '{}'".format(key, value, data_type.__name__))

    def get_variable(self, key, per_reference=None, access_key=None, default=None):
        """Fetches the value of a global variable

        :param key: the key of the global variable to be fetched
        :param bool per_reference: a flag to decide if the variable should be stored per reference or per value
        :param access_key: if the variable was explicitly locked with the  rafcon.state lock_variable
        :param default: a value to be returned if the key does not exist
        :return: The value stored at in the global variable key
        :raises exceptions.RuntimeError: if a wrong access key is passed or the variable cannot be accessd by reference
        """
        if self.variable_exist(key):
            unlock = True
            if self.is_locked(key):
                if self.__access_keys[key] == access_key:
                    unlock = False
                else:
                    if not access_key:
                        access_key = self.lock_variable(key)
                    else:
                        raise RuntimeError("Wrong access key for accessing global variable")
            else:
                access_key = self.lock_variable(key)

            # --- variable locked
            if self.variable_can_be_referenced(key):
                if per_reference or per_reference is None:
                    return_value = self.__global_variable_dictionary[key]
                else:
                    return_value = copy.deepcopy(self.__global_variable_dictionary[key])
            else:
                if per_reference:
                    self.unlock_variable(key, access_key)
                    raise RuntimeError("Variable cannot be accessed by reference")
                else:
                    return_value = copy.deepcopy(self.__global_variable_dictionary[key])
            # --- release variable

            if unlock:
                self.unlock_variable(key, access_key)
            return return_value
        else:
            # logger.warn("Global variable '{0}' not existing, returning default value".format(key))
            return default

    def variable_can_be_referenced(self, key):
        """Checks whether the value of the variable can be returned by reference

        :param str key: Name of the variable
        :return: True if value of variable can be returned by reference, False else
        """
        return key in self.__variable_references and self.__variable_references[key]

    @Observable.observed
    def delete_variable(self, key):
        """Deletes a global variable

        :param key: the key of the global variable to be deleted
        :raises exceptions.AttributeError:  if the global variable does not exist
        """
        if self.is_locked(key):
            raise RuntimeError("Global variable is locked")

        self.__dictionary_lock.acquire()
        if key in self.__global_variable_dictionary:
            access_key = self.lock_variable(key)
            del self.__global_variable_dictionary[key]
            self.unlock_variable(key, access_key)
            del self.__variable_locks[key]
            del self.__variable_references[key]
        else:
            raise AttributeError("Global variable %s does not exist!" % str(key))
        self.__dictionary_lock.release()
        logger.debug("Global variable %s was deleted!" % str(key))

    @Observable.observed
    def lock_variable(self, key):
        """Locks a global variable

        :param key: the key of the global variable to be locked
        """
        if key in self.__variable_locks:
            self.__variable_locks[key].acquire()
            access_key = global_variable_id_generator()
            self.__access_keys[key] = access_key
            return access_key

    @Observable.observed
    def unlock_variable(self, key, access_key):
        """Unlocks a global variable

        :param key: the key of the global variable to be unlocked
        :param access_key: the access key to be able to unlock the global variable
        :raises exceptions.AttributeError: if the global variable does not exist
        :raises exceptions.RuntimeError: if the wrong access key is passed
        """
        if self.__access_keys[key] == access_key:
            if key in self.__variable_locks:
                self.__variable_locks[key].release()
            else:
                raise AttributeError("Global variable %s does not exist!" % str(key))
        else:
            raise RuntimeError("Wrong access key for accessing global variable")

    @Observable.observed
    def set_locked_variable(self, key, access_key, value):
        """Set an already locked global variable

        :param key: the key of the global variable to be set
        :param access_key: the access key to the already locked global variable
        :param value: the new value of the global variable
        """
        return self.set_variable(key, value, per_reference=False, access_key=access_key)

    def get_locked_variable(self, key, access_key):
        """Returns the value of an global variable that is already locked

        :param key: the key of the global variable
        :param access_key: the access_key to the global variable that is already locked
        """
        return self.get_variable(key, per_reference=False, access_key=access_key)

    def variable_exist(self, key):
        """Checks if a global variable exist

        :param key: the name of the global variable
        """
        return key in self.__global_variable_dictionary

    variable_exists = variable_exist

    def data_type_exist(self, key):
        """Checks if a global variable exist

        :param key: the name of the global variable
        """
        return key in self.__global_variable_type_dictionary

    def is_locked(self, key):
        """Returns the status of the lock of a global variable

        :param key: the unique key of the global variable
        :return:
        """
        if key in self.__variable_locks:
            return self.__variable_locks[key].locked()
        return False

#########################################################################
# Properties for all class fields that must be observed by gtkmvc
#########################################################################

    @property
    def global_variable_dictionary(self):
        """Property for the _global_variable_dictionary field"""
        dict_copy = {}
        for key, value in self.__global_variable_dictionary:
            if key in self.__variable_references and self.__variable_references[key]:
                dict_copy[key] = value
            else:
                dict_copy[key] = copy.deepcopy(value)

        return dict_copy

    def get_all_keys(self):
        """Returns all variable names in the GVM

        :return: Keys of all variables
        """
        return self.__global_variable_dictionary.keys()

    def get_representation(self, key):
        if not self.variable_exist(key):
            return None
        return self.__global_variable_dictionary[key]

    def get_data_type(self, key):
        if not self.data_type_exist(key):
            return None
        return self.__global_variable_type_dictionary[key]

    @staticmethod
    def check_value_and_type(value, data_type):
        """Checks if a given value is of a specific type

        :param value: the value to check
        :param data_type: the type to be checked upon
        :return:
        """
        if value is not None and data_type is not type(None):
            if not isinstance(value, data_type):
                raise TypeError("Value: '{0}' is not of data type: '{1}', value type: {2}".format(value, data_type , type(value)))
