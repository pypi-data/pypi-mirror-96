﻿'''_2680.py

HypoidGearSteadyStateSynchronousResponseOnAShaft
'''


from mastapy.system_model.part_model.gears import _2180
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6502
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2622
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft', 'HypoidGearSteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSteadyStateSynchronousResponseOnAShaft',)


class HypoidGearSteadyStateSynchronousResponseOnAShaft(_2622.AGMAGleasonConicalGearSteadyStateSynchronousResponseOnAShaft):
    '''HypoidGearSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSteadyStateSynchronousResponseOnAShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2180.HypoidGear':
        '''HypoidGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2180.HypoidGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def component_load_case(self) -> '_6502.HypoidGearLoadCase':
        '''HypoidGearLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6502.HypoidGearLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase else None
