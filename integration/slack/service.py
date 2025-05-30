import httpx


async def send_webhook(team_id: str, channel_id: str, webhook_token: str, data: dict):
    """
    Send slack webhook to a channel.

    Args:
        team_id: Slack team ID
        channel_id: Slack channel ID
        webhook_token: Slack webhook token
        data: Data to send to Slack
            Example:
                {
                  "attachments": [
                    {
                      "color": "#ff0000",
                      "title": "DTOOS ниже 30 дней",
                      "text": "Acne Patches (ASIN: B0BLHJ55LL) - 10 дней\nAcne Patches (ASIN: B0BLHJ55LL) - 10 дней",
                      "footer": "Всего продуктов: 2"
                    },
                    {
                      "color": "#ff8000",
                      "title": "DTOOS ниже 60 дней",
                      "text": "Acne Patches (ASIN: B0BLHJ55LL) - 10 дней\nAcne Patches (ASIN: B0BLHJ55LL) - 10 дней",
                      "footer": "Всего продуктов: 1"
                    },
                    {
                      "color": "#ffe39f",
                      "title": "DTOOS ниже 90 дней",
                      "text": "Acne Patches (ASIN: B0BLHJ55LL) - 10 дней\nAcne Patches (ASIN: B0BLHJ55LL) - 10 дней",
                      "footer": "Всего продуктов: 0"
                    }
                  ]
                }

    Returns:
        Response from Slack API
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://hooks.slack.com/services/{team_id}/{channel_id}/{webhook_token}", json=data
        )
        response.raise_for_status()
        return response



async def get_users_list(token: str):
    """
    Fetches the list of all users from Slack API.

    Args:
        token: Slack API token (xoxb-*)

    Returns:
        List of users
    """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}

    async with httpx.AsyncClient() as client:
        response = await client.get("https://slack.com/api/users.list", headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data.get("ok"):
            error = data.get("error", "Unknown error")
            raise Exception(f"Slack API error: {error}")

        return data.get("members", [])


async def get_user_profile(token: str, user_id: str):
    """
    Fetches detailed profile for a specific user.

    Args:
        token: Slack API token (xoxb-*)
        user_id: Slack user ID

    Returns:
        User profile data
    """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}

    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://slack.com/api/users.profile.get?user={user_id}", headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data.get("ok"):
            error = data.get("error", "Unknown error")
            raise Exception(f"Slack API error when fetching profile for {user_id}: {error}")

        return data.get("profile", {})


async def post_message_to_channel(token: str, channel_id: str, data: dict):
    """
    Send a message to a Slack channel using Bearer token authentication.

    Args:
        token: Slack API token (xoxb-*)
        channel_id: Slack channel ID
        data: Message data to send
            Example:
                {
                  "text": "Hello, world!"
                }

                or

                {
                  "attachments": [
                    {
                      "color": "#ff0000",
                      "title": "DTOOS ниже 30 дней",
                      "text": "Acne Patches (ASIN: B0BLHJ55LL) - 10 дней\nAcne Patches (ASIN: B0BLHJ55LL) - 10 дней",
                      "footer": "Всего продуктов: 2"
                    },
                    {
                      "color": "#ff8000",
                      "title": "DTOOS ниже 60 дней",
                      "text": "Acne Patches (ASIN: B0BLHJ55LL) - 10 дней\nAcne Patches (ASIN: B0BLHJ55LL) - 10 дней",
                      "footer": "Всего продуктов: 1"
                    },
                    {
                      "color": "#ffe39f",
                      "title": "DTOOS ниже 90 дней",
                      "text": "Acne Patches (ASIN: B0BLHJ55LL) - 10 дней\nAcne Patches (ASIN: B0BLHJ55LL) - 10 дней",
                      "footer": "Всего продуктов: 0"
                    }
                  ]
                }

    Returns:
        Response from Slack API
    """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}

    payload = {"channel": channel_id} | data

    async with httpx.AsyncClient() as client:
        response = await client.post("https://slack.com/api/chat.postMessage", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        if not data.get("ok"):
            error = data.get("error", "Unknown error")
            raise Exception(f"Slack API error when posting message: {error}")

        return data

async def get_users_list(token: str):
    """
    Fetches the list of all users from Slack API.

    Args:
        token: Slack API token (xoxb-*)

    Returns:
        List of users
    """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}

    async with httpx.AsyncClient() as client:
        response = await client.get("https://slack.com/api/users.list", headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data.get("ok"):
            error = data.get("error", "Unknown error")
            raise Exception(f"Slack API error: {error}")

        return data.get("members", [])


async def get_user_profile(token: str, user_id: str):
    """
    Fetches detailed profile for a specific user.

    Args:
        token: Slack API token (xoxb-*)
        user_id: Slack user ID

    Returns:
        User profile data
    """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}

    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://slack.com/api/users.profile.get?user={user_id}", headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data.get("ok"):
            error = data.get("error", "Unknown error")
            raise Exception(f"Slack API error when fetching profile for {user_id}: {error}")

        return data.get("profile", {})
