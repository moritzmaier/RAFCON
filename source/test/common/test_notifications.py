from gtkmvc.observer import Observer

# core elements
from rafcon.statemachine.states.execution_state import ExecutionState
from rafcon.statemachine.states.hierarchy_state import HierarchyState
from rafcon.statemachine.state_machine import StateMachine

# singleton elements
from rafcon.statemachine.singleton import state_machine_manager
from rafcon.mvc.singleton import state_machine_manager_model

import utils
import pytest

with_print = False

class NotificationLogObserver(Observer):
    """ This observer is a abstract class to counts and store notification
    """

    def __init__(self, model, with_print=False):

        self.log = {"before": {}, "after": {}}
        self.reset()
        self.observed_model = model
        self.with_print = with_print
        self.no_failure = True

        Observer.__init__(self, model)

    def reset(self):
        """ Initiate and reset the log dictionary """

    def get_number_of_notifications(self):
        nr = 0
        for key, l in self.log['before'].iteritems():
            nr += len(l)
        for key, l in self.log['after'].iteritems():
            nr += len(l)
        return nr


class StateNotificationLogObserver(NotificationLogObserver):
    """ This observer counts and stores notification of StateModel-Class
    """

    def __init__(self, model, with_print=False):
        NotificationLogObserver.__init__(self, model, with_print)

    def reset(self):
        self.log = {"before": {'states': [], 'state': [],
                               'outcomes': [], 'input_data_ports': [], 'output_data_ports': [], 'scoped_variables': [],
                               'transitions': [], 'data_flows': [], 'is_start': []},
                    "after": {'states': [], 'state': [],
                              'outcomes': [], 'input_data_ports': [], 'output_data_ports': [], 'scoped_variables': [],
                              'transitions': [], 'data_flows': [], 'is_start': []}}
        self.no_failure = True

    @Observer.observe('states', before=True)
    @Observer.observe("state", before=True)
    @Observer.observe("outcomes", before=True)
    @Observer.observe("input_data_ports", before=True)
    @Observer.observe("output_data_ports", before=True)
    @Observer.observe("scoped_variables", before=True)
    @Observer.observe("transitions", before=True)
    @Observer.observe("data_flows", before=True)
    @Observer.observe("is_start", before=True)
    def notification_before(self, model, prop_name, info):
        # print "parent call_notification - AFTER:\n-%s\n-%s\n-%s\n-%s\n" %\
        #       (prop_name, info.instance, info.method_name, info.result)
        #if info.method_name in self.method_list:
        if prop_name in self.log['before']:
            self.log['before'][prop_name].append({'model': model, 'prop_name': prop_name, 'info': info})
            if self.with_print:
                print "++++++++ log BEFORE instance '%s' and property '%s' in state %s" % \
                      (info.instance, prop_name, self.observed_model.state.name)
                print "observer: ", self
        else:
            print "!!!! NOT a prop_name '%s' to be observed in BEFORE %s %s" % (prop_name, model, info)
            self.no_failure = False

    @Observer.observe('states', after=True)
    @Observer.observe("state", after=True)
    @Observer.observe("outcomes", after=True)
    @Observer.observe("input_data_ports", after=True)
    @Observer.observe("output_data_ports", after=True)
    @Observer.observe("scoped_variables", after=True)
    @Observer.observe("transitions", after=True)
    @Observer.observe("data_flows", after=True)
    @Observer.observe("is_start", after=True)
    def notification_after(self, model, prop_name, info):
        if prop_name in self.log['after']:
            self.log['after'][prop_name].append({'model': model, 'prop_name': prop_name, 'info': info})
            if self.with_print:
                print "++++++++ log AFTER instance '%s' and property '%s' in state %s" % \
                      (info.instance, prop_name, self.observed_model.state.name)
                print "observer: ", self
        else:
            print "!!!! NOT a prop_name '%s' to be observed in AFTER %s %s" % (prop_name, model, info)
            self.no_failure = False


class OutcomeNotificationLogObserver(NotificationLogObserver):
    """ This observer counts and stores notification of a OutcomeModel-Class
    """

    def __init__(self, model, with_print=False):
        NotificationLogObserver.__init__(self, model, with_print)

    def reset(self):
        self.log = {"before": {'outcome': []},
                    "after": {'outcome': []}}
        self.no_failure = True

    @Observer.observe("outcome", before=True)
    def notification_before(self, model, prop_name, info):
        if prop_name in self.log['before']:
            self.log['before'][prop_name].append({'model': model, 'prop_name': prop_name, 'info': info})
            if self.with_print:
                print "++++++++ log BEFORE instance '%s' and property '%s' in outcome %s" % \
                      (info.instance, prop_name, self.observed_model.outcome.name)
        else:
            print "!!!! NOT a prop_name '%s' to be observed in BEFORE" % prop_name
            self.no_failure = False

    @Observer.observe("outcome", after=True)
    def notification_after(self, model, prop_name, info):
        if prop_name in self.log['after']:
            self.log['after'][prop_name].append({'model': model, 'prop_name': prop_name, 'info': info})
            if self.with_print:
                print "++++++++ log AFTER instance '%s' and property '%s' in outcome %s" % \
                      (info.instance, prop_name, self.observed_model.outcome.name)
        else:
            print "!!!! NOT a prop_name '%s' to be observed in AFTER" % prop_name
            self.no_failure = False


class DataPortNotificationLogObserver(NotificationLogObserver):
    """ This observer counts and stores notification for DataPortModel inherent objects which are
    InputPorts and OutputPorts.
    """

    def __init__(self, model, with_print=False):
        NotificationLogObserver.__init__(self, model, with_print)

    def reset(self):
        self.log = {"before": {'data_port': []},
                    "after": {'data_port': []}}
        self.no_failure = True

    @Observer.observe("data_port", before=True)
    def notification_before(self, model, prop_name, info):
        if prop_name in self.log['before']:
            self.log['before'][prop_name].append({'model': model, 'prop_name': prop_name, 'info': info})
            if self.with_print:
                print "++++++++ log BEFORE instance '%s' and property '%s' in data_port %s" % \
                      (info.instance, prop_name, self.observed_model.data_port.name)
        else:
            print "!!!! NOT a prop_name '%s' to be observed in BEFORE" % prop_name
            self.no_failure = False

    @Observer.observe("data_port", after=True)
    def notification_after(self, model, prop_name, info):
        if prop_name in self.log['after']:
            self.log['after'][prop_name].append({'model': model, 'prop_name': prop_name, 'info': info})
            if self.with_print:
                print "++++++++ log AFTER instance '%s' and property '%s' in data_port %s" % \
                      (info.instance, prop_name, self.observed_model.data_port.name)
        else:
            print "!!!! NOT a prop_name '%s' to be observed in AFTER" % prop_name
            self.no_failure = False


