import time
import qcware
import pytest

Q = {(0, 0): 1, (1, 1): 1, (0, 1): -2, (2, 2): -2, (3, 3): -4, (3, 2): -6}


def test_timeout_with_solve_binary():
    old_timeout = qcware.config.client_timeout()
    qcware.config.set_client_timeout(0)
    old_server_timeout = qcware.config.server_timeout()
    qcware.config.set_server_timeout(0)

    with pytest.raises(qcware.exceptions.ApiTimeoutError):
        sol = qcware.optimization.find_optimal_qaoa_angles(
            Q,
            num_evals=100,
            num_min_vals=10,
            fastmath_flag_in=True,
            precision=30)
        print(sol)

    qcware.config.set_client_timeout(old_timeout)
    qcware.config.set_server_timeout(old_server_timeout)


def test_retrieve_result_with_timeout():
    old_timeout = qcware.config.client_timeout()
    qcware.config.set_client_timeout(0)
    old_server_timeout = qcware.config.server_timeout()
    qcware.config.set_server_timeout(0)

    try:
        result = qcware.optimization.solve_binary(Q=Q, backend='qcware/cpu')
    except qcware.exceptions.ApiTimeoutError as e:
        time.sleep(5)
        result = qcware.api_calls.retrieve_result(e.api_call_info['uid'])
        assert (result['solution'] == [0, 0, 1, 1]
                or result['solution'] == [1, 1, 1, 1])
    qcware.config.set_client_timeout(old_timeout)
    qcware.config.set_server_timeout(old_server_timeout)


@pytest.mark.asyncio
async def test_async():
    old_timeout = qcware.config.client_timeout()
    qcware.config.set_client_timeout(0)
    old_server_timeout = qcware.config.server_timeout()
    qcware.config.set_server_timeout(0)

    result = await qcware.optimization.async_solve_binary(Q=Q,
                                                          backend='qcware/cpu')
    assert (result['solution'] == [0, 0, 1, 1]
            or result['solution'] == [1, 1, 1, 1])

    qcware.config.set_client_timeout(old_timeout)
    qcware.config.set_server_timeout(old_server_timeout)
