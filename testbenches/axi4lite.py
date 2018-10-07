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

from unittest import TestCase
from myhdl import intbv, Simulation

from axi4lite import AxiBusInterface, AxiMemory


def tb_read(xbar, in_addr, expected):
    xbar.araddr.next = in_addr
    xbar.arvalid.next = True
    xbar.rready.next = True

    yield xbar.aclk.posedge
    while not xbar.arready:
        yield xbar.aclk.posedge

    xbar.araddr.next = 0
    xbar.arvalid.next = False

    while not xbar.rvalid:
        yield xbar.aclk.posedge

    xbar.rready.next = False

    yield xbar.aclk.posedge
    xbar.rready.next = True

    assert xbar.rdata == expected


def tb_write(xbar, in_addr, out_value, in_register):
    xbar.awaddr.next = in_addr
    xbar.awvalid.next = True
    xbar.wdata.next = out_value
    xbar.wstrb.next = intbv(0xFF)[xbar.dw/8:]
    xbar.wvalid.next = True
    xbar.bready.next = True

    yield xbar.aclk.posedge
    while not xbar.awready:
        yield xbar.aclk.posedge

    xbar.awaddr.next = 0
    xbar.awvalid.next = False

    while not xbar.wready:
        yield xbar.aclk.posedge

    xbar.wdata.next = 0
    xbar.wstrb.next = 0
    xbar.wvalid.next = False

    while not xbar.bvalid:
        yield xbar.aclk.posedge

    xbar.bready.next = False

    assert out_value == in_register


class TestAxi4lite(TestCase):
    @staticmethod
    def test_read():
        mem = AxiMemory()
        xbar = AxiBusInterface()
        dut = xbar.map(mem)

        sim = Simulation(dut, tb_read(xbar, 0, 3))
        sim.run(quiet=1)
