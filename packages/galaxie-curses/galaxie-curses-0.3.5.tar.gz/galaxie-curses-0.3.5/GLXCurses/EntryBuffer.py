#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

# Inspired by: https://developer.gnome.org/gtk3/stable/GtkEntryBuffer.html

import GLXCurses
import sys


class EntryBuffer(GLXCurses.Object):
    """
    EntryBuffer — Text buffer for :func:`GLXCurses.Entry <GLXCurses.Entry.Entry>`
    """

    def __init__(self):
        """
        **Description**

        The :func:`GLXCurses.EntryBuffer <GLXCurses.EntryBuffer.EntryBuffer>` class contains the actual
        text displayed in a :func:`GLXCurses.Entry <GLXCurses.Entry.Entry>` widget.

        A single :func:`GLXCurses.EntryBuffer <GLXCurses.EntryBuffer.EntryBuffer>` object can be shared
        by multiple :func:`GLXCurses.Entry <GLXCurses.Entry.Entry>` widgets which will then share the same text
        content, but not the cursor position, visibility attributes, etc.

        :func:`GLXCurses.EntryBuffer <GLXCurses.EntryBuffer.EntryBuffer>` may be derived from.
        Such a derived class might allow text to be stored in an alternate
        location, such as non-pageable memory, useful in the case of important passwords. Or a derived class could
        integrate with an application’s concept of undo/redo.
        """
        # Load heritage
        GLXCurses.Object.__init__(self)

        # It's a GLXCurse Type
        self.glxc_type = "GLXCurses.EntryBuffer"

        # Widgets can be named, which allows you to refer to them from a GLXCStyle
        self.name = "{0}{1}".format(self.__class__.__name__, self.id)

        # Widget Setting
        self.flags = self.default_flags

        # Properties

        self.__max_length = None
        self.__text = None

        self.max_length = 0
        self.text = None

    @property
    def max_length(self):
        return self.__max_length

    @max_length.setter
    def max_length(self, value=None):
        if value is None:
            value = 0

        if type(value) != int:
            raise TypeError("'max_length' value must be int type or None")

        if self.max_length != GLXCurses.clamp(value=value, smallest=0, largest=65535):
            self.__max_length = GLXCurses.clamp(value=value, smallest=0, largest=65535)

        # If the current contents are longer than the given length, then they will be truncated to fit.
        if self.text is not None and len(self.text) > self.max_length:
            self.set_text(self.text)

    @property
    def length(self):
        """
        The ``length`` property

        Allowed values: <= 65535

        Default value: 0

        :return: The length (in characters) of the text in buffer.
        :rtype: int
        """
        if len(self.text) < 65535:
            return len(self.text)
        return 65535

    @property
    def text(self):
        """
        The ``text`` property

        :return: The contents of the buffer.
        :rtype: char
        """
        return self.__text

    @text.setter
    def text(self, value=None):
        if value is None:
            value = ""
        if type(value) != str:
            raise TypeError("'text' value must be a str type or None")
        if value != self.text:
            self.__text = value

    # GLXC EntryBuffer Functions
    def new(self, initial_chars=None, n_initial_chars=-1):
        """
        Create a new :func:`GLXCurses.EntryBuffer <GLXCurses.EntryBuffer.EntryBuffer>` object.

        Optionally, specify initial text to set in the buffer.

        :param initial_chars: initial buffer text, or None
        :param n_initial_chars: number of characters in initial_chars , or -1
        :return: the new EntryBuffer
        :rtype: GLXCurses.EntryBuffer.EntryBuffer
        :raise TypeError: if ``initial_chars`` is not printable string or None
        :raise TypeError: if ``n_initial_chars`` is not int or -1
        """
        # Try to exit as soon of possible
        if initial_chars is not None:
            for character in initial_chars:
                if character not in GLXCurses.GLXC.Printable:
                    raise TypeError('"initial_chars" must be printable string or None')

        if type(n_initial_chars) != int:
            raise TypeError('"n_initial_chars" must be int type')

        # The big flush, it back to default values
        self.__init__()

        # After init in case we set the initial text
        if initial_chars is not None:
            self.set_text(initial_chars, n_chars=n_initial_chars)
        else:
            self.set_text("")

        # Return something that because we must return something
        return self

    def get_text(self):
        """
        Retrieves the contents of the buffer.

        The memory pointer returned by this call will not change unless this object emits a signal, or is finalized.

        :return: a pointer to the contents of the widget as a string. This string points to internally allocated storage
         in the buffer and must not be freed, modified or stored.
        :rtype: str
        """
        return self.__text

    def set_text(self, chars="", n_chars=-1):
        """
        Sets the text in the buffer.

        This is roughly equivalent to calling EntryBuffer.delete_text() and EntryBuffer.insert_text().

        .. note:: n_chars is in characters, not in bytes.

        :param chars: the new text
        :param n_chars: the number of characters in text , or -1
        :type chars: str
        :type n_chars: int
        :raise TypeError: if ``chars`` is not str
        :raise TypeError: if ``n_chars`` is not int or -1
        """
        # Exit as soon of possible
        # if chars is not None:
        #     for character in chars:
        #         raise TypeError('"chars" must be printable string')

        if type(n_chars) != int:
            raise TypeError('"n_chars" must be int type')

        # Clamp to Max and Min value then set self.text
        if self.max_length <= 0:
            if n_chars <= 0:
                self.text = chars
            else:
                self.text = chars[:n_chars]
        else:
            if n_chars <= 0:
                self.text = chars[: self.max_length]
            else:
                self.text = chars[: self.max_length][:n_chars]

    def get_bytes(self):
        """
        Retrieves the length in bytes of the buffer.

        .. seealso:: EntryBuffer.get_length().

        :return: The byte length of the buffer.
        :rtype: int
        """
        return sys.getsizeof(self.text)

    def get_length(self):
        """
        Retrieves the length in characters of the buffer.

        :return: The number of characters in the buffer.
        :rtype: int
        """
        return self.length

    def get_max_length(self):
        """
        Retrieves the maximum allowed length of the text in buffer .

        .. seealso:: EntryBuffer.set_max_length().

        :return: the maximum allowed number of characters in EntryBuffer, or 0 if there is no maximum.
        :rtype: int
        """
        return self.max_length

    def set_max_length(self, max_length=0):
        """
        Sets the maximum allowed length of the contents of the buffer. If the current contents are longer than the
        given length, then they will be truncated to fit.

        :param max_length: The maximum length of the entry buffer, or 0 for no maximum. (other than the maximum length \
        of entries.) The value passed in will be clamped to the range 0-65536.
        :type max_length: int
        :raise TypeError: if ``max_length`` is not int
        """
        self.max_length = max_length

    def insert_text(self, position=0, chars="", n_chars=-1):
        """
        Inserts ``n_chars`` characters of ``chars`` into the contents of the buffer, at position ``position`` .

        If ``n_chars`` is negative, then characters from chars will be inserted until a null-terminator is found.
        If ``position`` or ``n_chars`` are out of bounds, or the maximum buffer text length is exceeded, then they
        are coerced to sane values.

        .. note:: The position and length are in characters, not in bytes.

        :param position: The position at which to insert text.
        :param chars: The text to insert into the buffer.
        :param n_chars: The length of the text in characters, or -1
        :type position: int
        :type chars: str
        :type n_chars: int
        :return: The number of characters actually inserted.
        :rtype: int
        :raise TypeError: if ``position`` is not int
        :raise TypeError: if ``chars`` is not printable str
        :raise TypeError: if ``n_chars`` is not int
        """
        # Exit as soon of possible
        if type(position) != int:
            raise TypeError('"position" must be int type')
        if chars is not None:
            for character in chars:
                if character not in GLXCurses.GLXC.Printable:
                    raise TypeError('"chars" must be printable string')
        if type(n_chars) != int:
            raise TypeError('"n_chars" must be int type')

        if len(self.text) > 0:

            # Convert the string to a list like a master ... (year !!!!!)
            hash_list = list(self.text)

            # Check n_chars
            if n_chars < 0:
                n_chars = len(self.text)
            else:
                n_chars = GLXCurses.clamp(value=n_chars, smallest=0, largest=65535)

            # Check max_length
            if self.get_max_length() == 0:
                number_of_characters_actually_inserted = len(chars[:n_chars])
            else:
                number_of_characters_actually_inserted = len(chars[:n_chars]) - position

            # Insertion
            hash_list.insert(position, chars[:n_chars])

            # Re assign the buffer text , it will re apply implicitly the max size contain inside self.set_text()
            self.set_text("".join(hash_list))

            # Emit a signal
            self._emit_signal_inserted_text(
                position=position, chars=chars, n_chars=n_chars
            )

            # Because we are like that we return something
            return number_of_characters_actually_inserted

        else:
            # Convert the string to a list like a master ... (year !!!!!)
            position = 0

            # Check n_chars
            if n_chars < 0:
                n_chars = len(chars)
            else:
                n_chars = GLXCurses.clamp(value=n_chars, smallest=0, largest=65535)

            # Check max_length
            number_of_characters_actually_inserted = len(chars[:n_chars])

            # Re assign the buffer text , it will re apply implicitly the max size contain inside self.set_text()
            self.set_text(chars[:n_chars])

            # Emit a signal
            self._emit_signal_inserted_text(
                position=position, chars=chars, n_chars=n_chars
            )

            # Because we are like that we return something
            return number_of_characters_actually_inserted

    def delete_text(self, position=None, n_chars=-1):
        """
        Deletes a sequence of characters from the buffer. ``n_chars`` characters are deleted starting at ``position`` .
        If ``n_chars`` is negative, then all characters until the end of the text are deleted.

        If ``position`` or ``n_chars`` are out of bounds, then they are coerced to sane values.

        .. note:: The positions are specified in characters, not bytes..

        :param position: Position at which to delete text
        :type position: int
        :param n_chars: Number of characters to delete
        :type n_chars: int
        :return: The number of characters deleted.
        :rtype: int
        :raise TypeError: if ``position`` is not int
        :raise TypeError: if ``n_chars`` is not int
        """

        # Try to exit as soon of possible
        if position is None:
            position = 0

        if type(position) != int:
            raise TypeError('"position" must be int type')

        if type(n_chars) != int:
            raise TypeError('"n_chars" must be int type')

        # Convert the string to a list like a master ...
        hash_list = list(self.text)

        # Check n_chars
        if n_chars < 0:
            n_chars = len(self.text)
        else:
            n_chars = GLXCurses.clamp(value=n_chars, smallest=0, largest=65535)

        # Check max_length
        if self.get_max_length() == 0:
            number_of_characters_actually_deleted = n_chars
        else:
            number_of_characters_actually_deleted = len(self.text) - position

        # Delete
        del hash_list[position : int(position + n_chars)]
        # Re assign the buffer text , it will re apply implicitly the max size contain inside self.set_text()
        self.set_text("".join(hash_list))

        # Check impossible case of number of deleted thing
        # if 0 > number_of_characters_actually_deleted:
        #    number_of_characters_actually_deleted = 0

        # Emit a signal
        self._emit_signal_deleted_text(position=position, n_chars=n_chars)

        # Because we are like that we return something
        return number_of_characters_actually_deleted

    def _emit_signal_deleted_text(self, position=None, n_chars=None, user_data=None):
        """
        This signal is emitted after text is deleted from the buffer.

        :param position: The position the text was deleted at.
        :type position: int
        :param n_chars: The number of characters that were deleted.
        :type n_chars: int
        :param user_data: User __area_data set when the signal handler was connected.
        :type user_data: dict or None
        :raise TypeError: if ``position`` is not int
        :raise TypeError: if ``n_chars`` is not int
        :raise TypeError: if ``user_data`` is not a dict or None
        """
        # If user_data is still None replace it by a empty list
        if user_data is None:
            user_data = dict()

        # Exit as soon of possible
        if type(user_data) != dict:
            raise TypeError('"user_data" must be dictionary type')

        if type(position) != int:
            raise TypeError('"position" must be int type')

        if type(n_chars) != int:
            raise TypeError('"n_chars" must be int type')

        # Create a Dict with everything
        instance = {
            "class": self.__class__.__name__,
            "type": "deleted-text",
            "id": self.id,
            "position": position,
            "n_chars": n_chars,
            "user_data": user_data,
        }
        # Emit the signal
        self.emit("SIGNALS", instance)

    def _emit_signal_inserted_text(
        self, position=None, chars=None, n_chars=None, user_data=None
    ):
        """
        This signal is emitted after text is inserted into the buffer.

        :param position: The position the text was inserted at.
        :type position: int
        :param chars: The text that was inserted.
        :type chars: str
        :param n_chars: The number of characters that were inserted.
        :type n_chars: int
        :param user_data: User __area_data set when the signal handler was connected.
        :type user_data: dict or None
        :raise TypeError: if ``position`` is not int
        :raise TypeError: if ``chars`` is not printable str
        :raise TypeError: if ``n_chars`` is not int
        :raise TypeError: if ``user_data`` is not a dict or None
        """
        # If user_data is still None replace it by a empty list
        if user_data is None:
            user_data = dict()

        # Exit as soon of possible
        if type(user_data) != dict:
            raise TypeError('"user_data" must be dictionary type')

        if type(position) != int:
            raise TypeError('"position" must be int type')

        if chars is not None:
            for character in chars:
                if character not in GLXCurses.GLXC.Printable:
                    raise TypeError('"chars" must be printable string')

        if type(n_chars) != int:
            raise TypeError('"n_chars" must be int type')

        # Create a Dict with everything
        instance = {
            "class": self.__class__.__name__,
            "type": "inserted-text",
            "id": self.id,
            "position": position,
            "chars": chars,
            "n_chars": n_chars,
            "user_data": user_data,
        }
        # EVENT EMIT
        self.emit("SIGNALS", instance)
