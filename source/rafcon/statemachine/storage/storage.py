"""
.. module:: storage
   :platform: Unix, Windows
   :synopsis: Helper functions to store a state machine in the local file system and load it from there

.. moduleauthor:: Sebastian Brunner
"""

import os
import shutil
import glob
import copy
import yaml

from rafcon.statemachine.state_machine import StateMachine
from rafcon.statemachine.custom_exceptions import LibraryNotFoundException
from rafcon.statemachine.enums import DEFAULT_SCRIPT_PATH

from rafcon.utils.filesystem import read_file, write_file
from rafcon.utils import storage_utils
from rafcon.utils import log
logger = log.get_logger(__name__)


LIBRARY_NOT_FOUND_DUMMY_STATE_NAME = "LIBRARY NOT FOUND DUMMY STATE"

#: File names for various purposes
FILE_NAME_META_DATA = 'meta_data.json'
FILE_NAME_META_DATA_OLD = 'gui_gtk.json'
FILE_NAME_CORE_DATA = 'core_data.json'
FILE_NAME_CORE_DATA_OLD = 'meta.json'
SCRIPT_FILE = 'script.py'
STATEMACHINE_FILE = 'statemachine.json'
STATEMACHINE_FILE_OLD = 'statemachine.yaml'


# clean the DEFAULT_SCRIPT_PATH folder at each program start
if os.path.exists(DEFAULT_SCRIPT_PATH):
    files = glob.glob(os.path.join(DEFAULT_SCRIPT_PATH, "*"))
    for f in files:
        shutil.rmtree(f)


#: each state machine holds a list of paths that are going to be removed while saving the state machine
_paths_to_remove_before_sm_save = {}


def mark_path_for_removal_for_sm_id(state_machine_id, path):
    """Mark path for removal

    The path is removed when the state machine of the specified state machine id is saved.

    :param int state_machine_id: the state machine id the path belongs to
    :param str path: the path to a state that is to be deleted
    """
    if state_machine_id not in _paths_to_remove_before_sm_save:
        _paths_to_remove_before_sm_save[state_machine_id] = []
    _paths_to_remove_before_sm_save[state_machine_id].append(path)


def unmark_path_for_removal_for_sm_id(state_machine_id, path):
    """Unmark path for removal

    Removes the given path for teh given state machine id from the list of path to be removed.

    :param int state_machine_id: the state machine id the path belongs to
    :param str path: the path to a state that should not be removed
    """
    if state_machine_id in _paths_to_remove_before_sm_save:
        if path in _paths_to_remove_before_sm_save[state_machine_id]:
            _paths_to_remove_before_sm_save[state_machine_id].remove(path)


def remove_state_machine_paths(state_machine_id):
    """Removes all paths marked for removal for the given state machine

    :param int state_machine_id: ID of the state machine whos paths are to be deleted
    """
    if state_machine_id in _paths_to_remove_before_sm_save:
        for path in _paths_to_remove_before_sm_save[state_machine_id]:
            if os.path.exists(path):
                shutil.rmtree(path)


def clean_state_machine_paths(state_machine_id):
    """Empties the list of paths marked for removal for the given state machine

    :param int state_machine_id: ID of the state machine whos paths are to be emptied
    """
    if state_machine_id in _paths_to_remove_before_sm_save:
        del _paths_to_remove_before_sm_save[state_machine_id]


def save_state_machine_to_path(state_machine, base_path, delete_old_state_machine=False, save_as=False,
                              temporary_storage=False):
    """Saves a state machine recursively to the file system

    :param rafcon.statemachine.state_machine.StateMachine state_machine: the state_machine to be saved
    :param str base_path: base_path to which all further relative paths refers to
    :param bool delete_old_state_machine: Whether to delete any state machine existing at the given path
    :param bool save_as: Whether to create a copy of the state machine
    :param bool temporary_storage: Whether to use a temporary storage for the state machine
    """

    if not temporary_storage:
        if save_as:
            # A copy of the state machine is created at a new place in the filesystem. Therefore, there are no paths
            # to be removed
            clean_state_machine_paths(state_machine.state_machine_id)
        else:
            # When saving the state machine, all changed made by the user should finally take affect on the
            # filesystem. This includes the removal of all information about deleted states.
            remove_state_machine_paths(state_machine.state_machine_id)

    root_state = state_machine.root_state

    # clean old path first
    if delete_old_state_machine:
        if os.path.exists(base_path):
            shutil.rmtree(base_path)

    # Ensure that path is existing
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    old_update_time = state_machine.last_update
    state_machine.last_update = storage_utils.get_current_time_string()
    state_machine_dict = state_machine.to_dict()
    storage_utils.write_dict_to_json(state_machine_dict, os.path.join(base_path, STATEMACHINE_FILE))
    storage_utils.write_dict_to_yaml(state_machine_dict, os.path.join(base_path, STATEMACHINE_FILE_OLD))

    # set the file_system_path of the state machine
    if not temporary_storage:
        state_machine.file_system_path = copy.copy(base_path)
    else:
        state_machine.last_update = old_update_time

    # add root state recursively
    save_state_recursively(root_state, base_path, "", temporary_storage)

    if state_machine.marked_dirty and not temporary_storage:
        state_machine.marked_dirty = False
    logger.debug("State machine with id {0} was saved at {1}".format(state_machine.state_machine_id, base_path))


