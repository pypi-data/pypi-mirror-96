﻿'''_4794.py

ConceptGearSetModalAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2120
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6147
from mastapy.system_model.analyses_and_results.system_deflections import _2298
from mastapy.system_model.analyses_and_results.modal_analyses import _4793, _4792, _4820
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_SET_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses', 'ConceptGearSetModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearSetModalAnalysis',)


class ConceptGearSetModalAnalysis(_4820.GearSetModalAnalysis):
    '''ConceptGearSetModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_SET_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearSetModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2120.ConceptGearSet':
        '''ConceptGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2120.ConceptGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None

    @property
    def assembly_load_case(self) -> '_6147.ConceptGearSetLoadCase':
        '''ConceptGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6147.ConceptGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase else None

    @property
    def system_deflection_results(self) -> '_2298.ConceptGearSetSystemDeflection':
        '''ConceptGearSetSystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2298.ConceptGearSetSystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults else None

    @property
    def concept_gears_modal_analysis(self) -> 'List[_4793.ConceptGearModalAnalysis]':
        '''List[ConceptGearModalAnalysis]: 'ConceptGearsModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearsModalAnalysis, constructor.new(_4793.ConceptGearModalAnalysis))
        return value

    @property
    def concept_meshes_modal_analysis(self) -> 'List[_4792.ConceptGearMeshModalAnalysis]':
        '''List[ConceptGearMeshModalAnalysis]: 'ConceptMeshesModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptMeshesModalAnalysis, constructor.new(_4792.ConceptGearMeshModalAnalysis))
        return value
