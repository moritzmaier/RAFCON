# core elements
from rafcon.statemachine.states.execution_state import ExecutionState
from rafcon.statemachine.states.preemptive_concurrency_state import PreemptiveConcurrencyState
from rafcon.statemachine.singleton import global_variable_manager as gvm
from rafcon.statemachine.state_machine import StateMachine

# singleton elements
import rafcon.statemachine.singleton

# test environment elements
import utils
import pytest


def create_preemptive_wait_statemachine():
    state1 = ExecutionState("state_1", path=rafcon.__path__[0] + "/../test_scripts", filename="preemptive_wait_test.py")
    state1.add_outcome("FirstOutcome", 3)

    state2 = ExecutionState("state_2", path=rafcon.__path__[0] + "/../test_scripts", filename="preemptive_wait_test.py")
    state2.add_outcome("FirstOutcome", 3)

    ctr_state = PreemptiveConcurrencyState("FirstConcurrencyState")
    ctr_state.add_state(state1)
    ctr_state.add_state(state2)
    ctr_state.add_outcome("end", 3)
    ctr_state.add_transition(state1.state_id, 3, ctr_state.state_id, 3)
    ctr_state.add_transition(state2.state_id, 3, ctr_state.state_id, 3)

    return StateMachine(ctr_state)


def test_preemptive_wait_daemon(caplog):
    utils.test_multithrading_lock.acquire()

    gvm.set_variable('state_1_wait', 0.5)
    gvm.set_variable('state_2_wait', None)

    run_statemachine()

    assert 0.5 < gvm.get_variable('state_1_wait_time')
    # cannot assert this as state 2 may be launched later and will thus have a shorter execution time
    # assert 0.5 < gvm.get_variable('state_2_wait_time')
    assert not gvm.get_variable('state_1_preempted')
    assert gvm.get_variable('state_2_preempted')

    utils.test_multithrading_lock.release()
    utils.assert_logger_warnings_and_errors(caplog)


def run_statemachine():

    preemption_state_sm = create_preemptive_wait_statemachine()
    rafcon.statemachine.singleton.state_machine_manager.add_state_machine(preemption_state_sm)
    rafcon.statemachine.singleton.state_machine_manager.active_state_machine_id = preemption_state_sm.state_machine_id
    rafcon.statemachine.singleton.state_machine_execution_engine.start()
    rafcon.statemachine.singleton.state_machine_execution_engine.join()
    rafcon.statemachine.singleton.state_machine_manager.remove_state_machine(preemption_state_sm.state_machine_id)


def test_preemptive_wait_timeout(caplog):
    utils.test_multithrading_lock.acquire()

    gvm.set_variable('state_1_wait', 0.5)
    gvm.set_variable('state_2_wait', 1.)

    run_statemachine()

    assert 0.5 < gvm.get_variable('state_1_wait_time')
    assert not gvm.get_variable('state_1_preempted')
    assert gvm.get_variable('state_2_preempted')

    utils.test_multithrading_lock.release()
    utils.assert_logger_warnings_and_errors(caplog)


def test_preemptive_wait2_timeout(caplog):
    utils.test_multithrading_lock.acquire()

    gvm.set_variable('state_2_wait', 0.5)
    gvm.set_variable('state_1_wait', 1.)

    run_statemachine()

    assert 0.5 < gvm.get_variable('state_2_wait_time')
    assert gvm.get_variable('state_1_preempted')
    assert not gvm.get_variable('state_2_preempted')

    utils.test_multithrading_lock.release()
    utils.assert_logger_warnings_and_errors(caplog)

if __name__ == '__main__':
    pytest.main([__file__])