def save_script_file_for_state_and_source_path(state, base_path, state_path, temporary_storage=False):
    """Saves the script file for a state to the directory of the state

    The script name will be set to the SCRIPT_FILE constant.
    :param state: The state of which the script file should be saved
    :param str base_path: The path to the state machone
    :param str state_path: The path of the state meta file
    :return:
    """
    from rafcon.statemachine.states.execution_state import ExecutionState
    if isinstance(state, ExecutionState):
        state_path_full = os.path.join(base_path, state_path)
        source_script_file = os.path.join(state.script.path, state.script.filename)
        destination_script_file = os.path.join(state_path_full, SCRIPT_FILE)

        try:
            write_file(destination_script_file, state.script_text)
        except Exception:
            logger.exception("Storing of script file failed: {0} -> {1}".format(state.get_path(),
                                                                                destination_script_file))
            raise

        if not source_script_file == destination_script_file and not temporary_storage:
            state.script.filename = SCRIPT_FILE
            state.script.path = state_path_full



def save_state_recursively(state, base_path, parent_path, temporary_storage=False):
    """Recursively saves a state to a yaml file

    It calls this method on all its substates.

    :param state: State to be stored
    :param base_path: Path to the state machine
    :param parent_path: Path to the parent state
    :return:
    """
    from rafcon.statemachine.states.execution_state import ExecutionState
    from rafcon.statemachine.states.container_state import ContainerState

    state_path = os.path.join(parent_path, str(state.state_id))
    state_path_full = os.path.join(base_path, state_path)
    if not os.path.exists(state_path_full):
        os.makedirs(state_path_full)
    if isinstance(state, ExecutionState):
        save_script_file_for_state_and_source_path(state, base_path, state_path, temporary_storage)

    storage_utils.write_dict_to_json(state, os.path.join(state_path_full, FILE_NAME_CORE_DATA))

    # create yaml files for all children
    if isinstance(state, ContainerState):
        for state in state.states.itervalues():
            save_state_recursively(state, base_path, state_path, temporary_storage)


def load_state_machine_from_path(base_path):
    """Loads a state machine from the given path

    :param base_path: An optional base path for the state machine.
    :return: a tuple of the loaded container state, the version of the state and the creation time
    :raises: ValueError, IOError
    """
    logger.debug("Loading state machine from path {0}...".format(base_path))

    state_machine_file_path = os.path.join(base_path, STATEMACHINE_FILE)
    state_machine_file_path_old = os.path.join(base_path, STATEMACHINE_FILE_OLD)

    if not os.path.exists(state_machine_file_path) and not os.path.exists(state_machine_file_path_old):
        base_path = os.path.dirname(base_path)
        state_machine_file_path = os.path.join(base_path, STATEMACHINE_FILE)
        state_machine_file_path_old = os.path.join(base_path, STATEMACHINE_FILE_OLD)

        if not os.path.exists(state_machine_file_path) and not os.path.exists(state_machine_file_path_old):
            raise ValueError("Provided path doesn't contain a valid state machine: {0}".format(base_path))

    if os.path.exists(state_machine_file_path):
        state_machine_dict = storage_utils.load_dict_from_json(state_machine_file_path)
        state_machine = StateMachine.from_dict(state_machine_dict)
        root_state_id = state_machine_dict['root_state_id']

    # TODO: Remove this with next minor release
    else:
        stream = file(state_machine_file_path_old, 'r')
        tmp_dict = yaml.load(stream)
        root_state_id = tmp_dict['root_state']
        version = tmp_dict['version']
        # Prevents storage as datetime object
        creation_time = str(tmp_dict['creation_time'])
        if 'last_update' not in tmp_dict:
            last_update = creation_time
        else:
            last_update = tmp_dict['last_update']
        state_machine = StateMachine(version=version, creation_time=creation_time, last_update=last_update)

    root_state_path = os.path.join(base_path, root_state_id)
    state_machine.file_system_path = base_path
    state_machine.root_state = load_state_recursively(parent=state_machine, state_path=root_state_path)
    state_machine.marked_dirty = False

    hierarchy_level = 0
    number_of_states, hierarchy_level = state_machine.root_state.get_states_statistics(hierarchy_level)
    logger.debug("Loaded state machine ({1}) has {0} states. (Max hierarchy level {2})".format(
        number_of_states, base_path, hierarchy_level))
    logger.debug("Loaded state machine ({1}) has {0} transitions.".format(
        state_machine.root_state.get_number_of_transitions(), base_path))

    return state_machine