class ScopedVariableNotificationLogObserver(NotificationLogObserver):
    """ This observer counts and stores notification for DataPortModel inherent objects which are
    InputPorts and OutputPorts.
    """

    def __init__(self, model, with_print=False):
        NotificationLogObserver.__init__(self, model, with_print)

    def reset(self):
        self.log = {"before": {'scoped_variable': []},
                    "after": {'scoped_variable': []}}
        self.no_failure = True

    @Observer.observe("scoped_variable", before=True)
    def notification_before(self, model, prop_name, info):
        if prop_name in self.log['before']:
            self.log['before'][prop_name].append({'model': model, 'prop_name': prop_name, 'info': info})
            if self.with_print:
                print "++++++++ log BEFORE instance '%s' and property '%s' in scoped_variable %s" % \
                      (info.instance, prop_name, self.observed_model.scoped_variable.name)
        else:
            print "!!!! NOT a prop_name '%s' to be observed in BEFORE" % prop_name
            self.no_failure = False

    @Observer.observe("scoped_variable", after=True)
    def notification_after(self, model, prop_name, info):
        if prop_name in self.log['after']:
            self.log['after'][prop_name].append({'model': model, 'prop_name': prop_name, 'info': info})
            if self.with_print:
                print "++++++++ log AFTER instance '%s' and property '%s' in scoped_variable %s" % \
                      (info.instance, prop_name, self.observed_model.scoped_variable.name)
        else:
            print "!!!! NOT a prop_name '%s' to be observed in AFTER" % prop_name
            self.no_failure = False


class DataFlowNotificationLogObserver(NotificationLogObserver):
    """ This observer counts and stores notification for DataFlowModel.
    """

    def __init__(self, model, with_print=False):
        NotificationLogObserver.__init__(self, model, with_print)

    def reset(self):
        self.log = {"before": {'data_flow': []},
                    "after": {'data_flow': []}}
        self.no_failure = True

    @Observer.observe("data_flow", before=True)
    def notification_before(self, model, prop_name, info):
        if prop_name in self.log['before']:
            self.log['before'][prop_name].append({'model': model, 'prop_name': prop_name, 'info': info})
            if self.with_print:
                print "++++++++ log BEFORE instance '%s' and property '%s' in data_flow %s" % \
                      (info.instance, prop_name, self.observed_model.data_flow)
        else:
            print "!!!! NOT a prop_name '%s' to be observed in BEFORE" % prop_name
            self.no_failure = False

    @Observer.observe("data_flow", after=True)
    def notification_after(self, model, prop_name, info):
        if prop_name in self.log['after']:
            self.log['after'][prop_name].append({'model': model, 'prop_name': prop_name, 'info': info})
            if self.with_print:
                print "++++++++ log AFTER instance '%s' and property '%s' in data_flow %s" % \
                      (info.instance, prop_name, self.observed_model.data_flow)
        else:
            print "!!!! NOT a prop_name '%s' to be observed in AFTER" % prop_name
            self.no_failure = False


class TransitionNotificationLogObserver(NotificationLogObserver):
    """ This observer counts and stores notification for TransitionModel.
    """

    def __init__(self, model, with_print=False):
        NotificationLogObserver.__init__(self, model, with_print)

    def reset(self):
        self.log = {"before": {'transition': []},
                    "after": {'transition': []}}
        self.no_failure = True

    @Observer.observe("transition", before=True)
    def notification_before(self, model, prop_name, info):
        if prop_name in self.log['before']:
            self.log['before'][prop_name].append({'model': model, 'prop_name': prop_name, 'info': info})
            if self.with_print:
                print "++++++++ log BEFORE instance '%s' and property '%s' in transition %s" % \
                      (info.instance, prop_name, self.observed_model.transition)
        else:
            print "!!!! NOT a prop_name '%s' to be observed in BEFORE" % prop_name
            self.no_failure = False

    @Observer.observe("transition", after=True)
    def notification_after(self, model, prop_name, info):
        if prop_name in self.log['after']:
            self.log['after'][prop_name].append({'model': model, 'prop_name': prop_name, 'info': info})
            if self.with_print:
                print "++++++++ log AFTER instance '%s' and property '%s' in transition %s" % \
                      (info.instance, prop_name, self.observed_model.transition)
        else:
            print "!!!! NOT a prop_name '%s' to be observed in AFTER" % prop_name
            self.no_failure = False


# TODO - ScopedData as a part of ContainerStateModel

# TODO - Check all other Core-, Model- and Controller-Classes to find all observables and to do there possible


def create_models(*args, **kargs):

    state1 = ExecutionState('State1')
    output_state1 = state1.add_output_data_port("output", "int")
    input_state1 = state1.add_input_data_port("input", "str", "zero")
    state2 = ExecutionState('State2')
    input_par_state2 = state2.add_input_data_port("par", "int", 0)
    output_res_state2 = state2.add_output_data_port("res", "int")
    state4 = HierarchyState(name='Nested')
    state4.add_outcome('GoGo')
    output_state4 = state4.add_output_data_port("out", "int")
    state5 = ExecutionState('Nested2')
    state5.add_outcome('HereWeGo')
    input_state5 = state5.add_input_data_port("in", "int", 0)
    state3 = HierarchyState(name='State3')
    input_state3 = state3.add_input_data_port("input", "int", 0)
    output_state3 = state3.add_output_data_port("output", "int")
    state3.add_state(state4)
    state3.add_state(state5)
    state3.set_start_state(state4)
    state3.add_scoped_variable("share", "int", 3)
    state3.add_transition(state4.state_id, 0, state5.state_id, None)
    state3.add_transition(state5.state_id, 0, state3.state_id, 0)
    state3.add_data_flow(state4.state_id, output_state4, state5.state_id, input_state5)
    state3.add_outcome('Branch1')
    state3.add_outcome('Branch2')

    ctr_state = HierarchyState(name="Container")
    ctr_state.add_state(state1)
    ctr_state.add_state(state2)
    ctr_state.add_state(state3)
    input_ctr_state = ctr_state.add_input_data_port("ctr_in", "str", "zero")
    output_ctr_state = ctr_state.add_output_data_port("ctr_out", "int")
    ctr_state.set_start_state(state1)
    ctr_state.add_transition(state1.state_id, 0, state2.state_id, None)
    ctr_state.add_transition(state2.state_id, 0, state3.state_id, None)
    ctr_state.add_transition(state3.state_id, 0, ctr_state.state_id, 0)
    ctr_state.add_data_flow(state1.state_id, output_state1, state2.state_id, input_par_state2)
    ctr_state.add_data_flow(state2.state_id, output_res_state2, state3.state_id, input_state3)
    ctr_state.add_data_flow(ctr_state.state_id, input_ctr_state, state1.state_id, input_state1)
    ctr_state.add_data_flow(state3.state_id, output_state3, ctr_state.state_id, output_ctr_state)
    ctr_state.name = "Container"

    ctr_state.add_input_data_port("input", "str", "default_value1")
    ctr_state.add_input_data_port("pos_x", "str", "default_value2")
    ctr_state.add_input_data_port("pos_y", "str", "default_value3")

    ctr_state.add_output_data_port("output", "str", "default_value1")
    ctr_state.add_output_data_port("result", "str", "default_value2")

    scoped_variable1_ctr_state = ctr_state.add_scoped_variable("scoped", "str", "default_value1")
    scoped_variable2_ctr_state = ctr_state.add_scoped_variable("my_var", "str", "default_value1")
    scoped_variable3_ctr_state = ctr_state.add_scoped_variable("ctr", "int", 42)

    ctr_state.add_data_flow(ctr_state.state_id, input_ctr_state, ctr_state.state_id, scoped_variable1_ctr_state)
    ctr_state.add_data_flow(state1.state_id, output_state1, ctr_state.state_id, scoped_variable3_ctr_state)

    state_dict = {'Container': ctr_state, 'State1': state1, 'State2': state2, 'State3': state3, 'Nested': state4, 'Nested2': state5}
    sm = StateMachine(ctr_state)
    state_machine_manager.add_state_machine(sm)

    sm_m = state_machine_manager_model.state_machines[sm.state_machine_id]

    return ctr_state, sm_m, state_dict


