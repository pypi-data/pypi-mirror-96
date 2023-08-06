﻿'''_5534.py

SpringDamperConnectionCompoundHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.connections_and_sockets.couplings import _2002
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5404
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import _5469
from mastapy._internal.python_net import python_net_import

_SPRING_DAMPER_CONNECTION_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound', 'SpringDamperConnectionCompoundHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('SpringDamperConnectionCompoundHarmonicAnalysisOfSingleExcitation',)


class SpringDamperConnectionCompoundHarmonicAnalysisOfSingleExcitation(_5469.CouplingConnectionCompoundHarmonicAnalysisOfSingleExcitation):
    '''SpringDamperConnectionCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _SPRING_DAMPER_CONNECTION_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpringDamperConnectionCompoundHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2002.SpringDamperConnection':
        '''SpringDamperConnection: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2002.SpringDamperConnection)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def connection_design(self) -> '_2002.SpringDamperConnection':
        '''SpringDamperConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2002.SpringDamperConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign else None

    @property
    def load_case_analyses_ready(self) -> 'List[_5404.SpringDamperConnectionHarmonicAnalysisOfSingleExcitation]':
        '''List[SpringDamperConnectionHarmonicAnalysisOfSingleExcitation]: 'LoadCaseAnalysesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseAnalysesReady, constructor.new(_5404.SpringDamperConnectionHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def connection_harmonic_analysis_of_single_excitation_load_cases(self) -> 'List[_5404.SpringDamperConnectionHarmonicAnalysisOfSingleExcitation]':
        '''List[SpringDamperConnectionHarmonicAnalysisOfSingleExcitation]: 'ConnectionHarmonicAnalysisOfSingleExcitationLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionHarmonicAnalysisOfSingleExcitationLoadCases, constructor.new(_5404.SpringDamperConnectionHarmonicAnalysisOfSingleExcitation))
        return value
