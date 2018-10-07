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

from sys import argv
from myhdl import block, always_comb, Signal, intbv

from blocks.axi4lite import AxiVersion, AxiMemory, AxiBusInterface

version = AxiVersion(1, 2)
name = "mem_test"

name_and_ver = '%s_v%s' % (name, str(version).replace('.', '_'))


@block
def top_level(xbar, ctrl_count, ctrl_en):
    mem = AxiMemory()

    v_ver = int(version.value)

    @always_comb
    def combi():
        mem.block_out[0].next = v_ver
        mem.block_out[1].next = mem.block_in[1]
        ctrl_en.next = mem.block_in[1][0]
        ctrl_count.next = mem.block_in[1][16:8]

    axi = xbar.map(mem)
    axi.name = "axilite"

    return combi, axi


def convert():
    xbar = AxiBusInterface()
    ctrl_en = Signal(False)
    ctrl_cnt = Signal(intbv(0)[8:])

    dut = top_level(xbar, ctrl_cnt, ctrl_en)
    dut.convert(hdl='VHDL',
                name=name_and_ver,
                path=argv[1])


if __name__ == '__main__':
    if argv[1] == '-v':
        print(name_and_ver)
    else:
        convert()
