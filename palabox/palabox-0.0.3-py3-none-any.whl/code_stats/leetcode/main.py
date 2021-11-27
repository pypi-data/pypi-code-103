"""LeetCode stats."""

import json
from dataclasses import asdict

import dacite
import requests

from palabox.code_stats.leetcode.types import LeetCodeData


def get_user_stats(username: str) -> LeetCodeData:
    """Get user stats."""
    # pylint: disable=line-too-long
    response = requests.get(
        "https://leetcode.com/graphql",
        json={
            "operationName": "getUserProfile",
            "variables": {"username": username},
            "query": "query getUserProfile($username: String!) {\n  allQuestionsCount {\n    difficulty\n    count\n    __typename\n  }\n  matchedUser(username: $username) {\n    username\n    socialAccounts\n    githubUrl\n    contributions {\n      points\n      questionCount\n      testcaseCount\n      __typename\n    }\n    profile {\n      realName\n      websites\n      countryName\n      skillTags\n      company\n      school\n      starRating\n      aboutMe\n      userAvatar\n      reputation\n      ranking\n      __typename\n    }\n    submissionCalendar\n    submitStats: submitStatsGlobal {\n      acSubmissionNum {\n        difficulty\n        count\n        submissions\n        __typename\n      }\n      totalSubmissionNum {\n        difficulty\n        count\n        submissions\n        __typename\n      }\n      __typename\n    }\n    badges {\n      id\n      displayName\n      icon\n      creationDate\n      __typename\n    }\n    upcomingBadges {\n      name\n      icon\n      __typename\n    }\n    activeBadge {\n      id\n      __typename\n    }\n    __typename\n  }\n}\n",
        },
    )
    if response.ok:
        return dacite.from_dict(LeetCodeData, response.json()["data"])
    raise ValueError(f"Problem with the request {response}, '{response.content.decode()}'")


if __name__ == "__main__":
    data = get_user_stats("MarcoBoucas")
    with open("test.json", "w", encoding="utf-8") as file:
        json.dump(asdict(data), file, indent=2)
