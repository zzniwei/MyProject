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
from listctrl import ListCtrl
from kivy.app import App
from kivy.uix.scrollview import ScrollView


class MyView(ScrollView):
    """docstring for MyView"""
    def __init__(self, *arg):
        super(MyView, self).__init__()
        
        self.root = BoxLayout(orientation='vertical', spacing=1)

        head_layout= BoxLayout(size_hint_y=0.1)
        btn1 = Button(text="name")
        head_layout.add_widget(btn1)
        btn2 = Button(text="time")
        head_layout.add_widget(btn2)
        btn3 = Button(text="open")
        head_layout.add_widget(btn3)
        btn4 = Button(text="high")
        head_layout.add_widget(btn4)
        btn5 = Button(text="low")
        head_layout.add_widget(btn5)
        btn6 = Button(text="close")
        head_layout.add_widget(btn6)

        self.root.add_widget(head_layout)
        self.price_view=BoxLayout()
        self.root.add_widget(self.price_view)

        self.add_widget(self.root)


    def InsertRow(self, obj):
        self.price_view.add_widget(obj)


if __name__ == '__main__':
    viw = MyView()
    data=['xauusd', '12:11', '1291.12', '1296.12', '1289.14', '1290.11']
    
    viw.InsertRow(ListCtrl(item_strings=data))
    from kivy.base import runTouchApp
    runTouchApp(viw)
    