﻿'''_1972.py

Socket
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model import (
    _2118, _2110, _2111, _2114,
    _2116, _2121, _2122, _2125,
    _2126, _2128, _2135, _2136,
    _2137, _2139, _2142, _2144,
    _2145, _2150, _2151, _2119
)
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.part_model.shaft_model import _2154
from mastapy.system_model.part_model.gears import (
    _2184, _2186, _2188, _2189,
    _2190, _2192, _2194, _2196,
    _2198, _2199, _2201, _2205,
    _2207, _2209, _2211, _2214,
    _2216, _2218, _2220, _2221,
    _2222, _2224
)
from mastapy.system_model.part_model.cycloidal import _2240, _2241
from mastapy.system_model.part_model.couplings import (
    _2250, _2253, _2255, _2258,
    _2260, _2261, _2267, _2269,
    _2272, _2275, _2276, _2277,
    _2279, _2281
)
from mastapy.system_model.connections_and_sockets import _1948
from mastapy._internal.python_net import python_net_import
from mastapy import _0

_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'Socket')
_COMPONENT = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'Component')


__docformat__ = 'restructuredtext en'
__all__ = ('Socket',)


class Socket(_0.APIBase):
    '''Socket

    This is a mastapy class.
    '''

    TYPE = _SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Socket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def owner(self) -> '_2118.Component':
        '''Component: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2118.Component.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Component. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_abstract_shaft(self) -> '_2110.AbstractShaft':
        '''AbstractShaft: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2110.AbstractShaft.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to AbstractShaft. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_abstract_shaft_or_housing(self) -> '_2111.AbstractShaftOrHousing':
        '''AbstractShaftOrHousing: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2111.AbstractShaftOrHousing.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to AbstractShaftOrHousing. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_bearing(self) -> '_2114.Bearing':
        '''Bearing: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2114.Bearing.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Bearing. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_bolt(self) -> '_2116.Bolt':
        '''Bolt: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2116.Bolt.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Bolt. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_connector(self) -> '_2121.Connector':
        '''Connector: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2121.Connector.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Connector. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_datum(self) -> '_2122.Datum':
        '''Datum: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2122.Datum.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Datum. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_external_cad_model(self) -> '_2125.ExternalCADModel':
        '''ExternalCADModel: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2125.ExternalCADModel.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to ExternalCADModel. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_fe_part(self) -> '_2126.FEPart':
        '''FEPart: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2126.FEPart.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to FEPart. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_guide_dxf_model(self) -> '_2128.GuideDxfModel':
        '''GuideDxfModel: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2128.GuideDxfModel.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to GuideDxfModel. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_mass_disc(self) -> '_2135.MassDisc':
        '''MassDisc: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2135.MassDisc.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to MassDisc. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_measurement_component(self) -> '_2136.MeasurementComponent':
        '''MeasurementComponent: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2136.MeasurementComponent.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to MeasurementComponent. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_mountable_component(self) -> '_2137.MountableComponent':
        '''MountableComponent: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2137.MountableComponent.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to MountableComponent. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_oil_seal(self) -> '_2139.OilSeal':
        '''OilSeal: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2139.OilSeal.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to OilSeal. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_planet_carrier(self) -> '_2142.PlanetCarrier':
        '''PlanetCarrier: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2142.PlanetCarrier.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to PlanetCarrier. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_point_load(self) -> '_2144.PointLoad':
        '''PointLoad: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2144.PointLoad.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to PointLoad. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_power_load(self) -> '_2145.PowerLoad':
        '''PowerLoad: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2145.PowerLoad.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to PowerLoad. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_unbalanced_mass(self) -> '_2150.UnbalancedMass':
        '''UnbalancedMass: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2150.UnbalancedMass.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to UnbalancedMass. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_virtual_component(self) -> '_2151.VirtualComponent':
        '''VirtualComponent: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2151.VirtualComponent.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to VirtualComponent. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_shaft(self) -> '_2154.Shaft':
        '''Shaft: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2154.Shaft.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Shaft. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_agma_gleason_conical_gear(self) -> '_2184.AGMAGleasonConicalGear':
        '''AGMAGleasonConicalGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2184.AGMAGleasonConicalGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to AGMAGleasonConicalGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_bevel_differential_gear(self) -> '_2186.BevelDifferentialGear':
        '''BevelDifferentialGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2186.BevelDifferentialGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to BevelDifferentialGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_bevel_differential_planet_gear(self) -> '_2188.BevelDifferentialPlanetGear':
        '''BevelDifferentialPlanetGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2188.BevelDifferentialPlanetGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to BevelDifferentialPlanetGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_bevel_differential_sun_gear(self) -> '_2189.BevelDifferentialSunGear':
        '''BevelDifferentialSunGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2189.BevelDifferentialSunGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to BevelDifferentialSunGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_bevel_gear(self) -> '_2190.BevelGear':
        '''BevelGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2190.BevelGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to BevelGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_concept_gear(self) -> '_2192.ConceptGear':
        '''ConceptGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2192.ConceptGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to ConceptGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_conical_gear(self) -> '_2194.ConicalGear':
        '''ConicalGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2194.ConicalGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to ConicalGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_cylindrical_gear(self) -> '_2196.CylindricalGear':
        '''CylindricalGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2196.CylindricalGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to CylindricalGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_cylindrical_planet_gear(self) -> '_2198.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2198.CylindricalPlanetGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to CylindricalPlanetGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_face_gear(self) -> '_2199.FaceGear':
        '''FaceGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2199.FaceGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to FaceGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_gear(self) -> '_2201.Gear':
        '''Gear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2201.Gear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Gear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_hypoid_gear(self) -> '_2205.HypoidGear':
        '''HypoidGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2205.HypoidGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to HypoidGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_klingelnberg_cyclo_palloid_conical_gear(self) -> '_2207.KlingelnbergCycloPalloidConicalGear':
        '''KlingelnbergCycloPalloidConicalGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2207.KlingelnbergCycloPalloidConicalGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to KlingelnbergCycloPalloidConicalGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_klingelnberg_cyclo_palloid_hypoid_gear(self) -> '_2209.KlingelnbergCycloPalloidHypoidGear':
        '''KlingelnbergCycloPalloidHypoidGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2209.KlingelnbergCycloPalloidHypoidGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to KlingelnbergCycloPalloidHypoidGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear(self) -> '_2211.KlingelnbergCycloPalloidSpiralBevelGear':
        '''KlingelnbergCycloPalloidSpiralBevelGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2211.KlingelnbergCycloPalloidSpiralBevelGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to KlingelnbergCycloPalloidSpiralBevelGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_spiral_bevel_gear(self) -> '_2214.SpiralBevelGear':
        '''SpiralBevelGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2214.SpiralBevelGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to SpiralBevelGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_straight_bevel_diff_gear(self) -> '_2216.StraightBevelDiffGear':
        '''StraightBevelDiffGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2216.StraightBevelDiffGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to StraightBevelDiffGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_straight_bevel_gear(self) -> '_2218.StraightBevelGear':
        '''StraightBevelGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2218.StraightBevelGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to StraightBevelGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_straight_bevel_planet_gear(self) -> '_2220.StraightBevelPlanetGear':
        '''StraightBevelPlanetGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2220.StraightBevelPlanetGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to StraightBevelPlanetGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_straight_bevel_sun_gear(self) -> '_2221.StraightBevelSunGear':
        '''StraightBevelSunGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2221.StraightBevelSunGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to StraightBevelSunGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_worm_gear(self) -> '_2222.WormGear':
        '''WormGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2222.WormGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to WormGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_zerol_bevel_gear(self) -> '_2224.ZerolBevelGear':
        '''ZerolBevelGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2224.ZerolBevelGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to ZerolBevelGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_cycloidal_disc(self) -> '_2240.CycloidalDisc':
        '''CycloidalDisc: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2240.CycloidalDisc.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to CycloidalDisc. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_ring_pins(self) -> '_2241.RingPins':
        '''RingPins: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2241.RingPins.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to RingPins. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_clutch_half(self) -> '_2250.ClutchHalf':
        '''ClutchHalf: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2250.ClutchHalf.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to ClutchHalf. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_concept_coupling_half(self) -> '_2253.ConceptCouplingHalf':
        '''ConceptCouplingHalf: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2253.ConceptCouplingHalf.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to ConceptCouplingHalf. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_coupling_half(self) -> '_2255.CouplingHalf':
        '''CouplingHalf: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2255.CouplingHalf.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to CouplingHalf. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_cvt_pulley(self) -> '_2258.CVTPulley':
        '''CVTPulley: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2258.CVTPulley.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to CVTPulley. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_part_to_part_shear_coupling_half(self) -> '_2260.PartToPartShearCouplingHalf':
        '''PartToPartShearCouplingHalf: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2260.PartToPartShearCouplingHalf.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to PartToPartShearCouplingHalf. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_pulley(self) -> '_2261.Pulley':
        '''Pulley: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2261.Pulley.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Pulley. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_rolling_ring(self) -> '_2267.RollingRing':
        '''RollingRing: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2267.RollingRing.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to RollingRing. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_shaft_hub_connection(self) -> '_2269.ShaftHubConnection':
        '''ShaftHubConnection: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2269.ShaftHubConnection.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to ShaftHubConnection. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_spring_damper_half(self) -> '_2272.SpringDamperHalf':
        '''SpringDamperHalf: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2272.SpringDamperHalf.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to SpringDamperHalf. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_synchroniser_half(self) -> '_2275.SynchroniserHalf':
        '''SynchroniserHalf: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2275.SynchroniserHalf.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to SynchroniserHalf. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_synchroniser_part(self) -> '_2276.SynchroniserPart':
        '''SynchroniserPart: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2276.SynchroniserPart.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to SynchroniserPart. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_synchroniser_sleeve(self) -> '_2277.SynchroniserSleeve':
        '''SynchroniserSleeve: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2277.SynchroniserSleeve.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to SynchroniserSleeve. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_torque_converter_pump(self) -> '_2279.TorqueConverterPump':
        '''TorqueConverterPump: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2279.TorqueConverterPump.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to TorqueConverterPump. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def owner_of_type_torque_converter_turbine(self) -> '_2281.TorqueConverterTurbine':
        '''TorqueConverterTurbine: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2281.TorqueConverterTurbine.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to TorqueConverterTurbine. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner else None

    @property
    def connections(self) -> 'List[_1948.Connection]':
        '''List[Connection]: 'Connections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Connections, constructor.new(_1948.Connection))
        return value

    @property
    def connected_components(self) -> 'List[_2118.Component]':
        '''List[Component]: 'ConnectedComponents' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectedComponents, constructor.new(_2118.Component))
        return value

    def connect_to_socket(self, socket: 'Socket') -> '_2119.ComponentsConnectedResult':
        ''' 'ConnectTo' is the original name of this method.

        Args:
            socket (mastapy.system_model.connections_and_sockets.Socket)

        Returns:
            mastapy.system_model.part_model.ComponentsConnectedResult
        '''

        method_result = self.wrapped.ConnectTo.Overloads[_SOCKET](socket.wrapped if socket else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result else None

    def get_possible_sockets_to_connect_to(self, component_to_connect_to: '_2118.Component') -> 'List[Socket]':
        ''' 'GetPossibleSocketsToConnectTo' is the original name of this method.

        Args:
            component_to_connect_to (mastapy.system_model.part_model.Component)

        Returns:
            List[mastapy.system_model.connections_and_sockets.Socket]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.GetPossibleSocketsToConnectTo(component_to_connect_to.wrapped if component_to_connect_to else None), constructor.new(Socket))

    def connect_to(self, component: '_2118.Component') -> '_2119.ComponentsConnectedResult':
        ''' 'ConnectTo' is the original name of this method.

        Args:
            component (mastapy.system_model.part_model.Component)

        Returns:
            mastapy.system_model.part_model.ComponentsConnectedResult
        '''

        method_result = self.wrapped.ConnectTo.Overloads[_COMPONENT](component.wrapped if component else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result else None

    def connection_to(self, socket: 'Socket') -> '_1948.Connection':
        ''' 'ConnectionTo' is the original name of this method.

        Args:
            socket (mastapy.system_model.connections_and_sockets.Socket)

        Returns:
            mastapy.system_model.connections_and_sockets.Connection
        '''

        method_result = self.wrapped.ConnectionTo(socket.wrapped if socket else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result else None
