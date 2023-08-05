# mautrix-facebook - A Matrix-Facebook Messenger puppeting bridge.
# Copyright (C) 2021 Tulir Asokan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import Dict, List, Any, Optional

from mautrix.types import SerializableAttrs
from attr import dataclass


@dataclass
class LoginResponse(SerializableAttrs['LoginResponse']):
    session_key: str
    uid: int
    secret: str
    access_token: str
    machine_id: str
    session_cookies: List[Dict[str, Any]]
    analytics_claim: str
    user_storage_key: str
    identifier: Optional[str] = None


@dataclass
class MobileConfigField(SerializableAttrs['MobileConfigField']):
    k: int
    bln: Optional[int] = None
    i64: Optional[int] = None
    str: Optional[str] = None
    pname: Optional[str] = None


@dataclass
class MobileConfigItem(SerializableAttrs['MobileConfigItem']):
    fields: List[MobileConfigField]
    hash: str


@dataclass
class MobileConfig(SerializableAttrs['MobileConfig']):
    configs: Dict[str, MobileConfigItem]
    query_hash: Optional[str]
    one_query_hash: Optional[str]
    ts: int
    ep_hash: str

    def find(self, number: int, field_k: int) -> Optional[MobileConfigField]:
        try:
            config = self.configs[str(number)]
        except IndexError:
            pass
        else:
            for field in config.fields:
                if field.k == field_k:
                    return field
        return None


@dataclass
class PasswordKeyResponse(SerializableAttrs['PasswordKeyResponse']):
    public_key: str
    key_id: int
    seconds_to_live: int
