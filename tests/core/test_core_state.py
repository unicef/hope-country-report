from unittest.mock import Mock, patch

from hope_country_report.middleware.state import StateClearMiddleware, StateSetMiddleware


def test_state_set_middleware_init():
    get_response = Mock()
    mw = StateSetMiddleware(get_response)
    assert mw.get_response is get_response


def test_state_set_middleware_call(rf, admin_user):
    request = rf.get("/")
    request.user = admin_user
    get_response = Mock(return_value=Mock(status_code=200))
    mw = StateSetMiddleware(get_response)

    with patch("hope_country_report.middleware.state.configure_scope"):
        response = mw(request)

    get_response.assert_called_once_with(request)
    assert response is not None


def test_state_set_middleware_calls_get_response(rf, admin_user):
    request = rf.get("/")
    request.user = admin_user
    get_response = Mock(return_value=Mock(status_code=200))
    mw = StateSetMiddleware(get_response)

    with patch("hope_country_report.middleware.state.configure_scope"):
        mw(request)

    get_response.assert_called_once()


def test_state_clear_middleware_init():
    get_response = Mock()
    mw = StateClearMiddleware(get_response)
    assert mw.get_response is get_response


def test_state_clear_middleware_call(rf):
    request = rf.get("/")
    response_mock = Mock(status_code=200, cookies={})
    get_response = Mock(return_value=response_mock)
    mw = StateClearMiddleware(get_response)

    response = mw(request)

    get_response.assert_called_once_with(request)
    assert response is response_mock
