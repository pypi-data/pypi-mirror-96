﻿'''_5709.py

RootAssemblyHarmonicAnalysis
'''


from mastapy.system_model.analyses_and_results.harmonic_analyses import (
    _5674, _2302, _2303, _5597
)
from mastapy._internal import constructor
from mastapy.system_model.part_model import _2147
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.system_deflections import _2462
from mastapy._internal.python_net import python_net_import

_ROOT_ASSEMBLY_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'RootAssemblyHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RootAssemblyHarmonicAnalysis',)


class RootAssemblyHarmonicAnalysis(_5597.AssemblyHarmonicAnalysis):
    '''RootAssemblyHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _ROOT_ASSEMBLY_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RootAssemblyHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def export(self) -> '_5674.HarmonicAnalysisRootAssemblyExportOptions':
        '''HarmonicAnalysisRootAssemblyExportOptions: 'Export' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5674.HarmonicAnalysisRootAssemblyExportOptions)(self.wrapped.Export) if self.wrapped.Export else None

    @property
    def assembly_design(self) -> '_2147.RootAssembly':
        '''RootAssembly: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2147.RootAssembly)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None

    @property
    def harmonic_analysis_inputs(self) -> '_2302.HarmonicAnalysis':
        '''HarmonicAnalysis: 'HarmonicAnalysisInputs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2302.HarmonicAnalysis.TYPE not in self.wrapped.HarmonicAnalysisInputs.__class__.__mro__:
            raise CastException('Failed to cast harmonic_analysis_inputs to HarmonicAnalysis. Expected: {}.'.format(self.wrapped.HarmonicAnalysisInputs.__class__.__qualname__))

        return constructor.new_override(self.wrapped.HarmonicAnalysisInputs.__class__)(self.wrapped.HarmonicAnalysisInputs) if self.wrapped.HarmonicAnalysisInputs else None

    @property
    def system_deflection_results(self) -> '_2462.RootAssemblySystemDeflection':
        '''RootAssemblySystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2462.RootAssemblySystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults else None
