import typing as t
from inspect import iscoroutinefunction, isasyncgenfunction, iscoroutine

import pytest

from .runners import get_runner
from .utils import get_testfunc


@pytest.hookimpl(tryfirst=True)
def pytest_pycollect_makeitem(collector, name, obj):
    if collector.istestfunction(obj, name):
        testfunc, _ = get_testfunc(obj)
        if iscoroutinefunction(testfunc):
            pytest.mark.usefixtures('aiolib')(obj)


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> t.Optional[bool]:
    backend = pyfuncitem.funcargs.get('aiolib')
    if not backend:
        return None

    testfunc, is_hypothesis = get_testfunc(pyfuncitem.obj)
    if not iscoroutinefunction(testfunc):
        return None

    aiolib: str = pyfuncitem.funcargs.get('aiolib', 'asyncio')  # type: ignore

    def run(**kwargs):
        with get_runner(aiolib) as runner:
            runner.run(testfunc, **kwargs)

    if is_hypothesis:
        pyfuncitem.obj.hypothesis.inner_test = run

    else:
        funcargs = pyfuncitem.funcargs
        testargs = {arg: funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}
        run(**testargs)

    return True


def pytest_fixture_setup(fixturedef, request):
    func = fixturedef.func
    if not (iscoroutinefunction(func) or isasyncgenfunction(func)):
        return

    if 'aiolib' not in request.fixturenames:
        return

    def wrapper(*args, aiolib, **kwargs):
        with get_runner(aiolib) as runner:
            if iscoroutinefunction(func):
                yield runner.run(func, *args, **kwargs)

            else:
                gen = func(*args, **kwargs)
                try:
                    value = runner.run(gen.asend, None)
                except StopIteration:
                    raise RuntimeError('Async generator did not yield')

                yield value

                try:
                    runner.run(gen.asend, None)
                except StopAsyncIteration:
                    pass
                else:
                    runner.run(gen.aclose)
                    raise RuntimeError('Async generator fixture did not stop')

    fixturedef.func = wrapper
    if 'aiolib' not in fixturedef.argnames:
        fixturedef.argnames += 'aiolib',


@pytest.fixture(params=['asyncio', 'trio', 'curio'])
def aiolib(request):
    return request.param
