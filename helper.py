import json
import discord
import re
import os
import time
import datetime
import shutil
import pytz

SUBCOM_ROLE = "Subcommittee"
EXEC_ROLE = "2023 Gensoc Team"

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
      "uids": []
    }
    data[discord_id] = user_entry

  write_file("users.json", data)
  return user_entry


# One time function for modifying database structure
# Modify this function to suit your need
def rewrite_structure():
	data = read_file("users.json")
	for user in data:
		if data[user].get("hsr_uids", None) == None:
			data[user]["hsr_uids"] = []
		
	write_file("users.json", data)

	print("Database modification complete")


# Determines whether user is subcom or exec
# Arg: Interaction (class)
# Return: True if user is part of team, False otherwise
def is_team(interaction):
  subcom = discord.utils.find(lambda r: r.name == SUBCOM_ROLE,
                              interaction.guild.roles)
  admin = discord.utils.find(lambda r: r.name == EXEC_ROLE,
                             interaction.guild.roles)

	# This no longer checks for subcom
  if admin not in interaction.user.roles:
    return False
  return True


# Determines whether user is a server booster
# Arg: Member (class)
# Return: True if user is booster, False otherwise
def is_booster(user):
  role_names = [role.name for role in user.roles]
  if "Server Booster" in role_names:
    return True
  return False


# Verifies user from moderator message
# Arg: Message (class)
# Return: User (member class) or None if user not found
async def verify_user(message):
	# Deals message type: either embed or not embed
	message_words = []
	if (len(message.embeds) > 0):
		message_words = message.embeds[0].description.split('\n')
	else:
		message_words = message.content.split('\n')

	old_username = False
	username = None
	for word in message_words:
		search_res = re.search(r'(?:!\w+\s+)?([^\n]*#[0-9]*)', word)
		if search_res != None and "JohnSmith#1234" not in word:  # Discord old username format found
			old_username = True
			username = search_res.group()
			username_list = username.split("#")

	for index, word1 in enumerate(message_words):
		if "What is your Discord ID?" in word1: # Discord new username format
			username = message_words[index + 1]

	role = discord.utils.get(message.guild.roles, name="Traveller")
	if role == None:
		return

	if old_username:
		user = discord.utils.get(message.guild.members,
														 name=username_list[0],
														 discriminator=username_list[1])
	else:
		user = discord.utils.get(message.guild.members,
														 name=username)
		
	if user == None:
		await message.add_reaction("❌")
		print(username + " does not exist in the server")
	else:
		await user.add_roles(role)
		await message.add_reaction("✅")
		print(username + " has been given a role")
	
	return user

