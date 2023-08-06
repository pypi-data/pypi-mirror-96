﻿'''_3883.py

PowerLoadCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model import _2120
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows import _3753
from mastapy.system_model.analyses_and_results.power_flows.compound import _3918
from mastapy._internal.python_net import python_net_import

_POWER_LOAD_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'PowerLoadCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('PowerLoadCompoundPowerFlow',)


class PowerLoadCompoundPowerFlow(_3918.VirtualComponentCompoundPowerFlow):
    '''PowerLoadCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _POWER_LOAD_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PowerLoadCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2120.PowerLoad':
        '''PowerLoad: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2120.PowerLoad)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def load_case_analyses_ready(self) -> 'List[_3753.PowerLoadPowerFlow]':
        '''List[PowerLoadPowerFlow]: 'LoadCaseAnalysesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseAnalysesReady, constructor.new(_3753.PowerLoadPowerFlow))
        return value

    @property
    def component_power_flow_load_cases(self) -> 'List[_3753.PowerLoadPowerFlow]':
        '''List[PowerLoadPowerFlow]: 'ComponentPowerFlowLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentPowerFlowLoadCases, constructor.new(_3753.PowerLoadPowerFlow))
        return value
