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

from myhdl import traceSignals, Simulation, StopSimulation, Signal, intbv, delay, always, always_comb, instance
from axi4lite import AxiMemory, AxiBusInterface
from axi4lite_tb import tb_read, tb_write


def simulate_read():
    mem = AxiMemory(depth=32)
    xbar = AxiBusInterface()

    ver = Signal(0x12345678)

    @always(delay(10))
    def gen_clk():
        xbar.aclk.next = not xbar.aclk

    @always_comb
    def comb():
        mem.block_out[0x18].next = ver

    @instance
    def run_test():
        yield xbar.aclk.posedge
        xbar.aresetn.next = True
        yield xbar.aclk.posedge

        yield tb_read(xbar, intbv(0x43C00018)[8:], ver.val)
  
        yield xbar.aclk.posedge
        ver.next = 0
        yield xbar.aclk.posedge
        
        raise StopSimulation()

    dut = xbar.map(mem)

    return dut, run_test, comb, gen_clk


def simulate_write():
    mem = AxiMemory(depth=32)
    xbar = AxiBusInterface()

    var = Signal(0x12345678)

    @always(delay(10))
    def gen_clk():
        xbar.aclk.next = not xbar.aclk

    @always_comb
    def comb():
        var.next = mem.block_in[0x18]

    @instance
    def run_test():
        yield xbar.aclk.posedge
        xbar.aresetn.next = True
        yield xbar.aclk.posedge

        yield tb_write(xbar, intbv(0x43C00018)[8:], 0x12345678, mem.block_in[0x18])
        
        yield xbar.aclk.posedge
        yield xbar.aclk.posedge
        
        raise StopSimulation()

    dut = xbar.map(mem)

    return dut, run_test, comb, gen_clk


traceSignals.name = "axi4lite_sim_read"
trace = traceSignals(simulate_read)
Simulation(trace).run(duration=1000, quiet=True)

traceSignals.name = "axi4lite_sim_write"
trace = traceSignals(simulate_write)
Simulation(trace).run(duration=1000, quiet=True)