def get_state_model_by_path(state_model, path):
    path_elems = path.split('/')
    path_elems.pop(0)
    current_state_model = state_model
    for element in path_elems:
        current_state_model = current_state_model.states[element]
    return current_state_model


def setup_observer_dict_for_state_model(state_model, with_print=False):

    def generate_observer_dict(state_m):
        observer_dict = {state_m.state.get_path(): StateNotificationLogObserver(state_m, with_print)}
        if hasattr(state_m, 'states'):
            for child_state_m in state_m.states.values():
                observer_dict.update(generate_observer_dict(child_state_m))
        return observer_dict

    return generate_observer_dict(state_model)


def check_count_of_model_notifications(model_observer, forecast_dict):
    number_of_all_notifications = 0
    for prop_name, nr_of_notifications in forecast_dict.iteritems():
        if 'parent' in forecast_dict:
            print model_observer
        print "estimated for %s: %s and occured %s" % (prop_name, nr_of_notifications,
                                                       [len(model_observer.log['before'][prop_name]),
                                                       len(model_observer.log['after'][prop_name])])
        # print "path: ", model_observer.observed_model.state.get_path()
        # print "observer: ", model_observer
        assert len(model_observer.log['before'][prop_name]) == nr_of_notifications
        assert len(model_observer.log['after'][prop_name]) == nr_of_notifications
        number_of_all_notifications += 2*nr_of_notifications
    # check if there are unforseen notifications
    # for key, elem in model_observer.log['before'].iteritems():
    #     print key, "      ", elem, "\n"
    # print "\n\n\n\n\n"
    # for key, elem in model_observer.log['after'].iteritems():
    #     print key, "      ", elem, "\n"
    print "over all estimated: %s and occured %s" % (number_of_all_notifications, model_observer.get_number_of_notifications())
    assert model_observer.get_number_of_notifications() == number_of_all_notifications
    assert model_observer.no_failure


def test_outcome_add_remove_notification(caplog):
    [state, sm_model, state_dict] = create_models()
    states_observer_dict = setup_observer_dict_for_state_model(sm_model.root_state, with_print=with_print)
    state_name = 'Nested2'

    #############
    # add outcome
    state_dict['Nested2'].add_outcome('super_geil')

    # check state
    state_model_observer = states_observer_dict[state_dict[state_name].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 1, 'outcomes': 1})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    for path, state_m_observer in states_observer_dict.iteritems():
        state_m_observer.reset()

    ################
    # remove outcome
    state_dict['Nested2'].remove_outcome(2)  # new outcome should be the third one

    # check state
    state_model_observer = states_observer_dict[state_dict[state_name].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 1, 'outcomes': 1})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    utils.assert_logger_warnings_and_errors(caplog)


def test_outcome_modify_notification(caplog):
    # create testbed
    [state, sm_model, state_dict] = create_models()

    # create observer
    states_observer_dict = setup_observer_dict_for_state_model(sm_model.root_state, with_print=with_print)

    ##########################
    # check for ExecutionState
    state_model = get_state_model_by_path(sm_model.root_state, state_dict['Nested2'].get_path())

    ####################################################
    # modify outcome and generate in previous a observer
    outcome_models_observer_dict = {}
    for outcome_id, outcome in state_dict['Nested2'].outcomes.iteritems():
        if not outcome_id < 0:
            outcome_models_observer_dict[outcome_id] = OutcomeNotificationLogObserver(state_model.outcomes[outcome_id],
                                                                                      with_print=with_print)
            outcome.name = "new_name_" + str(outcome_id)

    # check grand-parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': len(state_dict['Nested2'].outcomes)-2})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': len(state_dict['Nested2'].outcomes)-2})

    # check state
    state_model_observer = states_observer_dict[state_dict['Nested2'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'outcomes': len(state_dict['Nested2'].outcomes)-2})

    for outcome_id, outcome_model_observer in outcome_models_observer_dict.iteritems():
        if not outcome_id < 0:
            assert outcome_model_observer.get_number_of_notifications() == 2
        else:
            assert outcome_model_observer.get_number_of_notifications() == 0

    # reset observers
    for path, state_m_observer in states_observer_dict.iteritems():
        state_m_observer.reset()

    ##########################
    # check for ContainerState -> should be unnecessary
    state_model = get_state_model_by_path(sm_model.root_state, state_dict['Nested'].get_path())

    ####################################################
    # modify outcome and generate in previous a observer
    outcome_models_observer_dict = {}
    for outcome_id, outcome in state_dict['Nested'].outcomes.iteritems():
        outcome_models_observer_dict[outcome_id] = OutcomeNotificationLogObserver(state_model.outcomes[outcome_id],
                                                                                  with_print=with_print)
        outcome.name = "new_name_" + str(outcome_id)

    # check grand-parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': len(state_dict['Nested'].outcomes)})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': len(state_dict['Nested'].outcomes)})

    # check state
    state_model_observer = states_observer_dict[state_dict['Nested'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'outcomes': len(state_dict['Nested'].outcomes)})

    for outcome_id, outcome_model_observer in outcome_models_observer_dict.iteritems():
        assert outcome_model_observer.get_number_of_notifications() == 2

    utils.assert_logger_warnings_and_errors(caplog)


