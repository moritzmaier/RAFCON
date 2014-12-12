"""
.. module:: preemptive_concurrency_state
   :platform: Unix, Windows
   :synopsis: A module to represent a preemptive concurrency state for the state machine

.. moduleauthor:: Sebastian Brunner


"""

from utils import log
logger = log.get_logger(__name__)

from statemachine.outcome import Outcome
from concurrency_state import ConcurrencyState
import Queue


class PreemptiveConcurrencyState(ConcurrencyState):

    def __init__(self, name=None, state_id=None, input_keys=None, output_keys=None, outcomes=None, sm_status=None,
                 states=None, transitions=None, data_flows=None, start_state=None, scoped_variables=None,
                 v_checker=None, path=None, filename=None):

        ConcurrencyState.__init__(self, name, state_id, input_keys, output_keys, outcomes, sm_status, states,
                                  transitions, data_flows, start_state, scoped_variables, v_checker, path, filename)

    def run(self):

        #TODO: make state init and close
        #initialize data structures
        input_data = self.input_data
        output_data = self.output_data
        if not isinstance(input_data, dict):
            raise TypeError("states must be of type dict")
        if not isinstance(output_data, dict):
            raise TypeError("states must be of type dict")
        self.scoped_variables = {}
        self.scoped_results = {}

        self.check_input_data_type(input_data)
        self.add_dict_to_scope_variables(input_data)

        try:
            logger.debug("Starting preemptive concurrency state with id %s" % self._state_id)
            self.enter()

            #infinite Queue size
            concurrency_queue = Queue(maxsize=0)

            queue_ids = 0
            for state in self.states:
                state.concurrency_queue = concurrency_queue
                state.concurrency_queue_id = queue_ids
                queue_ids +=1
                state.start()

            finished_thread_id = concurrency_queue.get()
            self.states[finished_thread_id].join()

            for state in self.states:
                state.preempted = True

            for state in self.states:
                state.join()

            #write output data back to the dictionary
            for output_key, value in output_data.iteritems():
                for data_flow_key, data_flow in self.data_flows.iteritems():
                    if data_flow.to_state is self:
                        if data_flow.from_state is self:
                            output_data[output_key] = self.scoped_variables[output_key].value()
                        else:
                            #primary key for scoped_results is key+state_id
                            output_data[output_key] =\
                                self.scoped_results[output_key+data_flow.from_state.state_id].value()

            self.check_output_data_type(output_data)

            #reset concurrency queue and preempted flag for all child states
            for state in self.states:
                state.concurrency_queue = None
                state.preempted = False

            if self.preempted:
                self.final_outcome = Outcome(2, "preempted")
                return

            self.final_outcome = Outcome(0, "success")
            return

        except RuntimeError:
            self.final_outcome = Outcome(1, "aborted")
            return