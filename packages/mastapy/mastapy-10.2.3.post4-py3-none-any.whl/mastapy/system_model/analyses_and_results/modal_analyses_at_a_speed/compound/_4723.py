﻿'''_4723.py

PlanetCarrierCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.part_model import _2069
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4602
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4715
from mastapy._internal.python_net import python_net_import

_PLANET_CARRIER_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'PlanetCarrierCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetCarrierCompoundModalAnalysisAtASpeed',)


class PlanetCarrierCompoundModalAnalysisAtASpeed(_4715.MountableComponentCompoundModalAnalysisAtASpeed):
    '''PlanetCarrierCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _PLANET_CARRIER_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetCarrierCompoundModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2069.PlanetCarrier':
        '''PlanetCarrier: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2069.PlanetCarrier)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def load_case_analyses_ready(self) -> 'List[_4602.PlanetCarrierModalAnalysisAtASpeed]':
        '''List[PlanetCarrierModalAnalysisAtASpeed]: 'LoadCaseAnalysesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseAnalysesReady, constructor.new(_4602.PlanetCarrierModalAnalysisAtASpeed))
        return value

    @property
    def component_modal_analysis_at_a_speed_load_cases(self) -> 'List[_4602.PlanetCarrierModalAnalysisAtASpeed]':
        '''List[PlanetCarrierModalAnalysisAtASpeed]: 'ComponentModalAnalysisAtASpeedLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentModalAnalysisAtASpeedLoadCases, constructor.new(_4602.PlanetCarrierModalAnalysisAtASpeed))
        return value
