"""Duolingo stats."""

from datetime import datetime
from typing import Dict, Optional, Tuple

import dacite
import requests

from palabox.stats.duolingo.types import DuolingoStats

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 "
    "Safari/537.36"
)


def make_duolingo_request(url: str, data: Optional[Dict] = None, jwt: Optional[str] = None):
    """Login to duolingo."""
    headers = {"User-Agent": USER_AGENT}
    if jwt:
        headers["Authorization"] = f"Bearer {jwt}"
    request = requests.request(
        method="POST" if data else "GET", url=url, json=data, headers=headers
    )
    if request.ok:
        return request
    raise ValueError(f"Duolingo request not working: '{request}'")


def login_duolingo(login: str, password: str) -> Tuple[str, str]:
    """Login into duolingo.

    :returns: (user_id, jwt_token)
    """
    request = make_duolingo_request(
        url="https://www.duolingo.com/login",
        data={"login": login, "password": password},
    )
    return request.json()["user_id"], request.headers["jwt"]


def generate_url(user_id: str) -> str:
    """Generate the request url."""
    # pylint: disable=line-too-long
    return (
        "https://www.duolingo.com/2017-06-30/users/"
        + user_id
        + "?fields=acquisitionSurveyReason,adsConfig,betaStatus,bio,blockedUserIds,canUseModerationTools,courses,creationDate,currentCourse,email,emailAnnouncement,emailAssignment,emailAssignmentComplete,emailClassroomJoin,emailClassroomLeave,emailComment,emailEditSuggested,emailEventsDigest,emailFollow,emailPass,emailPromotion,emailWeeklyProgressReport,emailSchoolsAnnouncement,emailStreamPost,emailVerified,emailWeeklyReport,enableMicrophone,enableSoundEffects,enableSpeaker,experiments{connect_web_remove_dictionary,courses_fr_ja_v1,courses_it_de_v1,hoots_web,hoots_web_100_crowns,hoots_web_rename,learning_det_scores_v1,learning_duolingo_score_v1,learning_fix_whitespace_grading,media_shorten_cant_speak_web,midas_new_years_2022_purchase_flow,midas_web_cta_purchase_start_my_14_day,midas_web_family_plan,midas_web_immersive_plus_v2,midas_web_longscroll,midas_web_new_years_discount_2022,midas_web_payment_requests_v2,midas_web_plus_applicable_taxes,midas_web_plus_dashboard_mobile_users,midas_web_plus_dashboard_stripe_users,nurr_web_coach_duo_in_placement_v2,nurr_web_simplify_first_skill_popouts,nurr_web_uo_home_message_v0,sigma_web_cancel_flow_crossgrade,sigma_web_direct_purchase_hide_monthly,sigma_web_family_plan_shop_promo,sigma_web_gold_empty_progress,sigma_web_legendary_partial_xp,sigma_web_legendary_price_30_lingots,sigma_web_mistakes_inbox,sigma_web_show_xp_in_skill_popover,sigma_web_split_purchase_page,spam_non_blocking_email_verification,speak_rewrite_speak_challenge,speak_web_port_speak_waveform,stories_web_column_match_challenge,stories_web_crown_pacing_new_labels,stories_web_freeform_writing_examples,stories_web_intro_callout_tier_1,stories_web_listen_mode_redesign,stories_web_newly_published_labels,unify_checkpoint_logic_web,web_alphabets_tab,web_delight_character_scaling_v2,web_delight_fullscreen_loading_v3},facebookId,fromLanguage,globalAmbassadorStatus,googleId,hasPlus,id,inviteURL,joinedClassroomIds,lastStreak{isAvailableForRepair,length},learningLanguage,lingots,location,monthlyXp,name,observedClassroomIds,persistentNotifications,picture,plusDiscounts,practiceReminderSettings,privacySettings,referralInfo,rewardBundles,roles,streak,streakData{length},timezone,timezoneOffset,totalXp,trackingProperties,unconsumedGiftIds,username,webNotificationIds,weeklyXp,xpGains,xpGoal,zhTw,_achievements&_="
        + str(int(datetime.now().timestamp()))
    )


def get_user_stats(username: str, password: str) -> DuolingoStats:
    """Get user stats."""
    user_id, jwt_token = login_duolingo(username, password)
    url = generate_url(user_id)
    response = make_duolingo_request(url, jwt=jwt_token)
    if response.ok:
        data: DuolingoStats = dacite.from_dict(DuolingoStats, response.json())
        return data

    raise ValueError(f"Problem with the request {response}, '{response.content.decode()}'")
