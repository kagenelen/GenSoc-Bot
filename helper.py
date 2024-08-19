import json
import discord
import re
import os
import time
import datetime
import shutil
import pytz

EXEC_ROLE = "2024 Hoyosoc Team"
PRIMOJEM_EMOTE = "<:Primojem:1108620629902626816>"
JEMDUST_EMOTE = "<:Jemdust:1108591111649362043>"
BETTER_EMOTE = "<:Betters:1122383400418934846>"
HEADS_EMOTE = "<:Heads:1137589987962015815>"
TAILS_EMOTE = "<:Tails:1137589996916850760>"


def write_file(file, data):
  absolute_path = os.path.dirname(os.path.abspath(__file__)) + "/json_files/"
  with open(absolute_path + file, "w") as f:
    json.dump(data, f, indent=4, separators=(',', ': '))

def read_file(file):
  absolute_path = os.path.dirname(os.path.abspath(__file__)) + "/json_files/"
  with open(absolute_path + file, 'rb') as f:
    data = json.load(f)
  return data

# Make file backup in backup folder
# Argument: file name (must be in json_file folder)
# Return: None
def backup_file(file):
	original = os.path.dirname(os.path.abspath(__file__)) + "/json_files/" + file
	
	tz_Sydney = pytz.timezone('Australia/Sydney')
	datetime_Sydney = datetime.datetime.now(tz_Sydney)
	date_format = datetime_Sydney.strftime("%d%b_%H.%M")

	target = os.path.dirname(os.path.abspath(__file__)) + "/backup/" + date_format + ".json"
	shutil.copyfile(original, target)
	print("Backup of " + file + " done at " + unix_to_syd(time.time()))

# Convert unix to sydney time
def unix_to_syd(unix_time):
	tz_Sydney = pytz.timezone('Australia/Sydney')
	datetime_Sydney = datetime.datetime.now(tz_Sydney)
	return datetime_Sydney.strftime("%d/%m %H:%M")

# Get user entry
# Function mainly used to create entry for new users
# Argument: discord id string
# Return: user entry
def get_user_entry(discord_id):
	discord_id = str(discord_id)
	data = read_file("users.json")
	user_entry = data.get(discord_id, None)
	
	if user_entry == None:
		# Create entry for new user
		user_entry = {
			"currency": 0,
			"next_checkin": int(time.time()),
			"role": {},
			"checkin_streak": 0,
			"role_icon": [],
			"jemdust": 0,
			"chat_cooldown": 0,
			"gambling_profit": 0,
			"gambling_loss": 0,
			"next_fortune": 0,
			"uids": {
				"genshin": [],
				"hsr": [],
				"honkai": [],
				"tot": [],
				"zzz": [],
				"wuwa": []
			}
		}
		data[discord_id] = user_entry
	
	write_file("users.json", data)
	return user_entry

# Get game thumbnail image url
# Game string
# Return: image url string
def game_thumbnail(game):
	if game == "genshin":
		return "https://play-lh.googleusercontent.com/DXwvOFxp_F8N9jw4FW8kCD0SWj8ba9YqDmMPphgkoG7qqEET_yV3vxuQcVcWQJkHX18"
	elif game == "hsr":
		return "https://play-lh.googleusercontent.com/cM6aszB0SawZNoAIPvtvy4xsfeFi5iXVBhZB57o-EGPWqE4pbyIUlKJzmdkH8hytuuQ"
	elif game == "tot":
		return "https://play-lh.googleusercontent.com/S1ruLmChgGXWGxODeR8UBngac3tvOHKQdpf_sgKpMhYjLHiTGxzz4iihvuCm_f4eqg"
	elif game == "wuwa":
		return "https://play-lh.googleusercontent.com/ameFGPYH-qhOSxdsSA_fA54I4Ch-eO8y7Pj4x6W6ejQkvKbhVjCehKlPerBY9X2L8ek"
	elif game == "zzz":
		return "https://play-lh.googleusercontent.com/DEkjrvPufl6TG4Gxq4m8goCSLYiE1bLNOTnlKrJbHDOAWZT40qG3oyALMZJ2BPHJoe8=w240-h480-rw"
	elif game == "hi3":
		return "https://play-lh.googleusercontent.com/GkTrAxuJjlp190L_rDqknKUpiqBouXP7imAVpVya6sgjVr1mcntKYDQPw2wUFwgdDQ0"
	else:
		return "https://img.utdstc.com/icon/408/9e2/4089e272d8c4774c9f7a62c50d394956282202e2386b722c155c6fad2c3bb6ab:200"

# One time function for modifying database structure
# Modify this function to suit your need
def rewrite_structure():
	data = read_file("users.json")
	for user in data:
		if data[user]["uids"].get("wuwa", None) == None:
			data[user]["uids"]["wuwa"] = []
		
	write_file("users.json", data)

	print("Database modification complete")


# Determines whether user is subcom or exec
# Argument: Interaction (class)
# Return: True if user is part of team, False otherwise
def is_team(interaction):
  admin = discord.utils.find(lambda r: r.name == EXEC_ROLE,
                             interaction.guild.roles)

	# This no longer checks for subcom
  if admin not in interaction.user.roles:
    return False
  return True


# Determines whether user is a server booster
# Argument: Member (class)
# Return: True if user is booster, False otherwise
def is_booster(user):
  role_names = [role.name for role in user.roles]
  if "Server Booster" in role_names:
    return True
  return False


