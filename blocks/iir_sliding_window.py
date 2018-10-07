# Copyright 2017 Wilfried Chauveau
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITEDa TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
# OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from myhdl import block, always_seq, Signal, ResetSignal, intbv, enum
from math import ceil, log2


@block
def iir_sliding_window(clk, rstn, ready, input, output, samples, count):

    c_floating_bit = ceil(log2(samples)) + 3
    c_mantissa_bit = ceil(log2(count))
    c_bit_count = c_mantissa_bit + c_floating_bit
    c_gain = round(2**c_floating_bit - (samples / count))

    t_state = enum("idle", "update_request")

    s_internal = Signal(intbv(0)[c_bit_count:])
    s_state = Signal(t_state.idle)

    @always_seq(clk.posedge, rstn)
    def on_clock():
        if ready and s_state == t_state.idle:
            if input:
                v_error = s_internal[:c_floating_bit] >= (count - 1)
                output.next = v_error
                if not v_error:
                    s_internal.next = s_internal + 2**c_floating_bit
            s_state.next = t_state.update_request
        elif s_state == t_state.update_request:
            v_value = intbv(int(s_internal))[(c_bit_count+c_floating_bit):]
            v_value *= c_gain
            s_internal.next = v_value[:c_floating_bit]

            output.next = False
            s_state.next = t_state.idle

    return on_clock


if __name__ == '__main__':
    clock = Signal(False)
    resetn = ResetSignal(False, False, True)

    rdy = Signal(False)
    inp = Signal(False)
    out = Signal(False)

    inst = iir_sliding_window(clock, resetn, rdy, inp, out, 3000, 300)
    inst.convert(hdl='VHDL')
