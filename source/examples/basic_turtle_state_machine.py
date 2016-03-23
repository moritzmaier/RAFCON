from twisted.internet import gtk2reactor

gtk2reactor.install()

from twisted.internet import reactor

import logging
import sys
import os
import gtk
import signal

from rafcon.utils import log
from rafcon.mvc.controllers import MainWindowController
from rafcon.mvc.views.main_window import MainWindowView
from rafcon.statemachine.states.hierarchy_state import HierarchyState
from rafcon.statemachine.states.execution_state import ExecutionState
from rafcon.statemachine.states.preemptive_concurrency_state import PreemptiveConcurrencyState
import rafcon.statemachine.singleton
import rafcon.mvc.singleton
from rafcon.mvc.config import global_gui_config
from rafcon.mvc.runtime_config import global_runtime_config
from rafcon.network.network_config import global_net_config
from rafcon.statemachine.config import global_config
from rafcon.statemachine.states.library_state import LibraryState


def setup_logger():
    import sys

    # Apply defaults to logger of gtkmvc
    for handler in logging.getLogger('gtkmvc').handlers:
        logging.getLogger('gtkmvc').removeHandler(handler)
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(logging.Formatter("%(asctime)s: %(levelname)-8s - %(name)s:  %(message)s"))
    stdout.setLevel(logging.DEBUG)
    logging.getLogger('gtkmvc').addHandler(stdout)

    # Set logging level
    # logging.getLogger('statemachine.state').setLevel(logging.DEBUG)
    # logging.getLogger('controllers.state_properties').setLevel(logging.DEBUG)


def create_turtle_statemachine():
    basic_turtle_demo_state = HierarchyState("BasicTurtleDemo")
    basic_turtle_demo_state.add_outcome("Success", 0)

    init_ros_node = LibraryState("ros_libraries", "init_ros_node", "0.1", "init ros node")

    basic_turtle_demo_state.add_state(init_ros_node)
    basic_turtle_demo_state.set_start_state(init_ros_node.state_id)

    ########################################################
    # Turtle Concurrency State
    ########################################################

    preemptive_concurrency_state = PreemptiveConcurrencyState("Turtle Concurrency State")
    preemptive_concurrency_state.add_outcome("Success", 0)
    basic_turtle_demo_state.add_state(preemptive_concurrency_state)
    basic_turtle_demo_state.add_transition(init_ros_node.state_id, 0, preemptive_concurrency_state.state_id, None)
    basic_turtle_demo_state.add_transition(preemptive_concurrency_state.state_id, 0, None, 0)

    ########################################################
    # Subscribe to turtle position concurrency State
    ########################################################

    subscribe_to_turtle_position_hierarchy_state = HierarchyState("Turtle Position Subscriber Hierarchy State")

    preemptive_concurrency_state.add_state(subscribe_to_turtle_position_hierarchy_state)

    spawn_turtle = LibraryState("turtle_libraries", "turtle_position_subscriber", "0.1", "subscribe to turtle position")
    subscribe_to_turtle_position_hierarchy_state.add_state(spawn_turtle)
    subscribe_to_turtle_position_hierarchy_state.set_start_state(spawn_turtle.state_id)
    subscribe_to_turtle_position_hierarchy_state.add_transition(spawn_turtle.state_id, 0, spawn_turtle.state_id, None)

    ########################################################
    # Move Turtle Hierarchy State
    ########################################################
    move_turtle_hierarchy_state = HierarchyState("Move Turtle Hierarchy State")
    move_turtle_hierarchy_state.add_outcome("Success", 0)
    preemptive_concurrency_state.add_state(move_turtle_hierarchy_state)
    preemptive_concurrency_state.add_transition(move_turtle_hierarchy_state.state_id, 0, None, 0)

    spawn_turtle = LibraryState("turtle_libraries", "spawn_turtle", "0.1", "spawn turtle")
    move_turtle_hierarchy_state.add_state(spawn_turtle)
    move_turtle_hierarchy_state.set_start_state(spawn_turtle.state_id)

    wait1 = ExecutionState("Wait1", path="../../test_scripts/tutorials/basic_turtle_demo", filename="wait.py")
    wait1.add_outcome("Success", 0)
    move_turtle_hierarchy_state.add_state(wait1)
    move_turtle_hierarchy_state.add_transition(spawn_turtle.state_id, 0, wait1.state_id, None)

    teleport_turtle = LibraryState("turtle_libraries", "teleport_turtle", "0.1", "teleport turtle")
    move_turtle_hierarchy_state.add_state(teleport_turtle)
    move_turtle_hierarchy_state.add_transition(wait1.state_id, 0, teleport_turtle.state_id, None)

    wait2 = ExecutionState("Wait2", path="../../test_scripts/tutorials/basic_turtle_demo", filename="wait.py")
    wait2.add_outcome("Success", 0)
    move_turtle_hierarchy_state.add_state(wait2)
    move_turtle_hierarchy_state.add_transition(teleport_turtle.state_id, 0, wait2.state_id, None)

    clear_field = LibraryState("turtle_libraries", "clear_field", "0.1", "clear field")
    move_turtle_hierarchy_state.add_state(clear_field)
    move_turtle_hierarchy_state.add_transition(wait2.state_id, 0, clear_field.state_id, None)

    wait3 = ExecutionState("Wait3", path="../../test_scripts/tutorials/basic_turtle_demo", filename="wait.py")
    wait3.add_outcome("Success", 0)
    move_turtle_hierarchy_state.add_state(wait3)
    move_turtle_hierarchy_state.add_transition(clear_field.state_id, 0, wait3.state_id, None)

    set_velocity1 = LibraryState("turtle_libraries", "set_velocity", "0.1", "set velocity1")
    move_turtle_hierarchy_state.add_state(set_velocity1)
    move_turtle_hierarchy_state.add_transition(wait3.state_id, 0, set_velocity1.state_id, None)

    wait4 = ExecutionState("Wait4", path="../../test_scripts/tutorials/basic_turtle_demo", filename="wait_medium.py")
    wait4.add_outcome("Success", 0)
    move_turtle_hierarchy_state.add_state(wait4)
    move_turtle_hierarchy_state.add_transition(set_velocity1.state_id, 0, wait4.state_id, None)

    # read_turtle_position = ExecutionState("Read turtle position",
    #                                       path="../../test_scripts/tutorials/basic_turtle_demo",
    #                                       filename="read_turtle_position.py")
    # turtle_name_input = read_turtle_position.add_input_data_port("turtle_name", "str", "new_turtle")
    # move_turtle_hierarchy_state.add_state(read_turtle_position)
    # move_turtle_hierarchy_state.add_transition(wait4.state_id, 0, read_turtle_position.state_id, None)

    move_to_position = LibraryState("turtle_libraries", "move_to_position", "0.1", "move to position")
    move_turtle_hierarchy_state.add_state(move_to_position)
    move_turtle_hierarchy_state.add_transition(wait4.state_id, 0, move_to_position.state_id, None)

    move_turtle_hierarchy_state.add_transition(move_to_position.state_id, 1, move_to_position.state_id, None)

    kill_turtle = LibraryState("turtle_libraries", "kill_turtle", "0.1", "kill turtle")
    move_turtle_hierarchy_state.add_state(kill_turtle)
    move_turtle_hierarchy_state.add_transition(move_to_position.state_id, 0, kill_turtle.state_id, None)

    move_turtle_hierarchy_state.add_transition(kill_turtle.state_id, 0, None, 0)

    return basic_turtle_demo_state


