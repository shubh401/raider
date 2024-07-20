# Copyright (C) 2024 Shubham Agarwal, CISPA.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from enum import Enum

class Sink(Enum):
    ALL_URLS = 0
    LS = 1
    SS = 2
    LS_SS = 3
    IDB = 4
    LS_IDB = 5
    SS_IDB = 6
    LS_SS_IDB = 7
    COOKIES = 8
    LS_COOKIES = 9
    SS_COOKIES = 10
    LS_SS_COOKIES = 11
    IDB_COOKIES = 12
    LS_IDB_COOKIES = 13
    SS_IDB_COOKIES = 14
    LS_SS_IDB_COOKIES = 15
    
class Script(Enum):
    CS = 1
    BG = 2
    CS_BG = 3
    WAR = 4
    CS_WAR = 5
    BG_WAR = 6
    CS_BG_WAR = 7
