from src.domain.auth import Principal, Role
from src.app.offline_sync import OfflineSyncService, SyncCommand
from src.infrastructure.database.auth import hash_password, verify_password


def test_password_hash_round_trip():
    encoded = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", encoded)
    assert not verify_password("wrong password", encoded)


def test_rbac_rejects_unauthorized_role():
    principal = Principal("u", "t", "s", frozenset({Role.CASHIER}))
    try:
        principal.require(Role.ADMIN)
    except PermissionError:
        pass
    else:
        raise AssertionError("cashier must not satisfy admin authorization")


def test_offline_replay_is_idempotent():
    executed = []
    service = OfflineSyncService(lambda command: executed.append(command.command_id) or command.payload)
    commands = [SyncCommand("1", "sale", {"amount": 10}), SyncCommand("1", "sale", {"amount": 10})]
    assert service.replay(commands) == [{"amount": 10}]
    assert executed == ["1"]
