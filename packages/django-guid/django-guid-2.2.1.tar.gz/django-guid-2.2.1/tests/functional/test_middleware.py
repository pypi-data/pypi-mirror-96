import pytest
from django.core.exceptions import ImproperlyConfigured


@pytest.fixture
def mock_uuid(monkeypatch):
    class MockUUid:
        hex = '704ae5472cae4f8daa8f2cc5a5a8mock'

    monkeypatch.setattr('django_guid.middleware.uuid.uuid4', MockUUid)


def test_request_with_no_correlation_id(client, caplog, mock_uuid):
    """
    Tests a request without any correlation-ID in it logs the correct things.
    In this case, it means that the first log message should not have any correlation-ID in it, but the next two
    (from views and services.useless_file) should have.
    :param mock_uuid: Monkeypatch fixture for mocking UUID
    :param client: Django client
    :param caplog: caplog fixture
    """
    response = client.get('/')
    expected = [
        (
            'Header `Correlation-ID` was not found in the incoming request. Generated new GUID: 704ae5472cae4f8daa8f2cc5a5a8mock',
            None,
        ),
        ('This log message should have a GUID', '704ae5472cae4f8daa8f2cc5a5a8mock'),
        ('Some warning in a function', '704ae5472cae4f8daa8f2cc5a5a8mock'),
        ('Received signal `request_finished`', '704ae5472cae4f8daa8f2cc5a5a8mock'),
        ('Deleting 704ae5472cae4f8daa8f2cc5a5a8mock from _guid', '704ae5472cae4f8daa8f2cc5a5a8mock'),
    ]
    assert [(x.message, x.correlation_id) for x in caplog.records] == expected
    assert response['Correlation-ID'] == '704ae5472cae4f8daa8f2cc5a5a8mock'


def test_request_with_correlation_id(client, caplog):
    """
    Tests a request _with_ a correlation-ID in it logs the correct things.
    :param client: Django client
    :param caplog: caplog fixture
    """
    response = client.get('/', **{'HTTP_Correlation-ID': '97c304252fd14b25b72d6aee31565843'})
    expected = [
        ('Correlation-ID found in the header: 97c304252fd14b25b72d6aee31565843', None),
        ('97c304252fd14b25b72d6aee31565843 is a valid GUID', None),
        ('This log message should have a GUID', '97c304252fd14b25b72d6aee31565843'),
        ('Some warning in a function', '97c304252fd14b25b72d6aee31565843'),
        ('Received signal `request_finished`', '97c304252fd14b25b72d6aee31565843'),
        ('Deleting 97c304252fd14b25b72d6aee31565843 from _guid', '97c304252fd14b25b72d6aee31565843'),
    ]
    assert [(x.message, x.correlation_id) for x in caplog.records] == expected
    assert response['Correlation-ID'] == '97c304252fd14b25b72d6aee31565843'


def test_request_with_invalid_correlation_id(client, caplog, mock_uuid):
    """
    Tests that a request with an invalid GUID is replaced when VALIDATE_GUID is True.
    :param client: Django client
    :param caplog: Caplog fixture
    :param mock_uuid: Monkeypatch fixture for mocking UUID
    """
    response = client.get('/', **{'HTTP_Correlation-ID': 'bad-guid'})
    expected = [
        ('Correlation-ID found in the header: bad-guid', None),
        ('Failed to validate GUID bad-guid', None),
        ('bad-guid is not a valid GUID. New GUID is 704ae5472cae4f8daa8f2cc5a5a8mock', None),
        ('This log message should have a GUID', '704ae5472cae4f8daa8f2cc5a5a8mock'),
        ('Some warning in a function', '704ae5472cae4f8daa8f2cc5a5a8mock'),
        ('Received signal `request_finished`', '704ae5472cae4f8daa8f2cc5a5a8mock'),
        ('Deleting 704ae5472cae4f8daa8f2cc5a5a8mock from _guid', '704ae5472cae4f8daa8f2cc5a5a8mock'),
    ]
    assert [(x.message, x.correlation_id) for x in caplog.records] == expected
    assert response['Correlation-ID'] == '704ae5472cae4f8daa8f2cc5a5a8mock'


def test_request_with_invalid_correlation_id_without_validation(client, caplog, monkeypatch):
    """
    Tests that a request with an invalid GUID is replaced when VALIDATE_GUID is False.
    :param client: Django client
    :param caplog: Caplog fixture
    :param monkeypatch: Monkeypatch for django settings
    """
    from django_guid.config import settings as guid_settings

    monkeypatch.setattr(guid_settings, 'VALIDATE_GUID', False)
    client.get('/', **{'HTTP_Correlation-ID': 'bad-guid'})
    expected = [
        ('Correlation-ID found in the header: bad-guid', None),
        ('Returning ID from header without validating it as a GUID', None),
        ('This log message should have a GUID', 'bad-guid'),
        ('Some warning in a function', 'bad-guid'),
        ('Received signal `request_finished`', 'bad-guid'),
        ('Deleting bad-guid from _guid', 'bad-guid'),
    ]
    assert [(x.message, x.correlation_id) for x in caplog.records] == expected


