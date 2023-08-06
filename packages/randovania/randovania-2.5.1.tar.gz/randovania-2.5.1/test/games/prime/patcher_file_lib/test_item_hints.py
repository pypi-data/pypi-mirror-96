import dataclasses
from unittest.mock import MagicMock

import pytest

from randovania.game_description.area import Area
from randovania.game_description.area_location import AreaLocation
from randovania.game_description.assignment import PickupTarget
from randovania.game_description.hint import Hint, HintType, HintLocationPrecision, HintItemPrecision, PrecisionPair, \
    RelativeDataItem, RelativeDataArea, HintRelativeAreaName, HintDarkTemple
from randovania.game_description.item.item_category import ItemCategory
from randovania.game_description.node import LogbookNode, PickupNode
from randovania.game_description.resources.pickup_entry import PickupEntry, ConditionalResources
from randovania.game_description.resources.pickup_index import PickupIndex
from randovania.game_description.world import World
from randovania.game_description.world_list import WorldList
from randovania.games.prime import echoes_items
from randovania.games.prime.patcher_file_lib import item_hints
from randovania.games.prime.patcher_file_lib.hint_name_creator import LocationHintCreator
from randovania.games.prime.patcher_file_lib.item_hints import RelativeItemFormatter, RelativeAreaFormatter
from randovania.interface_common.players_configuration import PlayersConfiguration


@pytest.fixture(name="pickup")
def _pickup() -> PickupEntry:
    return PickupEntry(
        name="Pickup",
        model_index=0,
        item_category=ItemCategory.MOVEMENT,
        broad_category=ItemCategory.LIFE_SUPPORT,
        resources=(
            ConditionalResources(None, None, ()),
        ),
    )


@pytest.fixture(name="players_config")
def _players_configuration() -> PlayersConfiguration:
    return PlayersConfiguration(
        player_index=0,
        player_names={0: "Player 1"},
    )


def _create_world_list(asset_id: int, pickup_index: PickupIndex):
    logbook_node = LogbookNode("Logbook A", True, None, 0, asset_id, None, None, None, None)
    pickup_node = PickupNode("Pickup Node", True, None, 1, pickup_index, True)

    world_list = WorldList([
        World("World", "Dark World", 5000, [
            Area("Area", False, 10000, 0, True, [logbook_node, pickup_node], {}),
            Area("Other Area", False, 20000, 0, True, [PickupNode(f"Pickup {i}", True, None, 1, PickupIndex(i), True)
                                                       for i in range(pickup_index.index)], {}),
        ]),
    ])

    return logbook_node, pickup_node, world_list


def test_create_hints_nothing(empty_patches, players_config):
    # Setup
    asset_id = 1000
    pickup_index = PickupIndex(0)

    logbook_node, _, world_list = _create_world_list(asset_id, pickup_index)

    patches = dataclasses.replace(
        empty_patches,
        hints={
            logbook_node.resource(): Hint(HintType.LOCATION,
                                          PrecisionPair(HintLocationPrecision.DETAILED, HintItemPrecision.DETAILED,
                                                        include_owner=False),
                                          pickup_index)
        })
    rng = MagicMock()

    # Run
    result = item_hints.create_hints({0: patches}, players_config, world_list, rng)

    # Assert
    message = ("The &push;&main-color=#FF6705B3;Energy Transfer Module&pop; can be found in "
               "&push;&main-color=#FF3333;World - Area&pop;.")
    assert result == [
        {'asset_id': asset_id, 'strings': [message, '', message]}
    ]


def test_create_hints_item_joke(empty_patches, players_config, pickup):
    # Setup
    asset_id = 1000
    logbook_node, _, world_list = _create_world_list(asset_id, PickupIndex(50))

    patches = dataclasses.replace(
        empty_patches,
        hints={
            logbook_node.resource(): Hint(HintType.JOKE, None)
        })
    rng = MagicMock()

    # Run
    result = item_hints.create_hints({0: patches}, players_config, world_list, rng)

    # Assert
    joke = "While walking, holding L makes you move faster."
    message = f"&push;&main-color=#45F731;{joke}&pop;"
    assert result[0]['strings'][0] == message
    assert result == [{'asset_id': asset_id, 'strings': [message, '', message]}]


