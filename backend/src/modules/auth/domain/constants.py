"""Tunable constants for the authentication flows (framework-free)."""

# One-time password used for e-mail verification.
OTP_LENGTH = 6
OTP_TTL_SECONDS = 10 * 60  # codes expire after 10 minutes
MAX_OTP_ATTEMPTS = 5  # wrong tries before a code is invalidated

# Password-reset token.
RESET_TOKEN_TTL_SECONDS = 60 * 60  # links expire after 1 hour

# Resend throttling. The same escalating schedule is used for sign-up OTP
# resends and password-reset link resends.
DAILY_SEND_LIMIT = 10  # max emails per address per 24h
SIGNUP_SESSION_TTL_SECONDS = 24 * 60 * 60  # bookkeeping kept for one day
DAILY_COUNTER_TTL_SECONDS = 24 * 60 * 60

# Cooldown (seconds) the client must wait before the Nth resend. Index 0 is the
# wait after the very first send, index 1 after the second, and so on. Sends
# beyond the schedule are capped by DAILY_SEND_LIMIT.
RESEND_COOLDOWNS_SECONDS = [
    60,  # 1 min
    120,  # 2 min
    300,  # 5 min
    600,  # 10 min
    900,  # 15 min
    1800,  # 30 min
    3600,  # 60 min
    7200,  # 2 h
    10800,  # 3 h
    21600,  # 6 h
]


def cooldown_for(send_count: int) -> int:
    """Seconds to wait before the next resend, given how many sends have happened.

    ``send_count`` is 1 after the first send. The cooldown is clamped to the last
    entry of the schedule for any further sends.
    """
    index = max(send_count - 1, 0)
    index = min(index, len(RESEND_COOLDOWNS_SECONDS) - 1)
    return RESEND_COOLDOWNS_SECONDS[index]
