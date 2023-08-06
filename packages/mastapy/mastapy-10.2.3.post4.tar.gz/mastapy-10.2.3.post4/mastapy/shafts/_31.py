﻿'''_31.py

ShaftRadialHole
'''


from typing import Callable

from mastapy._internal import constructor
from mastapy.shafts import _38, _20
from mastapy._internal.python_net import python_net_import

_SHAFT_RADIAL_HOLE = python_net_import('SMT.MastaAPI.Shafts', 'ShaftRadialHole')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftRadialHole',)


class ShaftRadialHole(_20.ShaftFeature):
    '''ShaftRadialHole

    This is a mastapy class.
    '''

    TYPE = _SHAFT_RADIAL_HOLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftRadialHole.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def add_new_radial_hole(self) -> 'Callable[..., None]':
        '''Callable[..., None]: 'AddNewRadialHole' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AddNewRadialHole

    @property
    def angle(self) -> 'float':
        '''float: 'Angle' is the original name of this property.'''

        return self.wrapped.Angle

    @angle.setter
    def angle(self, value: 'float'):
        self.wrapped.Angle = float(value) if value else 0.0

    @property
    def diameter(self) -> 'float':
        '''float: 'Diameter' is the original name of this property.'''

        return self.wrapped.Diameter

    @diameter.setter
    def diameter(self, value: 'float'):
        self.wrapped.Diameter = float(value) if value else 0.0

    @property
    def surface_roughness(self) -> '_38.ShaftSurfaceRoughness':
        '''ShaftSurfaceRoughness: 'SurfaceRoughness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_38.ShaftSurfaceRoughness)(self.wrapped.SurfaceRoughness) if self.wrapped.SurfaceRoughness else None
