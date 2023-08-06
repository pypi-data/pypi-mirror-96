﻿'''_3871.py

MassDiscCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model import _2110
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows import _3739
from mastapy.system_model.analyses_and_results.power_flows.compound import _3918
from mastapy._internal.python_net import python_net_import

_MASS_DISC_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'MassDiscCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('MassDiscCompoundPowerFlow',)


class MassDiscCompoundPowerFlow(_3918.VirtualComponentCompoundPowerFlow):
    '''MassDiscCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _MASS_DISC_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MassDiscCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2110.MassDisc':
        '''MassDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2110.MassDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def load_case_analyses_ready(self) -> 'List[_3739.MassDiscPowerFlow]':
        '''List[MassDiscPowerFlow]: 'LoadCaseAnalysesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseAnalysesReady, constructor.new(_3739.MassDiscPowerFlow))
        return value

    @property
    def component_power_flow_load_cases(self) -> 'List[_3739.MassDiscPowerFlow]':
        '''List[MassDiscPowerFlow]: 'ComponentPowerFlowLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentPowerFlowLoadCases, constructor.new(_3739.MassDiscPowerFlow))
        return value
