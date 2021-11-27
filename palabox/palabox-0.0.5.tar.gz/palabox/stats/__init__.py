"""Code Stats."""

from palabox.stats.codingame.main import get_user_stats as get_codingame
from palabox.stats.duolingo.main import get_user_stats as get_duolingo
from palabox.stats.leetcode.main import get_user_stats as get_leetcode
from palabox.stats.wakatime.main import get_user_stats as get_wakatime

__all__ = ["get_codingame", "get_wakatime", "get_leetcode", "get_duolingo"]
