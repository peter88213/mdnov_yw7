#!/usr/bin/python3
"""Converter between .mdnov and .yw7 file format.

usage: mdnov_yw7.py sourcefile

Version 0.2.0
Requires Python 3.6+
Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/mdnov_yw7
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
import os
import sys

from calendar import day_name
from calendar import month_name
from datetime import date
from datetime import time
import gettext
import locale

ROOT_PREFIX = 'rt'
CHAPTER_PREFIX = 'ch'
PLOT_LINE_PREFIX = 'ac'
SECTION_PREFIX = 'sc'
PLOT_POINT_PREFIX = 'ap'
CHARACTER_PREFIX = 'cr'
LOCATION_PREFIX = 'lc'
ITEM_PREFIX = 'it'
PRJ_NOTE_PREFIX = 'pn'
CH_ROOT = f'{ROOT_PREFIX}{CHAPTER_PREFIX}'
PL_ROOT = f'{ROOT_PREFIX}{PLOT_LINE_PREFIX}'
CR_ROOT = f'{ROOT_PREFIX}{CHARACTER_PREFIX}'
LC_ROOT = f'{ROOT_PREFIX}{LOCATION_PREFIX}'
IT_ROOT = f'{ROOT_PREFIX}{ITEM_PREFIX}'
PN_ROOT = f'{ROOT_PREFIX}{PRJ_NOTE_PREFIX}'

BRF_SYNOPSIS_SUFFIX = '_brf_synopsis'
CHAPTERS_SUFFIX = '_chapters'
CHARACTER_REPORT_SUFFIX = '_character_report'
CHARACTERS_SUFFIX = '_characters'
CHARLIST_SUFFIX = '_charlist'
DATA_SUFFIX = '_data'
GRID_SUFFIX = '_grid'
ITEM_REPORT_SUFFIX = '_item_report'
ITEMLIST_SUFFIX = '_itemlist'
ITEMS_SUFFIX = '_items'
LOCATION_REPORT_SUFFIX = '_location_report'
LOCATIONS_SUFFIX = '_locations'
LOCLIST_SUFFIX = '_loclist'
PARTS_SUFFIX = '_parts'
PLOTLIST_SUFFIX = '_plotlist'
PLOTLINES_SUFFIX = '_plotlines'
PROJECTNOTES_SUFFIX = '_projectnote_report'
SECTIONLIST_SUFFIX = '_sectionlist'
SECTIONS_SUFFIX = '_sections'
STAGES_SUFFIX = '_structure'


class Error(Exception):
    pass


locale.setlocale(locale.LC_TIME, "")
LOCALE_PATH = f'{os.path.dirname(sys.argv[0])}/locale/'
try:
    CURRENT_LANGUAGE = locale.getlocale()[0][:2]
except:
    CURRENT_LANGUAGE = locale.getdefaultlocale()[0][:2]
try:
    t = gettext.translation('mdnovel', LOCALE_PATH, languages=[CURRENT_LANGUAGE])
    _ = t.gettext
except:

    def _(message):
        return message

WEEKDAYS = day_name
MONTHS = month_name


def norm_path(path):
    if path is None:
        path = ''
    return os.path.normpath(path)


def string_to_list(text, divider=';'):
    elements = []
    try:
        tempList = text.split(divider)
        for element in tempList:
            element = element.strip()
            if element and not element in elements:
                elements.append(element)
        return elements

    except:
        return []


def list_to_string(elements, divider=';'):
    try:
        text = divider.join(elements)
        return text

    except:
        return ''


def intersection(elemList, refList):
    return [elem for elem in elemList if elem in refList]


def verified_date(dateStr):
    if dateStr is not None:
        date.fromisoformat(dateStr)
    return dateStr


def verified_int_string(intStr):
    if intStr is not None:
        int(intStr)
    return intStr


def verified_time(timeStr):
    if  timeStr is not None:
        time.fromisoformat(timeStr)
        while timeStr.count(':') < 2:
            timeStr = f'{timeStr}:00'
    return timeStr



class Ui:

    def __init__(self, title):
        self.infoWhatText = ''
        self.infoHowText = ''

    def ask_yes_no(self, text):
        return True

    def set_status(self, message):
        if message.startswith('!'):
            message = f'FAIL: {message.split("!", maxsplit=1)[1].strip()}'
            sys.stderr.write(message)
        self.infoHowText = message

    def set_info(self, message):
        self.infoWhatText = message

    def show_warning(self, message):
        pass

    def start(self):
        pass



class UiCmd(Ui):

    def __init__(self, title):
        super().__init__(title)
        print(title)

    def ask_yes_no(self, text):
        result = input(f'{_("WARNING")}: {text} (y/n)')
        if result.lower() == 'y':
            return True
        else:
            return False

    def set_info_how(self, message):
        if message.startswith('!'):
            message = f'FAIL: {message.split("!", maxsplit=1)[1].strip()}'
        self.infoHowText = message
        print(message)

    def set_info_what(self, message):
        print(message)

    def show_warning(self, message):
        print(f'\nWARNING: {message}\n')
from datetime import date

from string import Template

from abc import ABC
from urllib.parse import quote



class File(ABC):
    DESCRIPTION = _('File')
    EXTENSION = None
    SUFFIX = None

    def __init__(self, filePath, **kwargs):
        self.novel = None
        self._filePath = None
        self.projectName = None
        self.projectPath = None
        self.sectionsSplit = False
        self.filePath = filePath

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, filePath: str):
        filePath = filePath.replace('\\', '/')
        if self.SUFFIX is not None:
            suffix = self.SUFFIX
        else:
            suffix = ''
        if filePath.lower().endswith(f'{suffix}{self.EXTENSION}'.lower()):
            self._filePath = filePath
            try:
                head, tail = os.path.split(os.path.realpath(filePath))
            except:
                head, tail = os.path.split(filePath)
            self.projectPath = quote(head.replace('\\', '/'), '/:')
            self.projectName = quote(tail.replace(f'{suffix}{self.EXTENSION}', ''))

    def is_locked(self):
        return False

    def read(self):
        raise NotImplementedError

    def write(self):
        raise NotImplementedError



class Filter:

    def accept(self, source, eId):
        return True

    def get_message(self, source):
        return ''
from urllib.parse import quote
from urllib.parse import unquote


class BasicElement:

    def __init__(self,
            on_element_change=None,
            title=None,
            desc=None,
            links=None):
        if on_element_change is None:
            self.on_element_change = self.do_nothing
        else:
            self.on_element_change = on_element_change
        self._title = title
        self._desc = desc
        if links is None:
            self._links = {}
        else:
            self._links = links

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._title != newVal:
            self._title = newVal
            self.on_element_change()

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._desc != newVal:
            self._desc = newVal
            self.on_element_change()

    @property
    def links(self):
        try:
            return self._links.copy()
        except AttributeError:
            return None

    @links.setter
    def links(self, newVal):
        if newVal is not None:
            for elem in newVal:
                val = newVal[elem]
                if val is not None:
                    assert type(val) == str
        if self._links != newVal:
            self._links = newVal
            self.on_element_change()

    def do_nothing(self):
        pass

    def from_yaml(self, yaml):
        self._metaDict = {}
        for entry in yaml:
            try:
                metaData = entry.split(':', maxsplit=1)
                metaKey = metaData[0].strip()
                metaValue = metaData[1].strip()
                self._metaDict[metaKey] = metaValue
            except:
                pass

        self.title = self._get_meta_value('Title')

    def get_links(self):
        linkList = []
        if self.links:
            for path in self.links:
                relativeLink = f'[LinkPath]({quote(path)})'
                if self.links[path]:
                    absoluteLink = f'[FullPath](file:///{quote(self.links[path])})'
                else:
                    absoluteLink = ''
                linkList.append((relativeLink, absoluteLink))
        return linkList

    def set_links(self, linkList):
        links = self.links
        for relativeLink, absoluteLink in linkList:
            links[unquote(relativeLink)] = unquote(absoluteLink).split('file:///')[1]
        self.links = links

    def to_yaml(self, yaml):
        if self.title:
            yaml.append(f'Title: {self.title}')
        return yaml

    def _get_meta_value(self, key, default=None):
        text = self._metaDict.get(key, None)
        if text is not None:
            return text
        else:
            return default



class BasicElementNotes(BasicElement):

    def __init__(self,
            notes=None,
            **kwargs):
        super().__init__(**kwargs)
        self._notes = notes

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._notes != newVal:
            self._notes = newVal
            self.on_element_change()



class BasicElementTags(BasicElementNotes):

    def __init__(self,
            tags=None,
            **kwargs):
        super().__init__(**kwargs)
        self._tags = tags

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, newVal):
        if newVal is not None:
            for elem in newVal:
                if elem is not None:
                    assert type(elem) == str
        if self._tags != newVal:
            self._tags = newVal
            self.on_element_change()

    def from_yaml(self, yaml):
        super().from_yaml(yaml)
        tags = string_to_list(self._get_meta_value('Tags'))
        strippedTags = []
        for tag in tags:
            strippedTags.append(tag.strip())
        self.tags = strippedTags

    def to_yaml(self, yaml):
        yaml = super().to_yaml(yaml)
        if self.tags:
            yaml.append(f'Tags: {list_to_string(self.tags)}')
        return yaml



class WorldElement(BasicElementTags):

    def __init__(self,
            aka=None,
            **kwargs):
        super().__init__(**kwargs)
        self._aka = aka

    @property
    def aka(self):
        return self._aka

    @aka.setter
    def aka(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._aka != newVal:
            self._aka = newVal
            self.on_element_change()

    def from_yaml(self, yaml):
        super().from_yaml(yaml)
        self.aka = self._get_meta_value('Aka')

    def to_yaml(self, yaml):
        yaml = super().to_yaml(yaml)
        if self.aka:
            yaml.append(f'Aka: {self.aka}')
        return yaml



class Character(WorldElement):
    MAJOR_MARKER = _('Major Character')
    MINOR_MARKER = _('Minor Character')

    def __init__(self,
            bio=None,
            goals=None,
            fullName=None,
            isMajor=None,
            birthDate=None,
            deathDate=None,
            **kwargs):
        super().__init__(**kwargs)
        self._bio = bio
        self._goals = goals
        self._fullName = fullName
        self._isMajor = isMajor
        self._birthDate = birthDate
        self._deathDate = deathDate

    @property
    def bio(self):
        return self._bio

    @bio.setter
    def bio(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._bio != newVal:
            self._bio = newVal
            self.on_element_change()

    @property
    def goals(self):
        return self._goals

    @goals.setter
    def goals(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._goals != newVal:
            self._goals = newVal
            self.on_element_change()

    @property
    def fullName(self):
        return self._fullName

    @fullName.setter
    def fullName(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._fullName != newVal:
            self._fullName = newVal
            self.on_element_change()

    @property
    def isMajor(self):
        return self._isMajor

    @isMajor.setter
    def isMajor(self, newVal):
        if newVal is not None:
            assert type(newVal) == bool
        if self._isMajor != newVal:
            self._isMajor = newVal
            self.on_element_change()

    @property
    def birthDate(self):
        return self._birthDate

    @birthDate.setter
    def birthDate(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._birthDate != newVal:
            self._birthDate = newVal
            self.on_element_change()

    @property
    def deathDate(self):
        return self._deathDate

    @deathDate.setter
    def deathDate(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._deathDate != newVal:
            self._deathDate = newVal
            self.on_element_change()

    def from_yaml(self, yaml):
        super().from_yaml(yaml)
        self.isMajor = self._get_meta_value('major', None) == '1'
        self.fullName = self._get_meta_value('FullName')
        self.birthDate = verified_date(self._get_meta_value('BirthDate'))
        self.deathDate = verified_date(self._get_meta_value('DeathDate'))

    def to_yaml(self, yaml):
        yaml = super().to_yaml(yaml)
        if self.isMajor:
            yaml.append(f'major: 1')
        if self.fullName:
            yaml.append(f'FullName: {self.fullName}')
        if self.birthDate:
            yaml.append(f'BirthDate: {self.birthDate}')
        if self.deathDate:
            yaml.append(f'DeathDate: {self.deathDate}')
        return yaml

from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
import re

from calendar import isleap
from datetime import date
from datetime import datetime
from datetime import timedelta


def difference_in_years(startDate, endDate):
    diffyears = endDate.year - startDate.year
    difference = endDate - startDate.replace(endDate.year)
    days_in_year = isleap(endDate.year) and 366 or 365
    years = diffyears + (difference.days + difference.seconds / 86400.0) / days_in_year
    return int(years)


def get_age(nowIso, birthDateIso, deathDateIso):
    now = datetime.fromisoformat(nowIso)
    if deathDateIso:
        deathDate = datetime.fromisoformat(deathDateIso)
        if now > deathDate:
            years = difference_in_years(deathDate, now)
            return -1 * years

    birthDate = datetime.fromisoformat(birthDateIso)
    years = difference_in_years(birthDate, now)
    return years


def get_specific_date(dayStr, refIso):
    refDate = date.fromisoformat(refIso)
    return date.isoformat(refDate + timedelta(days=int(dayStr)))


def get_unspecific_date(dateIso, refIso):
    refDate = date.fromisoformat(refIso)
    return str((date.fromisoformat(dateIso) - refDate).days)


ADDITIONAL_WORD_LIMITS = re.compile(r'--|—|–|\<\/p\>')

NO_WORD_LIMITS = re.compile(r'\<note\>.*?\<\/note\>|\<comment\>.*?\<\/comment\>|\<.+?\>')


class Section(BasicElementTags):

    SCENE = ['-', 'A', 'R', 'x']

    STATUS = [
        None,
        _('Outline'),
        _('Draft'),
        _('1st Edit'),
        _('2nd Edit'),
        _('Done')
    ]

    NULL_DATE = '0001-01-01'
    NULL_TIME = '00:00:00'

    def __init__(self,
            scType=None,
            scene=None,
            status=None,
            appendToPrev=None,
            goal=None,
            conflict=None,
            outcome=None,
            plotNotes=None,
            scDate=None,
            scTime=None,
            day=None,
            lastsMinutes=None,
            lastsHours=None,
            lastsDays=None,
            characters=None,
            locations=None,
            items=None,
            **kwargs):
        super().__init__(**kwargs)
        self._sectionContent = None
        self.wordCount = 0

        self._scType = scType
        self._scene = scene
        self._status = status
        self._appendToPrev = appendToPrev
        self._goal = goal
        self._conflict = conflict
        self._outcome = outcome
        self._plotlineNotes = plotNotes
        try:
            newDate = date.fromisoformat(scDate)
            self._weekDay = newDate.weekday()
            self._localeDate = newDate.strftime('%x')
            self._date = scDate
        except:
            self._weekDay = None
            self._localeDate = None
            self._date = None
        self._time = scTime
        self._day = day
        self._lastsMinutes = lastsMinutes
        self._lastsHours = lastsHours
        self._lastsDays = lastsDays
        self._characters = characters
        self._locations = locations
        self._items = items

        self.scPlotLines = []
        self.scPlotPoints = {}

    @property
    def sectionContent(self):
        return self._sectionContent

    @sectionContent.setter
    def sectionContent(self, text):
        if text is not None:
            assert type(text) == str
        if self._sectionContent != text:
            self._sectionContent = text
            if text is not None:
                text = ADDITIONAL_WORD_LIMITS.sub(' ', text)
                text = NO_WORD_LIMITS.sub('', text)
                wordList = text.split()
                self.wordCount = len(wordList)
            else:
                self.wordCount = 0
            self.on_element_change()

    @property
    def scType(self):
        return self._scType

    @scType.setter
    def scType(self, newVal):
        if newVal is not None:
            assert type(newVal) == int
        if self._scType != newVal:
            self._scType = newVal
            self.on_element_change()

    @property
    def scene(self):
        return self._scene

    @scene.setter
    def scene(self, newVal):
        if newVal is not None:
            assert type(newVal) == int
        if self._scene != newVal:
            self._scene = newVal
            self.on_element_change()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, newVal):
        if newVal is not None:
            assert type(newVal) == int
        if self._status != newVal:
            self._status = newVal
            self.on_element_change()

    @property
    def appendToPrev(self):
        return self._appendToPrev

    @appendToPrev.setter
    def appendToPrev(self, newVal):
        if newVal is not None:
            assert type(newVal) == bool
        if self._appendToPrev != newVal:
            self._appendToPrev = newVal
            self.on_element_change()

    @property
    def goal(self):
        return self._goal

    @goal.setter
    def goal(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._goal != newVal:
            self._goal = newVal
            self.on_element_change()

    @property
    def conflict(self):
        return self._conflict

    @conflict.setter
    def conflict(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._conflict != newVal:
            self._conflict = newVal
            self.on_element_change()

    @property
    def outcome(self):
        return self._outcome

    @outcome.setter
    def outcome(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._outcome != newVal:
            self._outcome = newVal
            self.on_element_change()

    @property
    def plotlineNotes(self):
        try:
            return dict(self._plotlineNotes)
        except TypeError:
            return None

    @plotlineNotes.setter
    def plotlineNotes(self, newVal):
        if newVal is not None:
            for elem in newVal:
                val = newVal[elem]
                if val is not None:
                    assert type(val) == str
        if self._plotlineNotes != newVal:
            self._plotlineNotes = newVal
            self.on_element_change()

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._date != newVal:
            if not newVal:
                self._date = None
                self._weekDay = None
                self._localeDate = None
                self.on_element_change()
                return

            try:
                newDate = date.fromisoformat(newVal)
                self._weekDay = newDate.weekday()
            except:
                return

            try:
                self._localeDate = newDate.strftime('%x')
            except:
                self._localeDate = newVal
            self._date = newVal
            self.on_element_change()

    @property
    def weekDay(self):
        return self._weekDay

    @property
    def localeDate(self):
        return self._localeDate

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._time != newVal:
            self._time = newVal
            self.on_element_change()

    @property
    def day(self):
        return self._day

    @day.setter
    def day(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._day != newVal:
            self._day = newVal
            self.on_element_change()

    @property
    def lastsMinutes(self):
        return self._lastsMinutes

    @lastsMinutes.setter
    def lastsMinutes(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._lastsMinutes != newVal:
            self._lastsMinutes = newVal
            self.on_element_change()

    @property
    def lastsHours(self):
        return self._lastsHours

    @lastsHours.setter
    def lastsHours(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._lastsHours != newVal:
            self._lastsHours = newVal
            self.on_element_change()

    @property
    def lastsDays(self):
        return self._lastsDays

    @lastsDays.setter
    def lastsDays(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._lastsDays != newVal:
            self._lastsDays = newVal
            self.on_element_change()

    @property
    def characters(self):
        try:
            return self._characters[:]
        except TypeError:
            return None

    @characters.setter
    def characters(self, newVal):
        if newVal is not None:
            for elem in newVal:
                if elem is not None:
                    assert type(elem) == str
        if self._characters != newVal:
            self._characters = newVal
            self.on_element_change()

    @property
    def locations(self):
        try:
            return self._locations[:]
        except TypeError:
            return None

    @locations.setter
    def locations(self, newVal):
        if newVal is not None:
            for elem in newVal:
                if elem is not None:
                    assert type(elem) == str
        if self._locations != newVal:
            self._locations = newVal
            self.on_element_change()

    @property
    def items(self):
        try:
            return self._items[:]
        except TypeError:
            return None

    @items.setter
    def items(self, newVal):
        if newVal is not None:
            for elem in newVal:
                if elem is not None:
                    assert type(elem) == str
        if self._items != newVal:
            self._items = newVal
            self.on_element_change()

    def day_to_date(self, referenceDate):
        if self._date:
            return True

        try:
            self.date = get_specific_date(self._day, referenceDate)
            self._day = None
            return True

        except:
            self.date = None
            return False

    def date_to_day(self, referenceDate):
        if self._day:
            return True

        try:
            self._day = get_unspecific_date(self._date, referenceDate)
            self.date = None
            return True

        except:
            self._day = None
            return False

    def from_yaml(self, yaml):
        super().from_yaml(yaml)

        typeStr = self._get_meta_value('type', '0')
        if typeStr in ('0', '1', '2', '3'):
            self.scType = int(typeStr)
        else:
            self.scType = 1
        status = self._get_meta_value('status', None)
        if status in ('2', '3', '4', '5'):
            self.status = int(status)
        else:
            self.status = 1
        scene = self._get_meta_value('scene', 0)
        if scene in ('1', '2', '3'):
            self.scene = int(scene)
        else:
            self.scene = 0

        if not self.scene:
            sceneKind = self._get_meta_value('pacing', None)
            if sceneKind in ('1', '2'):
                self.scene = int(sceneKind) + 1

        self.appendToPrev = self._get_meta_value('append', None) == '1'

        self.date = verified_date(self._get_meta_value('Date'))
        if not self.date:
            self.day = verified_int_string(self._get_meta_value('Day'))

        self.time = verified_time(self._get_meta_value('Time'))

        self.lastsDays = verified_int_string(self._get_meta_value('LastsDays'))
        self.lastsHours = verified_int_string(self._get_meta_value('LastsHours'))
        self.lastsMinutes = verified_int_string(self._get_meta_value('LastsMinutes'))

        scCharacters = self._get_meta_value('Characters')
        self.characters = string_to_list(scCharacters)

        scLocations = self._get_meta_value('Locations')
        self.locations = string_to_list(scLocations)

        scItems = self._get_meta_value('Items')
        self.items = string_to_list(scItems)

    def get_end_date_time(self):
        endDate = None
        endTime = None
        endDay = None
        if self.lastsDays:
            lastsDays = int(self.lastsDays)
        else:
            lastsDays = 0
        if self.lastsHours:
            lastsSeconds = int(self.lastsHours) * 3600
        else:
            lastsSeconds = 0
        if self.lastsMinutes:
            lastsSeconds += int(self.lastsMinutes) * 60
        sectionDuration = timedelta(days=lastsDays, seconds=lastsSeconds)
        if self.time:
            if self.date:
                try:
                    sectionStart = datetime.fromisoformat(f'{self.date} {self.time}')
                    sectionEnd = sectionStart + sectionDuration
                    endDate, endTime = sectionEnd.isoformat().split('T')
                except:
                    pass
            else:
                try:
                    if self.day:
                        dayInt = int(self.day)
                    else:
                        dayInt = 0
                    startDate = (date.min + timedelta(days=dayInt)).isoformat()
                    sectionStart = datetime.fromisoformat(f'{startDate} {self.time}')
                    sectionEnd = sectionStart + sectionDuration
                    endDate, endTime = sectionEnd.isoformat().split('T')
                    endDay = str((date.fromisoformat(endDate) - date.min).days)
                    endDate = None
                except:
                    pass
        return endDate, endTime, endDay

    def to_yaml(self, yaml):
        yaml = super().to_yaml(yaml)
        if self.scType:
            yaml.append(f'type: {self.scType}')
        if self.status > 1:
            yaml.append(f'status: {self.status}')
        if self.scene > 0:
            yaml.append(f'scene: {self.scene}')
        if self.appendToPrev:
            yaml.append(f'append: 1')

        if self.date:
            yaml.append(f'Date: {self.date}')
        elif self.day:
            yaml.append(f'Day: {self.day}')
        if self.time:
            yaml.append(f'Time: {self.time}')

        if self.lastsDays and self.lastsDays != '0':
            yaml.append(f'LastsDays: {self.lastsDays}')
        if self.lastsHours and self.lastsHours != '0':
            yaml.append(f'LastsHours: {self.lastsHours}')
        if self.lastsMinutes and self.lastsMinutes != '0':
            yaml.append(f'LastsMinutes: {self.lastsMinutes}')

        if self.characters:
            yaml.append(f'Characters: {list_to_string(self.characters)}')

        if self.locations:
            yaml.append(f'Locations: {list_to_string(self.locations)}')

        if self.items:
            yaml.append(f'Items: {list_to_string(self.items)}')

        return yaml


class FileExport(File):
    SUFFIX = ''
    _fileHeader = ''
    _partTemplate = ''
    _chapterTemplate = ''
    _unusedChapterTemplate = ''
    _sectionTemplate = ''
    _firstSectionTemplate = ''
    _unusedSectionTemplate = ''
    _stage1Template = ''
    _stage2Template = ''
    _sectionDivider = ''
    _chapterEndTemplate = ''
    _unusedChapterEndTemplate = ''
    _characterSectionHeading = ''
    _characterTemplate = ''
    _locationSectionHeading = ''
    _locationTemplate = ''
    _itemSectionHeading = ''
    _itemTemplate = ''
    _fileFooter = ''
    _projectNoteTemplate = ''
    _arcTemplate = ''

    _DIVIDER = ', '

    def __init__(self, filePath, **kwargs):
        super().__init__(filePath, **kwargs)
        self.sectionFilter = Filter()
        self.chapterFilter = Filter()
        self.characterFilter = Filter()
        self.locationFilter = Filter()
        self.itemFilter = Filter()
        self.arcFilter = Filter()
        self.turningPointFilter = Filter()

    def write(self):
        text = self._get_text()
        backedUp = False
        if os.path.isfile(self.filePath):
            try:
                os.replace(self.filePath, f'{self.filePath}.bak')
            except:
                raise Error(f'{_("Cannot overwrite file")}: "{norm_path(self.filePath)}".')
            else:
                backedUp = True
        try:
            with open(self.filePath, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            if backedUp:
                os.replace(f'{self.filePath}.bak', self.filePath)
            raise Error(f'{_("Cannot write file")}: "{norm_path(self.filePath)}".')

    def _convert_from_mdnov(self, text, **kwargs):
        if text is None:
            text = ''
        return(text)

    def _get_arcMapping(self, plId):
        arcMapping = dict(
            ID=plId,
            Title=self._convert_from_mdnov(self.novel.plotLines[plId].title, quick=True),
            Desc=self._convert_from_mdnov(self.novel.plotLines[plId].desc),
            Notes=self._convert_from_mdnov(self.novel.plotLines[plId].notes),
            ProjectName=self._convert_from_mdnov(self.projectName, quick=True),
            ProjectPath=self.projectPath,
        )
        return arcMapping

    def _get_arcs(self):
        lines = []
        for plId in self.novel.tree.get_children(PL_ROOT):
            if self.arcFilter.accept(self, plId):
                if self._arcTemplate:
                    template = Template(self._arcTemplate)
                    lines.append(template.safe_substitute(self._get_arcMapping(plId)))
        return lines

    def _get_chapterMapping(self, chId, chapterNumber):
        if chapterNumber == 0:
            chapterNumber = ''

        chapterMapping = dict(
            ID=chId,
            ChapterNumber=chapterNumber,
            Title=self._convert_from_mdnov(self.novel.chapters[chId].title, quick=True),
            Desc=self._convert_from_mdnov(self.novel.chapters[chId].desc),
            Notes=self._convert_from_mdnov(self.novel.chapters[chId].notes),
            ProjectName=self._convert_from_mdnov(self.projectName, quick=True),
            ProjectPath=self.projectPath,
        )
        return chapterMapping

    def _get_chapters(self):
        lines = []
        chapterNumber = 0
        sectionNumber = 0
        wordsTotal = 0
        for chId in self.novel.tree.get_children(CH_ROOT):
            dispNumber = 0
            if not self.chapterFilter.accept(self, chId):
                continue

            template = None
            if self.novel.chapters[chId].chType == 1:
                if self._unusedChapterTemplate:
                    template = Template(self._unusedChapterTemplate)
            elif self.novel.chapters[chId].chLevel == 1 and self._partTemplate:
                template = Template(self._partTemplate)
            else:
                template = Template(self._chapterTemplate)
                chapterNumber += 1
                dispNumber = chapterNumber
            if template is not None:
                lines.append(template.safe_substitute(self._get_chapterMapping(chId, dispNumber)))

            sectionLines, sectionNumber, wordsTotal = self._get_sections(chId, sectionNumber, wordsTotal)
            lines.extend(sectionLines)

            template = None
            if self.novel.chapters[chId].chType == 1:
                if self._unusedChapterEndTemplate:
                    template = Template(self._unusedChapterEndTemplate)
            elif self._chapterEndTemplate:
                template = Template(self._chapterEndTemplate)
            if template is not None:
                lines.append(template.safe_substitute(self._get_chapterMapping(chId, dispNumber)))
        return lines

    def _get_characterMapping(self, crId):
        if self.novel.characters[crId].tags is not None:
            tags = list_to_string(self.novel.characters[crId].tags, divider=self._DIVIDER)
        else:
            tags = ''
        if self.novel.characters[crId].isMajor:
            characterStatus = Character.MAJOR_MARKER
        else:
            characterStatus = Character.MINOR_MARKER

        __, __, __, __, __, __, chrBio, chrGls = self._get_renamings()

        characterMapping = dict(
            ID=crId,
            Title=self._convert_from_mdnov(self.novel.characters[crId].title, quick=True),
            Desc=self._convert_from_mdnov(self.novel.characters[crId].desc),
            Tags=self._convert_from_mdnov(tags),
            AKA=self._convert_from_mdnov(self.novel.characters[crId].aka, quick=True),
            Notes=self._convert_from_mdnov(self.novel.characters[crId].notes),
            Bio=self._convert_from_mdnov(self.novel.characters[crId].bio),
            Goals=self._convert_from_mdnov(self.novel.characters[crId].goals),
            FullName=self._convert_from_mdnov(self.novel.characters[crId].fullName, quick=True),
            Status=characterStatus,
            ProjectName=self._convert_from_mdnov(self.projectName, quick=True),
            ProjectPath=self.projectPath,
            CharactersSuffix=CHARACTERS_SUFFIX,
            CustomChrBio=chrBio,
            CustomChrGoals=chrGls
        )
        return characterMapping

    def _get_characters(self):
        if self._characterSectionHeading:
            lines = [self._characterSectionHeading]
        else:
            lines = []
        template = Template(self._characterTemplate)
        for crId in self.novel.tree.get_children(CR_ROOT):
            if self.characterFilter.accept(self, crId):
                lines.append(template.safe_substitute(self._get_characterMapping(crId)))
        return lines

    def _get_fileFooter(self):
        lines = []
        template = Template(self._fileFooter)
        lines.append(template.safe_substitute(self._get_fileFooterMapping()))
        return lines

    def _get_fileFooterMapping(self):
        return []

    def _get_fileHeader(self):
        lines = []
        template = Template(self._fileHeader)
        lines.append(template.safe_substitute(self._get_fileHeaderMapping()))
        return lines

    def _get_fileHeaderMapping(self):
        filterMessages = []
        expFilters = [
            self.chapterFilter,
            self.sectionFilter,
            self.characterFilter,
            self.locationFilter,
            self.itemFilter,
            self.arcFilter,
            self.turningPointFilter,
            ]
        for expFilter in expFilters:
            message = expFilter.get_message(self)
            if message:
                filterMessages.append(message)
            if filterMessages:
                filters = self._convert_from_mdnov('\n'.join(filterMessages))
            else:
                filters = ''
            pltPrgs, chrczn, wrldbld, goal, cflct, outcm, chrBio, chrGls = self._get_renamings()

        fileHeaderMapping = dict(
            Title=self._convert_from_mdnov(self.novel.title, quick=True),
            Filters=filters,
            Desc=self._convert_from_mdnov(self.novel.desc),
            AuthorName=self._convert_from_mdnov(self.novel.authorName, quick=True),
            CustomPlotProgress=pltPrgs,
            CustomCharacterization=chrczn,
            CustomWorldBuilding=wrldbld,
            CustomGoal=goal,
            CustomConflict=cflct,
            CustomOutcome=outcm,
            CustomChrBio=chrBio,
            CustomChrGoals=chrGls
        )
        return fileHeaderMapping

    def _get_itemMapping(self, itId):
        if self.novel.items[itId].tags is not None:
            tags = list_to_string(self.novel.items[itId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        itemMapping = dict(
            ID=itId,
            Title=self._convert_from_mdnov(self.novel.items[itId].title, quick=True),
            Desc=self._convert_from_mdnov(self.novel.items[itId].desc),
            Notes=self._convert_from_mdnov(self.novel.items[itId].notes),
            Tags=self._convert_from_mdnov(tags, quick=True),
            AKA=self._convert_from_mdnov(self.novel.items[itId].aka, quick=True),
            ProjectName=self._convert_from_mdnov(self.projectName, quick=True),
            ProjectPath=self.projectPath,
            ItemsSuffix=ITEMS_SUFFIX,
        )
        return itemMapping

    def _get_items(self):
        if self._itemSectionHeading:
            lines = [self._itemSectionHeading]
        else:
            lines = []
        template = Template(self._itemTemplate)
        for itId in self.novel.tree.get_children(IT_ROOT):
            if self.itemFilter.accept(self, itId):
                lines.append(template.safe_substitute(self._get_itemMapping(itId)))
        return lines

    def _get_locationMapping(self, lcId):
        if self.novel.locations[lcId].tags is not None:
            tags = list_to_string(self.novel.locations[lcId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        locationMapping = dict(
            ID=lcId,
            Title=self._convert_from_mdnov(self.novel.locations[lcId].title, quick=True),
            Desc=self._convert_from_mdnov(self.novel.locations[lcId].desc),
            Notes=self._convert_from_mdnov(self.novel.locations[lcId].notes),
            Tags=self._convert_from_mdnov(tags, quick=True),
            AKA=self._convert_from_mdnov(self.novel.locations[lcId].aka, quick=True),
            ProjectName=self._convert_from_mdnov(self.projectName, quick=True),
            ProjectPath=self.projectPath,
            LocationsSuffix=LOCATIONS_SUFFIX,
        )
        return locationMapping

    def _get_locations(self):
        if self._locationSectionHeading:
            lines = [self._locationSectionHeading]
        else:
            lines = []
        template = Template(self._locationTemplate)
        for lcId in self.novel.tree.get_children(LC_ROOT):
            if self.locationFilter.accept(self, lcId):
                lines.append(template.safe_substitute(self._get_locationMapping(lcId)))
        return lines

    def _get_renamings(self):
        if self.novel.customPlotProgress:
            pltPrgs = self.novel.customPlotProgress
        else:
            pltPrgs = _('Plot progress')
        if self.novel.customCharacterization:
            chrczn = self.novel.customCharacterization
        else:
            chrczn = _('Characterization')
        if self.novel.customWorldBuilding:
            wrldbld = self.novel.customWorldBuilding
        else:
            wrldbld = _('World building')
        if self.novel.customGoal:
            goal = self.novel.customGoal
        else:
            goal = _('Opening')
        if self.novel.customConflict:
            cflct = self.novel.customConflict
        else:
            cflct = _('Peak em. moment')
        if self.novel.customOutcome:
            outcm = self.novel.customOutcome
        else:
            outcm = _('Ending')
        if self.novel.customChrBio:
            chrBio = self.novel.customChrBio
        else:
            chrBio = _('Bio')
        if self.novel.customChrGoals:
            chrGls = self.novel.customChrGoals
        else:
            chrGls = _('Goals')
        return pltPrgs, chrczn, wrldbld, goal, cflct, outcm, chrBio, chrGls

    def _get_sectionMapping(self, scId, sectionNumber, wordsTotal, firstInChapter=False):

        if sectionNumber == 0:
            sectionNumber = ''
        if self.novel.sections[scId].tags is not None:
            tags = list_to_string(self.novel.sections[scId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        if self.novel.sections[scId].characters is not None:
            sChList = []
            for crId in self.novel.sections[scId].characters:
                sChList.append(self.novel.characters[crId].title)
            sectionChars = list_to_string(sChList, divider=self._DIVIDER)

            if sChList:
                viewpointChar = sChList[0]
            else:
                viewpointChar = ''
        else:
            sectionChars = ''
            viewpointChar = ''

        if self.novel.sections[scId].locations is not None:
            sLcList = []
            for lcId in self.novel.sections[scId].locations:
                sLcList.append(self.novel.locations[lcId].title)
            sectionLocs = list_to_string(sLcList, divider=self._DIVIDER)
        else:
            sectionLocs = ''

        if self.novel.sections[scId].items is not None:
            sItList = []
            for itId in self.novel.sections[scId].items:
                sItList.append(self.novel.items[itId].title)
            sectionItems = list_to_string(sItList, divider=self._DIVIDER)
        else:
            sectionItems = ''

        if self.novel.sections[scId].date is not None and self.novel.sections[scId].date != Section.NULL_DATE:
            scDay = ''
            isoDate = self.novel.sections[scId].date
            cmbDate = self.novel.sections[scId].localeDate
            yearStr, monthStr, dayStr = isoDate.split('-')
            dtMonth = MONTHS[int(monthStr) - 1]
            try:
                dtWeekday = WEEKDAYS[self.novel.sections[scId].weekDay]
            except TypeError:
                dtWeekday = ''

        else:
            isoDate = ''
            yearStr = ''
            monthStr = ''
            dayStr = ''
            dtMonth = ''
            dtWeekday = ''
            if self.novel.sections[scId].day is not None:
                scDay = self.novel.sections[scId].day
                cmbDate = f'{_("Day")} {self.novel.sections[scId].day}'
            else:
                scDay = ''
                cmbDate = ''

        if self.novel.sections[scId].time is not None:
            h, m, s = self.novel.sections[scId].time.split(':')
            scTime = f'{h}:{m}'
            odsTime = f'PT{h}H{m}M{s}S'
        else:
            scTime = ''
            odsTime = ''

        if self.novel.sections[scId].lastsDays is not None and self.novel.sections[scId].lastsDays != '0':
            lastsDays = self.novel.sections[scId].lastsDays
            days = f'{self.novel.sections[scId].lastsDays}d '
        else:
            lastsDays = ''
            days = ''

        if self.novel.sections[scId].lastsHours is not None and self.novel.sections[scId].lastsHours != '0':
            lastsHours = self.novel.sections[scId].lastsHours
            hours = f'{self.novel.sections[scId].lastsHours}h '
        else:
            lastsHours = ''
            hours = ''

        if self.novel.sections[scId].lastsMinutes is not None and self.novel.sections[scId].lastsMinutes != '0':
            lastsMinutes = self.novel.sections[scId].lastsMinutes
            minutes = f'{self.novel.sections[scId].lastsMinutes}min'
        else:
            lastsMinutes = ''
            minutes = ''

        duration = f'{days}{hours}{minutes}'

        pltPrgs, chrczn, wrldbld, goal, cflct, outcm, __, __ = self._get_renamings()
        sectionMapping = dict(
            ID=scId,
            SectionNumber=sectionNumber,
            Title=self._convert_from_mdnov(
                self.novel.sections[scId].title,
                quick=True
                ),
            Desc=self._convert_from_mdnov(
                self.novel.sections[scId].desc,
                append=self.novel.sections[scId].appendToPrev
                ),
            WordCount=str(self.novel.sections[scId].wordCount),
            WordsTotal=wordsTotal,
            Status=int(self.novel.sections[scId].status),
            SectionContent=self._convert_from_mdnov(
                        self.novel.sections[scId].sectionContent,
                        append=self.novel.sections[scId].appendToPrev,
                        firstInChapter=firstInChapter,
                        ),
            Date=isoDate,
            Time=scTime,
            OdsTime=odsTime,
            Day=scDay,
            ScDate=cmbDate,
            DateYear=yearStr,
            DateMonth=monthStr,
            DateDay=dayStr,
            DateWeekday=dtWeekday,
            MonthName=dtMonth,
            LastsDays=lastsDays,
            LastsHours=lastsHours,
            LastsMinutes=lastsMinutes,
            Duration=duration,
            Scene=Section.SCENE[self.novel.sections[scId].scene],
            Goal=self._convert_from_mdnov(self.novel.sections[scId].goal),
            Conflict=self._convert_from_mdnov(self.novel.sections[scId].conflict),
            Outcome=self._convert_from_mdnov(self.novel.sections[scId].outcome),
            Tags=self._convert_from_mdnov(tags, quick=True),
            Characters=sectionChars,
            Viewpoint=viewpointChar,
            Locations=sectionLocs,
            Items=sectionItems,
            Notes=self._convert_from_mdnov(self.novel.sections[scId].notes),
            ProjectName=self._convert_from_mdnov(self.projectName, quick=True),
            ProjectPath=self.projectPath,
            SectionsSuffix=SECTIONS_SUFFIX,
            CustomPlotProgress=pltPrgs,
            CustomCharacterization=chrczn,
            CustomWorldBuilding=wrldbld,
            CustomGoal=goal,
            CustomConflict=cflct,
            CustomOutcome=outcm
        )
        return sectionMapping

    def _get_sections(self, chId, sectionNumber, wordsTotal):
        lines = []
        firstSectionInChapter = True
        for scId in self.novel.tree.get_children(chId):
            template = None
            dispNumber = 0
            if not self.sectionFilter.accept(self, scId):
                continue

            sectionContent = self.novel.sections[scId].sectionContent
            if sectionContent is None:
                sectionContent = ''

            if self.novel.sections[scId].scType == 2:
                if self._stage1Template:
                    template = Template(self._stage1Template)
                else:
                    continue

            elif self.novel.sections[scId].scType == 3:
                if self._stage2Template:
                    template = Template(self._stage2Template)
                else:
                    continue

            elif self.novel.sections[scId].scType == 1 or self.novel.chapters[chId].chType == 1:
                if self._unusedSectionTemplate:
                    template = Template(self._unusedSectionTemplate)
                else:
                    continue

            else:
                sectionNumber += 1
                dispNumber = sectionNumber
                wordsTotal += self.novel.sections[scId].wordCount
                template = Template(self._sectionTemplate)
                if firstSectionInChapter and self._firstSectionTemplate:
                    template = Template(self._firstSectionTemplate)
            if not (firstSectionInChapter or self.novel.sections[scId].appendToPrev or self.novel.sections[scId].scType > 1):
                lines.append(self._sectionDivider)
            if template is not None:
                lines.append(
                    template.safe_substitute(
                        self._get_sectionMapping(
                            scId, dispNumber,
                            wordsTotal,
                            firstInChapter=firstSectionInChapter,
                            )
                        )
                    )
            if self.novel.sections[scId].scType < 2:
                firstSectionInChapter = False
        return lines, sectionNumber, wordsTotal

    def _get_prjNoteMapping(self, pnId):
        noteMapping = dict(
            ID=pnId,
            Title=self._convert_from_mdnov(self.novel.projectNotes[pnId].title, quick=True),
            Desc=self._convert_from_mdnov(self.novel.projectNotes[pnId].desc),
            ProjectName=self._convert_from_mdnov(self.projectName, quick=True),
            ProjectPath=self.projectPath,
        )
        return noteMapping

    def _get_projectNotes(self):
        lines = []
        template = Template(self._projectNoteTemplate)
        for pnId in self.novel.tree.get_children(PN_ROOT):
            pnMap = self._get_prjNoteMapping(pnId)
            lines.append(template.safe_substitute(pnMap))
        return lines

    def _get_text(self):
        lines = self._get_fileHeader()
        lines.extend(self._get_chapters())
        lines.extend(self._get_characters())
        lines.extend(self._get_locations())
        lines.extend(self._get_items())
        lines.extend(self._get_arcs())
        lines.extend(self._get_projectNotes())
        lines.extend(self._get_fileFooter())
        return ''.join(lines)



def sanitize_markdown(text):
    while '\n---' in text:
        text = text.replace('\n---', '\n???')
    text = text.replace('@@', '??')
    text = text.replace('%%', '??')
    while '\n\n' in text:
        text = text.replace('\n\n', '\n')
    text = text.replace('\n', '\n\n').strip()
    return text


class MdFile(FileExport):
    DESCRIPTION = 'Markdown file'
    EXTENSION = '.md'
    SUFFIX = ''
    SECTION_DIVIDER = '* * *'
    _fileHeader = '''**${Title}**  
  
*${AuthorName}*  
  
'''

    def _convert_from_mdnov(self, text, quick=False, append=False, firstInChapter=False):
        if text is None:
            return ''

        return sanitize_markdown(text)



class Chapter(BasicElementNotes):

    def __init__(self,
            chLevel=None,
            chType=None,
            noNumber=None,
            isTrash=None,
            **kwargs):
        super().__init__(**kwargs)
        self._chLevel = chLevel
        self._chType = chType
        self._noNumber = noNumber
        self._isTrash = isTrash

    @property
    def chLevel(self):
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
from datetime import date



class Novel(BasicElement):

    def __init__(self,
            authorName=None,
            wordTarget=None,
            wordCountStart=None,
            renumberChapters=None,
            renumberParts=None,
            renumberWithinParts=None,
            romanChapterNumbers=None,
            romanPartNumbers=None,
            saveWordCount=None,
            workPhase=None,
            chapterHeadingPrefix=None,
            chapterHeadingSuffix=None,
            partHeadingPrefix=None,
            partHeadingSuffix=None,
            customPlotProgress=None,
            customCharacterization=None,
            customWorldBuilding=None,
            customGoal=None,
            customConflict=None,
            customOutcome=None,
            customChrBio=None,
            customChrGoals=None,
            referenceDate=None,
            tree=None,
            **kwargs):
        super().__init__(**kwargs)
        self._authorName = authorName
        self._wordTarget = wordTarget
        self._wordCountStart = wordCountStart
        self._renumberChapters = renumberChapters
        self._renumberParts = renumberParts
        self._renumberWithinParts = renumberWithinParts
        self._romanChapterNumbers = romanChapterNumbers
        self._romanPartNumbers = romanPartNumbers
        self._saveWordCount = saveWordCount
        self._workPhase = workPhase
        self._chapterHeadingPrefix = chapterHeadingPrefix
        self._chapterHeadingSuffix = chapterHeadingSuffix
        self._partHeadingPrefix = partHeadingPrefix
        self._partHeadingSuffix = partHeadingSuffix
        self._customPlotProgress = customPlotProgress
        self._customCharacterization = customCharacterization
        self._customWorldBuilding = customWorldBuilding
        self._customGoal = customGoal
        self._customConflict = customConflict
        self._customOutcome = customOutcome
        self._customChrBio = customChrBio
        self._customChrGoals = customChrGoals

        self.chapters = {}
        self.sections = {}
        self.plotPoints = {}
        self.languages = None
        self.plotLines = {}
        self.locations = {}
        self.items = {}
        self.characters = {}
        self.projectNotes = {}
        try:
            self.referenceWeekDay = date.fromisoformat(referenceDate).weekday()
            self._referenceDate = referenceDate
        except:
            self.referenceWeekDay = None
            self._referenceDate = None
        self.tree = tree

    @property
    def authorName(self):
        return self._authorName

    @authorName.setter
    def authorName(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._authorName != newVal:
            self._authorName = newVal
            self.on_element_change()

    @property
    def wordTarget(self):
        return self._wordTarget

    @wordTarget.setter
    def wordTarget(self, newVal):
        if newVal is not None:
            assert type(newVal) == int
        if self._wordTarget != newVal:
            self._wordTarget = newVal
            self.on_element_change()

    @property
    def wordCountStart(self):
        return self._wordCountStart

    @wordCountStart.setter
    def wordCountStart(self, newVal):
        if newVal is not None:
            assert type(newVal) == int
        if self._wordCountStart != newVal:
            self._wordCountStart = newVal
            self.on_element_change()

    @property
    def renumberChapters(self):
        return self._renumberChapters

    @renumberChapters.setter
    def renumberChapters(self, newVal):
        if newVal is not None:
            assert type(newVal) == bool
        if self._renumberChapters != newVal:
            self._renumberChapters = newVal
            self.on_element_change()

    @property
    def renumberParts(self):
        return self._renumberParts

    @renumberParts.setter
    def renumberParts(self, newVal):
        if newVal is not None:
            assert type(newVal) == bool
        if self._renumberParts != newVal:
            self._renumberParts = newVal
            self.on_element_change()

    @property
    def renumberWithinParts(self):
        return self._renumberWithinParts

    @renumberWithinParts.setter
    def renumberWithinParts(self, newVal):
        if newVal is not None:
            assert type(newVal) == bool
        if self._renumberWithinParts != newVal:
            self._renumberWithinParts = newVal
            self.on_element_change()

    @property
    def romanChapterNumbers(self):
        return self._romanChapterNumbers

    @romanChapterNumbers.setter
    def romanChapterNumbers(self, newVal):
        if newVal is not None:
            assert type(newVal) == bool
        if self._romanChapterNumbers != newVal:
            self._romanChapterNumbers = newVal
            self.on_element_change()

    @property
    def romanPartNumbers(self):
        return self._romanPartNumbers

    @romanPartNumbers.setter
    def romanPartNumbers(self, newVal):
        if newVal is not None:
            assert type(newVal) == bool
        if self._romanPartNumbers != newVal:
            self._romanPartNumbers = newVal
            self.on_element_change()

    @property
    def saveWordCount(self):
        return self._saveWordCount

    @saveWordCount.setter
    def saveWordCount(self, newVal):
        if newVal is not None:
            assert type(newVal) == bool
        if self._saveWordCount != newVal:
            self._saveWordCount = newVal
            self.on_element_change()

    @property
    def workPhase(self):
        return self._workPhase

    @workPhase.setter
    def workPhase(self, newVal):
        if newVal is not None:
            assert type(newVal) == int
        if self._workPhase != newVal:
            self._workPhase = newVal
            self.on_element_change()

    @property
    def chapterHeadingPrefix(self):
        return self._chapterHeadingPrefix

    @chapterHeadingPrefix.setter
    def chapterHeadingPrefix(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._chapterHeadingPrefix != newVal:
            self._chapterHeadingPrefix = newVal
            self.on_element_change()

    @property
    def chapterHeadingSuffix(self):
        return self._chapterHeadingSuffix

    @chapterHeadingSuffix.setter
    def chapterHeadingSuffix(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._chapterHeadingSuffix != newVal:
            self._chapterHeadingSuffix = newVal
            self.on_element_change()

    @property
    def partHeadingPrefix(self):
        return self._partHeadingPrefix

    @partHeadingPrefix.setter
    def partHeadingPrefix(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._partHeadingPrefix != newVal:
            self._partHeadingPrefix = newVal
            self.on_element_change()

    @property
    def partHeadingSuffix(self):
        return self._partHeadingSuffix

    @partHeadingSuffix.setter
    def partHeadingSuffix(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._partHeadingSuffix != newVal:
            self._partHeadingSuffix = newVal
            self.on_element_change()

    @property
    def customPlotProgress(self):
        return self._customPlotProgress

    @customPlotProgress.setter
    def customPlotProgress(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._customPlotProgress != newVal:
            self._customPlotProgress = newVal
            self.on_element_change()

    @property
    def customCharacterization(self):
        return self._customCharacterization

    @customCharacterization.setter
    def customCharacterization(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._customCharacterization != newVal:
            self._customCharacterization = newVal
            self.on_element_change()

    @property
    def customWorldBuilding(self):
        return self._customWorldBuilding

    @customWorldBuilding.setter
    def customWorldBuilding(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._customWorldBuilding != newVal:
            self._customWorldBuilding = newVal
            self.on_element_change()

    @property
    def customGoal(self):
        return self._customGoal

    @customGoal.setter
    def customGoal(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._customGoal != newVal:
            self._customGoal = newVal
            self.on_element_change()

    @property
    def customConflict(self):
        return self._customConflict

    @customConflict.setter
    def customConflict(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._customConflict != newVal:
            self._customConflict = newVal
            self.on_element_change()

    @property
    def customOutcome(self):
        return self._customOutcome

    @customOutcome.setter
    def customOutcome(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._customOutcome != newVal:
            self._customOutcome = newVal
            self.on_element_change()

    @property
    def customChrBio(self):
        return self._customChrBio

    @customChrBio.setter
    def customChrBio(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._customChrBio != newVal:
            self._customChrBio = newVal
            self.on_element_change()

    @property
    def customChrGoals(self):
        return self._customChrGoals

    @customChrGoals.setter
    def customChrGoals(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._customChrGoals != newVal:
            self._customChrGoals = newVal
            self.on_element_change()

    @property
    def referenceDate(self):
        return self._referenceDate

    @referenceDate.setter
    def referenceDate(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._referenceDate != newVal:
            if not newVal:
                self._referenceDate = None
                self.referenceWeekDay = None
                self.on_element_change()
            else:
                try:
                    self.referenceWeekDay = date.fromisoformat(newVal).weekday()
                except:
                    pass
                else:
                    self._referenceDate = newVal
                    self.on_element_change()

    def from_yaml(self, yaml):
        super().from_yaml(yaml)
        self.renumberChapters = self._get_meta_value('renumberChapters', None) == '1'
        self.renumberParts = self._get_meta_value('renumberParts', None) == '1'
        self.renumberWithinParts = self._get_meta_value('renumberWithinParts', None) == '1'
        self.romanChapterNumbers = self._get_meta_value('romanChapterNumbers', None) == '1'
        self.romanPartNumbers = self._get_meta_value('romanPartNumbers', None) == '1'
        self.saveWordCount = self._get_meta_value('saveWordCount', None) == '1'
        workPhase = self._get_meta_value('workPhase', None)
        if workPhase in ('1', '2', '3', '4', '5'):
            self.workPhase = int(workPhase)
        else:
            self.workPhase = None

        self.authorName = self._get_meta_value('Author')

        chapterHeadingPrefix = self._get_meta_value('ChapterHeadingPrefix')
        if chapterHeadingPrefix:
            chapterHeadingPrefix = chapterHeadingPrefix[1:-1]
        self.chapterHeadingPrefix = chapterHeadingPrefix

        chapterHeadingSuffix = self._get_meta_value('ChapterHeadingSuffix')
        if chapterHeadingSuffix:
            chapterHeadingSuffix = chapterHeadingSuffix[1:-1]
        self.chapterHeadingSuffix = chapterHeadingSuffix

        partHeadingPrefix = self._get_meta_value('PartHeadingPrefix')
        if partHeadingPrefix:
            partHeadingPrefix = partHeadingPrefix[1:-1]
        self.partHeadingPrefix = partHeadingPrefix

        partHeadingSuffix = self._get_meta_value('PartHeadingSuffix')
        if partHeadingSuffix:
            partHeadingSuffix = partHeadingSuffix[1:-1]
        self.partHeadingSuffix = partHeadingSuffix

        self.customPlotProgress = self._get_meta_value('CustomPlotProgress')
        self.customCharacterization = self._get_meta_value('CustomCharacterization')
        self.customWorldBuilding = self._get_meta_value('CustomWorldBuilding')

        self.customGoal = self._get_meta_value('CustomGoal')
        self.customConflict = self._get_meta_value('CustomConflict')
        self.customOutcome = self._get_meta_value('CustomOutcome')

        self.customChrBio = self._get_meta_value('CustomChrBio')
        self.customChrGoals = self._get_meta_value('CustomChrGoals')

        ws = self._get_meta_value('WordCountStart')
        if ws is not None:
            self.wordCountStart = int(ws)
        wt = self._get_meta_value('WordTarget')
        if wt is not None:
            self.wordTarget = int(wt)

        self.referenceDate = verified_date(self._get_meta_value('ReferenceDate'))

    def to_yaml(self, yaml):
        yaml = super().to_yaml(yaml)
        if self.renumberChapters:
            yaml.append(f'renumberChapters: 1')
        if self.renumberParts:
            yaml.append(f'renumberParts: 1')
        if self.renumberWithinParts:
            yaml.append(f'renumberWithinParts: 1')
        if self.romanChapterNumbers:
            yaml.append(f'romanChapterNumbers: 1')
        if self.romanPartNumbers:
            yaml.append(f'romanPartNumbers: 1')
        if self.saveWordCount:
            yaml.append(f'saveWordCount: 1')
        if self.workPhase is not None:
            yaml.append(f'workPhase: {self.workPhase}')

        if self.authorName:
            yaml.append(f'Author: {self.authorName}')

        if self.chapterHeadingPrefix:
            yaml.append(f'ChapterHeadingPrefix: "{self.chapterHeadingPrefix}"')
        if self.chapterHeadingSuffix:
            yaml.append(f'ChapterHeadingSuffix: "{self.chapterHeadingSuffix}"')

        if self.partHeadingPrefix:
            yaml.append(f'PartHeadingPrefix: "{self.partHeadingPrefix}"')
        if self.partHeadingSuffix:
            yaml.append(f'PartHeadingSuffix: "{self.partHeadingSuffix}"')

        if self.customPlotProgress:
            yaml.append(f'CustomPlotProgress: {self.customPlotProgress}')
        if self.customCharacterization:
            yaml.append(f'CustomCharacterization: {self.customCharacterization}')
        if self.customWorldBuilding:
            yaml.append(f'CustomWorldBuilding: {self.customWorldBuilding}')

        if self.customGoal:
            yaml.append(f'CustomGoal: {self.customGoal}')
        if self.customConflict:
            yaml.append(f'CustomConflict: {self.customConflict}')
        if self.customOutcome:
            yaml.append(f'CustomOutcome: {self.customOutcome}')

        if self.customChrBio:
            yaml.append(f'CustomChrBio: {self.customChrBio}')
        if self.customChrGoals:
            yaml.append(f'CustomChrGoals: {self.customChrGoals}')

        if self.wordCountStart:
            yaml.append(f'WordCountStart: {self.wordCountStart}')
        if self.wordTarget:
            yaml.append(f'WordTarget: {self.wordTarget}')

        if self.referenceDate:
            yaml.append(f'ReferenceDate: {self.referenceDate}')
        return yaml

    def update_plot_lines(self):
        for scId in self.sections:
            self.sections[scId].scPlotPoints = {}
            self.sections[scId].scPlotLines = []
            for plId in self.plotLines:
                if scId in self.plotLines[plId].sections:
                    self.sections[scId].scPlotLines.append(plId)
                    for ppId in self.tree.get_children(plId):
                        if self.plotPoints[ppId].sectionAssoc == scId:
                            self.sections[scId].scPlotPoints[ppId] = plId
                            break



class PlotLine(BasicElementNotes):

    def __init__(self,
            shortName=None,
            sections=None,
            **kwargs):
        super().__init__(**kwargs)

        self._shortName = shortName
        self._sections = sections

    @property
    def shortName(self):
        return self._shortName

    @shortName.setter
    def shortName(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._shortName != newVal:
            self._shortName = newVal
            self.on_element_change()

    @property
    def sections(self):
        try:
            return self._sections[:]
        except TypeError:
            return None

    @sections.setter
    def sections(self, newVal):
        if newVal is not None:
            for elem in newVal:
                if elem is not None:
                    assert type(elem) == str
        if self._sections != newVal:
            self._sections = newVal
            self.on_element_change()

    def from_yaml(self, yaml):
        super().from_yaml(yaml)
        self.shortName = self._get_meta_value('ShortName')
        plSections = self._get_meta_value('Sections')
        self.sections = string_to_list(plSections)

    def to_yaml(self, yaml):
        yaml = super().to_yaml(yaml)
        if self.shortName:
            yaml.append(f'ShortName: {self.shortName}')
        if self.sections:
            yaml.append(f'Sections: {list_to_string(self.sections)}')
        return yaml


class PlotPoint(BasicElementNotes):

    def __init__(self,
            sectionAssoc=None,
            **kwargs):
        super().__init__(**kwargs)

        self._sectionAssoc = sectionAssoc

    @property
    def sectionAssoc(self):
        return self._sectionAssoc

    @sectionAssoc.setter
    def sectionAssoc(self, newVal):
        if newVal is not None:
            assert type(newVal) == str
        if self._sectionAssoc != newVal:
            self._sectionAssoc = newVal
            self.on_element_change()

    def from_yaml(self, yaml):
        super().from_yaml(yaml)
        self.sectionAssoc = self._get_meta_value('Section')

    def to_yaml(self, yaml):
        yaml = super().to_yaml(yaml)
        if self.sectionAssoc:
            yaml.append(f'Section: {self.sectionAssoc}')
        return yaml


class MdnovFile(MdFile):
    DESCRIPTION = _('mdnovel project')
    EXTENSION = '.mdnov'

    _fileHeader = '''@@book
    
---
$YAML
---


$Links
%%

'''
    _chapterTemplate = '''
@@$ID
    
---
$YAML
---

$Links$Desc$Notes
%%

'''
    _partTemplate = _chapterTemplate
    _unusedChapterTemplate = _chapterTemplate
    _sectionTemplate = '''
@@$ID
    
---
$YAML
---

$Links$Desc$Notes$Goal$Conflict$Outcome$Plotlines$SectionContent%%
'''
    _unusedSectionTemplate = _sectionTemplate
    _stage1Template = _sectionTemplate
    _stage2Template = _sectionTemplate
    _sectionDivider = ''
    _chapterEndTemplate = ''
    _unusedChapterEndTemplate = ''
    _characterSectionHeading = ''
    _characterTemplate = '''
@@$ID
    
---
$YAML
---

$Links$Desc$Bio$Goals
%%

'''
    _locationSectionHeading = ''
    _locationTemplate = '''
@@$ID
    
---
$YAML
---

$Links$Desc
%%

'''
    _itemSectionHeading = ''
    _itemTemplate = _locationTemplate
    _projectNoteTemplate = _locationTemplate
    _arcTemplate = '''
@@$ID
    
---
$YAML
---

$Links$Desc
%%

'''
    _fileFooter = '\n$Wordcountlog\n\n%%'

    def __init__(self, filePath, **kwargs):
        super().__init__(filePath)
        self.on_element_change = None

        self.wcLog = {}

        self.wcLogUpdate = {}

        self.timestamp = None
        self._range = None
        self._collectedLines = None
        self._properties = {}
        self._plId = None

    def adjust_section_types(self):
        partType = 0
        for chId in self.novel.tree.get_children(CH_ROOT):
            if self.novel.chapters[chId].chLevel == 1:
                partType = self.novel.chapters[chId].chType
            elif partType != 0 and not self.novel.chapters[chId].isTrash:
                self.novel.chapters[chId].chType = partType
            for scId in self.novel.tree.get_children(chId):
                if self.novel.sections[scId].scType < self.novel.chapters[chId].chType:
                    self.novel.sections[scId].scType = self.novel.chapters[chId].chType

    def count_words(self):
        count = 0
        totalCount = 0
        for chId in self.novel.tree.get_children(CH_ROOT):
            if not self.novel.chapters[chId].isTrash:
                for scId in self.novel.tree.get_children(chId):
                    if self.novel.sections[scId].scType < 2:
                        totalCount += self.novel.sections[scId].wordCount
                        if self.novel.sections[scId].scType == 0:
                            count += self.novel.sections[scId].wordCount
        return count, totalCount

    def read(self):
        with open(self.filePath, 'r', encoding='utf-8') as f:
            lines = f.read().split('\n')
        processor = None
        elemId = None
        chId = None
        self._collectedLines = None
        self.novel.tree.reset()
        for self._line in lines:
            if self._line.startswith('@@book'):
                processor = self._read_project
                elemId = None
                element = self.novel
                continue

            if self._line.startswith(f'@@{CHAPTER_PREFIX}'):
                processor = self._read_chapter
                elemId = self._line.split('@@')[1].strip()
                self.novel.chapters[elemId] = Chapter(on_element_change=self.on_element_change)
                self.novel.tree.append(CH_ROOT, elemId)
                element = self.novel.chapters[elemId]
                chId = elemId
                continue

            if self._line.startswith(f'@@{CHARACTER_PREFIX}'):
                processor = self._read_character
                elemId = self._line.split('@@')[1].strip()
                self.novel.characters[elemId] = Character(on_element_change=self.on_element_change)
                self.novel.tree.append(CR_ROOT, elemId)
                element = self.novel.characters[elemId]
                continue

            if self._line.startswith(f'@@{ITEM_PREFIX}'):
                processor = self._read_world_element
                elemId = self._line.split('@@')[1].strip()
                self.novel.items[elemId] = WorldElement(on_element_change=self.on_element_change)
                self.novel.tree.append(IT_ROOT, elemId)
                element = self.novel.items[elemId]
                continue

            if self._line.startswith(f'@@{LOCATION_PREFIX}'):
                processor = self._read_world_element
                elemId = self._line.split('@@')[1].strip()
                self.novel.locations[elemId] = WorldElement(on_element_change=self.on_element_change)
                self.novel.tree.append(LC_ROOT, elemId)
                element = self.novel.locations[elemId]
                continue

            if self._line.startswith(f'@@{PLOT_LINE_PREFIX}'):
                processor = self._read_plot_line
                elemId = self._line.split('@@')[1].strip()
                self.novel.plotLines[elemId] = PlotLine(on_element_change=self.on_element_change)
                self.novel.tree.append(PL_ROOT, elemId)
                element = self.novel.plotLines[elemId]
                plId = elemId
                continue

            if self._line.startswith(f'@@{PLOT_POINT_PREFIX}'):
                processor = self._read_plot_point
                elemId = self._line.split('@@')[1].strip()
                self.novel.plotPoints[elemId] = PlotPoint(on_element_change=self.on_element_change)
                self.novel.tree.append(plId, elemId)
                element = (self.novel.plotPoints[elemId])
                continue

            if self._line.startswith(f'@@{PRJ_NOTE_PREFIX}'):
                processor = self._read_project_note
                elemId = self._line.split('@@')[1].strip()
                self.novel.projectNotes[elemId] = BasicElement()
                self.novel.tree.append(PN_ROOT, elemId)
                element = self.novel.projectNotes[elemId]
                continue

            if self._line.startswith(f'@@{SECTION_PREFIX}'):
                processor = self._read_section
                elemId = self._line.split('@@')[1].strip()
                self.novel.sections[elemId] = Section(on_element_change=self.on_element_change)
                self.novel.tree.append(chId, elemId)
                element = self.novel.sections[elemId]
                continue

            if self._line.startswith(f'@@Progress'):
                processor = self._read_word_count_log
                elemId = None
                continue

            if processor is not None:
                processor(element)

        for scId in self.novel.sections:

            self.novel.sections[scId].characters = intersection(self.novel.sections[scId].characters, self.novel.characters)
            self.novel.sections[scId].locations = intersection(self.novel.sections[scId].locations, self.novel.locations)
            self.novel.sections[scId].items = intersection(self.novel.sections[scId].items, self.novel.items)

        for ppId in self.novel.plotPoints:

            scId = self.novel.plotPoints[ppId].sectionAssoc
            if scId in self.novel.sections:
                self.novel.sections[scId].scPlotPoints[ppId] = plId
            else:
                self.novel.plotPoints[ppId].sectionAssoc = None

        for plId in self.novel.plotLines:

            self.novel.plotLines[plId].sections = intersection(self.novel.plotLines[plId].sections, self.novel.sections)

            for scId in self.novel.plotLines[plId].sections:
                self.novel.sections[scId].scPlotLines.append(plId)

        self._get_timestamp()
        self._keep_word_count()

    def write(self):
        self._update_word_count_log()
        self.adjust_section_types()
        super().write()
        self._get_timestamp()

    def _add_key(self, text, key):
        if not key:
            return ''

        if not text:
            return ''

        return f'%%{key}:\n\n{sanitize_markdown(text)}\n\n'

    def _add_links(self, element, mapping):
        links = element.get_links()
        linkRepr = []
        if links:
            for relativeLink, absoluteLink in links:
                linkRepr.append('%%Link:')
                linkRepr.append(relativeLink)
                linkRepr.append(absoluteLink)
        links = '\n\n'.join(linkRepr)
        mapping['Links'] = f'{links}\n'
        return mapping

    def _add_plotline_notes(self, prjScn, mapping):
        plRepr = []
        if prjScn.plotlineNotes:
            for plId in prjScn.plotlineNotes:
                if not plId in prjScn.scPlotLines:
                    continue

                if not prjScn.plotlineNotes[plId]:
                    continue

                plRepr.append('%%Plotline:')
                plRepr.append(plId)

                plRepr.append('%%Plotline note:')
                plRepr.append(sanitize_markdown(prjScn.plotlineNotes[plId]))
        plStr = '\n\n'.join(plRepr)
        mapping['Plotlines'] = f'{plStr}\n\n'
        return mapping

    def _add_yaml(self, element, mapping):
        yaml = element.to_yaml([])
        mapping['YAML'] = '\n'.join(yaml)
        return mapping

    def _get_arcMapping(self, plId):
        mapping = super()._get_arcMapping(plId)
        element = self.novel.plotLines[plId]
        mapping = self._add_yaml(element, mapping)
        mapping = self._add_links(element, mapping)
        mapping['Desc'] = self._add_key(element.desc, 'Desc')
        return mapping

    def _get_chapterMapping(self, chId, chapterNumber):
        mapping = super()._get_chapterMapping(chId, chapterNumber)
        element = self.novel.chapters[chId]
        mapping = self._add_yaml(element, mapping)
        mapping = self._add_links(element, mapping)
        mapping['Desc'] = self._add_key(element.desc, 'Desc')
        mapping['Notes'] = self._add_key(element.desc, 'Notes')
        return mapping

    def _get_characterMapping(self, crId):
        mapping = super()._get_characterMapping(crId)
        element = self.novel.characters[crId]
        mapping = self._add_yaml(element, mapping)
        mapping = self._add_links(element, mapping)
        mapping['Desc'] = self._add_key(element.desc, 'Desc')
        mapping['Bio'] = self._add_key(element.bio, 'Bio')
        mapping['Goals'] = self._add_key(element.goals, 'Goals')
        mapping['Notes'] = self._add_key(element.desc, 'Notes')
        return mapping

    def _get_fileFooterMapping(self):
        mapping = {}
        if not self.wcLog:
            mapping['Wordcountlog'] = ''
            return mapping

        lines = ['@@Progress']
        wcLastCount = None
        wcLastTotalCount = None
        for wc in self.wcLog:
            if self.novel.saveWordCount:
                if self.wcLog[wc][0] == wcLastCount and self.wcLog[wc][1] == wcLastTotalCount:
                    continue

                wcLastCount = self.wcLog[wc][0]
                wcLastTotalCount = self.wcLog[wc][1]
            lines.append(f'- {list_to_string([wc, self.wcLog[wc][0], self.wcLog[wc][1]])}')
        mapping['Wordcountlog'] = '\n'.join(lines)
        return mapping

    def _get_fileHeaderMapping(self):
        mapping = super()._get_fileHeaderMapping()
        element = self.novel
        mapping = self._add_yaml(element, mapping)
        mapping = self._add_links(element, mapping)
        mapping['Desc'] = self._add_key(element.desc, 'Desc')
        return mapping

    def _get_itemMapping(self, itId):
        mapping = super()._get_itemMapping(itId)
        element = self.novel.items[itId]
        mapping = self._add_yaml(element, mapping)
        mapping = self._add_links(element, mapping)
        mapping['Desc'] = self._add_key(element.desc, 'Desc')
        mapping['Notes'] = self._add_key(element.desc, 'Notes')
        return mapping

    def _get_locationMapping(self, lcId):
        mapping = super()._get_locationMapping(lcId)
        element = self.novel.locations[lcId]
        mapping = self._add_yaml(element, mapping)
        mapping = self._add_links(element, mapping)
        mapping['Desc'] = self._add_key(element.desc, 'Desc')
        mapping['Notes'] = self._add_key(element.desc, 'Notes')
        return mapping

    def _get_prjNoteMapping(self, pnId):
        mapping = super()._get_prjNoteMapping(pnId)
        element = self.novel.projectNotes[pnId]
        mapping = self._add_yaml(element, mapping)
        mapping = self._add_links(element, mapping)
        mapping['Desc'] = self._add_key(element.desc, 'Desc')
        return mapping

    def _get_sectionMapping(self, scId, sectionNumber, wordsTotal, firstInChapter=False):
        mapping = super()._get_sectionMapping(scId, sectionNumber, wordsTotal)
        element = self.novel.sections[scId]
        mapping = self._add_yaml(element, mapping)
        mapping = self._add_links(element, mapping)
        mapping = self._add_plotline_notes(element, mapping)
        mapping['Desc'] = self._add_key(element.desc, 'Desc')
        mapping['Goal'] = self._add_key(element.goal, 'Goal')
        mapping['Conflict'] = self._add_key(element.conflict, 'Conflict')
        mapping['Outcome'] = self._add_key(element.outcome, 'Outcome')
        mapping['Notes'] = self._add_key(element.notes, 'Notes')
        mapping['SectionContent'] = self._add_key(element.sectionContent, 'Content')
        return mapping

    def _get_timestamp(self):
        try:
            self.timestamp = os.path.getmtime(self.filePath)
        except:
            self.timestamp = None

    def _keep_word_count(self):
        if not self.wcLog:
            return

        actualCountInt, actualTotalCountInt = self.count_words()
        actualCount = str(actualCountInt)
        actualTotalCount = str(actualTotalCountInt)
        latestDate = list(self.wcLog)[-1]
        latestCount = self.wcLog[latestDate][0]
        latestTotalCount = self.wcLog[latestDate][1]
        if actualCount != latestCount or actualTotalCount != latestTotalCount:
            try:
                fileDateIso = date.fromtimestamp(self.timestamp).isoformat()
            except:
                fileDateIso = date.today().isoformat()
            self.wcLogUpdate[fileDateIso] = [actualCount, actualTotalCount]

    def _read_element(self, element):
        if self._line.startswith('---'):
            if self._range != 'yaml':
                self._range = 'yaml'
                self._collectedLines = []
            else:
                element.from_yaml(self._collectedLines)
                self._range = None
            return

        if self._line.startswith('%%'):

            if self._range is not None:
                text = '\n'.join(self._collectedLines).strip()
                classProperty = self._properties.get(self._range, None)
                if classProperty is not None:
                    classProperty.fset(element, f'{text}\n')
                    self._plId = None
                elif self._range == 'Plotline':
                    self._plId = text
                elif self._range == 'Plotline note'and self._plId is not None:
                    plNotes = element.plotlineNotes
                    plNotes[self._plId] = text
                    element.plotlineNotes = plNotes
                    self._plId = None
                elif self._range == 'Link':
                    self._set_links(element, text)
                elif self._range == 'Progress':
                    self._set_word_count(text)
            self._collectedLines = []
            tag = self._line.strip('%: ')
            if tag:
                self._range = tag

        elif self._range is not None:
            self._collectedLines.append(self._line)

    def _read_chapter(self, element):
        self._properties = {
            'Desc':Chapter.desc,
            'Notes':Chapter.notes,
        }
        self._read_element(element)

    def _read_character(self, element):
        self._properties = {
            'Desc':Character.desc,
            'Notes':Character.notes,
            'Bio':Character.bio,
            'Goals':Character.goals,
        }
        self._read_element(element)

    def _read_world_element(self, element):
        self._properties = {
            'Desc':WorldElement.desc,
            'Notes':WorldElement.notes,
        }
        self._read_element(element)

    def _read_plot_line(self, element):
        self._properties = {
            'Desc':PlotLine.desc,
            'Notes':PlotLine.notes,
        }
        self._read_element(element)

    def _read_plot_point(self, element):
        self._properties = {
            'Desc':PlotPoint.desc,
            'Notes':PlotPoint.notes,
        }
        self._read_element(element)

    def _read_project(self, element):
        self._properties = {
            'Desc':Novel.desc,
        }
        self._read_element(element)

    def _read_project_note(self, element):
        self._properties = {
            'Desc':BasicElement.desc,
        }
        self._read_element(element)

    def _read_section(self, element):
        if element.plotlineNotes is None:
            element.plotlineNotes = {}
        self._properties = {
            'Desc':Section.desc,
            'Notes':Section.notes,
            'Goal':Section.goal,
            'Conflict':Section.conflict,
            'Outcome':Section.outcome,
            'Content':Section.sectionContent,
        }
        self._read_element(element)

    def _read_word_count_log(self, element):
        self._range = 'Progress'
        self._read_element(element)

    def _set_links(self, element, text):
        linkList = []
        relativeLink = ''
        absoluteLink = ''
        for line in text.split('\n'):
            if not line:
                continue

            linkType, link = line.split('](')
            if linkType == '[LinkPath':
                relativeLink = link.strip(') ')
            elif linkType == '[FullPath':
                absoluteLink = link.strip(') ')
                if relativeLink:
                    linkList.append((relativeLink, absoluteLink))
                relativeLink = ''
                absoluteLink = ''
        element.set_links(linkList)

    def _set_word_count(self, text):
        for line in text.split('\n'):
            if not line:
                continue

            wc = (line.strip('- ').split(';'))
            self.wcLog[wc[0]] = [wc[1], wc[2]]

    def _update_word_count_log(self):
        if self.novel.saveWordCount:
            newCountInt, newTotalCountInt = self.count_words()
            newCount = str(newCountInt)
            newTotalCount = str(newTotalCountInt)
            todayIso = date.today().isoformat()
            self.wcLogUpdate[todayIso] = [newCount, newTotalCount]
            for wcDate in self.wcLogUpdate:
                self.wcLog[wcDate] = self.wcLogUpdate[wcDate]
        self.wcLogUpdate = {}



class NvTree:

    def __init__(self):
        self.roots = {
            CH_ROOT:[],
            CR_ROOT:[],
            LC_ROOT:[],
            IT_ROOT:[],
            PL_ROOT:[],
            PN_ROOT:[],
        }
        self.srtSections = {}
        self.srtTurningPoints = {}

    def append(self, parent, iid):
        if parent in self.roots:
            self.roots[parent].append(iid)
            if parent == CH_ROOT:
                self.srtSections[iid] = []
            elif parent == PL_ROOT:
                self.srtTurningPoints[iid] = []
            return

        if parent.startswith(CHAPTER_PREFIX):
            if parent in self.srtSections:
                self.srtSections[parent].append(iid)
            else:
                self.srtSections[parent] = [iid]
            return

        if parent.startswith(PLOT_LINE_PREFIX):
            if parent in self.srtTurningPoints:
                self.srtTurningPoints[parent].append(iid)
            else:
                self.srtTurningPoints[parent] = [iid]

    def delete(self, *items):
        raise NotImplementedError

    def delete_children(self, parent):
        if parent in self.roots:
            self.roots[parent] = []
            if parent == CH_ROOT:
                self.srtSections = {}
                return

            if parent == PL_ROOT:
                self.srtTurningPoints = {}
            return

        if parent.startswith(CHAPTER_PREFIX):
            self.srtSections[parent] = []
            return

        if parent.startswith(PLOT_LINE_PREFIX):
            self.srtTurningPoints[parent] = []

    def get_children(self, item):
        if item in self.roots:
            return self.roots[item]

        if item.startswith(CHAPTER_PREFIX):
            return self.srtSections.get(item, [])

        if item.startswith(PLOT_LINE_PREFIX):
            return self.srtTurningPoints.get(item, [])

    def index(self, item):
        raise NotImplementedError

    def insert(self, parent, index, iid):
        if parent in self.roots:
            self.roots[parent].insert(index, iid)
            if parent == CH_ROOT:
                self.srtSections[iid] = []
            elif parent == PL_ROOT:
                self.srtTurningPoints[iid] = []
            return

        if parent.startswith(CHAPTER_PREFIX):
            if parent in self.srtSections:
                self.srtSections[parent].insert(index, iid)
            else:
                self.srtSections[parent] = [iid]
            return

        if parent.startswith(PLOT_LINE_PREFIX):
            if parent in self.srtTurningPoints:
                self.srtTurningPoints[parent].insert(index, iid)
            else:
                self.srtTurningPoints[parent] = [iid]

    def move(self, item, parent, index):
        raise NotImplementedError

    def next(self, item):
        raise NotImplementedError

    def parent(self, item):
        raise NotImplementedError

    def prev(self, item):
        raise NotImplementedError

    def reset(self):
        for item in self.roots:
            self.roots[item] = []
        self.srtSections = {}
        self.srtTurningPoints = {}

    def set_children(self, item, newchildren):
        if item in self.roots:
            self.roots[item] = newchildren[:]
            if item == CH_ROOT:
                self.srtSections = {}
                return

            if item == PL_ROOT:
                self.srtTurningPoints = {}
            return

        if item.startswith(CHAPTER_PREFIX):
            self.srtSections[item] = newchildren[:]
            return

        if item.startswith(PLOT_LINE_PREFIX):
            self.srtTurningPoints[item] = newchildren[:]

from datetime import datetime
from html import unescape



def create_id(elements, prefix=''):
    i = 1
    while f'{prefix}{i}' in elements:
        i += 1
    return f'{prefix}{i}'

import xml.etree.ElementTree as ET


def strip_illegal_characters(text):
    return re.sub('[\x00-\x08|\x0b-\x0c|\x0e-\x1f]', '', text)



def indent(elem, level=0):
    PARAGRAPH_LEVEL = 5

    i = f'\n{level * "  "}'
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = f'{i}  '
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        if level < PARAGRAPH_LEVEL:
            for elem in elem:
                indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


class Yw7File(File):
    DESCRIPTION = _('yWriter 7 project')
    EXTENSION = '.yw7'

    PRJ_KWVAR_YW7 = [
        'Field_WorkPhase',
        'Field_RenumberChapters',
        'Field_RenumberParts',
        'Field_RenumberWithinParts',
        'Field_RomanChapterNumbers',
        'Field_RomanPartNumbers',
        'Field_ChapterHeadingPrefix',
        'Field_ChapterHeadingSuffix',
        'Field_PartHeadingPrefix',
        'Field_PartHeadingSuffix',
        'Field_CustomGoal',
        'Field_CustomConflict',
        'Field_CustomOutcome',
        'Field_CustomChrBio',
        'Field_CustomChrGoals',
        'Field_SaveWordCount',
        'Field_LanguageCode',
        'Field_CountryCode',
        ]

    CHP_KWVAR_YW7 = [
        'Field_NoNumber',
        'Field_ArcDefinition',
        'Field_Arc_Definition',
        ]

    SCN_KWVAR_YW7 = [
        'Field_SceneArcs',
        'Field_SceneAssoc',
        'Field_CustomAR',
        'Field_SceneMode',
        ]

    CRT_KWVAR_YW7 = [
        'Field_Link',
        'Field_BirthDate',
        'Field_DeathDate',
        ]

    LOC_KWVAR_YW7 = [
        'Field_Link',
        ]

    ITM_KWVAR_YW7 = [
        'Field_Link',
        ]

    _CDATA_TAGS = [
        'Title',
        'AuthorName',
        'Bio',
        'Desc',
        'FieldTitle1',
        'FieldTitle2',
        'FieldTitle3',
        'FieldTitle4',
        'LaTeXHeaderFile',
        'Tags',
        'AKA',
        'ImageFile',
        'FullName',
        'Goals',
        'Notes',
        'RTFFile',
        'SceneContent',
        'Outcome',
        'Goal',
        'Conflict'
        'Field_ChapterHeadingPrefix',
        'Field_ChapterHeadingSuffix',
        'Field_PartHeadingPrefix',
        'Field_PartHeadingSuffix',
        'Field_CustomGoal',
        'Field_CustomConflict',
        'Field_CustomOutcome',
        'Field_CustomChrBio',
        'Field_CustomChrGoals',
        'Field_ArcDefinition',
        'Field_SceneArcs',
        'Field_CustomAR',
        ]

    STAGE_MARKER = 'stage'

    def __init__(self, filePath, **kwargs):
        super().__init__(filePath)
        self.tree = None
        self.wcLog = {}
        self._ywApIds = None

    def is_locked(self):
        return os.path.isfile(f'{self.filePath}.lock')

    def read(self):
        if self.is_locked():
            raise Error(f'{_("yWriter seems to be open. Please close first")}.')

        self._noteCounter = 0
        self._noteNumber = 0
        try:
            try:
                with open(self.filePath, 'r', encoding='utf-8') as f:
                    xmlText = f.read()
            except:
                with open(self.filePath, 'r', encoding='utf-16') as f:
                    xmlText = f.read()
        except:
            try:
                self.tree = ET.parse(self.filePath)
            except Exception as ex:
                raise Error(f'{_("Can not process file")} - {str(ex)}')

        xmlText = strip_illegal_characters(xmlText)
        root = ET.fromstring(xmlText)
        del xmlText

        self._ywApIds = []
        self.wcLog = {}
        self._read_project(root)
        self._read_locations(root)
        self._read_items(root)
        self._read_characters(root)
        self._read_chapters(root)
        self._read_scenes(root)
        self._read_project_notes(root)

        xmlWclog = root.find('WCLog')
        if xmlWclog is not None:
            for xmlWc in xmlWclog.iterfind('WC'):
                wcDate = xmlWc.find('Date').text
                wcCount = xmlWc.find('Count').text
                wcTotalCount = xmlWc.find('TotalCount').text
                self.wcLog[wcDate] = [wcCount, wcTotalCount]

        for scId in self.novel.sections:
            if self.novel.sections[scId].characters is None:
                self.novel.sections[scId].characters = []
            if self.novel.sections[scId].locations is None:
                self.novel.sections[scId].locations = []
            if self.novel.sections[scId].items is None:
                self.novel.sections[scId].items = []
            if self.novel.sections[scId].status is None:
                self.novel.sections[scId].status = 1

    def write(self):
        if self.is_locked():
            raise Error(f'{_("yWriter seems to be open. Please close first")}.')

        self._noteCounter = 0
        self._noteNumber = 0
        self._build_element_tree()
        self._write_element_tree(self)
        self._postprocess_xml_file(self.filePath)

    def _build_element_tree(self):

        def isTrue(value):
            if value:
                return '1'

        def set_element(parent, tag, text, index):
            if text is not None:
                subelement = ET.Element(tag)
                parent.insert(index, subelement)
                subelement.text = text
                index += 1
            return index

        def build_scene_subtree(xmlScene, prjScn, plotPoint=False):
            i = 1
            i = set_element(xmlScene, 'Title', prjScn.title, i)
            if prjScn.desc is not None:
                ET.SubElement(xmlScene, 'Desc').text = prjScn.desc

            if not plotPoint:
                scTags = prjScn.tags


            scTypeEncoding = (
                (False, None),
                (True, '1'),
                (True, '2'),
                (True, '0'),
                )
            if plotPoint:
                scType = 2
            elif prjScn.scType in (0, None):
                scType = 0
            elif prjScn.scType > 1:
                scType = 2
                if not scTags:
                    scTags = [self.STAGE_MARKER]
                elif not self.STAGE_MARKER in scTags:
                    scTags.append(self.STAGE_MARKER)
            else:
                scType = 3
            yUnused, ySceneType = scTypeEncoding[scType]
            if yUnused:
                ET.SubElement(xmlScene, 'Unused').text = '-1'
            if ySceneType is not None:
                ET.SubElement(xmlSceneFields[scId], 'Field_SceneType').text = ySceneType
            if plotPoint:
                ET.SubElement(xmlScene, 'Status').text = '1'
            elif prjScn.status is not None:
                ET.SubElement(xmlScene, 'Status').text = str(prjScn.status)

            if plotPoint:
                ET.SubElement(xmlScene, 'SceneContent')
                return

            ET.SubElement(xmlScene, 'SceneContent').text = self._to_yw(prjScn.sectionContent)
            if prjScn.notes:
                ET.SubElement(xmlScene, 'Notes').text = prjScn.notes
            if scTags:
                ET.SubElement(xmlScene, 'Tags').text = list_to_string(scTags)
            if prjScn.appendToPrev:
                ET.SubElement(xmlScene, 'AppendToPrev').text = '-1'

            if (prjScn.date) and (prjScn.time):
                separator = ' '
                dateTime = f'{prjScn.date}{separator}{prjScn.time}'
                ET.SubElement(xmlScene, 'SpecificDateTime').text = dateTime
                ET.SubElement(xmlScene, 'SpecificDateMode').text = '-1'
            elif (prjScn.day) or (prjScn.time):
                if prjScn.day:
                    ET.SubElement(xmlScene, 'Day').text = prjScn.day
                if prjScn.time:
                    hours, minutes, __ = prjScn.time.split(':')
                    ET.SubElement(xmlScene, 'Hour').text = hours
                    ET.SubElement(xmlScene, 'Minute').text = minutes

            if prjScn.lastsDays:
                ET.SubElement(xmlScene, 'LastsDays').text = prjScn.lastsDays
            if prjScn.lastsHours:
                ET.SubElement(xmlScene, 'LastsHours').text = prjScn.lastsHours
            if prjScn.lastsMinutes:
                ET.SubElement(xmlScene, 'LastsMinutes').text = prjScn.lastsMinutes

            if prjScn.scene == 2:
                ET.SubElement(xmlScene, 'ReactionScene').text = '-1'
            if prjScn.goal:
                ET.SubElement(xmlScene, 'Goal').text = prjScn.goal
            if prjScn.conflict:
                ET.SubElement(xmlScene, 'Conflict').text = prjScn.conflict
            if prjScn.outcome:
                ET.SubElement(xmlScene, 'Outcome').text = prjScn.outcome

            if prjScn.characters:
                xmlCharacters = ET.SubElement(xmlScene, 'Characters')
                for crId in prjScn.characters:
                    ET.SubElement(xmlCharacters, 'CharID').text = crId[2:]
            if prjScn.locations:
                xmlLocations = ET.SubElement(xmlScene, 'Locations')
                for lcId in prjScn.locations:
                    ET.SubElement(xmlLocations, 'LocID').text = lcId[2:]
            if prjScn.items:
                xmlItems = ET.SubElement(xmlScene, 'Items')
                for itId in prjScn.items:
                    ET.SubElement(xmlItems, 'ItemID').text = itId[2:]

        def build_chapter_subtree(xmlChapter, prjChp, plId=None, chType=None):

            chTypeEncoding = (
                (False, '0', '0'),
                (True, '1', '1'),
                (True, '1', '2'),
                (True, '1', '0'),
                )
            if chType is None:
                if plId is not None:
                    chType = 2
                elif prjChp.chType in (0, None):
                    chType = 0
                else:
                    chType = 3
            yUnused, yType, yChapterType = chTypeEncoding[chType]

            i = 1
            i = set_element(xmlChapter, 'Title', prjChp.title, i)
            i = set_element(xmlChapter, 'Desc', prjChp.desc, i)

            if yUnused:
                elem = ET.Element('Unused')
                elem.text = '-1'
                xmlChapter.insert(i, elem)
                i += 1

            xmlChapterFields = ET.SubElement(xmlChapter, 'Fields')
            i += 1
            if plId is None and prjChp.isTrash:
                ET.SubElement(xmlChapterFields, 'Field_IsTrash').text = '1'

            if plId is None:
                fields = { 'Field_NoNumber': isTrue(prjChp.noNumber)}
            else:
                fields = {'Field_ArcDefinition': self.novel.plotLines[plId].shortName}
            for field in fields:
                if fields[field]:
                    ET.SubElement(xmlChapterFields, field).text = fields[field]
            if plId is None and prjChp.chLevel == 1:
                ET.SubElement(xmlChapter, 'SectionStart').text = '-1'
                i += 1
            i = set_element(xmlChapter, 'Type', yType, i)
            i = set_element(xmlChapter, 'ChapterType', yChapterType, i)

        def build_location_subtree(xmlLoc, prjLoc):
            if prjLoc.title:
                ET.SubElement(xmlLoc, 'Title').text = prjLoc.title
            if prjLoc.desc:
                ET.SubElement(xmlLoc, 'Desc').text = prjLoc.desc
            if prjLoc.aka:
                ET.SubElement(xmlLoc, 'AKA').text = prjLoc.aka
            if prjLoc.tags:
                ET.SubElement(xmlLoc, 'Tags').text = list_to_string(prjLoc.tags)

        def build_item_subtree(xmlItm, prjItm):
            if prjItm.title:
                ET.SubElement(xmlItm, 'Title').text = prjItm.title
            if prjItm.desc:
                ET.SubElement(xmlItm, 'Desc').text = prjItm.desc
            if prjItm.aka:
                ET.SubElement(xmlItm, 'AKA').text = prjItm.aka
            if prjItm.tags:
                ET.SubElement(xmlItm, 'Tags').text = list_to_string(prjItm.tags)

        def build_character_subtree(xmlCrt, prjCrt):
            if prjCrt.title:
                ET.SubElement(xmlCrt, 'Title').text = prjCrt.title
            if prjCrt.desc:
                ET.SubElement(xmlCrt, 'Desc').text = prjCrt.desc
            if prjCrt.notes:
                ET.SubElement(xmlCrt, 'Notes').text = prjCrt.notes
            if prjCrt.aka:
                ET.SubElement(xmlCrt, 'AKA').text = prjCrt.aka
            if prjCrt.tags:
                ET.SubElement(xmlCrt, 'Tags').text = list_to_string(prjCrt.tags)
            if prjCrt.bio:
                ET.SubElement(xmlCrt, 'Bio').text = prjCrt.bio
            if prjCrt.goals:
                ET.SubElement(xmlCrt, 'Goals').text = prjCrt.goals
            if prjCrt.fullName:
                ET.SubElement(xmlCrt, 'FullName').text = prjCrt.fullName
            if prjCrt.isMajor:
                ET.SubElement(xmlCrt, 'Major').text = '-1'
            fields = {
                'Field_BirthDate': prjCrt.birthDate,
                'Field_DeathDate': prjCrt.deathDate,
                }
            xmlCrtFields = None
            for field in fields:
                if fields[field]:
                    if xmlCrtFields is None:
                        xmlCrtFields = ET.SubElement(xmlCrt, 'Fields')
                    ET.SubElement(xmlCrtFields, field).text = fields[field]

        def build_project_subtree(xmlProject):
            ET.SubElement(xmlProject, 'Ver').text = '7'
            if self.novel.title:
                ET.SubElement(xmlProject, 'Title').text = self.novel.title
            if self.novel.desc:
                ET.SubElement(xmlProject, 'Desc').text = self.novel.desc
            if self.novel.authorName:
                ET.SubElement(xmlProject, 'AuthorName').text = self.novel.authorName
            if self.novel.wordCountStart is not None:
                ET.SubElement(xmlProject, 'WordCountStart').text = str(self.novel.wordCountStart)
            if self.novel.wordTarget is not None:
                ET.SubElement(xmlProject, 'WordTarget').text = str(self.novel.wordTarget)

            workPhase = self.novel.workPhase
            if workPhase is not None:
                workPhase = str(workPhase)
            fields = {
                'Field_WorkPhase': workPhase,
                'Field_RenumberChapters': isTrue(self.novel.renumberChapters),
                'Field_RenumberParts': isTrue(self.novel.renumberParts),
                'Field_RenumberWithinParts': isTrue(self.novel.renumberWithinParts),
                'Field_RomanChapterNumbers': isTrue(self.novel.romanChapterNumbers),
                'Field_RomanPartNumbers': isTrue(self.novel.romanPartNumbers),
                'Field_ChapterHeadingPrefix': self.novel.chapterHeadingPrefix,
                'Field_ChapterHeadingSuffix': self.novel.chapterHeadingSuffix,
                'Field_PartHeadingPrefix': self.novel.partHeadingPrefix,
                'Field_PartHeadingSuffix': self.novel.partHeadingSuffix,
                'Field_CustomGoal': self.novel.customGoal,
                'Field_CustomConflict': self.novel.customConflict,
                'Field_CustomOutcome': self.novel.customOutcome,
                'Field_CustomChrBio': self.novel.customChrBio,
                'Field_CustomChrGoals': self.novel.customChrGoals,
                'Field_SaveWordCount': isTrue(self.novel.saveWordCount),
                'Field_ReferenceDate': self.novel.referenceDate,
                }
            xmlProjectFields = ET.SubElement(xmlProject, 'Fields')
            for field in fields:
                if fields[field]:
                    ET.SubElement(xmlProjectFields, field).text = fields[field]

        def build_prjNote_subtree(xmlProjectnote, projectNote):
            if projectNote.title is not None:
                ET.SubElement(xmlProjectnote, 'Title').text = projectNote.title

            if projectNote.desc is not None:
                ET.SubElement(xmlProjectnote, 'Desc').text = projectNote.desc

        root = ET.Element('YWRITER7')
        xmlProject = ET.SubElement(root, 'PROJECT')
        xmlLocations = ET.SubElement(root, 'LOCATIONS')
        xmlItems = ET.SubElement(root, 'ITEMS')
        xmlCharacters = ET.SubElement(root, 'CHARACTERS')
        xmlScenes = ET.SubElement(root, 'SCENES')
        xmlChapters = ET.SubElement(root, 'CHAPTERS')

        build_project_subtree(xmlProject)

        for lcId in self.novel.tree.get_children(LC_ROOT):
            xmlLoc = ET.SubElement(xmlLocations, 'LOCATION')
            ET.SubElement(xmlLoc, 'ID').text = lcId[2:]
            build_location_subtree(xmlLoc, self.novel.locations[lcId])

        for itId in self.novel.tree.get_children(IT_ROOT):
            xmlItm = ET.SubElement(xmlItems, 'ITEM')
            ET.SubElement(xmlItm, 'ID').text = itId[2:]
            build_item_subtree(xmlItm, self.novel.items[itId])

        for crId in self.novel.tree.get_children(CR_ROOT):
            xmlCrt = ET.SubElement(xmlCharacters, 'CHARACTER')
            ET.SubElement(xmlCrt, 'ID').text = crId[2:]
            build_character_subtree(xmlCrt, self.novel.characters[crId])

        xmlSceneFields = {}
        scIds = list(self.novel.sections)
        for scId in scIds:
            xmlScene = ET.SubElement(xmlScenes, 'SCENE')
            ET.SubElement(xmlScene, 'ID').text = scId[2:]
            xmlSceneFields[scId] = ET.SubElement(xmlScene, 'Fields')
            build_scene_subtree(xmlScene, self.novel.sections[scId])

        newScIds = {}
        for ppId in self.novel.plotPoints:
            scId = create_id(scIds, prefix=SECTION_PREFIX)
            scIds.append(scId)
            newScIds[ppId] = scId
            xmlScene = ET.SubElement(xmlScenes, 'SCENE')
            ET.SubElement(xmlScene, 'ID').text = scId[2:]
            xmlSceneFields[scId] = ET.SubElement(xmlScene, 'Fields')
            build_scene_subtree(xmlScene, self.novel.plotPoints[ppId], plotPoint=True)

        chIds = list(self.novel.tree.get_children(CH_ROOT))
        for chId in chIds:
            xmlChapter = ET.SubElement(xmlChapters, 'CHAPTER')
            ET.SubElement(xmlChapter, 'ID').text = chId[2:]
            build_chapter_subtree(xmlChapter, self.novel.chapters[chId])
            srtScenes = self.novel.tree.get_children(chId)
            if srtScenes:
                xmlScnList = ET.SubElement(xmlChapter, 'Scenes')
                for scId in self.novel.tree.get_children(chId):
                    ET.SubElement(xmlScnList, 'ScID').text = scId[2:]

        chId = create_id(chIds, prefix=CHAPTER_PREFIX)
        chIds.append(chId)
        xmlChapter = ET.SubElement(xmlChapters, 'CHAPTER')
        ET.SubElement(xmlChapter, 'ID').text = chId[2:]
        arcPart = Chapter(title=_('Plot lines'), chLevel=1)
        build_chapter_subtree(xmlChapter, arcPart, chType=2)
        for plId in self.novel.tree.get_children(PL_ROOT):
            chId = create_id(chIds, prefix=CHAPTER_PREFIX)
            chIds.append(chId)
            xmlChapter = ET.SubElement(xmlChapters, 'CHAPTER')
            ET.SubElement(xmlChapter, 'ID').text = chId[2:]
            build_chapter_subtree(xmlChapter, self.novel.plotLines[plId], plId=plId)
            srtScenes = self.novel.tree.get_children(plId)
            if srtScenes:
                xmlScnList = ET.SubElement(xmlChapter, 'Scenes')
                for ppId in srtScenes:
                    ET.SubElement(xmlScnList, 'ScID').text = newScIds[ppId][2:]

        if self.novel.tree.get_children(PN_ROOT):
            xmlProjectnotes = ET.SubElement(root, 'PROJECTNOTES')
            for pnId in self.novel.tree.get_children(PN_ROOT):
                xmlProjectnote = ET.SubElement(xmlProjectnotes, 'PROJECTNOTE')
                ET.SubElement(xmlProjectnote, 'ID').text = pnId[2:]
                build_prjNote_subtree(xmlProjectnote, self.novel.projectNotes[pnId])

        scPlotLines = {}
        sectionAssoc = {}
        for scId in scIds:
            scPlotLines[scId] = []
            sectionAssoc[scId] = []
        for plId in self.novel.plotLines:
            for scId in self.novel.plotLines[plId].sections:
                scPlotLines[scId].append(self.novel.plotLines[plId].shortName)
            for ppId in self.novel.tree.get_children(plId):
                scPlotLines[newScIds[ppId]].append(self.novel.plotLines[plId].shortName)
        for ppId in self.novel.plotPoints:
            if self.novel.plotPoints[ppId].sectionAssoc:
                sectionAssoc[self.novel.plotPoints[ppId].sectionAssoc].append(newScIds[ppId][2:])
                sectionAssoc[newScIds[ppId]].append(self.novel.plotPoints[ppId].sectionAssoc[2:])
        for scId in scIds:
            fields = {
                'Field_SceneArcs': list_to_string(scPlotLines[scId]),
                'Field_SceneAssoc': list_to_string(sectionAssoc[scId]),
                }
            for field in fields:
                if fields[field]:
                    ET.SubElement(xmlSceneFields[scId], field).text = fields[field]

        if self.wcLog:
            xmlWcLog = ET.SubElement(root, 'WCLog')
            wcLastCount = None
            wcLastTotalCount = None
            for wc in self.wcLog:
                if self.novel.saveWordCount:
                    if self.wcLog[wc][0] == wcLastCount and self.wcLog[wc][1] == wcLastTotalCount:
                        continue

                    wcLastCount = self.wcLog[wc][0]
                    wcLastTotalCount = self.wcLog[wc][1]
                xmlWc = ET.SubElement(xmlWcLog, 'WC')
                ET.SubElement(xmlWc, 'Date').text = wc
                ET.SubElement(xmlWc, 'Count').text = self.wcLog[wc][0]
                ET.SubElement(xmlWc, 'TotalCount').text = self.wcLog[wc][1]

        indent(root)
        self.tree = ET.ElementTree(root)

    def _from_yw(self, text, quick=False):
        if quick:
            if text is None:
                return ''
            else:
                return text

        MD_REPLACEMENTS = [
            ('\n', '\n\n'),
            ('[i] ', ' [i]'),
            ('[b] ', ' [b]'),
            ('[s] ', ' [s]'),
            ('[i]', '*'),
            ('[/i]', '*'),
            ('[b]', '**'),
            ('[/b]', '**'),
            ('/*', '<!---'),
            ('*/', '--->'),
            ('  ', ' '),
        ]
        try:
            for yw, md in MD_REPLACEMENTS:
                text = text.replace(yw, md)
            text = re.sub(r'\[\/*[h|c|r|s|u]\d*\]', '', text)
        except AttributeError:
            text = ''
        return text

    def _postprocess_xml_file(self, filePath):
        with open(filePath, 'r', encoding='utf-8') as f:
            text = f.read()
        lines = text.split('\n')
        newlines = ['<?xml version="1.0" encoding="utf-8"?>']
        for line in lines:
            for tag in self._CDATA_TAGS:
                line = re.sub(fr'\<{tag}\>', f'<{tag}><![CDATA[', line)
                line = re.sub(fr'\<\/{tag}\>', f']]></{tag}>', line)
            newlines.append(line)
        text = '\n'.join(newlines)
        text = text.replace('[CDATA[ \n', '[CDATA[')
        text = text.replace('\n]]', ']]')
        if not self.novel.chapters:
            text = text.replace('<CHAPTERS />', '<CHAPTERS></CHAPTERS>')
        text = unescape(text)
        try:
            with open(filePath, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            raise Error(f'{_("Cannot write file")}: "{norm_path(filePath)}".')

    def _read_locations(self, root):
        self.novel.tree.delete_children(LC_ROOT)
        for xmlLocation in root.find('LOCATIONS'):
            lcId = f"{LOCATION_PREFIX}{xmlLocation.find('ID').text}"
            self.novel.tree.append(LC_ROOT, lcId)
            self.novel.locations[lcId] = WorldElement()

            if xmlLocation.find('Title') is not None:
                self.novel.locations[lcId].title = xmlLocation.find('Title').text


            if xmlLocation.find('Desc') is not None:
                self.novel.locations[lcId].desc = xmlLocation.find('Desc').text

            if xmlLocation.find('AKA') is not None:
                self.novel.locations[lcId].aka = xmlLocation.find('AKA').text

            if xmlLocation.find('Tags') is not None:
                if xmlLocation.find('Tags').text is not None:
                    tags = string_to_list(xmlLocation.find('Tags').text)
                    self.novel.locations[lcId].tags = self._strip_spaces(tags)

    def _read_items(self, root):
        self.novel.tree.delete_children(IT_ROOT)
        for xmlItem in root.find('ITEMS'):
            itId = f"{ITEM_PREFIX}{xmlItem.find('ID').text}"
            self.novel.tree.append(IT_ROOT, itId)
            self.novel.items[itId] = WorldElement()

            if xmlItem.find('Title') is not None:
                self.novel.items[itId].title = xmlItem.find('Title').text


            if xmlItem.find('Desc') is not None:
                self.novel.items[itId].desc = xmlItem.find('Desc').text

            if xmlItem.find('AKA') is not None:
                self.novel.items[itId].aka = xmlItem.find('AKA').text

            if xmlItem.find('Tags') is not None:
                if xmlItem.find('Tags').text is not None:
                    tags = string_to_list(xmlItem.find('Tags').text)
                    self.novel.items[itId].tags = self._strip_spaces(tags)

    def _read_chapters(self, root):
        self.novel.tree.delete_children(CH_ROOT)
        self.novel.tree.delete_children(PL_ROOT)
        for xmlChapter in root.find('CHAPTERS'):
            prjChapter = Chapter()

            if xmlChapter.find('Title') is not None:
                prjChapter.title = xmlChapter.find('Title').text

            if xmlChapter.find('Desc') is not None:
                prjChapter.desc = xmlChapter.find('Desc').text

            if xmlChapter.find('SectionStart') is not None:
                prjChapter.chLevel = 1
            else:
                prjChapter.chLevel = 2


            prjChapter.chType = 0
            if xmlChapter.find('Unused') is not None:
                yUnused = True
            else:
                yUnused = False
            if xmlChapter.find('ChapterType') is not None:
                yChapterType = xmlChapter.find('ChapterType').text
                if yChapterType == '2':
                    prjChapter.chType = 1
                elif yChapterType == '1':
                    prjChapter.chType = 1
                elif yUnused:
                    prjChapter.chType = 1
            else:
                if xmlChapter.find('Type') is not None:
                    yType = xmlChapter.find('Type').text
                    if yType == '1':
                        prjChapter.chType = 1
                    elif yUnused:
                        prjChapter.chType = 1

            kwVarYw7 = {}
            for xmlChapterFields in xmlChapter.iterfind('Fields'):
                prjChapter.isTrash = False
                if xmlChapterFields.find('Field_IsTrash') is not None:
                    if xmlChapterFields.find('Field_IsTrash').text == '1':
                        prjChapter.isTrash = True

                for fieldName in self.CHP_KWVAR_YW7:
                    xmlField = xmlChapterFields.find(fieldName)
                    if xmlField  is not None:
                        kwVarYw7[fieldName] = xmlField .text
            prjChapter.noNumber = kwVarYw7.get('Field_NoNumber', False) == '1'
            shortName = kwVarYw7.get('Field_ArcDefinition', '')

            field = kwVarYw7.get('Field_Arc_Definition', None)
            if field is not None:
                shortName = field

            scenes = []
            if xmlChapter.find('Scenes') is not None:
                for scn in xmlChapter.find('Scenes').iterfind('ScID'):
                    scId = scn.text
                    scenes.append(scId)

            if shortName:
                plId = f"{PLOT_LINE_PREFIX}{xmlChapter.find('ID').text}"
                self.novel.plotLines[plId] = PlotLine()
                self.novel.plotLines[plId].title = prjChapter.title
                self.novel.plotLines[plId].desc = prjChapter.desc
                self.novel.plotLines[plId].shortName = shortName
                self.novel.tree.append(PL_ROOT, plId)
                for scId in scenes:
                    self.novel.tree.append(plId, f'{PLOT_POINT_PREFIX}{scId}')
                    self._ywApIds.append(scId)
            else:
                chId = f"{CHAPTER_PREFIX}{xmlChapter.find('ID').text}"
                self.novel.chapters[chId] = prjChapter
                self.novel.tree.append(CH_ROOT, chId)
                for scId in scenes:
                    self.novel.tree.append(chId, f'{SECTION_PREFIX}{scId}')

    def _read_characters(self, root):
        self.novel.tree.delete_children(CR_ROOT)
        for xmlCharacter in root.find('CHARACTERS'):
            crId = f"{CHARACTER_PREFIX}{xmlCharacter.find('ID').text}"
            self.novel.tree.append(CR_ROOT, crId)
            self.novel.characters[crId] = Character()

            if xmlCharacter.find('Title') is not None:
                self.novel.characters[crId].title = xmlCharacter.find('Title').text


            if xmlCharacter.find('Desc') is not None:
                self.novel.characters[crId].desc = xmlCharacter.find('Desc').text

            if xmlCharacter.find('AKA') is not None:
                self.novel.characters[crId].aka = xmlCharacter.find('AKA').text

            if xmlCharacter.find('Tags') is not None:
                if xmlCharacter.find('Tags').text is not None:
                    tags = string_to_list(xmlCharacter.find('Tags').text)
                    self.novel.characters[crId].tags = self._strip_spaces(tags)

            if xmlCharacter.find('Notes') is not None:
                self.novel.characters[crId].notes = xmlCharacter.find('Notes').text

            if xmlCharacter.find('Bio') is not None:
                self.novel.characters[crId].bio = xmlCharacter.find('Bio').text

            if xmlCharacter.find('Goals') is not None:
                self.novel.characters[crId].goals = xmlCharacter.find('Goals').text

            if xmlCharacter.find('FullName') is not None:
                self.novel.characters[crId].fullName = xmlCharacter.find('FullName').text

            if xmlCharacter.find('Major') is not None:
                self.novel.characters[crId].isMajor = True
            else:
                self.novel.characters[crId].isMajor = False

            kwVarYw7 = {}
            xmlCharacterFields = xmlCharacter.find('Fields')
            if xmlCharacterFields is not None:
                for fieldName in self.CRT_KWVAR_YW7:
                    xmlField = xmlCharacterFields.find(fieldName)
                    if xmlField  is not None:
                        kwVarYw7[fieldName] = xmlField.text
            self.novel.characters[crId].birthDate = kwVarYw7.get('Field_BirthDate', '')
            self.novel.characters[crId].deathDate = kwVarYw7.get('Field_DeathDate', '')

    def _read_project(self, root):
        xmlProject = root.find('PROJECT')

        if xmlProject.find('Title') is not None:
            self.novel.title = xmlProject.find('Title').text

        if xmlProject.find('AuthorName') is not None:
            self.novel.authorName = xmlProject.find('AuthorName').text

        if xmlProject.find('Desc') is not None:
            self.novel.desc = xmlProject.find('Desc').text

        if xmlProject.find('WordCountStart') is not None:
            try:
                self.novel.wordCountStart = int(xmlProject.find('WordCountStart').text)
            except:
                pass
        if xmlProject.find('WordTarget') is not None:
            try:
                self.novel.wordTarget = int(xmlProject.find('WordTarget').text)
            except:
                pass

        kwVarYw7 = {}
        for xmlProjectFields in xmlProject.iterfind('Fields'):
            for fieldName in self.PRJ_KWVAR_YW7:
                xmlField = xmlProjectFields.find(fieldName)
                if xmlField  is not None:
                    if xmlField.text:
                        kwVarYw7[fieldName] = xmlField.text
        try:
            self.novel.workPhase = int(kwVarYw7.get('Field_WorkPhase', None))
        except:
            self.novel.workPhase = None
        self.novel.renumberChapters = kwVarYw7.get('Field_RenumberChapters', False) == '1'
        self.novel.renumberParts = kwVarYw7.get('Field_RenumberParts', False) == '1'
        self.novel.renumberWithinParts = kwVarYw7.get('Field_RenumberWithinParts', False) == '1'
        self.novel.romanChapterNumbers = kwVarYw7.get('Field_RomanChapterNumbers', False) == '1'
        self.novel.romanPartNumbers = kwVarYw7.get('Field_RomanPartNumbers', False) == '1'
        self.novel.chapterHeadingPrefix = kwVarYw7.get('Field_ChapterHeadingPrefix', '')
        self.novel.chapterHeadingSuffix = kwVarYw7.get('Field_ChapterHeadingSuffix', '')
        self.novel.partHeadingPrefix = kwVarYw7.get('Field_PartHeadingPrefix', '')
        self.novel.partHeadingSuffix = kwVarYw7.get('Field_PartHeadingSuffix', '')
        self.novel.customGoal = kwVarYw7.get('Field_CustomGoal', '')
        self.novel.customConflict = kwVarYw7.get('Field_CustomConflict', '')
        self.novel.customOutcome = kwVarYw7.get('Field_CustomOutcome', '')
        self.novel.customChrBio = kwVarYw7.get('Field_CustomChrBio', '')
        self.novel.customChrGoals = kwVarYw7.get('Field_CustomChrGoals', '')
        self.novel.saveWordCount = kwVarYw7.get('Field_SaveWordCount', False) == '1'

    def _read_project_notes(self, root):
        if root.find('PROJECTNOTES') is not None:
            for xmlProjectnote in root.find('PROJECTNOTES'):
                if xmlProjectnote.find('ID') is not None:
                    pnId = f"{PRJ_NOTE_PREFIX}{xmlProjectnote.find('ID').text}"
                    self.novel.tree.append(PN_ROOT, pnId)
                    self.novel.projectNotes[pnId] = BasicElement()
                    if xmlProjectnote.find('Title') is not None:
                        self.novel.projectNotes[pnId].title = xmlProjectnote.find('Title').text
                    if xmlProjectnote.find('Desc') is not None:
                        self.novel.projectNotes[pnId].desc = xmlProjectnote.find('Desc').text

    def _read_scenes(self, root):
        for xmlScene in root.find('SCENES'):
            prjScn = Section()

            if xmlScene.find('Title') is not None:
                prjScn.title = xmlScene.find('Title').text

            if xmlScene.find('Desc') is not None:
                prjScn.desc = xmlScene.find('Desc').text

            if xmlScene.find('SceneContent') is not None:
                sceneContent = xmlScene.find('SceneContent').text
                if sceneContent is not None:
                    prjScn.sectionContent = self._from_yw(sceneContent)



            prjScn.scType = 0
            kwVarYw7 = {}
            for xmlSceneFields in xmlScene.iterfind('Fields'):
                if xmlSceneFields.find('Field_SceneType') is not None:
                    if xmlSceneFields.find('Field_SceneType').text == '1':
                        prjScn.scType = 1
                    elif xmlSceneFields.find('Field_SceneType').text == '2':
                        prjScn.scType = 1

                for fieldName in self.SCN_KWVAR_YW7:
                    xmlField = xmlSceneFields.find(fieldName)
                    if xmlField  is not None:
                        kwVarYw7[fieldName] = xmlField.text

            ywScnArcs = string_to_list(kwVarYw7.get('Field_SceneArcs', ''))
            for shortName in ywScnArcs:
                for plId in self.novel.plotLines:
                    if self.novel.plotLines[plId].shortName == shortName:
                        if prjScn.scType == 0:
                            arcSections = self.novel.plotLines[plId].sections
                            if not arcSections:
                                arcSections = [f"{SECTION_PREFIX}{xmlScene.find('ID').text}"]
                            else:
                                arcSections.append(f"{SECTION_PREFIX}{xmlScene.find('ID').text}")
                            self.novel.plotLines[plId].sections = arcSections
                        break

            ywScnAssocs = string_to_list(kwVarYw7.get('Field_SceneAssoc', ''))
            prjScn.plotPoints = [f'{PLOT_POINT_PREFIX}{plotPoint}' for plotPoint in ywScnAssocs]

            if xmlScene.find('Goal') is not None:
                prjScn.goal = xmlScene.find('Goal').text

            if xmlScene.find('Conflict') is not None:
                prjScn.conflict = xmlScene.find('Conflict').text

            if xmlScene.find('Outcome') is not None:
                prjScn.outcome = xmlScene.find('Outcome').text

            if kwVarYw7.get('Field_CustomAR', None) is not None:
                prjScn.scene = 3
            elif xmlScene.find('ReactionScene') is not None:
                prjScn.scene = 2
            elif prjScn.goal or prjScn.conflict or prjScn.outcome:
                prjScn.scene = 1
            else:
                prjScn.scene = 0

            if xmlScene.find('Unused') is not None:
                if prjScn.scType == 0:
                    prjScn.scType = 1

            if xmlScene.find('Status') is not None:
                prjScn.status = int(xmlScene.find('Status').text)

            if xmlScene.find('Notes') is not None:
                prjScn.notes = xmlScene.find('Notes').text

            if xmlScene.find('Tags') is not None:
                if xmlScene.find('Tags').text is not None:
                    tags = string_to_list(xmlScene.find('Tags').text)
                    prjScn.tags = self._strip_spaces(tags)

            if xmlScene.find('AppendToPrev') is not None:
                prjScn.appendToPrev = True
            else:
                prjScn.appendToPrev = False

            if xmlScene.find('SpecificDateTime') is not None:
                dateTimeStr = xmlScene.find('SpecificDateTime').text

                try:
                    dateTime = datetime.fromisoformat(dateTimeStr)
                except:
                    prjScn.date = ''
                    prjScn.time = ''
                else:
                    startDateTime = dateTime.isoformat().split('T')
                    prjScn.date = startDateTime[0]
                    prjScn.time = startDateTime[1]
            else:
                if xmlScene.find('Day') is not None:
                    day = xmlScene.find('Day').text

                    try:
                        int(day)
                    except ValueError:
                        day = ''
                    prjScn.day = day

                hasUnspecificTime = False
                if xmlScene.find('Hour') is not None:
                    hour = xmlScene.find('Hour').text.zfill(2)
                    hasUnspecificTime = True
                else:
                    hour = '00'
                if xmlScene.find('Minute') is not None:
                    minute = xmlScene.find('Minute').text.zfill(2)
                    hasUnspecificTime = True
                else:
                    minute = '00'
                if hasUnspecificTime:
                    prjScn.time = f'{hour}:{minute}:00'

            if xmlScene.find('LastsDays') is not None:
                prjScn.lastsDays = xmlScene.find('LastsDays').text

            if xmlScene.find('LastsHours') is not None:
                prjScn.lastsHours = xmlScene.find('LastsHours').text

            if xmlScene.find('LastsMinutes') is not None:
                prjScn.lastsMinutes = xmlScene.find('LastsMinutes').text


            scCharacters = []
            if xmlScene.find('Characters') is not None:
                for character in xmlScene.find('Characters').iter('CharID'):
                    crId = f"{CHARACTER_PREFIX}{character.text}"
                    if crId in self.novel.tree.get_children(CR_ROOT):
                        scCharacters.append(crId)
            prjScn.characters = scCharacters

            scLocations = []
            if xmlScene.find('Locations') is not None:
                for location in xmlScene.find('Locations').iter('LocID'):
                    lcId = f"{LOCATION_PREFIX}{location.text}"
                    if lcId in self.novel.tree.get_children(LC_ROOT):
                        scLocations.append(lcId)
            prjScn.locations = scLocations

            scItems = []
            if xmlScene.find('Items') is not None:
                for item in xmlScene.find('Items').iter('ItemID'):
                    itId = f"{ITEM_PREFIX}{item.text}"
                    if itId in self.novel.tree.get_children(IT_ROOT):
                        scItems.append(itId)
            prjScn.items = scItems

            ywScId = xmlScene.find('ID').text
            if ywScId in self._ywApIds:
                ppId = f"{PLOT_POINT_PREFIX}{ywScId}"
                self.novel.plotPoints[ppId] = PlotPoint(title=prjScn.title,
                                                      desc=prjScn.desc
                                                      )
                if ywScnAssocs:
                    self.novel.plotPoints[ppId].sectionAssoc = f'{SECTION_PREFIX}{ywScnAssocs[0]}'
            else:
                if prjScn.tags and self.STAGE_MARKER in prjScn.tags:
                    prjScn.scType = 3
                    prjScn.tags = prjScn.tags.remove(self.STAGE_MARKER)
                scId = f"{SECTION_PREFIX}{ywScId}"
                self.novel.sections[scId] = prjScn

    def _strip_spaces(self, lines):
        stripped = []
        for line in lines:
            stripped.append(line.strip())
        return stripped

    def _to_yw(self, text):
        if not text:
            return ''

        while '\n\n' in text:
            text = text.replace('\n\n', '@%&').strip()
        while '***' in text:
            text = text.replace('***', '§%§')
        text = re.sub(r'([^\*])\*\*(.+?)\*\*', '\\1[b]\\2[/b]', text)
        text = re.sub(r'([^\*])\*(.+?)\*', '\\1[i]\\2[/i]', text)
        while '§%§' in text:
            text = text.replace('§%§', '***')
        newlines = []
        for line in text.split('@%&'):
            newlines.append(line)
        text = '\n'.join(newlines)
        text = re.sub(r'\*\*(.+?)\*\*', '[b]\\1[/b]', text)
        text = re.sub(r'\*([^ ].+?[^ ])\*', '[i]\\1[/i]', text)
        MD_REPLACEMENTS = [
            ('\n\n', '\n'),
            ('<!---', '/*'),
            ('--->', '*/'),
        ]
        try:
            for md, yw in MD_REPLACEMENTS:
                text = text.replace(md, yw)
        except AttributeError:
            text = ''
        return text

    def _write_element_tree(self, ywProject):
        backedUp = False
        if os.path.isfile(ywProject.filePath):
            try:
                os.replace(ywProject.filePath, f'{ywProject.filePath}.bak')
            except:
                raise Error(f'{_("Cannot overwrite file")}: "{norm_path(ywProject.filePath)}".')
            else:
                backedUp = True
        try:
            ywProject.tree.write(ywProject.filePath, xml_declaration=False, encoding='utf-8')
        except:
            if backedUp:
                os.replace(f'{ywProject.filePath}.bak', ywProject.filePath)
            raise Error(f'{_("Cannot write file")}: "{norm_path(ywProject.filePath)}".')



class Yw7Converter():

    def run(self, sourcePath):
        sourceRoot, sourceExtension = os.path.splitext(sourcePath)
        if sourceExtension == Yw7File.EXTENSION:
            targetPath = f'{sourceRoot}{MdnovFile.EXTENSION}'
            source = Yw7File(sourcePath)
            target = MdnovFile(targetPath)
        elif sourceExtension == MdnovFile.EXTENSION:
            targetPath = f'{sourceRoot}{Yw7File.EXTENSION}'
            source = MdnovFile(sourcePath)
            target = Yw7File(targetPath)
        else:
            self.ui.set_info_how(f'!File format "{sourceExtension}" is not supported.')
            return

        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'!File not found: "{sourcePath}".')
            return

        if os.path.isfile(targetPath):
            if not self.ui.ask_yes_no(f'Overwrite existing file "{norm_path(targetPath)}"?'):
                self.ui.set_info_how('!Action canceled by user.')
                return

        source.novel = Novel(tree=NvTree())
        source.read()
        target.novel = source.novel
        target.wcLog = source.wcLog
        target.write()
        self.ui.set_info_how(f'File written: "{norm_path(targetPath)}".')


def main(sourcePath, suffix=''):
    ui = UiCmd('Converter between .mdnov and .yw7 file format')
    converter = Yw7Converter()
    converter.ui = ui
    converter.run(sourcePath)
    ui.start()


if __name__ == '__main__':
    main(sys.argv[1])