def test_input_port_add_remove_notification(caplog):
    # create testbed
    [state, sm_model, state_dict] = create_models()

    #create observer
    states_observer_dict = setup_observer_dict_for_state_model(sm_model.root_state, with_print=with_print)

    #####################
    # add input_data_port
    new_input_data_port_id = state_dict['Nested2'].add_input_data_port(name='new_input')

    # check state
    state_model_observer = states_observer_dict[state_dict['Nested2'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 1, 'input_data_ports': 1})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    for path, state_m_observer in states_observer_dict.iteritems():
        state_m_observer.reset()

    ########################
    # remove input_data_port
    state_dict['Nested2'].remove_input_data_port(new_input_data_port_id)  # new outcome should be the third one

    # check state
    state_model_observer = states_observer_dict[state_dict['Nested2'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 1, 'input_data_ports': 1})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    utils.assert_logger_warnings_and_errors(caplog)


def test_input_port_modify_notification(caplog):

    def check_input_notifications(input_observer, states_obs_dict, _state_dict, forecast=1):

        # check grand-parent
        state_model_observer = states_obs_dict[_state_dict['Container'].get_path()]
        check_count_of_model_notifications(state_model_observer, {'states': forecast})

        # check parent
        state_model_observer = states_obs_dict[_state_dict['State3'].get_path()]
        check_count_of_model_notifications(state_model_observer, {'states': forecast})

        # check state
        state_model_observer = states_obs_dict[_state_dict['Nested2'].get_path()]
        check_count_of_model_notifications(state_model_observer, {'input_data_ports': forecast})

        print "input_data_port_model over all estimated %s occurred %s" % \
              (input_observer.get_number_of_notifications(), 2*forecast)
        assert input_observer.get_number_of_notifications() == 2*forecast

    # create testbed
    [state, sm_model, state_dict] = create_models()
    new_input_data_port_id = state_dict['Nested2'].add_input_data_port(name='new_input', data_type='str')

    # create observer
    state_model_nested2 = get_state_model_by_path(sm_model.root_state, state_dict['Nested2'].get_path())
    port_model = None
    for input_data_port_model in state_model_nested2.input_data_ports:
        if input_data_port_model.data_port.data_port_id == new_input_data_port_id:
            port_model = input_data_port_model
    assert port_model
    input_port_observer = DataPortNotificationLogObserver(port_model)

    states_m_observer_dict = setup_observer_dict_for_state_model(sm_model.root_state, with_print=with_print)
    ################################
    # check for modification of name
    state_dict['Nested2'].input_data_ports[new_input_data_port_id].name = 'changed_new_input_name'
    check_input_notifications(input_port_observer, states_m_observer_dict, state_dict, forecast=1)

    #####################################
    # check for modification of data_type
    state_dict['Nested2'].input_data_ports[new_input_data_port_id].data_type = 'int'
    check_input_notifications(input_port_observer, states_m_observer_dict, state_dict, forecast=2)

    #########################################
    # check for modification of default_value
    state_dict['Nested2'].input_data_ports[new_input_data_port_id].default_value = 5
    check_input_notifications(input_port_observer, states_m_observer_dict, state_dict, forecast=3)

    ###########################################
    # check for modification of change_datatype
    state_dict['Nested2'].input_data_ports[new_input_data_port_id].change_data_type(data_type='str',
                                                                                    default_value='awesome_tool')
    check_input_notifications(input_port_observer, states_m_observer_dict, state_dict, forecast=5)

    utils.assert_logger_warnings_and_errors(caplog)


def test_output_port_add_remove_notification(caplog):
    # create testbed
    [state, sm_model, state_dict] = create_models()

    #create observer
    states_observer_dict = setup_observer_dict_for_state_model(sm_model.root_state, with_print=with_print)

    ######################
    # add output data port
    new_output_data_port_id = state_dict['Nested2'].add_output_data_port(name='new_output', data_type='str')

    # check state
    state_model_observer = states_observer_dict[state_dict['Nested2'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 1, 'output_data_ports': 1})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    for path, state_m_observer in states_observer_dict.iteritems():
        state_m_observer.reset()

    #########################
    # remove output data port
    state_dict['Nested2'].remove_output_data_port(new_output_data_port_id)  # new outcome should be the third one

    # check state
    state_model_observer = states_observer_dict[state_dict['Nested2'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 1, 'output_data_ports': 1})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    utils.assert_logger_warnings_and_errors(caplog)


def test_output_port_modify_notification(caplog):

    def check_output_notifications(output_observer, states_obs_dict, _state_dict, forecast=1):

        # check grand-parent
        state_model_observer = states_obs_dict[_state_dict['Container'].get_path()]
        check_count_of_model_notifications(state_model_observer, {'states': forecast})

        # check parent
        state_model_observer = states_obs_dict[_state_dict['State3'].get_path()]
        check_count_of_model_notifications(state_model_observer, {'states': forecast})

        # check state
        state_model_observer = states_obs_dict[_state_dict['Nested2'].get_path()]
        check_count_of_model_notifications(state_model_observer, {'output_data_ports': forecast})

        print "output_data_port_model over all estimated %s occurred %s" % \
              (output_observer.get_number_of_notifications(), 2*forecast)
        assert output_observer.get_number_of_notifications() == 2*forecast

    # create testbed
    [state, sm_model, state_dict] = create_models()
    new_output_data_port_id = state_dict['Nested2'].add_output_data_port(name='new_output', data_type='str')

    # create observer
    state_model_nested2 = get_state_model_by_path(sm_model.root_state, state_dict['Nested2'].get_path())
    port_model = None
    for output_data_port_model in state_model_nested2.output_data_ports:
        if output_data_port_model.data_port.data_port_id == new_output_data_port_id:
            port_model = output_data_port_model
    assert port_model
    output_port_observer = DataPortNotificationLogObserver(port_model)

    states_m_observer_dict = setup_observer_dict_for_state_model(sm_model.root_state, with_print=with_print)

    ################################
    # check for modification of name
    state_dict['Nested2'].output_data_ports[new_output_data_port_id].name = 'changed_new_output_name'
    check_output_notifications(output_port_observer, states_m_observer_dict, state_dict, forecast=1)

    #####################################
    # check for modification of data_type
    state_dict['Nested2'].output_data_ports[new_output_data_port_id].data_type = 'int'
    check_output_notifications(output_port_observer, states_m_observer_dict, state_dict, forecast=2)

    #########################################
    # check for modification of default_value
    state_dict['Nested2'].output_data_ports[new_output_data_port_id].default_value = 5
    check_output_notifications(output_port_observer, states_m_observer_dict, state_dict, forecast=3)

    ###########################################
    # check for modification of change_datatype
    state_dict['Nested2'].output_data_ports[new_output_data_port_id].change_data_type(data_type='str',
                                                                                      default_value='awesome_tool')
    check_output_notifications(output_port_observer, states_m_observer_dict, state_dict, forecast=5)

    utils.assert_logger_warnings_and_errors(caplog)


