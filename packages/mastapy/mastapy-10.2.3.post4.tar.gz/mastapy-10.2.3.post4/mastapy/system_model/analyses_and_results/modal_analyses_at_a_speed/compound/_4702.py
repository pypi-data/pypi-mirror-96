﻿'''_4702.py

ImportedFEComponentCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.part_model import _2058
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4580
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4645
from mastapy._internal.python_net import python_net_import

_IMPORTED_FE_COMPONENT_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'ImportedFEComponentCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('ImportedFEComponentCompoundModalAnalysisAtASpeed',)


class ImportedFEComponentCompoundModalAnalysisAtASpeed(_4645.AbstractShaftOrHousingCompoundModalAnalysisAtASpeed):
    '''ImportedFEComponentCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _IMPORTED_FE_COMPONENT_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ImportedFEComponentCompoundModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2058.ImportedFEComponent':
        '''ImportedFEComponent: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2058.ImportedFEComponent)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def load_case_analyses_ready(self) -> 'List[_4580.ImportedFEComponentModalAnalysisAtASpeed]':
        '''List[ImportedFEComponentModalAnalysisAtASpeed]: 'LoadCaseAnalysesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseAnalysesReady, constructor.new(_4580.ImportedFEComponentModalAnalysisAtASpeed))
        return value

    @property
    def component_modal_analysis_at_a_speed_load_cases(self) -> 'List[_4580.ImportedFEComponentModalAnalysisAtASpeed]':
        '''List[ImportedFEComponentModalAnalysisAtASpeed]: 'ComponentModalAnalysisAtASpeedLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentModalAnalysisAtASpeedLoadCases, constructor.new(_4580.ImportedFEComponentModalAnalysisAtASpeed))
        return value

    @property
    def planetaries(self) -> 'List[ImportedFEComponentCompoundModalAnalysisAtASpeed]':
        '''List[ImportedFEComponentCompoundModalAnalysisAtASpeed]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ImportedFEComponentCompoundModalAnalysisAtASpeed))
        return value
