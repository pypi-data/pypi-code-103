def failure(name, repo, job_url, web_hook):
    import requests as r
    from datetime import datetime
    payload = {
        "attachments": [
            {
                "color": "FF0000",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                                "type": "plain_text",
                                "text": "Github Action Build Error",
                                "emoji": True
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                                {
                                    "text": f"*{name}*  |  {datetime.utcnow()}",
                                    "type": "mrkdwn"
                                }
                        ]
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "actions",
                        "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Build Error",
                                        "emoji": True
                                    },
                                    "value": "click_me_123",
                                    "url": job_url,
                                    "action_id": "actionId-0"
                                },
                            {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Repository",
                                        "emoji": True
                                    },
                                    "value": "click_me_123",
                                    "url": f"https://github.com/{repo}",
                                    "action_id": "actionId-1"
                                    }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                                "type": "mrkdwn",
                                "text": "Assignee"
                        },
                        "accessory": {
                            "type": "users_select",
                            "placeholder": {
                                    "type": "plain_text",
                                    "text": "Select a user",
                                    "emoji": True
                            },
                            "action_id": "users_select-action"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                                "type": "mrkdwn",
                                "text": "Status"
                        },
                        "accessory": {
                            "type": "static_select",
                            "placeholder": {
                                    "type": "plain_text",
                                    "text": "Select a status",
                                    "emoji": True
                            },
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Open",
                                        "emoji": True
                                    },
                                    "value": "value-0"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Resolved",
                                        "emoji": True
                                    },
                                    "value": "value-0"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Created Issue",
                                        "emoji": True
                                    },
                                    "value": "value-1"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Closed (No Resolution)",
                                        "emoji": True
                                    },
                                    "value": "value-2"
                                }
                            ],
                            "action_id": "static_select-action"
                        }
                    }
                ]
            }
        ]
    }
    headers = {'Content-Type': 'application/json'}
    response = r.post(web_hook, json=payload, headers=headers)


def success(web_hook):
    import requests as r
    payload = {
        "attachments": [
            {
                "color": "#86B049",
                "blocks": [
                    {
                        "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "Github Action Success: Google Data Share - unload_data_usage_al"
                                }
                    }
                ]
            }
        ]
    }
    headers = {'Content-Type': 'application/json'}
    response = r.post(web_hook, json=payload, headers=headers)