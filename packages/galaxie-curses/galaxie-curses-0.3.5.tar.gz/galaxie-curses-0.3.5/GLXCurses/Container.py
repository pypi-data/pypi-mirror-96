#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

import GLXCurses


# Reference Document: https://developer.gnome.org/gtk3/stable/GtkContainer.html
class Container(GLXCurses.Widget):
    """
    GLXCurses.Container — Base class for widgets which contain other widgets

    Description:

    A GLXCurse user interface is constructed by nesting widgets inside widgets. Container widgets are the
    inner nodes in the resulting tree of widgets: they contain other widgets. So, for example, you might have a
    GLXCurse.Window containing a GLXCurse.Frame containing a GLXCurse.Label. If you wanted an image instead of a
    textual label inside the frame, you might replace the GLXCurse.Label widget with a GLXCurse.Image widget.

    There are two major kinds of container widgets in GLXCurses. Both are subclasses of the abstract GLXCurse.Container
    base class.

    The first type of container widget has a single child widget and derives from GLXCurses.Bin. These containers are
    decorators, which add some kind of functionality to the child. For example, a GLXCurses.Button makes its child
    into a clickable button; a GLXCurses.Frame draws a frame around its child and a GLXCurses.Window places its child
    widget inside a top-level window.

    The second type of container can have more than one child; its purpose is to manage layout. This means that these
    containers assign sizes and positions to their children. For example, a GLXCurses.HBox arranges its children in a
    horizontal row, and a GLXCurses.Grid arranges the widgets it contains in a two-dimensional grid.

    For implementations of GLXCurses.Container the virtual method GLXCurses.Container.forall() is always required,
    since it's used for drawing and other internal operations on the children. If the GLXCurses.Container
    implementation expect to have non internal children it's needed to implement both GLXCurses.Container.add() and
    GLXCurses.Container.remove(). If the GLXCurses.Container implementation has internal children, they should be
    added widget.set_parent() on __init__() and removed with widget.unparent() in the GLXCurses.Widget.destroy()
    implementation. See more about implementing custom widgets at https://wiki.gnome.org/HowDoI/CustomWidgets
    """

    def __init__(self):
        GLXCurses.Widget.__init__(self)

        # It's a GLXCurse Type
        self.glxc_type = "GLXCurses.Container"
        self.name = "{0}{1}".format(self.__class__.__name__, self.id)

        # Properties
        self.__child = None
        self.__border_width = None
        self.__resize_mode = None

        self.child = None
        self.border_width = None
        self.resize_mode = None

        # Internal Properties
        # The child widget that has the focus
        self.focus_child = None
        # If True the container needs resizing
        self.need_resize = False
        # if True redraw the container when a child gets reallocated
        self.reallocate_redraws = True
        # If True the container had its focus chain explicitly set
        self.has_focus_chain = False

        # Internal
        self._focus_vadjustment = None
        self._focus_hadjustment = None

    @property
    def border_width(self):
        """
        Set the ``border_width`` property value

        Allowed values: <= 65535

        Default value: 0

        :return: The width of the empty border outside the containers children.
        :rtype: int
        """
        return self.__border_width

    @border_width.setter
    def border_width(self, border_width=None):
        """
        Get the ``border_width`` property value

        Allowed values: <= 65535

        Default value: 0

        :param border_width: The width of the empty border outside the containers children.
        :type border_width: int or None
        """
        if border_width is None:
            border_width = 0

        if type(border_width) != int:
            raise TypeError("'border_width' property value must be a int type or None")
        if not border_width <= 65535:
            raise ValueError("'border_width' property value must be <= to 65535")
        if border_width != self.border_width:
            self.__border_width = border_width

    @property
    def child(self):
        """
        Set the ``child`` property value

        :return: Child element
        :rtype: GLXCurses.ChildElement or None
        """
        return self.__child

    @child.setter
    def child(self, child=None):
        """
        Set the ``child`` property value

        :param child: Child element
        :type child: GLXCurses.ChildElement or None
        :raise TypeError: when ``child`` property value must be a instance of GLXCurses.ChildElement or None
        """
        if child is not None and not isinstance(child, GLXCurses.ChildElement):
            raise TypeError(
                "'child' property value must be a instance of GLXCurses.ChildElement or None"
            )

        if self.child != child:
            self.__child = child

    @property
    def resize_mode(self):
        """
        Set the ``resize_mode`` property value

        Default value: ``GLXC.RESIZE_PARENT``

        :return: Specify how resize events are handled.
        :rtype: str
        """
        return self.__resize_mode

    @resize_mode.setter
    def resize_mode(self, resize_mode=None):
        """
        Get the ``resize_mode`` property value

        Default value: GLXCurses.GLXC.RESIZE_PARENT

        :param resize_mode: Specify how resize events are handled.
        :type resize_mode: str or None
        :raise TypeError: when 'resize_mode' is not a str type or None
        :raise ValueError; when 'resize_mode' is not in GLXC.ResizeMode valid list
        """
        if resize_mode is None:
            resize_mode = GLXCurses.GLXC.RESIZE_PARENT

        if type(resize_mode) != str:
            raise TypeError("'resize_mode' must must be a str type or None")

        if resize_mode not in GLXCurses.GLXC.ResizeMode:
            raise ValueError("'resize_mode' must a GLXC.ResizeMode")

        if self.resize_mode != resize_mode:
            self.__resize_mode = resize_mode

    def add(self, widget=None):
        """
        Adds widget to container .

        Typically used for simple containers such as Window, Frame, or Button;

        For more complicated layout containers such as Box or Grid, this function will pick default packing
        parameters that may not be correct.

        So consider functions such as
        :func:`GLXCurses.Box.pack_start() <GLXCurses.Box.Box.pack_start>` and
        :func:`GLXCurses.Grid.attach() <GLXCurses.Grid.Grid.attach>` as an alternative to
        :func:`GLXCurses.Container.add() <GLXCurses.Container.Container.add>` in those cases.

        A widget may be added to only one container at a time;
        you (should not) place the same widget inside two different containers.

        :param widget: a widget to be placed inside container
        :type widget: GLXCurses.Widget
        :raise TypeError: if ``widget`` is not a instance of GLXCurses.Widget
        """
        # Try to exit as soon of possible
        if not isinstance(widget, GLXCurses.Widget):
            raise TypeError("'widget' must be an instance of GLXCurses.Widget")

        # If we are here everything look ok
        if bool(self.child):
            if callable(getattr(self.child.widget, "unparent")):
                self.child.widget.unparent()

        # The added widget receive a parent
        widget.parent = self
        widget.stdscr = GLXCurses.Application().stdscr

        self.child = GLXCurses.ChildElement(
            widget=widget,
            widget_name=widget.name,
            widget_type=widget.glxc_type,
            widget_id=widget.id,
            widget_properties=GLXCurses.ChildProperty(position=0),
        )

        if hasattr(self.child.widget, 'update_preferred_sizes'):
            self.child.widget.update_preferred_sizes()
        self.emit("add", {"widget": self.child.widget, "id": self.child.id})

    def remove(self, widget=None):
        """
        Removes widget from container .

        Widget must be inside container .

        Note that container will own a reference to widget , and that this may be the last reference held; so
        removing a widget from its container can destroy that widget. If you want to use widget again, you need to
        add a reference to it before removing it from a container, using g_object_ref(). If you don’t want to use
        widget again it’s usually more efficient to simply destroy it directly using Widget.destroy() since this
        will remove it from the container and help break any circular reference count cycles.

        :param widget: a current child of container
        :type widget: GLXCurses Widget
        :raise TypeError: if widget is not a instance of GLXCurses.Widget
        """
        # Try to exit as soon of possible
        if not isinstance(widget, GLXCurses.Widget):
            raise TypeError("'widget' must be an instance of GLXCurses.Widget")

        # If we are here everything look ok
        if self.__class__.__name__ in GLXCurses.GLXC.CHILDREN_CONTAINER:
            if hasattr(self, "children"):
                if bool(self.children):
                    count = 0
                    last_found = None
                    for children in self.children:
                        if widget == children.widget:
                            last_found = count
                        count += 1
                    if last_found is not None:
                        self.children.pop(last_found)
                        if callable(getattr(widget, "unparent")):
                            widget.unparent()
        else:
            if hasattr(self, "child"):
                if bool(self.child):
                    if self.child.widget == widget:
                        self.child = None
                        if callable(getattr(widget, "unparent")):
                            widget.unparent()

    def add_with_properties(self, widget=None, properties=None):
        """
        Adds widget to container , setting child properties at the same time. See GLXCurses.Container.add() and
        GLXCurses.Container.child_set() for more details.

        :param widget: a widget to be placed inside container
        :type widget: GLXCurses.Widget
        :param properties: properties to set
        :type properties: GLXCurses.ChildProperty
        :raise TypeError: if ``properties`` is not a GLXCurses.ChildProperty instance
        :raise TypeError: if widget is not a instance of GLXCurses.Widget
        """
        # Try to exit as soon of possible
        if not isinstance(widget, GLXCurses.Widget):
            raise TypeError("'widget' must be an instance of GLXCurses.Widget")
        if not isinstance(properties, GLXCurses.ChildProperty):
            raise TypeError("'properties' must be ChildProperty instance")

        # If we are here everything look ok
        self.add(widget)
        self.child_set(widget, properties)

    def get_resize_mode(self):
        """
        Returns the resize mode for the container.

        Allowed value:
            * GLXC.RESIZE_PARENT
            * GLXC.RESIZE_QUEUE
            * GLXC.RESIZE_IMMEDIATE

        .. seealso:: :func:`GLXCurses.Container.set_resize_mode() <GLXCurses.Constants.Constants.set_resize_mode>`.

        .. warning:: :func:`GLXCurses.Container.get_resize_mode() <GLXCurses.Container.Container.get_resize_mode>`\
        has been deprecated since version 3.12 of GTK+, if will be remove as soon of possible.

        :return: the current resize mode
        :rtype: GLXCurses.Constants
        """
        return self.resize_mode

    def set_resize_mode(self, resize_mode=None):
        """
        Sets the resize mode for the container.

        The resize mode of a container determines whether a resize request will be passed to the container’s parent,
        queued for later execution or executed immediately.

        Allowed value:
            * GLXC.RESIZE_PARENT
            * GLXC.RESIZE_QUEUE
            * GLXC.RESIZE_IMMEDIATE

        .. seealso:: :func:`GLXCurses.Container.get_resize_mode() <GLXCurses.Container.Container.get_resize_mode>`.

        .. warning:: :func:`GLXCurses.Container.set_resize_mode() <GLXCurses.Container.Container.set_resize_mode>`\
        has been deprecated since version 3.12 of GTK+, if will be remove as soon of possible.

        :param resize_mode: the new resize mode
        :type resize_mode: GLXCurses.Constants
        """
        self.resize_mode = resize_mode

    def check_resize(self):
        """
        The check_resize() method emits the "check-resize" signal on the container.
        """
        if self.resize_mode == "PARENT":
            if self.children:
                for child in self.children:
                    pass

    def foreachs(self, callback, *callback_data):
        """
        Invokes callback on each non-internal child of container . See GLXCurses.Container.forall() for details on
        what constitutes an “internal” child. For all practical purposes, this function should iterate over precisely
        those child widgets that were added to the container by the application with explicit add() calls.

        Most applications should use GLXCurses.Container.foreachs(), rather than GLXCurses.Container.forall().

        :param callback: a callback.
        :param callback_data: callback user __area_data
        """
        # Dispatch to every children and child
        if self.__class__.__name__ in GLXCurses.GLXC.CHILDREN_CONTAINER:

            if hasattr(self, "children"):
                if bool(self.children):
                    for child in self.children:
                        for detailed_signal, handler in list(
                            child.widget.subscriptions.items()
                        ):
                            if handler[0] == callback:
                                handler[0](*callback_data)
        else:
            if hasattr(self, "child"):
                if bool(self.child):
                    for detailed_signal, handler in list(
                        self.child.widget.subscriptions.items()
                    ):
                        if handler[0] == callback:
                            handler[0](*callback_data)

    def get_path_for_child(self, child=None):
        """
        Returns a newly created widget path representing all the widget hierarchy from the toplevel down to and
        including child .

        :return: A newly created WidgetPath
        """
        if child is None:
            return None

        # Try to exit as soon of possible
        if not GLXCurses.glxc_type(child):
            raise TypeError('"container" argument must be a GLXCurses object type')

        # If we are here everything look ok
        if self.__class__.__name__ in GLXCurses.GLXC.CHILDREN_CONTAINER:
            if bool(self.children):
                count = 0
                last_found = None
                for children in self.children:
                    if child == children.widget:
                        last_found = count
                    count += 1
                if last_found is not None:
                    if (
                        self.children[last_found].widget.__class__.__name__
                        in GLXCurses.GLXC.CHILDREN_CONTAINER
                    ):
                        return self.children[last_found].widget.glxc_type
                    else:
                        if not bool(self.children[last_found].widget.child):
                            return self.children[last_found].widget.glxc_type
                        else:
                            # no more space in the container
                            return None
                else:
                    # the child is not found
                    return -1
            else:
                # the child is not found that because it have no child in the child list
                return -1
        else:
            if bool(self.child):
                if self.child.widget == child:
                    if (
                        self.child.widget.__class__.__name__
                        in GLXCurses.GLXC.CHILDREN_CONTAINER
                    ):
                        return self.child.widget.glxc_type
                    else:
                        if not bool(self.child.widget.child):
                            return self.child.widget.glxc_type
                        else:
                            # no more space in the container
                            return None
                else:
                    # the child is not found
                    return -1
            else:
                # the child is not found that because it have no child in the child list
                return -1

        parent_list = []
        # parent = self._pop_last_event()
        if bool(parent_list):
            return parent_list
        else:
            return list()

    def forall(self, callback, callback_data):
        pass

    def propagate_expose(self, child, event):
        pass

    def set_focus_chain(self, focusable_widgets):
        pass

    def get_focus_chain(self):
        pass

    def unset_focus_chain(self):
        pass

    def set_reallocate_redraws(self, needs_redraws):
        pass

    def set_focus_child(self, child):
        pass

    def get_focus_child(self):
        pass

    def get_focus_vadjustment(self):
        """
        Retrieves the vertical focus adjustment for the container. See \
        :func:`Container.set_focus_vadjustment() <GLXCurses.Container.Container.set_focus_vadjustment()>`.

        :return: the vertical focus adjustment, or :py:__area_data:`None` if none has been set.
        :rtype: :class:`Adjustment() <GLXCurses.Adjustment.Adjustment()>` or :py:__area_data:`None`
        """
        return self._focus_vadjustment

    def set_focus_vadjustment(self, adjustment=None):
        """
        Hooks up an adjustment to focus handling in a container, so when a child of the container is focused,
        the adjustment is scrolled to show that widget. This function sets the vertical alignment.
        See scrolled_window_get_vadjustment() for a typical way of obtaining the adjustment and
        :func:`Container.set_focus_hadjustment() <GLXCurses.Container.Container.set_focus_hadjustment()>`
        for setting the horizontal adjustment.

        The adjustments have to be in character units and in the same coordinate system as the allocation for
        immediate children of the container.

        :param adjustment: an adjustment which should be adjusted when the focus is \
        moved among the descendants of ``container``
        :type adjustment: :class:`Adjustment() <GLXCurses.Adjustment.Adjustment()>` or :py:__area_data:`None`
        :raise TypeError: if ``adjustment`` is not a :class:`Adjustment() <GLXCurses.Adjustment.Adjustment()>`
        """
        # Try to exit as soon of possible
        if adjustment is not None and not GLXCurses.glxc_type(adjustment):
            raise TypeError('"adjustment" argument must be a GLXCurses object type')

        if adjustment is not None and adjustment.glxc_type != "GLXCurses.Adjustment":
            raise TypeError('"adjustment" argument must be a GLXCurses.Adjustment')

        if adjustment is not None:
            adjustment_info = GLXCurses.ChildElement()
            adjustment_info.widget = adjustment
            adjustment_info.type = adjustment.glxc_type
            adjustment_info.id = adjustment.id

            if self._focus_vadjustment != adjustment_info:
                self._focus_vadjustment = adjustment_info
        else:
            if self._focus_vadjustment is not None:
                self._focus_vadjustment = None

    def get_focus_hadjustment(self):
        """
        Retrieves the horizontal focus adjustment for the container. See \
        :func:`Container.set_focus_hadjustment() <GLXCurses.Container.Container.set_focus_hadjustment()>`.

        :return: the horizontal focus adjustment, or :py:__area_data:`None` if none has been set.
        :rtype: :class:`Adjustment() <GLXCurses.Adjustment.Adjustment()>` or :py:__area_data:`None`
        """
        return self._focus_hadjustment

    def set_focus_hadjustment(self, adjustment):
        """
        Hooks up an adjustment to focus handling in a container, so when a child of the container is focused,
        the adjustment is scrolled to show that widget. This function sets the horizontal alignment.
        See scrolled_window_get_hadjustment() for a typical way of obtaining the adjustment and
        :func:`Container.set_focus_vadjustment() <GLXCurses.Container.Container.set_focus_vadjustment()>`
        for setting the vertical adjustment.

        The adjustments have to be in pixel units and in the same coordinate system as the allocation for immediate
        children of the container.

        :param adjustment: an adjustment which should be adjusted when the focus is \
        moved among the descendants of ``container``
        :type adjustment: :class:`Adjustment() <GLXCurses.Adjustment.Adjustment()>` or :py:__area_data:`None`
        :raise TypeError: if ``adjustment`` is not a :class:`Adjustment() <GLXCurses.Adjustment.Adjustment()>`
        """
        # Try to exit as soon of possible
        if adjustment is not None and not GLXCurses.glxc_type(adjustment):
            raise TypeError('"adjustment" argument must be a GLXCurses object type')

        if adjustment is not None and adjustment.glxc_type != "GLXCurses.Adjustment":
            raise TypeError('"adjustment" argument must be a GLXCurses.Adjustment')

        if adjustment is not None:
            adjustment_info = GLXCurses.ChildElement(
                widget=adjustment,
                widget_name=adjustment.name,
                widget_type=adjustment.glxc_type,
                widget_id=adjustment.id,
            )

            if self._focus_hadjustment != adjustment_info:
                self._focus_hadjustment = adjustment_info
        else:
            if self._focus_hadjustment is not None:
                self._focus_hadjustment = None

    # def resize_children(self):
    #     pass

    def child_type(self, container):
        """
        Returns the type of the children supported by the container.

        Note that this may return ``None`` to indicate that no more children can be added,
        e.g. for a Paned which already has two children.

        Note that this may return ``-1`` to indicate ``container`` is not found

        :param container:
        :return: the type of children
        :rtype: str , None or -1
        :raise TypeError: if ``child`` is not a GLXCurses type as tested by \
        :func:`glxc_type() <GLXCurses.Utils.glxc_type>`
        """
        # Try to exit as soon of possible
        if not GLXCurses.glxc_type(container):
            raise TypeError('"container" argument must be a GLXCurses object type')

        # If we are here everything look ok
        if self.__class__.__name__ in GLXCurses.GLXC.CHILDREN_CONTAINER:
            if bool(self.children):
                count = 0
                last_found = None
                for children in self.children:
                    if container == children.widget:
                        last_found = count
                    count += 1
                if last_found is not None:
                    if (
                        self.children[last_found].widget.__class__.__name__
                        in GLXCurses.GLXC.CHILDREN_CONTAINER
                    ):
                        return self.children[last_found].widget.glxc_type
                    else:
                        if not bool(self.children[last_found].widget.child):
                            return self.children[last_found].widget.glxc_type
                        else:
                            # no more space in the container
                            return None
                else:
                    # the child is not found
                    return -1
            else:
                # the child is not found that because it have no child in the child list
                return -1
        else:
            if self.child is not None:
                if self.child.widget == container:
                    if (
                        self.child.widget.__class__.__name__
                        in GLXCurses.GLXC.CHILDREN_CONTAINER
                    ):
                        return self.child.widget.glxc_type
                    else:
                        if not bool(self.child.widget.child):
                            return self.child.widget.glxc_type
                        else:
                            # no more space in the container
                            return None
                else:
                    # the child is not found
                    return -1
            else:
                # the child is not found that because it have no child in the child list
                return -1

    def child_set(self, child, properties=None):
        """
        Sets one or more child properties for child and container .

        :param child: a GLXCurses.Widget which is a child of container
        :type child: A GLXCurses.Widget
        :param properties: properties to set
        :type properties: GLXCurses.ChildProperty
        :raise TypeError: if ``child`` is not a GLXCurses type as tested by \
        :func:`glxc_type() <GLXCurses.Utils.glxc_type>`
        :raise TypeError: if ``properties`` is not a dict type
        """
        # Try to exit as soon of possible
        if not GLXCurses.glxc_type(child):
            raise TypeError('"child" argument must be a GLXCurses object type')
        if not isinstance(properties, GLXCurses.ChildProperty):
            raise TypeError('"properties" argument must be a ChildProperty instance')

        # If we are here everything look ok
        if self.__class__.__name__ in GLXCurses.GLXC.CHILDREN_CONTAINER:
            if bool(self.children):
                count = 0
                last_found = None
                for children in self.children:
                    if child == children.widget:
                        last_found = count
                    count += 1
                if last_found is not None:
                    self.children[last_found].properties = properties

        else:
            if self.child is not None:
                if self.child.widget == child:
                    self.child.properties = properties

    def child_get(self, child):
        """
        Gets the values of one or more child properties for child and container .

        :param child: a widget which is a child of container
        :type child: A GLXCurses object
        :return: properties of the child or None if child not found
        :rtype: dict or None
        :raise TypeError: if ``child`` is not a GLXCurses type as tested by \
        :func:`glxc_type() <GLXCurses.Utils.glxc_type>`
        """
        # Try to exit as soon of possible
        if not GLXCurses.glxc_type(child):
            raise TypeError('"child" argument must be a GLXCurses object type')

        # If we are here everything look ok
        if self.__class__.__name__ in GLXCurses.GLXC.CHILDREN_CONTAINER:
            if bool(self.children):
                count = 0
                last_found = None
                for children in self.children:
                    if child == children.widget:
                        last_found = count
                    count += 1
                if last_found is not None:
                    return self.children[last_found].properties
                else:
                    # the child is not found
                    return None
        else:
            if child is not None:
                if self.child.widget == child:
                    return self.child.properties
                else:
                    # the child is not found
                    return None

    def child_set_property(self, child, property_name=None, value=None):
        """
        Sets a child property for child and container .

        :param child: a GLXCurses.Widget which is a child of GLXCurses.Container
        :type child: a GLXCures.Widget
        :param property_name: the name of the property to set
        :type property_name: str
        :param value: the value to set the property to
        :type value: everything except None
        :raise TypeError: if ``child`` is not a GLXCurses type as tested by \
        :func:`glxc_type() <GLXCurses.Utils.glxc_type>`
        :raise TypeError: if ``property_name`` is not str type
        :raise TypeError: if ``value`` is None type
        """
        # Try to exit as soon of possible
        if not GLXCurses.glxc_type(child):
            raise TypeError('"child" argument must be a GLXCurses object type')
        if type(property_name) != str:
            raise TypeError('"property_name" argument must be a str type')
        if value is None:
            raise TypeError('"value" argument cant be a None type')

        # If we are here everything look ok
        property_to_set = {property_name: value}
        if self.__class__.__name__ in GLXCurses.GLXC.CHILDREN_CONTAINER:
            if bool(self.children):
                count = 0
                last_found = None
                for children in self.children:
                    if child == children.widget:
                        last_found = count
                    count += 1
                if last_found is not None:
                    setattr(self.children[last_found].properties, property_name, value)
        else:
            if self.child is not None:
                if self.child.widget == child:
                    setattr(self.child.properties, property_name, value)

    def child_get_property(self, child, property_name=None):
        """
        Gets the value of a child property for child and container .

        :param child: a widget which is a child of container
        :type child: a GLXCures Object
        :param property_name: the name of the property to set
        :type property_name: str
        :raise TypeError: if ``child`` is not a GLXCurses type as tested by \
        :func:`glxc_type() <GLXCurses.Utils.glxc_type>`
        :raise TypeError: if ``property_name`` is not str type
        """
        # Try to exit as soon of possible
        if not GLXCurses.glxc_type(child):
            raise TypeError('"child" argument must be a GLXCurses object type')
        if type(property_name) != str:
            raise TypeError('"property_name" argument must be a str type')

        # If we are here everything look ok
        if self.__class__.__name__ in GLXCurses.GLXC.CHILDREN_CONTAINER:
            if bool(self.children):
                count = 0
                last_found = None
                for children in self.children:
                    if child == children.widget:
                        last_found = count
                    count += 1
                if last_found is not None:
                    try:
                        return getattr(
                            self.children[last_found].properties, property_name
                        )
                    except KeyError:
                        # the property is not found
                        return None
                else:
                    # the child is not found
                    return None
        else:
            if bool(self.child):
                if self.child.widget == child:
                    try:
                        return getattr(self.child.properties, property_name)
                    except KeyError:
                        # the property is not found
                        return None
                else:
                    # the child is not found
                    return None

    def get_border_width(self):
        """
        Retrieves the border width of the container.

        See GLXCurses.Container.set_border_width().

        :return: the current border width
        :rtype: int
        """
        return self.border_width

    def set_border_width(self, border_width=0):
        """
        Sets the border width of the container.

        The border width of a container is the amount of space to leave around the outside of the container. The only
        exception to this is GLXCurses.Window; because toplevel windows can’t leave space outside, they leave the space
        inside. The border is added on all sides of the container. To add space to only one side, use a specific
        “margin” property on the child widget, for example “margin-top”.

        border_width have valid values are in the range 0-65535 chars and will be clamp to value.

        :param border_width: amount of blank space to leave outside the container.
        :type border_width: int
        :raise TypeError: When border_width is not a int
        """
        # Exit as soon of possible
        if type(border_width) != int:
            raise TypeError("'border_width' must be a int type")

        # Clamp on range 0-65535
        border_width = GLXCurses.clamp(value=border_width, smallest=0, largest=65535)
        # make the job
        if self.border_width != border_width:
            self.border_width = border_width
