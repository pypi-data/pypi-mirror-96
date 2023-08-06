﻿'''_4073.py

SpiralBevelGearSetParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.gears import _2215
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6585
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4072, _4071, _3972
from mastapy.system_model.analyses_and_results.system_deflections import _2470
from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_GEAR_SET_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'SpiralBevelGearSetParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelGearSetParametricStudyTool',)


class SpiralBevelGearSetParametricStudyTool(_3972.BevelGearSetParametricStudyTool):
    '''SpiralBevelGearSetParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _SPIRAL_BEVEL_GEAR_SET_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpiralBevelGearSetParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2215.SpiralBevelGearSet':
        '''SpiralBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2215.SpiralBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None

    @property
    def assembly_load_case(self) -> '_6585.SpiralBevelGearSetLoadCase':
        '''SpiralBevelGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6585.SpiralBevelGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase else None

    @property
    def spiral_bevel_gears_parametric_study_tool(self) -> 'List[_4072.SpiralBevelGearParametricStudyTool]':
        '''List[SpiralBevelGearParametricStudyTool]: 'SpiralBevelGearsParametricStudyTool' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGearsParametricStudyTool, constructor.new(_4072.SpiralBevelGearParametricStudyTool))
        return value

    @property
    def spiral_bevel_meshes_parametric_study_tool(self) -> 'List[_4071.SpiralBevelGearMeshParametricStudyTool]':
        '''List[SpiralBevelGearMeshParametricStudyTool]: 'SpiralBevelMeshesParametricStudyTool' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelMeshesParametricStudyTool, constructor.new(_4071.SpiralBevelGearMeshParametricStudyTool))
        return value

    @property
    def assembly_system_deflection_results(self) -> 'List[_2470.SpiralBevelGearSetSystemDeflection]':
        '''List[SpiralBevelGearSetSystemDeflection]: 'AssemblySystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblySystemDeflectionResults, constructor.new(_2470.SpiralBevelGearSetSystemDeflection))
        return value
