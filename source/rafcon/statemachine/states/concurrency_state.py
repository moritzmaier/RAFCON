"""
.. module:: concurrency_state
   :platform: Unix, Windows
   :synopsis: A module to represent a concurrency state for the state machine

.. moduleauthor:: Sebastian Brunner


"""
from gtkmvc import Observable

from rafcon.statemachine.states.container_state import ContainerState
from rafcon.statemachine.enums import CallType
from rafcon.statemachine.execution.execution_history import CallItem, ReturnItem, ConcurrencyItem
from rafcon.statemachine.enums import StateExecutionState


class ConcurrencyState(ContainerState):
    """A class to represent a concurrency state for the state machine

    The concurrency state holds several child states, that can be container states again
    """

    def __init__(self, name=None, state_id=None, input_keys=None, output_keys=None, outcomes=None,
                 states=None, transitions=None, data_flows=None, start_state_id=None, scoped_variables=None,
                 v_checker=None):
        ContainerState.__init__(self, name, state_id, input_keys, output_keys, outcomes, states, transitions,
                                data_flows, start_state_id, scoped_variables, v_checker)

    def run(self, *args, **kwargs):
        raise NotImplementedError("The ContainerState.run() function has to be implemented!")

    def _check_start_transition(self, start_transition):
        return False, "No start transitions are allowed in concurrency state"

    def setup_forward_or_backward_execution(self):
        if self.backward_execution:
            # pop the return item of this concurrency state to get the correct scoped data
            last_history_item = self.execution_history.pop_last_item()
            assert isinstance(last_history_item, ReturnItem)
            self.scoped_data = last_history_item.scoped_data
            # get the concurrency item for the children execution historys
            concurrency_history_item = self.execution_history.get_last_history_item()
            assert isinstance(concurrency_history_item, ConcurrencyItem)

        else:  # forward_execution
            self.execution_history.add_call_history_item(self, CallType.CONTAINER, self)
            concurrency_history_item = self.execution_history.add_concurrency_history_item(self, len(self.states))
        return concurrency_history_item

    def finalize_backward_execution(self):
        # backward_execution needs to be True to signal the parent container state the backward execution
        self.backward_execution = True
        # pop the ConcurrencyItem as we are leaving the barrier concurrency state
        last_history_item = self.execution_history.pop_last_item()
        assert isinstance(last_history_item, ConcurrencyItem)

        last_history_item = self.execution_history.pop_last_item()
        assert isinstance(last_history_item, CallItem)
        # this copy is convenience and not required here
        self.scoped_data = last_history_item.scoped_data
        # do not write the output of the entry script
        self.state_execution_status = StateExecutionState.WAIT_FOR_NEXT_STATE
        return self.finalize()

        # @Observable.observed
        # def add_transition(self, from_state_id, from_outcome, to_state_id=None, to_outcome=None, transition_id=None):
        #     """Adds a transition to the container state
        #
        #     Note: Either the toState or the toOutcome needs to be "None"
        #
        #     :param from_state_id: The source state of the transition
        #     :param from_outcome: The outcome of the source state to connect the transition to
        #     :param to_state_id: The target state of the transition
        #     :param to_outcome: The target outcome of a container state
        #     :param transition_id: An optional transition id for the new transition
        #     """
        #
        #     transition_id = self.check_transition_id(transition_id)
        #
        #     self.basic_transition_checks(from_state_id, from_outcome, to_state_id, to_outcome, transition_id)
        #
        #     self.check_if_outcome_already_connected(from_state_id, from_outcome)
        #
        #     # in concurrency states only transitions to the parents are allowed
        #     if to_state_id is not None and to_state_id is not self.state_id:  # None means that the target state is
        #  the containing state
        #         raise AttributeError("In concurrency states the to_state must be the container state itself")
        #
        #     self.create_transition(from_state_id, from_outcome, to_state_id, to_outcome, transition_id)
        #
        #     return transition_id