@pytest.mark.parametrize(["indices", "expected_message"], [
    ((0, 1, 2), "The keys to &push;&main-color=#FF6705B3;Dark Torvus Temple&pop; can "
                "all be found in &push;&main-color=#FF3333;Temple Grounds&pop;."),
    ((0, 1, 118), "The keys to &push;&main-color=#FF6705B3;Dark Torvus Temple&pop; can "
                  "be found in &push;&main-color=#FF3333;Sanctuary Fortress&pop; "
                  "and &push;&main-color=#FF3333;Temple Grounds&pop;."),
    ((0, 41, 118), "The keys to &push;&main-color=#FF6705B3;Dark Torvus Temple&pop; can "
                   "be found in &push;&main-color=#FF3333;Dark Agon Wastes&pop;, "
                   "&push;&main-color=#FF3333;Sanctuary Fortress&pop; and "
                   "&push;&main-color=#FF3333;Temple Grounds&pop;."),
])
def test_create_hints_item_dark_temple_keys(empty_patches, players_config, echoes_game_description, pickup,
                                            indices, expected_message):
    # Setup
    db = echoes_game_description.resource_database
    keys = [
        (
            PickupIndex(index),
            dataclasses.replace(pickup, resources=(
                ConditionalResources(None, None, ((db.get_item(item), 1),)),
            ))
        )
        for index, item in zip(indices, echoes_items.DARK_TEMPLE_KEY_ITEMS[1])
    ]

    patches = dataclasses.replace(
        empty_patches,
        pickup_assignment={
            pickup_index: PickupTarget(key, 0)
            for pickup_index, key in keys
        })

    hint = Hint(HintType.RED_TEMPLE_KEY_SET, None, dark_temple=HintDarkTemple.TORVUS_BOG)

    # Run
    result = item_hints.create_message_for_hint(hint, {0: patches}, players_config, None, {},
                                                echoes_game_description.world_list)

    # Assert
    assert result == expected_message


def test_create_message_for_hint_dark_temple_no_keys(empty_patches, players_config, echoes_game_description):
    # Setup
    hint = Hint(HintType.RED_TEMPLE_KEY_SET, None, dark_temple=HintDarkTemple.TORVUS_BOG)

    # Run
    result = item_hints.create_message_for_hint(hint, {0: empty_patches}, players_config, None, {},
                                                echoes_game_description.world_list)

    # Assert
    assert result == 'The keys to &push;&main-color=#FF6705B3;Dark Torvus Temple&pop; are nowhere to be found.'


