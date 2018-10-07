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

from myhdl import enum, Signal, ResetSignal, intbv
from myhdl import block, always_seq, always_comb

# from xilinx's datasheet [1]
#
# noqa [1]: https://www.xilinx.com/support/documentation/ip_documentation/axi_lite_ipif/v2_0/pg155-axi-lite-ipif.pdf
#

t_Resp = enum("OKAY", "reserved", "SLVERR", "reserved2", encoding="binary")


class AxiVersion:
    def __init__(self, major=1, minor=0, rev_id=0, patch=0, rev_number=0):
        self.major = major
        self.minor = minor
        self.rev_id = rev_id

        self.value = intbv(
            ((major & 0xFF) << 24) |
            ((minor & 0xFF) << 16) |
            ((rev_id & 0xF) << 12),
            max=2**32
        )

    def __str__(self):
        return "%d.%d" % (self.major, self.minor)


class AxiMemory:
    def __init__(self, depth=8, data_width=32):
        self.block_in = [Signal(intbv(0)[data_width:]) for _ in range(depth)]
        self.block_out = [Signal(intbv(0)[data_width:]) for _ in range(depth)]


class AxiBusInterface:
    def __init__(self, addr_width=8, data_width=32):
        assert data_width in (32, 64)

        # AXI Global System Signals
        # in
        self.aclk = Signal(False)
        # in
        self.aresetn = ResetSignal(False, active=False, async=True)

        # AXI Write Address Channel Signals
        # in
        self.awaddr = Signal(intbv(0)[addr_width:])
        # in
        self.awvalid = Signal(False)
        # out
        self.awready = Signal(True)

        # AXI Write Data Channel Signals
        # in
        self.wdata = Signal(intbv(0)[data_width:])
        # in
        self.wstrb = Signal(intbv(0)[data_width/8:])
        # in
        self.wvalid = Signal(False)
        # out
        self.wready = Signal(True)

        # AXI Write Response Channel Signals
        # out
        self.bresp = Signal(intbv(0)[2:])
        # out
        self.bvalid = Signal(False)
        # in
        self.bready = Signal(False)

        # AXI Read Address Channel Signals
        # in
        self.araddr = Signal(intbv(0)[addr_width:])
        # in
        self.arvalid = Signal(False)
        # out
        self.arready = Signal(True)

        # AXI Read Data Channel Signals
        # out
        self.rdata = Signal(intbv(0)[data_width:])
        # out
        self.rresp = Signal(intbv(0)[2:])
        # out
        self.rvalid = Signal(False)
        # in
        self.rready = Signal(True)

        self.aw = addr_width
        self.dw = data_width

    @block
    def map(self, memory):
        xbar = self

        # these are required to have a consistent naming on the vhdl port
        # this can be a point of improvement for myhdl :/
        s_clk = Signal(False)
        s_rst = ResetSignal(False, False, True)

        s_arready = Signal(True)
        s_rvalid = Signal(False)

        s_awready = Signal(False)
        s_wready = Signal(False)
        s_bvalid = Signal(False)

        v_okay = int(t_Resp.OKAY)

        v_word_cnt = xbar.dw >> 3

        @always_seq(s_clk.posedge, s_rst)
        def read_on_clock():
            if xbar.arvalid and s_arready:
                s_arready.next = False
            else:
                s_arready.next = True

            if xbar.arvalid and s_arready and not s_rvalid:
                v_addr = xbar.araddr[xbar.aw:2]
                v_addr_low = xbar.araddr[2:0]

                if v_addr_low == 0 and v_addr < len(memory.block_out):
                    xbar.rdata.next = memory.block_out[v_addr]
                xbar.rresp.next = v_okay
                s_rvalid.next = True
            elif xbar.rready and s_rvalid:
                s_rvalid.next = False

        @always_seq(s_clk.posedge, s_rst)
        def write_on_clock():
            if xbar.awvalid and not s_awready:
                s_awready.next = True
            else:
                s_awready.next = False

            if xbar.awvalid and xbar.wvalid and not s_wready:
                v_addr = xbar.awaddr[xbar.aw:2]
                v_addr_low = xbar.awaddr[2:0]

                if v_addr_low == 0 and v_addr < len(memory.block_in):
                    for i in range(v_word_cnt):
                        lsb = i * 8
                        if xbar.wstrb[i]:
                            entry = memory.block_in[v_addr]
                            entry.next[lsb+8:lsb] = xbar.wdata[lsb+8:lsb]
                s_wready.next = True
            elif xbar.wvalid and s_wready and not s_bvalid:
                s_wready.next = False
                xbar.bresp.next = v_okay
                s_bvalid.next = True
            elif s_bvalid and xbar.bready:
                s_bvalid.next = False

        @always_comb
        def combi():
            xbar.arready.next = s_arready
            xbar.rvalid.next = s_rvalid

            s_rst.next = xbar.aresetn
            s_clk.next = xbar.aclk

            xbar.awready.next = s_awready
            xbar.wready.next = s_wready
            xbar.bvalid.next = s_bvalid

        return read_on_clock, write_on_clock, combi
