﻿'''_5371.py

KlingelnbergCycloPalloidHypoidGearHarmonicAnalysisOfSingleExcitation
'''


from mastapy.system_model.part_model.gears import _2184
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6511
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5368
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'KlingelnbergCycloPalloidHypoidGearHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidHypoidGearHarmonicAnalysisOfSingleExcitation',)


class KlingelnbergCycloPalloidHypoidGearHarmonicAnalysisOfSingleExcitation(_5368.KlingelnbergCycloPalloidConicalGearHarmonicAnalysisOfSingleExcitation):
    '''KlingelnbergCycloPalloidHypoidGearHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidHypoidGearHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2184.KlingelnbergCycloPalloidHypoidGear':
        '''KlingelnbergCycloPalloidHypoidGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2184.KlingelnbergCycloPalloidHypoidGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def component_load_case(self) -> '_6511.KlingelnbergCycloPalloidHypoidGearLoadCase':
        '''KlingelnbergCycloPalloidHypoidGearLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6511.KlingelnbergCycloPalloidHypoidGearLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase else None
