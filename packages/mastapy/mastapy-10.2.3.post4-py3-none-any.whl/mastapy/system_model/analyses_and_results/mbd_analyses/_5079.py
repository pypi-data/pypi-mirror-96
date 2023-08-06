﻿'''_5079.py

CylindricalPlanetGearMultiBodyDynamicsAnalysis
'''


from mastapy.system_model.part_model.gears import _2125
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.mbd_analyses import _5077
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_PLANET_GEAR_MULTI_BODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'CylindricalPlanetGearMultiBodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalPlanetGearMultiBodyDynamicsAnalysis',)


class CylindricalPlanetGearMultiBodyDynamicsAnalysis(_5077.CylindricalGearMultiBodyDynamicsAnalysis):
    '''CylindricalPlanetGearMultiBodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_PLANET_GEAR_MULTI_BODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalPlanetGearMultiBodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2125.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2125.CylindricalPlanetGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None