def test_scoped_variable_add_remove_notification(caplog):
    # create testbed
    [state, sm_model, state_dict] = create_models()

    # create observer
    states_observer_dict = setup_observer_dict_for_state_model(sm_model.root_state, with_print=with_print)

    #####################
    # add scoped variable
    new_scoped_variable_port_id = state_dict['Nested'].add_scoped_variable(name='new_scoped_var')

    # check state
    state_model_observer = states_observer_dict[state_dict['Nested'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 1, 'scoped_variables': 1})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    for path, state_m_observer in states_observer_dict.iteritems():
        state_m_observer.reset()

    ########################
    # remove scoped variable
    state_dict['Nested'].remove_scoped_variable(new_scoped_variable_port_id)  # new outcome should be the third one

    # check state
    state_model_observer = states_observer_dict[state_dict['Nested'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 1, 'scoped_variables': 1})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    utils.assert_logger_warnings_and_errors(caplog)


def test_scoped_variable_modify_notification(caplog):

    def check_output_notifications(output_observer, states_obs_dict, _state_dict, forecast=1):

        # check grand-parent
        state_model_observer = states_obs_dict[_state_dict['Container'].get_path()]
        check_count_of_model_notifications(state_model_observer, {'states': forecast})

        # check parent
        state_model_observer = states_obs_dict[_state_dict['State3'].get_path()]
        check_count_of_model_notifications(state_model_observer, {'states': forecast})

        # check state
        state_model_observer = states_obs_dict[_state_dict['Nested'].get_path()]
        check_count_of_model_notifications(state_model_observer, {'scoped_variables': forecast})

        print "scoped_variable_model over all estimated %s occurred %s" % \
              (output_observer.get_number_of_notifications(), 2*forecast)
        assert output_observer.get_number_of_notifications() == 2*forecast

    # create testbed
    [state, sm_model, state_dict] = create_models()
    new_scoped_variable_id = state_dict['Nested'].add_scoped_variable(name='new_output', data_type='str')

    # create observer
    state_model_nested2 = get_state_model_by_path(sm_model.root_state, state_dict['Nested'].get_path())
    scoped_variable_model = None
    for scoped_variable_model in state_model_nested2.scoped_variables:
        if scoped_variable_model.scoped_variable.data_port_id == new_scoped_variable_id:
            scoped_variable_model = scoped_variable_model
    assert scoped_variable_model
    scoped_variable_observer = ScopedVariableNotificationLogObserver(scoped_variable_model)

    states_m_observer_dict = setup_observer_dict_for_state_model(sm_model.root_state, with_print=with_print)

    ################################
    # check for modification of name
    state_dict['Nested'].scoped_variables[new_scoped_variable_id].name = 'changed_new_scoped_var_name'
    check_output_notifications(scoped_variable_observer, states_m_observer_dict, state_dict, forecast=1)

    #####################################
    # check for modification of data_type
    state_dict['Nested'].scoped_variables[new_scoped_variable_id].data_type = 'int'
    check_output_notifications(scoped_variable_observer, states_m_observer_dict, state_dict, forecast=2)

    #########################################
    # check for modification of default_value
    state_dict['Nested'].scoped_variables[new_scoped_variable_id].default_value = 5
    check_output_notifications(scoped_variable_observer, states_m_observer_dict, state_dict, forecast=3)

    ###########################################
    # check for modification of change_datatype
    state_dict['Nested'].scoped_variables[new_scoped_variable_id].change_data_type(data_type='str',
                                                                                   default_value='awesome_tool')
    check_output_notifications(scoped_variable_observer, states_m_observer_dict, state_dict, forecast=5)

    utils.assert_logger_warnings_and_errors(caplog)

# add state
# - change state

# remove state

# add outcome
# - change outcome

# remove outcome

# add transition
# - change transition

# remove transition

# add input_data_port
# - change input_data_port

# remove input_data_port

# add output_data_port
# - change output_data_port

# remove output_data_port

# add scoped_variable
# - change scoped_variable

# remove scoped_variable

# add data_flow
# - change data_flow

# remove data_flow


def test_data_flow_add_remove_notification(caplog):
    # create testbed
    [state, sm_model, state_dict] = create_models()

    state1 = ExecutionState('State1')
    output_state1 = state1.add_output_data_port("output", "int")
    input_state1 = state1.add_input_data_port("input", "str", "zero")
    state2 = ExecutionState('State2')
    input_par_state2 = state2.add_input_data_port("par", "int", 0)
    output_res_state2 = state2.add_output_data_port("res", "int")
    state_dict['Nested'].add_state(state1)
    state_dict['Nested'].add_state(state2)

    # create observer
    states_observer_dict = setup_observer_dict_for_state_model(sm_model.root_state, with_print=with_print)
    state_name = 'Nested'

    #############
    # add data_flow
    new_df_id = state_dict['Nested'].add_data_flow(from_state_id=state1.state_id, from_data_port_id=output_state1,
                                                   to_state_id=state2.state_id, to_data_port_id=input_par_state2)

    # check state
    state_model_observer = states_observer_dict[state_dict[state_name].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 1, 'data_flows': 1})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    for path, state_m_observer in states_observer_dict.iteritems():
        state_m_observer.reset()

    ################
    # remove data_flow
    state_dict['Nested'].remove_data_flow(new_df_id)  # new outcome should be the third one

    # check state
    state_model_observer = states_observer_dict[state_dict[state_name].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 1, 'data_flows': 1})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    utils.assert_logger_warnings_and_errors(caplog)