def test_no_return_header_and_drf_url(client, caplog, monkeypatch, mock_uuid):
    """
    Tests that it does not return the GUID if RETURN_HEADER is false.
    This test also tests a DRF response, just to confirm everything works in both worlds.
    """
    from django_guid.config import settings as guid_settings

    monkeypatch.setattr(guid_settings, 'RETURN_HEADER', False)
    response = client.get('/api')
    expected = [
        (
            'Header `Correlation-ID` was not found in the incoming request. Generated new GUID: 704ae5472cae4f8daa8f2cc5a5a8mock',
            None,
        ),
        ('This is a DRF view log, and should have a GUID.', '704ae5472cae4f8daa8f2cc5a5a8mock'),
        ('Some warning in a function', '704ae5472cae4f8daa8f2cc5a5a8mock'),
        ('Received signal `request_finished`', '704ae5472cae4f8daa8f2cc5a5a8mock'),
        ('Deleting 704ae5472cae4f8daa8f2cc5a5a8mock from _guid', '704ae5472cae4f8daa8f2cc5a5a8mock'),
    ]
    assert [(x.message, x.correlation_id) for x in caplog.records] == expected
    assert not response.get('Correlation-ID')


def test_no_expose_header_return_header_true(client, monkeypatch, mock_uuid):
    """
    Tests that it does not return the Access-Control-Allow-Origin when EXPOSE_HEADER is set to False
    and RETURN_HEADER is True
    """
    from django_guid.config import settings as guid_settings

    monkeypatch.setattr(guid_settings, 'EXPOSE_HEADER', False)
    response = client.get('/api')
    assert not response.get('Access-Control-Expose-Headers')


def test_expose_header_return_header_true(client, monkeypatch, mock_uuid):
    """
    Tests that it does return the Access-Control-Allow-Origin when EXPOSE_HEADER is set to True
    and RETURN_HEADER is True
    """
    from django_guid.config import settings as guid_settings

    monkeypatch.setattr(guid_settings, 'EXPOSE_HEADER', True)
    response = client.get('/api')
    assert response.get('Access-Control-Expose-Headers')


def test_no_expose_header_return_header_false(client, monkeypatch, mock_uuid):
    """
    Tests that it does not return the Access-Control-Allow-Origin when EXPOSE_HEADER is set to False
    and RETURN_HEADER is False
    """
    from django_guid.config import settings as guid_settings

    monkeypatch.setattr(guid_settings, 'EXPOSE_HEADER', False)
    monkeypatch.setattr(guid_settings, 'RETURN_HEADER', False)
    response = client.get('/api')
    assert not response.get('Access-Control-Expose-Headers')


def test_expose_header_return_header_false(client, monkeypatch, mock_uuid):
    """
    Tests that it does not return the Access-Control-Allow-Origin when EXPOSE_HEADER is set to True
    and RETURN_HEADER is False
    """
    from django_guid.config import settings as guid_settings

    monkeypatch.setattr(guid_settings, 'EXPOSE_HEADER', True)
    monkeypatch.setattr(guid_settings, 'RETURN_HEADER', False)
    response = client.get('/api')
    assert not response.get('Access-Control-Expose-Headers')


def test_cleanup_signal(client, caplog, monkeypatch):
    """
    Tests that a request cleans up a request after finishing.
    :param client: Django client
    :param caplog: Caplog fixture
    :param monkeypatch: Monkeypatch for django settings
    """
    from django_guid.config import settings as guid_settings

    monkeypatch.setattr(guid_settings, 'VALIDATE_GUID', False)
    client.get('/', **{'HTTP_Correlation-ID': 'bad-guid'})
    client.get('/', **{'HTTP_Correlation-ID': 'another-bad-guid'})

    expected = [
        # First request
        ('Correlation-ID found in the header: bad-guid', None),
        ('Returning ID from header without validating it as a GUID', None),
        ('This log message should have a GUID', 'bad-guid'),
        ('Some warning in a function', 'bad-guid'),
        ('Received signal `request_finished`', 'bad-guid'),
        ('Deleting bad-guid from _guid', 'bad-guid'),
        # Second request
        ('Correlation-ID found in the header: another-bad-guid', None),
        ('Returning ID from header without validating it as a GUID', None),
        ('This log message should have a GUID', 'another-bad-guid'),
        ('Some warning in a function', 'another-bad-guid'),
        ('Received signal `request_finished`', 'another-bad-guid'),
        ('Deleting another-bad-guid from _guid', 'another-bad-guid'),
    ]
    assert [(x.message, x.correlation_id) for x in caplog.records] == expected


def test_improperly_configured_if_not_in_installed_apps(client, monkeypatch):
    """
    Test that the app will fail if `is_installed('django_guid')` is `False`.
    """
    monkeypatch.setattr('django_guid.middleware.apps.is_installed', lambda x: False)
    with pytest.raises(ImproperlyConfigured, match='django_guid must be in installed apps'):
        client.get('/')


def test_url_ignored(client, caplog, monkeypatch):
    """
    Test that a URL specified in IGNORE_URLS is ignored.
    :param client: Django client
    :param caplog: Caplog fixture
    :param monkeypatch: Monkeypatch for django settings
    """
    from django_guid.config import settings as guid_settings

    monkeypatch.setattr(guid_settings, 'IGNORE_URLS', {'no_guid'})  # Same as it would be after config conversion
    client.get('/no_guid', **{'HTTP_Correlation-ID': 'bad-guid'})
    # No log message should have a GUID, aka `None` on index 1.
    expected = [
        ('This log message should NOT have a GUID - the URL is in IGNORE_URLS', None),
        ('Some warning in a function', None),
        ('Received signal `request_finished`', None),
    ]
    assert [(x.message, x.correlation_id) for x in caplog.records] == expected