@pytest.mark.parametrize("item", [
    (HintItemPrecision.DETAILED, "The", "&push;&main-color=#FF6705B3;Pickup&pop;"),
    (HintItemPrecision.PRECISE_CATEGORY, "A", "&push;&main-color=#FF6705B3;movement system&pop;"),
    (HintItemPrecision.GENERAL_CATEGORY, "A", "&push;&main-color=#FF6705B3;major upgrade&pop;"),
    (HintItemPrecision.BROAD_CATEGORY, "A", "&push;&main-color=#FF6705B3;life support system&pop;"),
])
@pytest.mark.parametrize("location", [
    (HintLocationPrecision.DETAILED, "&push;&main-color=#FF3333;World - Area&pop;"),
    (HintLocationPrecision.WORLD_ONLY, "&push;&main-color=#FF3333;World&pop;"),
])
@pytest.mark.parametrize("owner", [False, True])
@pytest.mark.parametrize("is_multiworld", [False, True])
def test_create_hints_item_location(empty_patches, pickup, item, location, owner, is_multiworld):
    # Setup
    asset_id = 1000
    pickup_index = PickupIndex(50)
    logbook_node, _, world_list = _create_world_list(asset_id, pickup_index)
    players_config = PlayersConfiguration(
        player_index=0,
        player_names={i: f"Player {i +  1}"
                      for i in range(int(is_multiworld) + 1)},
    )
    location_precision, determiner, item_name = item
    if owner and is_multiworld:
        determiner = "Player 1's"

    patches = dataclasses.replace(
        empty_patches,
        pickup_assignment={
            pickup_index: PickupTarget(pickup, 0),
        },
        hints={
            logbook_node.resource(): Hint(HintType.LOCATION,
                                          PrecisionPair(location[0], location_precision, include_owner=owner),
                                          pickup_index)
        })
    rng = MagicMock()

    # Run
    result = item_hints.create_hints({0: patches}, players_config, world_list, rng)

    # Assert
    message = "{} {} can be found in {}.".format(determiner, item_name, location[1])
    # message = "The Flying Ing Cache in {} contains {}.".format(location[1], item[1])
    assert result[0]['strings'][0] == message
    assert result == [{'asset_id': asset_id, 'strings': [message, '', message]}]


@pytest.mark.parametrize("pickup_index_and_guardian", [
    (PickupIndex(43), "&push;&main-color=#FF3333;Amorbis&pop;"),
    (PickupIndex(79), "&push;&main-color=#FF3333;Chykka&pop;"),
    (PickupIndex(115), "&push;&main-color=#FF3333;Quadraxis&pop;"),
])
@pytest.mark.parametrize("item", [
    (HintItemPrecision.DETAILED, "the &push;&main-color=#FF6705B3;Pickup&pop;"),
    (HintItemPrecision.PRECISE_CATEGORY, "a &push;&main-color=#FF6705B3;movement system&pop;"),
    (HintItemPrecision.GENERAL_CATEGORY, "a &push;&main-color=#FF6705B3;major upgrade&pop;"),
    (HintItemPrecision.BROAD_CATEGORY, "a &push;&main-color=#FF6705B3;life support system&pop;"),
])
def test_create_hints_guardians(empty_patches, pickup_index_and_guardian, pickup, item, players_config):
    # Setup
    asset_id = 1000
    pickup_index, guardian = pickup_index_and_guardian

    logbook_node, _, world_list = _create_world_list(asset_id, pickup_index)

    patches = dataclasses.replace(
        empty_patches,
        pickup_assignment={
            pickup_index: PickupTarget(pickup, 0),
        },
        hints={
            logbook_node.resource(): Hint(HintType.LOCATION,
                                          PrecisionPair(HintLocationPrecision.GUARDIAN, item[0],
                                                        include_owner=False),
                                          pickup_index)
        })
    rng = MagicMock()

    # Run
    result = item_hints.create_hints({0: patches}, players_config, world_list, rng)

    # Assert
    message = f"{guardian} is guarding {item[1]}."
    assert result == [{'asset_id': asset_id, 'strings': [message, '', message]}]


@pytest.mark.parametrize("item", [
    (HintItemPrecision.DETAILED, "the &push;&main-color=#FF6705B3;Pickup&pop;"),
    (HintItemPrecision.PRECISE_CATEGORY, "a &push;&main-color=#FF6705B3;movement system&pop;"),
    (HintItemPrecision.GENERAL_CATEGORY, "a &push;&main-color=#FF6705B3;major upgrade&pop;"),
    (HintItemPrecision.BROAD_CATEGORY, "a &push;&main-color=#FF6705B3;life support system&pop;"),
])
def test_create_hints_light_suit_location(empty_patches, players_config, pickup, item):
    # Setup
    asset_id = 1000
    pickup_index = PickupIndex(50)

    logbook_node, _, world_list = _create_world_list(asset_id, pickup_index)

    patches = dataclasses.replace(
        empty_patches,
        pickup_assignment={
            pickup_index: PickupTarget(pickup, 0),
        },
        hints={
            logbook_node.resource(): Hint(HintType.LOCATION,
                                          PrecisionPair(HintLocationPrecision.LIGHT_SUIT_LOCATION, item[0],
                                                        include_owner=False),
                                          pickup_index)
        })
    rng = MagicMock()

    # Run
    result = item_hints.create_hints({0: patches}, players_config, world_list, rng)

    # Assert
    message = f"U-Mos's reward for returning the Sanctuary energy is {item[1]}."
    assert result == [{'asset_id': asset_id, 'strings': [message, '', message]}]


