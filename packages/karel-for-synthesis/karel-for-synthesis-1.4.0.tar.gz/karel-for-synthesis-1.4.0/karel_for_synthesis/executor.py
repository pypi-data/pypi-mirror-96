import collections
import operator
import traceback

import numpy as np
import pylru
import attr

from .parser_for_synthesis import (
    KarelForSynthesisParser,
    KarelSyntaxError,
    TimeoutError,
)
from .errors import Timeout, ExecutorSyntaxException, ExecutorRuntimeException

ExecutionResult = collections.namedtuple("ExecutionResult", ["result", "trace"])


KarelTrace = collections.namedtuple("KarelTrace", ["grids", "events"])
KarelEvent = collections.namedtuple(
    "KarelEvent",
    [
        "timestep",  # event happened before corresponding index in grids
        "type",  # move, turnLeft/Right, put/pickMarker, if, ifElse, repeat
        "span",  # (i, j) for first, last token for block
        "cond_span",  # (i, j)  for first, last token contained in c( c)
        "cond_value",  # True/False for if/ifElse, remaining iters for repeat
        "success",  # False if action failed or loop will repeat forever
    ],
)

ACTIONS = {
    x.lower() for x in ("move", "turnRight", "turnLeft", "pickMarker", "putMarker")
}
REPEATS = {"repeat"}
BRANCHES = {x.lower() for x in ("ifElse", "while", "if")}


class KarelExecutor(object):
    def __init__(self, action_limit=1000):
        self.parser = KarelForSynthesisParser()
        self.action_limit = action_limit
        self.code_cache = pylru.lrucache(100000)

    def execute(self, code, inp, record_trace=False, strict=True):
        if not isinstance(code, tuple):
            code = tuple(code)

        field = inp.copy()

        trace = None
        timeout = Timeout(self.action_limit)
        if record_trace:
            trace = KarelTrace([inp], [])

            def action_callback(action_name, success, span):
                trace.events.append(
                    KarelEvent(
                        timestep=len(trace.grids),
                        type=action_name,
                        span=span,
                        cond_span=None,
                        cond_value=None,
                        success=success,
                    )
                )
                trace.grids.append(field)
                timeout.inc()

            def event_callback(
                block_name, block_span, cond_span, cond_value, selected_span
            ):
                trace.events.append(
                    KarelEvent(
                        timestep=len(trace.grids),
                        type=block_name,
                        span=block_span,
                        cond_span=cond_span,
                        cond_value=cond_value,
                        success=True,
                    )
                )
                timeout.inc()

        else:

            def action_callback(action_name, success, metadata):
                if strict and not success:
                    raise ExecutorRuntimeException
                timeout.inc()

            def event_callback(block_name, *args):
                timeout.inc()

        self.parser.karel.init_from_array(field)
        self.parser.karel.action_callback = action_callback
        self.parser.karel.event_callback = event_callback
        try:
            if code not in self.code_cache:
                compiled = self.parser.parse(code, debug=False)
                self.code_cache[code] = compiled
            else:
                compiled = self.code_cache[code]
            compiled()
        except KarelSyntaxError:
            raise ExecutorSyntaxException(str(code))
        except (TimeoutError, ExecutorRuntimeException) as e:
            if not record_trace:
                if isinstance(e, TimeoutError):
                    raise ExecutorRuntimeException
                raise
            if isinstance(e, TimeoutError):
                # Heuristic to find the root cause of TimeoutError:
                # - while with the longest current string of True cond_value
                # - repeat nested too much
                while_counts = collections.defaultdict(int)
                while_locs = {}
                for i, event in enumerate(trace.events):
                    if event.type != "while":
                        continue
                    if event.cond_value:
                        if while_counts[event.span] == 0:
                            while_locs[event.span] = i
                        while_counts[event.span] += 1
                    else:
                        while_counts[event.span] = 0

                finished = False
                if while_locs and while_counts:
                    offending_span, count = max(
                        while_counts.items(), key=operator.itemgetter(1)
                    )
                    if count > 0 and offending_span in while_locs:
                        offending_loc = while_locs[offending_span]
                        del trace.events[offending_loc + 1 :]
                        trace.events[-1] = KarelEvent(
                            *(trace.events[-1][:-1] + (False,))
                        )
                        finished = True

                if not finished:
                    # No whiles in the code; blame the first repeat
                    repeat_found = False
                    for i, event in enumerate(trace.events):
                        if event.type == "repeat":
                            repeat_found = True
                            break
                    if not repeat_found:
                        pass
                        # TODO stopgap to prevent errors
                        # print(trace.events)
                        # raise Exception(
                        #        'Karel timeout with neither while nor repeat. '
                        #        'Code: ' + ' '.join(code))
                    del trace.events[i + 1 :]
                    trace.events[-1] = KarelEvent(*(trace.events[-1][:-1] + (False,)))

                # Delete all grids accumulated after where we decided to have
                # the cutoff
                del trace.grids[trace.events[-1].timestep :]

            return ExecutionResult(None, trace)

        if record_trace:
            # Cut off at last failed action
            failure = False
            for i, event in enumerate(trace.events):
                if not event.success:
                    failure = True
                    break
            if failure:
                del trace.events[i + 1 :]
                # Delete all grids accumulated after where we decided to have
                # the cutoff
                del trace.grids[trace.events[-1].timestep :]
                return ExecutionResult(None, trace)

        return ExecutionResult(field, trace)


_standard_executor = KarelExecutor()


def execute(program, grid, record_trace=False):
    return _standard_executor.execute(program, grid, record_trace=record_trace)
