"""Provide a class for mdnovel chapter representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/mdnvlib
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from mdnvlib.model.basic_element_notes import BasicElementNotes


class Chapter(BasicElementNotes):
    """mdnovel chapter representation."""

    def __init__(self,
            chLevel=None,
            chType=None,
            noNumber=None,
            isTrash=None,
            **kwargs):
        """Extends the superclass constructor."""
        super().__init__(**kwargs)
        self._chLevel = chLevel
        self._chType = chType
        self._noNumber = noNumber
        self._isTrash = isTrash

    @property
    def chLevel(self):
        # 1 = Part level.
        # 2 = Regular chapter level.
        return self._chLevel

    @chLevel.setter
    def chLevel(self, newVal):
        if newVal is not None:
            assert type(newVal) == int
        if self._chLevel != newVal:
            self._chLevel = newVal
            self.on_element_change()

    @property
    def chType(self):
        # 0 = Normal.
        # 1 = Unused.
        return self._chType

    @chType.setter
    def chType(self, newVal):
        if newVal is not None:
            assert type(newVal) == int
        if self._chType != newVal:
            self._chType = newVal
            self.on_element_change()

    @property
    def noNumber(self):
        # True: Exclude this chapter from auto-numbering.
        # False: Auto-number this chapter, if applicable.
        return self._noNumber

    @noNumber.setter
    def noNumber(self, newVal):
        if newVal is not None:
            assert type(newVal) == bool
        if self._noNumber != newVal:
            self._noNumber = newVal
            self.on_element_change()

    @property
    def isTrash(self):
        # True: This chapter is the mdnovel project's "trash bin"
        # False: This is a chapter or part.
        return self._isTrash

    @isTrash.setter
    def isTrash(self, newVal):
        if newVal is not None:
            assert type(newVal) == bool
        if self._isTrash != newVal:
            self._isTrash = newVal
            self.on_element_change()

    def from_yaml(self, yaml):
        super().from_yaml(yaml)
        typeStr = self._get_meta_value('type', '0')
        if typeStr in ('0', '1'):
            self.chType = int(typeStr)
        else:
            self.chType = 1
        chLevel = self._get_meta_value('level', None)
        if chLevel == '1':
            self.chLevel = 1
        else:
            self.chLevel = 2
        self.isTrash = self._get_meta_value('isTrash', None) == '1'
        self.noNumber = self._get_meta_value('noNumber', None) == '1'

    def to_yaml(self, yaml):
        yaml = super().to_yaml(yaml)
        if self.chType:
            yaml.append(f'type: {self.chType}')
        if self.chLevel == 1:
            yaml.append(f'level: 1')
        if self.isTrash:
            yaml.append(f'isTrash: 1')
        if self.noNumber:
            yaml.append(f'noNumber: 1')
        return yaml