@pytest.mark.parametrize(["reference_precision", "reference_name"], [
    (HintItemPrecision.DETAILED, "the Reference Pickup"),
    (HintItemPrecision.PRECISE_CATEGORY, "a movement system"),
    (HintItemPrecision.BROAD_CATEGORY, "a life support system"),
])
@pytest.mark.parametrize(["distance_precise", "distance_text"], [
    (1, "up to"),
    (0, "exactly"),
])
def test_create_message_for_hint_relative_item(echoes_game_description, pickup, players_config,
                                               distance_precise, distance_text,
                                               reference_precision, reference_name):
    world_list = echoes_game_description.world_list
    patches = echoes_game_description.create_game_patches().assign_pickup_assignment({
        PickupIndex(5): PickupTarget(pickup, 0),
        PickupIndex(15): PickupTarget(dataclasses.replace(pickup, name="Reference Pickup"), 0),
    })

    hint_name_creator = LocationHintCreator(world_list, None, None)
    location_formatters = {
        HintLocationPrecision.RELATIVE_TO_INDEX: RelativeItemFormatter(world_list, patches, players_config),
    }
    hint = Hint(
        HintType.LOCATION,
        PrecisionPair(HintLocationPrecision.RELATIVE_TO_INDEX, HintItemPrecision.DETAILED, include_owner=False,
                      relative=RelativeDataItem(distance_precise, PickupIndex(15), reference_precision)),
        PickupIndex(5)
    )

    # Run
    result = item_hints.create_message_for_hint(hint, {0: patches}, players_config, hint_name_creator,
                                                location_formatters,
                                                world_list)

    # Assert
    assert result == (f'The &push;&main-color=#FF6705B3;Pickup&pop; can be found '
                      f'&push;&main-color=#FF3333;{distance_text} {7 + distance_precise} rooms&pop; away from {reference_name}.')


@pytest.mark.parametrize(["offset", "distance_text"], [
    (2, "up to"),
    (0, "exactly"),
])
def test_create_message_for_hint_relative_area(echoes_game_description, pickup, players_config,
                                               offset, distance_text):
    world_list = echoes_game_description.world_list
    patches = echoes_game_description.create_game_patches().assign_pickup_assignment({
        PickupIndex(5): PickupTarget(pickup, 0),
    })

    hint_name_creator = LocationHintCreator(world_list, None, None)
    location_formatters = {HintLocationPrecision.RELATIVE_TO_AREA: RelativeAreaFormatter(world_list, patches)}
    hint = Hint(
        HintType.LOCATION,
        PrecisionPair(HintLocationPrecision.RELATIVE_TO_AREA, HintItemPrecision.DETAILED, include_owner=False,
                      relative=RelativeDataArea(offset,
                                                AreaLocation(1039999561, 3822429534),
                                                HintRelativeAreaName.NAME)),
        PickupIndex(5)
    )

    # Run
    result = item_hints.create_message_for_hint(hint, {0: patches}, players_config,
                                                hint_name_creator, location_formatters,
                                                world_list)

    # Assert
    assert result == (f'The &push;&main-color=#FF6705B3;Pickup&pop; can be found '
                      f'&push;&main-color=#FF3333;{distance_text} {10 + offset} rooms&pop; away from '
                      f'Torvus Bog - Great Bridge.')
