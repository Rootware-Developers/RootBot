from datetime import datetime
from discord.ui import Container, View


def create_logs_container(TYPE, MODTYPE, USER, REASON, MODERATOR, CASE, DURATION):
    # Create a Discord UI Container
    # return it with View
    # more in moderation.py
    CONTAINER = Container()

    # Check type & modtype and add the correct header to Container
    if (MODTYPE == "add"):
        if (TYPE == "WARNING"):
            CONTAINER.add_text("# <:warning:1397873177283264594>  User got warned ")
        elif (TYPE == "MUTE"):
            CONTAINER.add_text("# <:mute:1398921067762024449>  User got muted ")
        elif (TYPE == "BAN"):
            CONTAINER.add_text("# <:banhammer:1404129307219066970>  User got banned ")

    elif (MODTYPE == "remove"):
        if (TYPE == "WARNING"):
            CONTAINER.add_text("# <:circle_check_mark:1398677122091847731>  User got unwarned ")
        elif (TYPE == "MUTE"):
            CONTAINER.add_text("# <:circle_check_mark:1398677122091847731>  User got unmuted ")
        elif (TYPE == "BAN"):
            CONTAINER.add_text("# <:circle_check_mark:1398677122091847731>  User got unbanned ")

    # Add a separator to Container
    CONTAINER.add_separator()

    # Check type & modtype and add the correct content to Container
    if (TYPE == "WARNING" or TYPE == "BAN" or TYPE== "MUTE" and MODTYPE == "remove"):
        CONTAINER.add_text(
            f"> **<:person:1397981170431688844>User:** {USER.mention}\n"
            f"> **<:paper:1397984129928265902>Reason:** `{REASON}`\n"
            f"> **<:moderator:1397981211640598719>Moderator: {MODERATOR.mention}** \n"
            f"> **<:wallet:1397981208763433112>Case:** `#{CASE}`"
        )

    elif (TYPE == "MUTE" and MODTYPE == "add"):
        CONTAINER.add_text(
            f"> **<:person:1397981170431688844>User:** {USER.mention}\n" 
            f"> **<:paper:1397984129928265902>Reason:** `{REASON}`\n"  
            f"> **<:moderator:1397981211640598719>Moderator:** {MODERATOR.mention} \n"
            f"> **<:timer:1398916124745142272>Duration:** `{DURATION}` \n"
            f"> **<:wallet:1397981208763433112>Case:** `#{CASE}`"
        )

    # Add a footer with timestamp to the container 
    CONTAINER.add_separator()
    CONTAINER.add_text(f"-# {datetime.now().strftime('%b %d, %Y %I:%M %p')}") # Date and Time

    # Return the Container as a View
    CONTAINER_VIEW = View(CONTAINER, timeout=None)
    return CONTAINER_VIEW



def create_user_container(TYPE, MODTYPE, REASON, MODERATOR, CASE, DURATION, APPEAL_BUTTON):
    # Create a Discord UI Container
    # return it with View
    # more in moderation.py
    CONTAINER = Container()

    # Check Type & Modtype and add right header to Container
    if (MODTYPE == "add"):
        if (TYPE == "WARNING"):
            CONTAINER.add_text("# <:warning:1397873177283264594>  You got warned ")
        elif (TYPE == "MUTE"):
            CONTAINER.add_text("# <:mute:1398921067762024449>  You got muted ")
        elif (TYPE == "BAN"):
            CONTAINER.add_text("# <:banhammer:1404129307219066970>  You got banned ")

    elif (MODTYPE == "remove"):
        if (TYPE == "WARNING"):
            CONTAINER.add_text("# <:circle_check_mark:1398677122091847731>  You got unwarned ")
        elif (TYPE == "MUTE"):
            CONTAINER.add_text("# <:circle_check_mark:1398677122091847731>  You got unmuted ")
        elif (TYPE == "BAN"):
            CONTAINER.add_text("# <:circle_check_mark:1398677122091847731>  You got unbanned ")

    # Add a separator to Container
    CONTAINER.add_separator()

    # Check type & modtype and add the correct content to Container
    if (TYPE == "WARNING" or TYPE == "BAN" or TYPE== "MUTE" and MODTYPE == "remove"):
        CONTAINER.add_text(
            f"> **<:paper:1397984129928265902>Reason:** `{REASON}`\n"
            f"> **<:moderator:1397981211640598719>Moderator: {MODERATOR.mention}** \n"
            f"> **<:wallet:1397981208763433112>Case:** `#{CASE}`"
        )

    elif (TYPE == "MUTE" and MODTYPE == "add"):
        CONTAINER.add_text(
            f"> **<:paper:1397984129928265902>Reason:** `{REASON}`\n"  
            f"> **<:moderator:1397981211640598719>Moderator:** {MODERATOR.mention} \n"
            f"> **<:timer:1398916124745142272>Duration:** `{DURATION}` \n"
            f"> **<:wallet:1397981208763433112>Case:** `#{CASE}`"
        )

    # Add footer section to container
    CONTAINER.add_separator()

    # Check type & modtype and add the correct footer content
    if (MODTYPE == "remove"):
        if (TYPE == "WARNING") or (TYPE == "MUTE"):
            CONTAINER.add_text(f"-# {datetime.now().strftime('%b %d, %Y %I:%M %p')}") # Date and Time
        elif (TYPE == "BAN"):
            CONTAINER.add_text("-# **Rejoin:** https://discord.gg/dSeAXPPBBD") # Link to Rejoin
    
    if (MODTYPE == "add"):
        CONTAINER.add_item(APPEAL_BUTTON) # Button to appeal

    # Return the Container as a View
    CONTAINER_VIEW = View(CONTAINER, timeout=None)
    return CONTAINER_VIEW