def test_data_flow_modify_notification(caplog):

    def check_data_flow_notifications(data_flow_m_observer, states_obs_dict, _state_dict, forecast=1):

        # check grand-parent
        state_model_observer = states_obs_dict[_state_dict['Container'].get_path()]
        check_count_of_model_notifications(state_model_observer, {'states': forecast})

        # check parent
        state_model_observer = states_obs_dict[_state_dict['State3'].get_path()]
        check_count_of_model_notifications(state_model_observer, {'states': forecast})

        # check state
        state_model_observer = states_obs_dict[_state_dict['Nested'].get_path()]
        check_count_of_model_notifications(state_model_observer, {'data_flows': forecast})

        print "data_flow_model over all estimated %s occurred %s" % \
              (data_flow_m_observer.get_number_of_notifications(), 2*forecast)
        assert data_flow_m_observer.get_number_of_notifications() == 2*forecast

    # create testbed
    [state, sm_model, state_dict] = create_models()

    state1 = ExecutionState('State1')
    output_state1 = state1.add_output_data_port("output", "int")
    input_state1 = state1.add_input_data_port("input", "str", "zero")
    state2 = ExecutionState('State2')
    input_par_state2 = state2.add_input_data_port("par", "int", 0)
    output_res_state2 = state2.add_output_data_port("res", "int")
    state_dict['Nested'].add_state(state1)
    state_dict['Nested'].add_state(state2)
    output_res_nested = state_dict['Nested'].add_output_data_port("res", "int")
    output_count_state1 = state1.add_output_data_port("count", "int")
    input_number_state2 = state2.add_input_data_port("number", "int", 5)

    new_df_id = state_dict['Nested'].add_data_flow(from_state_id=state2.state_id,
                                                   from_data_port_id=output_res_state2,
                                                   to_state_id=state_dict['Nested'].state_id,
                                                   to_data_port_id=output_res_nested)

    # create observer
    state_model_nested = get_state_model_by_path(sm_model.root_state, state_dict['Nested'].get_path())
    data_flow_model = None
    for df_model in state_model_nested.data_flows:
        if df_model.data_flow.data_flow_id == new_df_id:
            data_flow_model = df_model
    assert data_flow_model
    data_flow_m_observer = DataFlowNotificationLogObserver(data_flow_model)
    states_m_observer_dict = setup_observer_dict_for_state_model(sm_model.root_state, with_print=with_print)

    ##### modify from data_flow #######
    # modify_origin(self, from_state, from_key)
    state_dict['Nested'].data_flows[new_df_id].modify_origin(from_state=state1.state_id, from_key=output_state1)
    check_data_flow_notifications(data_flow_m_observer, states_m_observer_dict, state_dict, forecast=1)

    # from_key(self, from_key)
    state_dict['Nested'].data_flows[new_df_id].from_key = output_count_state1
    check_data_flow_notifications(data_flow_m_observer, states_m_observer_dict, state_dict, forecast=2)

    # modify_target(self, to_state, to_key)
    state_dict['Nested'].data_flows[new_df_id].modify_target(to_state=state2.state_id, to_key=input_par_state2)
    check_data_flow_notifications(data_flow_m_observer, states_m_observer_dict, state_dict, forecast=3)

    # to_key(self, to_key)
    state_dict['Nested'].data_flows[new_df_id].to_key = input_number_state2
    check_data_flow_notifications(data_flow_m_observer, states_m_observer_dict, state_dict, forecast=4)

    # data_flow_id(self, data_flow_id)
    state_dict['Nested'].data_flows[new_df_id].data_flow_id += 1
    check_data_flow_notifications(data_flow_m_observer, states_m_observer_dict, state_dict, forecast=5)

    # reset observer and testbed
    state_dict['Nested'].remove_data_flow(new_df_id)
    new_df_id = state_dict['Nested'].add_data_flow(from_state_id=state2.state_id,
                                                   from_data_port_id=output_res_state2,
                                                   to_state_id=state_dict['Nested'].state_id,
                                                   to_data_port_id=output_res_nested)

    for path, state_m_observer in states_m_observer_dict.iteritems():
        state_m_observer.reset()
    data_flow_model = None
    for df_model in state_model_nested.data_flows:
        if df_model.data_flow.data_flow_id == new_df_id:
            data_flow_model = df_model
    assert data_flow_model
    data_flow_m_observer = DataFlowNotificationLogObserver(data_flow_model)

    ##### modify from parent state #######
    # modify_data_flow_from_state(self, data_flow_id, from_state, from_key)
    # state_dict['Nested'].modify_data_flow_from_state(new_df_id, from_state=state1.state_id, from_key=output_state1)
    state_dict['Nested'].data_flows[new_df_id].modify_origin(state1.state_id, output_count_state1)
    check_data_flow_notifications(data_flow_m_observer, states_m_observer_dict, state_dict, forecast=1)

    # modify_data_flow_from_key(self, data_flow_id, from_key)
    # state_dict['Nested'].modify_data_flow_from_key(new_df_id, from_key=output_count_state1)
    state_dict['Nested'].data_flows[new_df_id].from_key = output_count_state1
    check_data_flow_notifications(data_flow_m_observer, states_m_observer_dict, state_dict, forecast=2)

    # modify_data_flow_to_state(self, data_flow_id, to_state, to_key)
    # state_dict['Nested'].modify_data_flow_to_state(new_df_id, to_state=state2.state_id, to_key=input_par_state2)
    state_dict['Nested'].data_flows[new_df_id].modify_target(state2.state_id, input_par_state2)
    check_data_flow_notifications(data_flow_m_observer, states_m_observer_dict, state_dict, forecast=3)

    # modify_data_flow_to_key(self, data_flow_id, to_key)
    # state_dict['Nested'].modify_data_flow_to_key(new_df_id, to_key=input_number_state2)
    state_dict['Nested'].data_flows[new_df_id].to_key = input_number_state2
    check_data_flow_notifications(data_flow_m_observer, states_m_observer_dict, state_dict, forecast=4)

    utils.assert_logger_warnings_and_errors(caplog)


def test_transition_add_remove_notification(caplog):
    # create testbed
    [state, sm_model, state_dict] = create_models()

    state1 = ExecutionState('State1')
    outcome_state1 = state1.add_outcome('UsedHere')
    state2 = ExecutionState('State2')
    outcome_state2 = state2.add_outcome('UsedHere')
    state_dict['Nested'].add_state(state1)
    state_dict['Nested'].add_state(state2)

    # create observer
    states_observer_dict = setup_observer_dict_for_state_model(sm_model.root_state, with_print=with_print)

    ################
    # add transition from_state_id, from_outcome, to_state_id=None, to_outcome=None, transition_id
    new_transition_id1 = state_dict['Nested'].add_transition(from_state_id=state1.state_id, from_outcome=outcome_state1,
                                                             to_state_id=state2.state_id, to_outcome=None)
    state_dict['Nested'].add_transition(from_state_id=state2.state_id, from_outcome=outcome_state2,
                                        to_state_id=state_dict['Nested'].state_id, to_outcome=-1)

    # check state
    state_model_observer = states_observer_dict[state_dict['Nested'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 2, 'transitions': 2})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 2})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 2})

    for path, state_m_observer in states_observer_dict.iteritems():
        state_m_observer.reset()

    ###################
    # remove transition
    state_dict['Nested'].remove_transition(new_transition_id1)  # new outcome should be the third one

    # check state
    state_model_observer = states_observer_dict[state_dict['Nested'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 1, 'transitions': 1})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    utils.assert_logger_warnings_and_errors(caplog)


