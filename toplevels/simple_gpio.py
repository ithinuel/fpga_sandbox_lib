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

from myhdl import block, Signal, always_comb, intbv

from blocks.axi4lite import AxiVersion
from blocks.gpio import GPIO

version = AxiVersion(1, 0)
name = "simple_gpio"

name_and_ver = '%s_v%s' % (name, str(version).replace('.', '_'))


@block
def top_level(gpio, reg_out):
    @always_comb
    def combi():
        gpio.tri_o.next = reg_out

    return combi


def convert(path="./"):
    gpio = GPIO(4, use_i=False, use_t=False)
    reg_out = Signal(intbv(0)[4:])

    dut = top_level(gpio, reg_out)
    dut.convert(hdl='VHDL', name=name_and_ver, path=path)
