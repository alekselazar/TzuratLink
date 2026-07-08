import logging

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

logger = logging.getLogger(__name__)


class LoggingSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    allauth's default adapter silently discards the exception on a failed
    social login (on_authentication_error is a no-op) - it never reaches any
    logger. This override logs it so the real cause is visible in
    kubectl logs/docker logs instead of just the generic error page.
    """

    def on_authentication_error(self, request, provider, error=None, exception=None, extra_context=None):
        logger.error(
            "Social login authentication error: provider=%s error=%s",
            provider, error, exc_info=exception,
        )
        return super().on_authentication_error(
            request, provider, error=error, exception=exception, extra_context=extra_context,
        )
