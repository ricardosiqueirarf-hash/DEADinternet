from __future__ import annotations

import math


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def calculate_score(*, views: int = 0, likes: int = 0, comments: int = 0, hook_strength: float = 0, recreation_ease: float = 0, monetization_potential: float = 0) -> float:
    safe_views = max(0, int(views or 0))
    safe_likes = max(0, int(likes or 0))
    safe_comments = max(0, int(comments or 0))
    reach = 0.0 if safe_views == 0 else clamp(math.log10(safe_views + 1) / 7 * 100, 0, 100)
    if safe_views:
        like_rate = safe_likes / safe_views
        comment_rate = safe_comments / safe_views
        engagement = clamp((like_rate / 0.10) * 70 + (comment_rate / 0.02) * 30, 0, 100)
    else:
        engagement = 0.0
    hook = clamp(float(hook_strength or 0), 0, 10) * 10
    ease = clamp(float(recreation_ease or 0), 0, 10) * 10
    monetization = clamp(float(monetization_potential or 0), 0, 10) * 10
    total = reach * 0.30 + engagement * 0.20 + hook * 0.20 + ease * 0.15 + monetization * 0.15
    return round(clamp(total, 0, 100), 2)
