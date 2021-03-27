import re
from typing import Union, Optional, List

import discord

from global_variables import STUDENT_ROLE_NAME
from utils.guild_config import GUILD_CONFIG

"""
####################################################################
########################## HELP FUNCTIONS ##########################
####################################################################
"""

GROUP_NAME_PATTERN = re.compile("Group[\s]+([0-9]+)")
ROLE_NAME_PATTERN = re.compile("member-group\s+([0-9]+)")

def get_lab_group_number(group_name: str) -> Optional[int]:
    if GROUP_NAME_PATTERN.search(group_name):
        return int(GROUP_NAME_PATTERN.search(group_name).group(1))
    return None


def get_lab_group_name(number: int):
    return f"Group {number:2}"


def get_role_name(number: int):
    return f"member-group {number:2}"


def get_text_channel_name(number: int):
    return f"text-channel-{number}"


def get_voice_channel_name(number: int):
    return f"voice-channel {number}"


def get_nick(member: discord.Member) -> str:
    return member.nick if member.nick else member.name


def get_lab_group(guild: discord.Guild, group: Union[int, str]) -> Optional[discord.CategoryChannel]:
    name = get_lab_group_name(group) if type(group) == int else group
    return discord.utils.get(guild.categories, name=name)


def get_lab_role(guild: discord.Guild, group: Union[int, str]) -> Optional[discord.Role]:
    if type(group) == str and GROUP_NAME_PATTERN.search(group):
        group = int(GROUP_NAME_PATTERN.search(group).group(1))
    return discord.utils.get(guild.roles, name=get_role_name(group))


def get_lab_text_channel(guild: discord.Guild, group: Union[int, str]) -> Optional[discord.TextChannel]:
    if type(group) == str and GROUP_NAME_PATTERN.search(group):
        group = int(GROUP_NAME_PATTERN.search(group).group(1))
    return discord.utils.get(guild.text_channels, name=get_text_channel_name(group))


def get_lab_voice_channel(guild: discord.Guild, group: Union[int, str]) -> Optional[discord.VoiceChannel]:
    if type(group) == str and GROUP_NAME_PATTERN.search(group):
        group = int(GROUP_NAME_PATTERN.search(group).group(1))
    return discord.utils.get(guild.voice_channels, name=get_voice_channel_name(group))


def all_existing_lab_roles(guild: discord.Guild) -> List[discord.Role]:
    return list(filter(lambda r: ROLE_NAME_PATTERN.search(r.name), guild.roles))


def all_existing_lab_groups(guild: discord.Guild) -> List[discord.CategoryChannel]:
    return [group for group in guild.categories if GROUP_NAME_PATTERN.search(group.name)]


def all_members_with_no_group(guild: discord.Guild) -> List[discord.Member]:
    return [member for member in guild.members if existing_member_lab_role(member) is None]

def all_online_members(guild: discord.Guild) -> List[discord.Member]:
    return select_online_members(guild, guild.members)

def select_online_members(guild: discord.Guild, members: List[discord.Member]) -> List[discord.Member]:
    return [member for member in members if member.status == discord.Status.online]

def all_students_with_no_group(guild: discord.Guild) -> List[discord.Member]:
    student_role = discord.utils.get(guild.roles, name=STUDENT_ROLE_NAME)
    return [member for member in guild.members if existing_member_lab_role(member) is None and student_role in member.roles]


def all_non_empty_groups(guild: discord.Guild) -> List[discord.CategoryChannel]:
    student_role = discord.utils.get(guild.roles, name=STUDENT_ROLE_NAME)
    groups = set()
    for member in guild.members:
        if student_role in member.roles:
            existing_lab_group = existing_member_lab_group(member)
            if existing_lab_group:
                groups.add(existing_lab_group)
    return list(groups)


def all_empty_groups(guild: discord.Guild) -> List[discord.CategoryChannel]:
    all_groups = set(all_existing_lab_groups(guild))
    non_empty_groups = set(all_non_empty_groups(guild))
    return list(all_groups - non_empty_groups)


def all_students_in_group(guild: discord.Guild, group: Union[int, str]) -> List[discord.Member]:
    existing_role = get_lab_role(guild, group)
    student_role = discord.utils.get(guild.roles, name=STUDENT_ROLE_NAME)
    if not existing_role:
        return []
    return [member for member in existing_role.members if student_role in member.roles]


def all_online_members_from_role(role: discord.Role) -> List[discord.Member]:
    return [member for member in role.members if member.status == discord.Status.online]


def all_teaching_team_roles(guild: discord.Guild) -> List[discord.Role]:
    return [role for role in guild.roles if role.name in GUILD_CONFIG[guild]["TT_ROLES"]]


def all_teaching_team_members(guild: discord.Guild) -> List[discord.Member]:
    tt_roles = all_teaching_team_roles(guild)
    available_team = []
    for role in tt_roles:
        available_team.extend(all_online_members_from_role(role))
    return available_team


def member_in_teaching_team(member: discord.Member, guild: discord.Guild) -> bool:
    tt_roles = all_teaching_team_roles(guild)
    for member_role in member.roles:
        if discord.utils.get(tt_roles, name=member_role.name):
            return True
    return False


def existing_group_number_from_role(role: discord.Role) -> Optional[int]:
    return int(ROLE_NAME_PATTERN.search(role.name).group(1)) if ROLE_NAME_PATTERN.search(role.name) else None


def existing_group_number(member: discord.Member) -> Optional[int]:
    member_roles = member.roles
    for role in member_roles:
        group = existing_group_number_from_role(role)
        if group:
            return group
    return None


def existing_member_lab_role(member: discord.Member) -> Optional[discord.Role]:
    member_roles = member.roles
    for role in member_roles:
        if ROLE_NAME_PATTERN.search(role.name):
            return role
    return None


def existing_member_lab_group(member: discord.Member) -> Optional[discord.CategoryChannel]:
    member_roles = member.roles
    for role in member_roles:
        if ROLE_NAME_PATTERN.search(role.name):
            num = int(ROLE_NAME_PATTERN.search(role.name).group(1))
            return get_lab_group(member.guild, num)
    return None


def existing_member_lab_text_channel(member: discord.Member) -> Optional[discord.TextChannel]:
    member_roles = member.roles
    for role in member_roles:
        if ROLE_NAME_PATTERN.search(role.name):
            num = int(ROLE_NAME_PATTERN.search(role.name).group(1))
            return get_lab_text_channel(member.guild, num)
    return None


def existing_member_lab_voice_channel(member: discord.Member) -> Optional[discord.VoiceChannel]:
    member_roles = member.roles
    for role in member_roles:
        if ROLE_NAME_PATTERN.search(role.name):
            num = int(ROLE_NAME_PATTERN.search(role.name).group(1))
            return get_lab_voice_channel(member.guild, num)
    return None


def get_general_text_channel(guild: discord.Guild) -> Optional[discord.TextChannel]:
    return discord.utils.get(guild.text_channels, name=GUILD_CONFIG[guild]["GENERAL_TEXT_CHANNEL_NAME"])


def get_general_voice_channel(guild: discord.Guild) -> Optional[discord.TextChannel]:
    return discord.utils.get(guild.voice_channels, name=GUILD_CONFIG[guild]["GENERAL_VOICE_CHANNEL_NAME"])


def get_excluded_groups(*args) -> List[int]:
    excluded_groups: List[int] = []
    for arg in args:
        try:
            excluded_groups.append(int(arg))
        except ValueError:
            continue
    return excluded_groups