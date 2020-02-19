#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-04-16 16:57:25
# @Author  : Wei Ni (km_niwei@163.com)
# @Link    : http://example.org
# @Version : V0.1

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.uix.listview import ListView , ListItemLabel,ListItemButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.abstractview import AbstractView
from kivy.event import EventDispatcher
from kivy.properties import *
from math import ceil, floor
from kivy.utils import deprecated
from kivy.adapters.simplelistadapter import SimpleListAdapter
from kivy.clock import Clock
from kivy.compat import PY2
from kivy.uix.widget import Widget



Builder.load_string('''
<ListCtrl>:
    container: container
    ScrollView:
        pos: root.pos
        on_scroll_x:root._scroll(args[1]) 
        do_scroll_y:False 
        GridLayout:
            cols: root.adapter.get_count()
            id: container
            size_hint_y: None
''')

class ListCtrl(AbstractView, EventDispatcher):
    ''':class:`ListCtrl` is a Horizon List View widget,handling the common task
     of presenting items in a scrolling list.Flexibility is afforded by use of a 
    variety of adapters to interface with data.

    The adapter property comes via the mixed in
    :class:`~kivy.uix.abstractview.AbstractView` class.

    :class:`~kivy.uix.listview.ListCtrl` also subclasses
    :class:`EventDispatcher` for scrolling. The event *on_scroll_complete* is
    used in refreshing the main view.

    For a simple list of string items, without selection, use
    :class:`~kivy.adapters.simplelistadapter.SimpleListAdapter`. For list items
    that respond to selection, ranging from simple items to advanced
    composites, use :class:`~kivy.adapters.listadapter.ListAdapter`. For an
    alternate powerful adapter, use
    :class:`~kivy.adapters.dictadapter.DictAdapter`, rounding out the choice
    for designing highly interactive lists.

    :Events:
        `on_scroll_complete`: (boolean, )
            Fired when scrolling completes.
    '''

    divider = ObjectProperty(None)
    '''[TODO] Not used.
    '''

    divider_height = NumericProperty(2)
    '''[TODO] Not used.
    '''

    container = ObjectProperty(None)
    '''The container is a :class:`~kivy.uix.gridlayout.GridLayout` widget held
    within a :class:`~kivy.uix.scrollview.ScrollView` widget.  (See the
    associated kv block in the Builder.load_string() setup). Item view
    instances managed and provided by the adapter are added to this container.
    The container is cleared with a call to clear_widgets() when the list is
    rebuilt by the populate() method. A padding
    :class:`~kivy.uix.widget.Widget` instance is also added as needed,
    depending on the row height calculations.

    :attr:`container` is an :class:`~kivy.properties.ObjectProperty` and
    defaults to None.
    '''

    col_width = NumericProperty(None)
    '''The col_width property is calculated on the basis of the width of the
    container and the count of items.

    :attr:`col_width` is a :class:`~kivy.properties.NumericProperty` and
    defaults to None.
    '''

    item_strings = ListProperty([])
    '''If item_strings is provided, create an instance of
    :class:`~kivy.adapters.simplelistadapter.SimpleListAdapter` with this list
    of strings, and use it to manage a no-selection list.

    :attr:`item_strings` is a :class:`~kivy.properties.ListProperty` and
    defaults to [].
    '''

    scrolling = BooleanProperty(False)
    '''If the scroll_to() method is called while scrolling operations are
    happening, a call recursion error can occur. scroll_to() checks to see that
    scrolling is False before calling populate(). scroll_to() dispatches a
    scrolling_complete event, which sets scrolling back to False.

    :attr:`scrolling` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False.
    '''

    _index = NumericProperty(0)
    _sizes = DictProperty({})
    _count = NumericProperty(0)

    _wstart = NumericProperty(0)
    _wend = NumericProperty(-1)

    __events__ = ('on_scroll_complete', )

    @deprecated
    def __init__(self, **kwargs):
        # Check for an adapter argument. If it doesn't exist, we
        # check for item_strings in use with SimpleListAdapter
        # to make a simple list.
        if 'adapter' not in kwargs:
            if 'item_strings' not in kwargs:
                # Could be missing, or it could be that the ListView is
                # declared in a kv file. If kv is in use, and item_strings is
                # declared there, then item_strings will not be set until after
                # __init__(). So, the data=[] set will temporarily serve for
                # SimpleListAdapter instantiation, with the binding to
                # item_strings_changed() handling the eventual set of the
                # item_strings property from the application of kv rules.
                list_adapter = SimpleListAdapter(data=[],
                                                 cls=Label)
            else:
                list_adapter = SimpleListAdapter(data=kwargs['item_strings'],
                                                 cls=Label)
            kwargs['adapter'] = list_adapter

        super(ListCtrl, self).__init__(**kwargs)

        populate = self._trigger_populate = Clock.create_trigger(
            self._spopulate, -1)
        self._trigger_reset_populate = \
            Clock.create_trigger(self._reset_spopulate, -1)

        fbind = self.fbind
        fbind('size', populate)
        fbind('pos', populate)
        fbind('item_strings', self.item_strings_changed)
        fbind('adapter', populate)

        bind_adapter = self._trigger_bind_adapter = Clock.create_trigger(
            lambda dt: self.adapter.bind_triggers_to_view(
                self._trigger_reset_populate),
            -1)
        fbind('adapter', bind_adapter)

        # The bindings setup above sets self._trigger_populate() to fire
        # when the adapter changes, but we also need this binding for when
        # adapter.data and other possible triggers change for view updating.
        # We don't know that these are, so we ask the adapter to set up the
        # bindings back to the view updating function here.
        bind_adapter()

    # Added to set data when item_strings is set in a kv template, but it will
    # be good to have also if item_strings is reset generally.
    def item_strings_changed(self, *args):
        self.adapter.data = self.item_strings

    def _scroll(self, scroll_x):
        if self.col_width is None:
            return
        self._scroll_x = scroll_x
        scroll_x = 1 - min(1, max(scroll_x, 0))
        container = self.container
        mstart = (container.width - self.width) * scroll_x
        mend = mstart + self.width

        # convert distance to index
        cw = self.col_width
        istart = int(ceil(mstart / cw))
        iend = int(floor(mend / cw))

        istart = max(0, istart - 1)
        iend = max(0, iend - 1)

        if istart < self._wstart:
            rstart = max(0, istart - 10)
            self.populate(rstart, iend)
            self._wstart = rstart
            self._wend = iend
        elif iend > self._wend:
            self.populate(istart, iend + 10)
            self._wstart = istart
            self._wend = iend + 10

    def _spopulate(self, *args):
        self.populate()

    def _reset_spopulate(self, *args):
        self._wend = -1
        self.populate()
        # simulate the scroll again, only if we already scrolled before
        # the position might not be the same, mostly because we don't know the
        # size of the new item.
        if hasattr(self, '_scroll_x'):
            self._scroll(self._scroll_x)

    def populate(self, istart=None, iend=None):
        container = self.container
        sizes = self._sizes
        cw = self.col_width

        # ensure we know what we want to show
        if istart is None:
            istart = self._wstart
            iend = self._wend

        # clear the view
        container.clear_widgets()

        # guess only ?
        if iend is not None and iend != -1:

            # fill with a "padding"
            fh = 0
            for x in range(istart):
                fh += sizes[x] if x in sizes else cw
            container.add_widget(Widget(size_hint_x=None, width=fh))

            # now fill with real item_view
            index = istart
            while index <= iend:
                item_view = self.adapter.get_view(index)
                index += 1
                if item_view is None:
                    continue
                sizes[index] = item_view.width
                container.add_widget(item_view)
        else:
            available_width = self.width
            real_width = 0
            index = self._index
            count = 0
            while available_width > 0:
                item_view = self.adapter.get_view(index)
                if item_view is None:
                    break
                sizes[index] = item_view.width
                index += 1
                count += 1
                container.add_widget(item_view)
                available_width -= item_view.width
                real_width += item_view.width

            self._count = count

            # extrapolate the full size of the container from the size
            # of view instances in the adapter
            if count:
                container.width = \
                    real_width / count * self.adapter.get_count()
                if self.col_width is None:
                    self.col_width = real_width / count

    def scroll_to(self, index=0):
        if not self.scrolling:
            self.scrolling = True
            self._index = index
            self.populate()
            self.dispatch('on_scroll_complete')

    def on_scroll_complete(self, *args):
        self.scrolling = False
    
    def test():
        pass
