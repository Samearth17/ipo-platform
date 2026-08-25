"""Request-time investor personalization helpers."""
from copy import copy

PERSONA_VALUES = {'conservative', 'balanced', 'growth', 'aggressive', 'moderate'}
OPTIMIZATION_METHODS = {'equal_weight', 'score_weighted', 'min_volatility', 'max_sharpe'}
DEFAULT_METHOD_BY_PERSONA = {
    'conservative': 'min_volatility',
    'moderate': 'max_sharpe',
    'balanced': 'max_sharpe',
    'growth': 'max_sharpe',
    'aggressive': 'max_sharpe',
}


def effective_profile(profile, requested_persona=None):
    """Return a request-scoped profile without changing the saved profile."""
    requested = (requested_persona or '').strip().lower()
    persona = requested if requested in PERSONA_VALUES else profile.persona
    if persona == profile.persona:
        return profile, persona
    request_profile = copy(profile)
    request_profile.persona = persona
    return request_profile, persona


def effective_method(requested_method, persona):
    """Resolve a valid optimizer method using existing optimizer semantics."""
    requested = (requested_method or '').strip().lower()
    return requested if requested in OPTIMIZATION_METHODS else DEFAULT_METHOD_BY_PERSONA.get(persona, 'max_sharpe')