def run_turtle_demo():
    signal.signal(signal.SIGINT, rafcon.statemachine.singleton.signal_handler)
    # setup logging view first
    setup_logger()
    logger = log.get_logger("turtle demo")

    home_path = os.path.join(os.path.expanduser('~'), '.config/rafcon')
    global_config.load(path=home_path)
    global_gui_config.load(path=home_path)
    global_net_config.load()
    global_runtime_config.load(path=home_path)

    rafcon.statemachine.singleton.library_manager.initialize()

    # basic_turtle_demo_state = create_turtle_statemachine()

    # set base path of global storage
    rafcon.statemachine.singleton.global_storage.base_path = "../../test_scripts/tutorials/basic_turtle_demo_sm"

    # load the state machine
    [state_machine, version, creation_time] = rafcon.statemachine.singleton. \
        global_storage.load_statemachine_from_path("../../test_scripts/tutorials/basic_turtle_demo_sm")

    rafcon.statemachine.singleton.library_manager.initialize()
    main_window_view = MainWindowView()
    rafcon.statemachine.singleton.state_machine_manager.add_state_machine(state_machine)
    sm_manager_model = rafcon.mvc.singleton.state_machine_manager_model

    main_window_controller = MainWindowController(sm_manager_model, main_window_view, editor_type="LogicDataGrouped")
    # main_window_controller = MainWindowController(sm_manager_model, main_window_view, emm_model, gvm_model)

    reactor.run()
    gtk.main()
    logger.debug("Gtk main loop exited!")

    sm = rafcon.statemachine.singleton.state_machine_manager.get_active_state_machine()
    if sm:
        sm.root_state.join()


if __name__ == '__main__':
    cur_path = os.path.abspath(os.path.dirname(__file__))
    test_script_path = os.path.join(cur_path, os.pardir, os.pardir, 'test_scripts')
    sys.path.insert(1, test_script_path)
    run_turtle_demo()