def test_transition_modify_notification(caplog):

    def check_transition_notifications(transition_m_observer, states_obs_dict, _state_dict, forecast=1):

        # check grand-parent
        state_model_observer = states_obs_dict[_state_dict['Container'].get_path()]
        check_count_of_model_notifications(state_model_observer, {'states': forecast})

        # check parent
        state_model_observer = states_obs_dict[_state_dict['State3'].get_path()]
        check_count_of_model_notifications(state_model_observer, {'states': forecast})

        # check state
        state_model_observer = states_obs_dict[_state_dict['Nested'].get_path()]
        check_count_of_model_notifications(state_model_observer, {'transitions': forecast})

        print "transition_model over all estimated %s occurred %s" % \
              (transition_m_observer.get_number_of_notifications(), 2*forecast)
        assert transition_m_observer.get_number_of_notifications() == 2*forecast

    # create testbed
    [state, sm_model, state_dict] = create_models()

    state1 = ExecutionState('State1')
    outcome_again_state1 = state1.add_outcome("again")
    state2 = ExecutionState('State2')
    oc_done_state2 = state2.add_outcome("done")
    oc_best_state2 = state2.add_outcome("best")
    state_dict['Nested'].add_state(state1)
    state_dict['Nested'].add_state(state2)
    oc_great_nested = state_dict['Nested'].add_outcome("great")
    outcome_counted_state1 = state1.add_outcome("counted")
    oc_full_state2 = state2.add_outcome("full")
    # assert False

    new_trans_id = state_dict['Nested'].add_transition(from_state_id=state1.state_id,
                                                       from_outcome=outcome_again_state1,
                                                       to_state_id=state1.state_id,
                                                       to_outcome=None)

    # create observer
    state_model_nested = get_state_model_by_path(sm_model.root_state, state_dict['Nested'].get_path())
    transition_model = None
    for df_model in state_model_nested.transitions:
        if df_model.transition.transition_id == new_trans_id:
            transition_model = df_model
    assert transition_model
    transition_m_observer = TransitionNotificationLogObserver(transition_model)
    states_m_observer_dict = setup_observer_dict_for_state_model(sm_model.root_state, with_print=with_print)

    # modify_origin(self, from_state, from_outcome)
    state_dict['Nested'].transitions[new_trans_id].modify_origin(from_state=state2.state_id,
                                                                 from_outcome=oc_full_state2)
    check_transition_notifications(transition_m_observer, states_m_observer_dict, state_dict, forecast=1)

    # from_outcome(self, from_outcome)
    state_dict['Nested'].transitions[new_trans_id].from_outcome = oc_done_state2
    check_transition_notifications(transition_m_observer, states_m_observer_dict, state_dict, forecast=2)

    # to_state(self, to_state)
    state_dict['Nested'].transitions[new_trans_id].to_state = state2.state_id
    check_transition_notifications(transition_m_observer, states_m_observer_dict, state_dict, forecast=3)

    # to_outcome(self, to_outcome)
    # Invalid test: to_outcome must be None as transition goes to child state
    # state_dict['Nested'].transitions[new_trans_id].to_outcome = oc_great_nested
    # check_transition_notifications(transition_m_observer, states_m_observer_dict, state_dict, forecast=4)

    # transition_id(self, transition_id)
    state_dict['Nested'].transitions[new_trans_id].transition_id += 1
    check_transition_notifications(transition_m_observer, states_m_observer_dict, state_dict, forecast=4)

    # reset observer and testbed
    state_dict['Nested'].remove_transition(new_trans_id)
    new_df_id = state_dict['Nested'].add_transition(from_state_id=state1.state_id,
                                                    from_outcome=outcome_again_state1,
                                                    to_state_id=state1.state_id,
                                                    to_outcome=None)

    for path, state_m_observer in states_m_observer_dict.iteritems():
        state_m_observer.reset()
    transition_model = None
    for df_model in state_model_nested.transitions:
        if df_model.transition.transition_id == new_df_id:
            transition_model = df_model
    assert transition_model
    transition_m_observer = TransitionNotificationLogObserver(transition_model)

    ##### modify from parent state #######
    # modify_transition_from_state(self, transition_id, from_state, from_outcome)
    # state_dict['Nested'].modify_transition_from_state(new_df_id, from_state=state2.state_id,
    #                                                   from_outcome=oc_full_state2)
    state_dict['Nested'].transitions[new_df_id].modify_origin(state2.state_id, oc_full_state2)
    check_transition_notifications(transition_m_observer, states_m_observer_dict, state_dict, forecast=1)

    # modify_transition_from_outcome(self, transition_id, from_outcome)
    # state_dict['Nested'].modify_transition_from_outcome(new_df_id, from_outcome=oc_done_state2)
    state_dict['Nested'].transitions[new_df_id].from_outcome = oc_done_state2
    check_transition_notifications(transition_m_observer, states_m_observer_dict, state_dict, forecast=2)

    # modify_transition_to_outcome(self, transition_id, to_outcome)
    # Invalid test: to_outcome must be None as transition goes to child state
    # state_dict['Nested'].modify_transition_to_outcome(new_df_id, to_outcome=oc_great_nested)
    # check_transition_notifications(transition_m_observer, states_m_observer_dict, state_dict, forecast=3)

    # modify_transition_to_state(self, transition_id, to_state, to_outcome)
    # state_dict['Nested'].modify_transition_to_state(new_df_id, to_state=state1.state_id)
    state_dict['Nested'].transitions[new_df_id].to_state = state1.state_id
    check_transition_notifications(transition_m_observer, states_m_observer_dict, state_dict, forecast=3)

    utils.assert_logger_warnings_and_errors(caplog)


def test_state_add_remove_notification(caplog):
    # create testbed
    [state, sm_model, state_dict] = create_models()

    state1 = ExecutionState('State1')
    outcome_state1 = state1.add_outcome('UsedHere')
    state2 = ExecutionState('State2')
    outcome_state2 = state2.add_outcome('UsedHere')

    # create observer
    states_observer_dict = setup_observer_dict_for_state_model(sm_model.root_state, with_print=with_print)

    ###########
    # add State
    state_dict['Nested'].add_state(state1)
    state_dict['Nested'].add_state(state2)

    # check state
    state_model_observer = states_observer_dict[state_dict['Nested'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 2, 'states': 2})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 2})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 2})

    for path, state_m_observer in states_observer_dict.iteritems():
        state_m_observer.reset()

    ##############
    # remove State
    state_dict['Nested'].remove_state(state1.state_id)  # new outcome should be the third one

    # check state
    state_model_observer = states_observer_dict[state_dict['Nested'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 1, 'states': 1})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    utils.assert_logger_warnings_and_errors(caplog)


