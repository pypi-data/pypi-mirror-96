﻿'''_5074.py

CVTMultiBodyDynamicsAnalysis
'''


from mastapy.system_model.part_model.couplings import _2180
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.mbd_analyses import _5042
from mastapy._internal.python_net import python_net_import

_CVT_MULTI_BODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'CVTMultiBodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTMultiBodyDynamicsAnalysis',)


class CVTMultiBodyDynamicsAnalysis(_5042.BeltDriveMultiBodyDynamicsAnalysis):
    '''CVTMultiBodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _CVT_MULTI_BODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTMultiBodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2180.CVT':
        '''CVT: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2180.CVT)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None
