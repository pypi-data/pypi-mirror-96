﻿'''_24.py

ShaftMaterialDatabase
'''


from mastapy.materials import _74
from mastapy.shafts import _23
from mastapy._internal.python_net import python_net_import

_SHAFT_MATERIAL_DATABASE = python_net_import('SMT.MastaAPI.Shafts', 'ShaftMaterialDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftMaterialDatabase',)


class ShaftMaterialDatabase(_74.MaterialDatabase['_23.ShaftMaterial']):
    '''ShaftMaterialDatabase

    This is a mastapy class.
    '''

    TYPE = _SHAFT_MATERIAL_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftMaterialDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
