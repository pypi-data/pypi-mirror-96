﻿'''_6529.py

PlanetaryGearSetLoadCase
'''


from mastapy.utility import _1261
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.system_model.part_model.gears import _2188
from mastapy.system_model.analyses_and_results.static_loads import _6463
from mastapy._internal.python_net import python_net_import

_PLANETARY_GEAR_SET_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'PlanetaryGearSetLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetaryGearSetLoadCase',)


class PlanetaryGearSetLoadCase(_6463.CylindricalGearSetLoadCase):
    '''PlanetaryGearSetLoadCase

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_GEAR_SET_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetaryGearSetLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def include_gear_blank_elastic_distortion(self) -> '_1261.LoadCaseOverrideOption':
        '''LoadCaseOverrideOption: 'IncludeGearBlankElasticDistortion' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.IncludeGearBlankElasticDistortion)
        return constructor.new(_1261.LoadCaseOverrideOption)(value) if value else None

    @include_gear_blank_elastic_distortion.setter
    def include_gear_blank_elastic_distortion(self, value: '_1261.LoadCaseOverrideOption'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.IncludeGearBlankElasticDistortion = value

    @property
    def specify_separate_micro_geometry_for_each_planet_gear(self) -> 'bool':
        '''bool: 'SpecifySeparateMicroGeometryForEachPlanetGear' is the original name of this property.'''

        return self.wrapped.SpecifySeparateMicroGeometryForEachPlanetGear

    @specify_separate_micro_geometry_for_each_planet_gear.setter
    def specify_separate_micro_geometry_for_each_planet_gear(self, value: 'bool'):
        self.wrapped.SpecifySeparateMicroGeometryForEachPlanetGear = bool(value) if value else False

    @property
    def assembly_design(self) -> '_2188.PlanetaryGearSet':
        '''PlanetaryGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2188.PlanetaryGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None
