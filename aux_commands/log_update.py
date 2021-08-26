from asyncio import Lock
from datetime import datetime
import os

import discord

from utils.guild_config import GUILD_CONFIG
from utils import helper_functions as hpf, bot_messages as btm

"""
####################################################################
####################### LOG-UPDATE FUNCTIONS #######################
####################################################################
"""

log_info_lock = Lock()


async def update_tt_members_log(ctx, member: discord.Member, group: str, message_size: int = 2000) -> bool:
    guild = ctx.guild
    log_info = GUILD_CONFIG.log_info(guild)
    last_log_update_date = log_info.get_last_log_update_date()
    last_log_messages_ids = log_info.get_log_message_id()
    today_short_date = datetime.today().strftime('%Y-%m-%d')
    log = str(group) + " / " + str(datetime.today().strftime('%H:%M'))
    if today_short_date == last_log_update_date:
        # Update actual log
        log_info.update_tt_member_log(member, hpf.member_role_in_teaching_team(member, guild), log)
    else:
        # Create new log
        log_info.delete_all_tt_members_log()
        log_info.update_last_log_update_date(today_short_date)
        last_log_messages_ids = log_info.update_log_message_id([0])
        tt_roles = hpf.all_teaching_team_roles(guild)
        for role in tt_roles:
            tt_role_members = []
            tt_role_members.extend(hpf.all_members_from_role(role))
            for tt_member in tt_role_members:
                log_info.add_tt_member_log(tt_member=tt_member, tt_role=role)
        log_info.update_tt_member_log(member, hpf.member_role_in_teaching_team(member, guild), log)

    log_text_channel = hpf.get_log_text_channel(ctx.guild)
    today = datetime.today().strftime('%d-%m-%Y')
    message_list = []
    message_acc = str("## " + today + " log resume:\n")
    for role in log_info.tt_members_log.keys():
        message_acc += str('- - -\n ### ' + role.name + ": ### \n")
        for member, member_log in log_info.tt_members_log[role].items():
            message = str("{}: {}\n".format(hpf.get_nick(member), member_log))
            if message and len(message_acc) + len(message) < message_size:
                message_acc += message
            elif message:
                message_list.append(message_acc)
                message_acc = '\n' + message
    message_list.append(message_acc)
    if not os.path.exists('logs'):
        os.makedirs('logs')

    f = open(f"logs/{today}_log.txt", "w")
    if last_log_messages_ids == [0]:
        if log_text_channel:
            messages_ids = []
            for log_message in message_list:
                f.write(log_message)
                #new_log = await log_text_channel.send(log_message)
                #messages_ids.append(new_log.id)
            f.close()
            new_log = await log_text_channel.send(file=discord.File(f"logs/{today}_log.txt"))
            messages_ids.append(new_log.id)
            log_info.update_log_message_id(messages_ids)
    else:       
        if log_text_channel:
            for last_log_message in last_log_messages_ids:
                supr = await log_text_channel.fetch_message(last_log_message)
                await supr.delete(delay = 0)
            messages_ids = []
            for log_message in message_list:
                f.write(log_message)
                #new_log = await log_text_channel.send(log_message)
                #messages_ids.append(new_log.id)
            f.close()
            new_log = await log_text_channel.send(file=discord.File(f"logs/{today}_log.txt"))
            messages_ids.append(new_log.id)
            log_info.update_log_message_id(messages_ids)