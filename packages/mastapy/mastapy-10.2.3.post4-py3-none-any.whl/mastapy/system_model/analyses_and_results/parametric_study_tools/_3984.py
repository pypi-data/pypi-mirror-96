﻿'''_3984.py

ExternalCADModelParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model import _2100
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6480
from mastapy.system_model.analyses_and_results.system_deflections import _2385
from mastapy.system_model.analyses_and_results.parametric_study_tools import _3950
from mastapy._internal.python_net import python_net_import

_EXTERNAL_CAD_MODEL_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'ExternalCADModelParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('ExternalCADModelParametricStudyTool',)


class ExternalCADModelParametricStudyTool(_3950.ComponentParametricStudyTool):
    '''ExternalCADModelParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _EXTERNAL_CAD_MODEL_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ExternalCADModelParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2100.ExternalCADModel':
        '''ExternalCADModel: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2100.ExternalCADModel)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def component_load_case(self) -> '_6480.ExternalCADModelLoadCase':
        '''ExternalCADModelLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6480.ExternalCADModelLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase else None

    @property
    def component_system_deflection_results(self) -> 'List[_2385.ExternalCADModelSystemDeflection]':
        '''List[ExternalCADModelSystemDeflection]: 'ComponentSystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentSystemDeflectionResults, constructor.new(_2385.ExternalCADModelSystemDeflection))
        return value