def test_state_property_modify_notification(caplog):

    def check_states_notifications(states_observer_dict, sub_state_name='Nested', forecast=1, child_effects={}):

        # check state
        state_model_observer = states_observer_dict[state_dict[sub_state_name].get_path()]
        check_dict = {'state': forecast}
        check_dict.update(child_effects)
        check_count_of_model_notifications(state_model_observer, check_dict)

        # check parent
        num_child_effects = 0
        # for num_prop_effects in child_effects.itervalues():
        #     num_child_effects += num_prop_effects
        if 'outcomes' in child_effects:
            num_child_effects = child_effects['outcomes']
        check_dict = {'states': forecast + num_child_effects}
        state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
        check_count_of_model_notifications(state_model_observer, check_dict)

        # check grand parent
        state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
        check_count_of_model_notifications(state_model_observer, check_dict)


    # create testbed
    [state, sm_model, state_dict] = create_models()

    state1 = ExecutionState('State1')
    input_state1 = state1.add_input_data_port("input", "str", "zero")
    output_state1 = state1.add_output_data_port("output", "int")
    output_count_state1 = state1.add_output_data_port("count", "int")

    state2 = ExecutionState('State2')
    input_par_state2 = state2.add_input_data_port("par", "int", 0)
    input_number_state2 = state2.add_input_data_port("number", "int", 5)
    output_res_state2 = state2.add_output_data_port("res", "int")

    state_dict['Nested'].add_state(state1)
    state_dict['Nested'].add_state(state2)
    output_res_nested = state_dict['Nested'].add_output_data_port("res", "int")

    oc_again_state1 = state1.add_outcome("again")
    oc_counted_state1 = state1.add_outcome("counted")

    oc_done_state2 = state2.add_outcome("done")
    oc_best_state2 = state2.add_outcome("best")
    oc_full_state2 = state2.add_outcome("full")

    oc_great_nested = state_dict['Nested'].add_outcome("great")

    # create observer
    states_observer_dict = setup_observer_dict_for_state_model(sm_model.root_state, with_print=with_print)

    #######################################
    ######## Properties of State ##########
    forecast = 0
    # name(self, name)
    state_dict['Nested'].name = 'nested'
    forecast += 1
    check_states_notifications(states_observer_dict, sub_state_name='Nested', forecast=forecast)

    # parent(self, parent) State
    state_dict['Nested'].parent = state_dict['State3']
    forecast += 1
    check_states_notifications(states_observer_dict, sub_state_name='Nested', forecast=forecast)

    # input_data_ports(self, input_data_ports) None or dict
    state_dict['Nested'].input_data_ports = None
    forecast += 1
    check_states_notifications(states_observer_dict, sub_state_name='Nested', forecast=forecast)

    # output_data_ports(self, output_data_ports) None or dict
    state_dict['Nested'].output_data_ports = None
    forecast += 1
    check_states_notifications(states_observer_dict, sub_state_name='Nested', forecast=forecast)

    # outcomes(self, outcomes) None or dict
    # state_dict['Nested'].outcomes = None
    # forecast += 4
    state_dict['Nested'].outcomes = state_dict['Nested'].outcomes
    forecast += 1
    check_states_notifications(states_observer_dict, sub_state_name='Nested', forecast=forecast,
                               child_effects={'outcomes': 5})

    # TODO NOTIFICATION of script assignment is wasted!!!!!!!!
    # # script(self, script) Script
    # if hasattr(state_dict['Nested2'], "script"):
    #     state_dict['Nested2'].script = Script(script_type=ScriptType.CONTAINER, state=state_dict['Nested2'])
    #     forecast += 1
    #     state_dict['Nested2'].script = Script(script_type=ScriptType.EXECUTION, state=state_dict['Nested2'])
    #     forecast += 1
    # check_states_notifications(states_observer_dict, sub_state_name='Nested2', forecast=2,
    #                            child_effects={'states': 5})

    # description(self, description) str
    state_dict['Nested'].description = "awesome"
    forecast += 1
    check_states_notifications(states_observer_dict, sub_state_name='Nested', forecast=forecast,
                               child_effects={'outcomes': 5})

    # active(self, active) bool
    # IMPORTANT: active flag is not used any more
    # state_dict['Nested'].active = True
    # forecast += 1
    # check_states_notifications(states_observer_dict, sub_state_name='Nested', forecast=forecast)

    ############################################
    ###### Properties of ContainerState ########
    for path, state_m_observer in states_observer_dict.iteritems():
        state_m_observer.reset()

    # set_start_state(self, state) State or state_id
    state_dict['Nested'].set_start_state(state1.state_id)

    # check state
    state_model_observer = states_observer_dict[state_dict['Nested'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 1, 'transitions': 1})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 1})

    for path, state_m_observer in states_observer_dict.iteritems():
        state_m_observer.reset()
    forecast = 0

    # set_start_state(self, state) State or state_id
    state_dict['Nested'].set_start_state(state2.state_id)

    # check state
    state_model_observer = states_observer_dict[state_dict['Nested'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'state': 2, 'transitions': 2})

    # check parent
    state_model_observer = states_observer_dict[state_dict['State3'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 2})

    # check grand parent
    state_model_observer = states_observer_dict[state_dict['Container'].get_path()]
    check_count_of_model_notifications(state_model_observer, {'states': 2})

    for path, state_m_observer in states_observer_dict.iteritems():
        state_m_observer.reset()
    forecast = 0

    # states(self, states) None or dict
    state_dict['Nested'].states = None
    forecast += 4
    check_states_notifications(states_observer_dict, sub_state_name='Nested', forecast=forecast, child_effects={
        'states': 2, 'transitions': 1})

    # transitions(self, transitions) None or dict
    state_dict['Nested'].transitions = None
    forecast += 1
    check_states_notifications(states_observer_dict, sub_state_name='Nested', forecast=forecast, child_effects={
        'states': 2, 'transitions': 1})

    # data_flows(self, data_flows) None or dict
    state_dict['Nested'].data_flows = None
    forecast += 1
    check_states_notifications(states_observer_dict, sub_state_name='Nested', forecast=forecast, child_effects={
        'states': 2, 'transitions': 1})

    # scoped_variables(self, scoped_variables) None or dict
    state_dict['Nested'].scoped_variables = None
    forecast += 1
    check_states_notifications(states_observer_dict, sub_state_name='Nested', forecast=forecast, child_effects={
        'states': 2, 'transitions': 1})

    # child_execution(self, child_execution) bool
    # IMPORTANT: child_execution flag is not used any more
    # state_dict['Nested'].child_execution = True
    # forecast += 1
    # check_states_notifications(states_observer_dict, sub_state_name='Nested', forecast=forecast)

    utils.assert_logger_warnings_and_errors(caplog)

if __name__ == '__main__':
    pytest.main([__file__])