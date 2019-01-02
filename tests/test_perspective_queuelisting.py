import os
from unittest import mock

import castero.config as config
from castero.episode import Episode
from castero.feed import Feed
from castero.player import Player
from castero.queue import Queue

my_dir = os.path.dirname(os.path.realpath(__file__))

feed = Feed(file=my_dir + "/feeds/valid_basic.xml")
episode = Episode(feed,
                  title="episode title",
                  description="episode description",
                  link="episode link",
                  pubdate="episode pubdate",
                  copyright="episode copyright",
                  enclosure="episode enclosure")
player1 = Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3", episode)
player2 = Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3", episode)
player3 = Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3", episode)
queue = Queue(None) # No one uses config here, we should break if we start
queue.add(player1)
queue.add(player2)


def get_queuelisting_perspective(display):
    """Retrieve the QueueListing perspective.

    Args:
        display: the display containing the loaded perspective

    Returns:
        QueueListing: the loaded QueueListing perspective
    """
    display._active_perspective = 2
    return display.perspectives[2]


def test_perspective_queuelisting_borders(display):
    perspective = get_queuelisting_perspective(display)

    display.display()
    assert perspective._queue_window.hline.call_count == 1
    assert perspective._queue_window.vline.call_count == 1
    assert perspective._metadata_window.hline.call_count == 1
    display._stdscr.reset_mock()


def test_perspective_queuelisting_display_episode_metadata(display):
    perspective = get_queuelisting_perspective(display)

    display._queue = queue

    perspective._draw_metadata = mock.MagicMock()
    display.display()
    perspective._draw_metadata.assert_called_with(perspective._metadata_window,
                                                  episode=queue.first.episode)
    display._stdscr.reset_mock()


def test_perspective_queuelisting_input_keys(display):
    perspective = get_queuelisting_perspective(display)

    display._queue = queue
    display._footer_window.getch = mock.MagicMock(return_value=10)

    myconfig = config._Config()
    ret_val = perspective.handle_input(ord('q'))
    assert not ret_val
    display._stdscr.reset_mock()

    ret_val = perspective.handle_input(ord('h'))
    assert ret_val
    display._stdscr.timeout.assert_any_call(-1)
    display._stdscr.reset_mock()

    movement_keys = [
        display.KEY_MAPPING[myconfig['key_up']],
        display.KEY_MAPPING[myconfig['key_right']],
        display.KEY_MAPPING[myconfig['key_down']],
        display.KEY_MAPPING[myconfig['key_left']],
        display.KEY_MAPPING[myconfig['key_scroll_up']],
        display.KEY_MAPPING[myconfig['key_scroll_down']],
    ]
    for key in movement_keys:
        perspective._metadata_updated = True
        ret_val = perspective.handle_input(key)
        assert ret_val
        assert not perspective._metadata_updated

    operation_keys = [
        display.KEY_MAPPING[myconfig['key_delete']],
        display.KEY_MAPPING[myconfig['key_reload']],
        display.KEY_MAPPING[myconfig['key_play_selected']],
        display.KEY_MAPPING[myconfig['key_add_selected']],
        display.KEY_MAPPING[myconfig['key_clear']],
        display.KEY_MAPPING[myconfig['key_next']],
        display.KEY_MAPPING[myconfig['key_pause_play']],
        display.KEY_MAPPING[myconfig['key_pause_play_alt']],
        display.KEY_MAPPING[myconfig['key_seek_forward']],
        display.KEY_MAPPING[myconfig['key_seek_forward_alt']],
        display.KEY_MAPPING[myconfig['key_seek_backward']],
        display.KEY_MAPPING[myconfig['key_seek_backward_alt']],
    ]
    for key in operation_keys:
        ret_val = perspective.handle_input(key)
        assert ret_val


def test_perspective_queuelisting_draw_metadata(display):
    perspective = get_queuelisting_perspective(display)

    feed.episodes.append(episode)
    display.feeds["feed url"] = feed
    perspective._draw_metadata(perspective._metadata_window, feed=feed)
    perspective._draw_metadata(perspective._metadata_window, episode=episode)


def test_perspective_queuelisting_get_active_menu(display):
    perspective = get_queuelisting_perspective(display)

    perspective._active_window = 0
    assert perspective._get_active_menu() == perspective._queue_menu


def test_perspective_queuelisting_cycle_queue_to_selected_first(display):
    perspective = get_queuelisting_perspective(display)

    perspective._queue_menu._selected = 0
    queue1 = Queue(config._Config)
    queue1.add(player1)
    queue1.add(player2)
    queue1.add(player3)
    display._queue = queue1
    perspective._cycle_queue_to_selected()
    assert queue1.first == player1
    assert queue1.length == 3


def test_perspective_queuelisting_cycle_queue_to_selected_middle(display):
    perspective = get_queuelisting_perspective(display)

    perspective._queue_menu._selected = 1
    queue1 = Queue(config._Config)
    queue1.add(player1)
    queue1.add(player2)
    queue1.add(player3)
    display._queue = queue1
    perspective._cycle_queue_to_selected()
    assert queue1.first == player2
    assert queue1.length == 2


def test_perspective_queuelisting_remove_selected_first(display):
    perspective = get_queuelisting_perspective(display)

    perspective._queue_menu._selected = 0
    queue1 = Queue(config._Config)
    queue1.add(player1)
    queue1.add(player2)
    queue1.add(player3)
    display._queue = queue1
    perspective._remove_selected_from_queue()
    assert queue1.first == player2
    assert queue1.length == 2


def test_perspective_queuelisting_remove_selected_middle(display):
    perspective = get_queuelisting_perspective(display)

    perspective._queue_menu._selected = 1
    queue1 = Queue(config._Config)
    queue1.add(player1)
    queue1.add(player2)
    queue1.add(player3)
    display._queue = queue1
    perspective._remove_selected_from_queue()
    assert queue1.first == player1
    assert queue1.length == 2
