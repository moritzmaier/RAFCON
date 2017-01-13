import time

# core elements
from rafcon.core.storage import storage
import rafcon.core.singleton
from rafcon.core.states.execution_state import ExecutionState
from rafcon.core.states.hierarchy_state import HierarchyState

# test environment elements
import testing_utils
import pytest


def wait_and_join(state_machine, state_id):
    time.sleep(0.05)  # let the state start properly
    state_machine.get_state_by_path(state_id).join()
    time.sleep(0.05)  # let the hierarchy properly chose the next state


def test_custom_entry_point(caplog):

    testing_utils.test_multithreading_lock.acquire()

    testing_utils.remove_all_libraries()
    rafcon.core.singleton.state_machine_manager.delete_all_state_machines()
    rafcon.core.singleton.library_manager.initialize()

    state_machine = storage.load_state_machine_from_path(testing_utils.get_test_sm_path(
        "unit_test_state_machines/stepping_test"))

    rafcon.core.singleton.state_machine_manager.add_state_machine(state_machine)

    rafcon.core.singleton.state_machine_execution_engine.step_mode()
    time.sleep(0.2)  # let the state machine start properly

    # sm structure

    # GLSUJY
    # GLSUJY/PXTKIH
    # GLSUJY/NDIVLD
    # GLSUJY/SFZGMH

    # GLSUJY/SMCOIB
    # GLSUJY/SMCOIB/YSBJGK
    # GLSUJY/SMCOIB/OUWQUJ
    # GLSUJY/SMCOIB/UGGFFI

    rafcon.core.singleton.state_machine_execution_engine.step_over()
    wait_and_join(state_machine, "GLSUJY/PXTKIH")
    rafcon.core.singleton.state_machine_execution_engine.step_over()
    wait_and_join(state_machine, "GLSUJY/NDIVLD")
    rafcon.core.singleton.state_machine_execution_engine.step_over()
    wait_and_join(state_machine, "GLSUJY/SFZGMH")
    rafcon.core.singleton.state_machine_execution_engine.step_over()
    wait_and_join(state_machine, "GLSUJY/SMCOIB")

    rafcon.core.singleton.state_machine_execution_engine.step_into()
    wait_and_join(state_machine, "GLSUJY/PXTKIH")
    rafcon.core.singleton.state_machine_execution_engine.step_into()
    wait_and_join(state_machine, "GLSUJY/NDIVLD")
    rafcon.core.singleton.state_machine_execution_engine.step_into()
    wait_and_join(state_machine, "GLSUJY/SFZGMH")
    rafcon.core.singleton.state_machine_execution_engine.step_into() # step into hierarchy state GLSUJY/SMCOIB
    rafcon.core.singleton.state_machine_execution_engine.step_into()
    wait_and_join(state_machine, "GLSUJY/SMCOIB/YSBJGK")

    rafcon.core.singleton.state_machine_execution_engine.step_out()
    wait_and_join(state_machine, "GLSUJY/SMCOIB")

    rafcon.core.singleton.state_machine_execution_engine.stop()
    rafcon.core.singleton.state_machine_execution_engine.join()

    assert rafcon.core.singleton.global_variable_manager.get_variable("bottles") == 95

    testing_utils.test_multithreading_lock.release()
    testing_utils.assert_logger_warnings_and_errors(caplog)


if __name__ == '__main__':
    test_custom_entry_point(None)
    # pytest.main([__file__])