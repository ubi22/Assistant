from kivy.lang.builder import Builder
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.dialog import MDDialog
from kivymd.toast.kivytoast.kivytoast import toast

import sqlite3

Window.size = (450, 800)

kivy = """
<SwipeToDeleteItem>:
    size_hint_y: None
    height: content.height

    MDCardSwipeLayerBox:
        padding: "8dp"

        MDIconButton:
            icon: "trash-can"
            pos_hint: {"center_y": .5}
            on_release: app.remove_item(root)

    MDCardSwipeFrontBox:

        OneLineListItem:
            id: content
            text: root.text
            _no_ripple_effect: True
<Content>
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "120dp"

    MDTextField:
        id: name_dish
        hint_text: "Название блюда"

    MDTextField:
        id: name_weekday
        hint_text: "День"
<Item>
    IconLeftWidget:
        icon: root.icon
<MDButton>
    text: root.text
    md_bg_color:0.25, 0.25, 0.25,1
    text_color: 1,1,1,1
    size_hint: .15, .3
    on_release: app.see_week(self.text)
Screen:
    MDScreenManager:
        id: screen_manager
        Screen:
            name: 'main_screen'
            MDScrollView:
                MDList:
                    id: list_dishes
                    padding: 0

            MDFloatingActionButton:
                icon: "plus"
                pos_hint: {"center_x": .85, "center_y": .15}
                on_release: app.screen("add_product_screen")
        Screen:
            name: 'add_product_screen'
            BoxLayout:
                orientation: 'vertical'

                MDTopAppBar:
                    md_bg_color: .1,.1,.1,1
                    left_action_items: [["arrow-left", lambda x: app.screen("main_screen")]]
                    right_action_items: [["menu", lambda x: app.dialog_menu()]]
                MDBottomNavigation:
                    panel_color: .1,.1,.1,1
                    selected_color_background: "orange"
                    text_color_active: "lightgrey"

                    MDBottomNavigationItem:
                        name: 'screen 1'
                        text: "1 Неделя"
                        MDGridLayout:
                            cols: 3
                            id: week1
                    MDBottomNavigationItem:
                        name: 'screen 2'
                        text: '2 Неделя'
                        MDGridLayout:
                            cols: 3
                            id: week2
        Screen:
            name: "dishes_day"
            BoxLayout:
                orientation: 'vertical'
                MDTopAppBar:
                    md_bg_color: .1,.1,.1,1
                    left_action_items: [["arrow-left", lambda x: app.screen("main_screen")]]
                MDBottomNavigation:
                    md_bg_color: .1,.1,.1,1
                    selected_color_background: "orange"
                    text_color_active: "lightgrey"

                    MDBottomNavigationItem:
                        name: 'screen 1'
                        text: "Блюда"
                        MDGridLayout:
                            cols: 3
                            id: grid_dishes
                    MDBottomNavigationItem:
                        text: "Каждый день"
                        MDGridLayout:
                            cols: 3
                            id: grid_dishes_every_day

"""

with sqlite3.connect("base_dishes.db") as db:
    cursor = db.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS dishes(
        weekday TEXT,
        dish TEXT

)
    """

    cursor.executescript(query)


class Content(MDBoxLayout):
    pass


class Item(OneLineIconListItem):
    divider = None
    icon = StringProperty()


class MDButton(MDRaisedButton):
    text = StringProperty()


class SwipeToDeleteItem(MDCardSwipe):
    text = StringProperty()


class MyAssistant(MDApp):
    dialog = None

    def on_start(self):
        week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
        for i in week: self.root.ids.week1.add_widget(MDButton(text=i+"1"))
        for i in week: self.root.ids.week2.add_widget(MDButton(text=i+"2"))

    def dialog_menu(self):
        self.dialog = MDDialog(
            title="Меню",
            type="simple",
            items=[
                Item(text="Новый гость", icon="account-plus", on_release=lambda x:self.clear_list()),
                Item(text="Добавить блюдо", icon="database-plus", on_release=lambda x: self.dialog_add_dishes())
            ],
        )
        self.dialog.open()

    def clear_list(self):
        self.dialog.dismiss()
        toast("Список очищен")
        self.root.ids.list_dishes.clear_widgets()

    def dialog_add_dishes(self):
        self.dialog.dismiss()
        self.dialog = MDDialog(
                title="Добавление блюда",
                type="custom",
                auto_dismiss=False,
                content_cls=Content(),
                buttons=[
                    MDRaisedButton(
                        text="Отмена",
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="Добавить",
                        on_release=lambda x: self.add_product_in_base()
                    ),
                ],
            )
        self.dialog.open()

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        return Builder.load_string(kivy)

    def screen(self, name):
        self.root.ids.screen_manager.current = name

    def see_week(self, week):
        with sqlite3.connect("base_dishes.db") as db:
            cursor = db.cursor()
            cursor.execute(f'''SELECT * FROM dishes WHERE weekday LIKE '%{week}%';''')
            three_results = cursor.fetchall()
            print(three_results)
            self.root.ids.grid_dishes.clear_widgets()
            for i in three_results:
                self.root.ids.grid_dishes.add_widget(
                    MDRaisedButton(
                        text=i[1],
                        md_bg_color=(0.25, 0.25, 0.25, 1),
                        text_color=(1, 1, 1, 1),
                        size_hint=(.15, .3),
                        on_release=lambda x:self.add_product(x.text),
                    )
                )
            cursor.execute(f'''SELECT * FROM dishes WHERE weekday LIKE '%Каждый день%';''')
            three_results = cursor.fetchall()
            for i in three_results:
                self.root.ids.grid_dishes_every_day.add_widget(
                    MDRaisedButton(
                        text=i[1],
                        md_bg_color=(0.25, 0.25, 0.25, 1),
                        text_color=(1, 1, 1, 1),
                        size_hint=(.15, .3),
                        on_release=lambda x: self.add_product(x.text),
                    )
                )
            self.screen("dishes_day")

    def remove_item(self, instance):
        self.root.ids.list_dishes.remove_widget(instance)

    def add_product_in_base(self):
        weekday = self.dialog.content_cls.ids.name_weekday.text
        name_dish = self.dialog.content_cls.ids.name_dish.text
        if len(name_dish) == 0 or len(weekday) == 0:
            toast('adad')
            return
        with sqlite3.connect("base_dishes.db") as db:
            cursor = db.cursor()
            values = [weekday, name_dish]
            cursor.execute("INSERT INTO dishes(weekday, dish) VALUES(?,?)", values)
            toast('Создано')

    def add_product(self, dish):
        print(dish)
        self.root.ids.list_dishes.add_widget(
            SwipeToDeleteItem(
                text=dish,
            )
        )


MyAssistant().run()
