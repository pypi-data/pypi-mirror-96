﻿'''_5409.py

StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2192
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6559
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5407, _5408, _5319
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_GEAR_SET_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation',)


class StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation(_5319.BevelGearSetHarmonicAnalysisOfSingleExcitation):
    '''StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_GEAR_SET_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2192.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2192.StraightBevelDiffGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None

    @property
    def assembly_load_case(self) -> '_6559.StraightBevelDiffGearSetLoadCase':
        '''StraightBevelDiffGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6559.StraightBevelDiffGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase else None

    @property
    def straight_bevel_diff_gears_harmonic_analysis_of_single_excitation(self) -> 'List[_5407.StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation]':
        '''List[StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation]: 'StraightBevelDiffGearsHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearsHarmonicAnalysisOfSingleExcitation, constructor.new(_5407.StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def straight_bevel_diff_meshes_harmonic_analysis_of_single_excitation(self) -> 'List[_5408.StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation]':
        '''List[StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation]: 'StraightBevelDiffMeshesHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffMeshesHarmonicAnalysisOfSingleExcitation, constructor.new(_5408.StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation))
        return value