def load_state_from_path(state_path):
    """Loads a state from a given path

    :param state_path: The path of the state on the file system.
    :return: the loaded state
    """
    return load_state_recursively(parent=None, state_path=state_path)


def load_state_recursively(parent, state_path=None):
    """Recursively loads the state

    It calls this method on each sub-state of a container state.

    :param parent:  the root state of the last load call to which the loaded state will be added
    :param state_path: the path on the filesystem where to find eht meta file for the state
    :return:
    """
    from rafcon.statemachine.states.state import State
    from rafcon.statemachine.states.hierarchy_state import HierarchyState

    path_core_data = os.path.join(state_path, FILE_NAME_CORE_DATA)

    # TODO: Should be removed with next minor release
    if not os.path.exists(path_core_data):
        path_core_data = os.path.join(state_path, FILE_NAME_CORE_DATA_OLD)

    try:
        state_info = load_data_file(path_core_data)
    except ValueError, e:
        logger.exception("Error while loading state data: {0}".format(e))
    except LibraryNotFoundException, e:
        logger.error("Library could not be loaded: {0}\n"
                     "Skipping library and continuing loading the state machine".format(str(e.message)))
        state_info = storage_utils.load_dict_from_json(path_core_data, as_dict=True)
        state_id = state_info["state_id"]
        dummy_state = HierarchyState(LIBRARY_NOT_FOUND_DUMMY_STATE_NAME, state_id=state_id)
        # set parent of dummy state
        if isinstance(parent, State):
            parent.add_state(dummy_state, storage_load=True)
        else:
            dummy_state.parent = parent
        return dummy_state

    # Transitions and data flows are not added when loading a state, as also states are not added.
    # We have to wait until the child states are loaded, before adding transitions and data flows, as otherwise the
    # validity checks for transitions and data flows would fail
    if not isinstance(state_info, tuple):
        state = state_info
    else:
        state = state_info[0]
        transitions = state_info[1]
        data_flows = state_info[2]

    # set parent of state
    if parent:
        if isinstance(parent, State):
            parent.add_state(state, storage_load=True)
        else:
            state.parent = parent
    else:
        # as the parent is None the state cannot calculate its path, therefore the path is cached for it
        state.set_file_system_path(state_path)

    from rafcon.statemachine.states.execution_state import ExecutionState
    if isinstance(state, ExecutionState):
        script = read_file(state.script.path, state.script.filename)
        state.script_text = script

    one_of_my_child_states_not_found = False

    # load child states
    for p in os.listdir(state_path):
        child_state_path = os.path.join(state_path, p)
        if os.path.isdir(child_state_path):
            child_state = load_state_recursively(state, child_state_path)
            if child_state.name is LIBRARY_NOT_FOUND_DUMMY_STATE_NAME:
                one_of_my_child_states_not_found = True

    if one_of_my_child_states_not_found:
        # omit adding transitions and data flows in this case
        pass
    else:
        # Now we can add transitions and data flows, as all child states were added
        if isinstance(state_info, tuple):
            state.transitions = transitions
            state.data_flows = data_flows

    return state


def load_data_file(filename):
    if os.path.exists(filename):
        return storage_utils.load_dict_from_json(filename)
    raise ValueError("Data file not found: {0}".format(filename))
