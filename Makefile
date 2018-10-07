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

IPS=$(basename $(notdir $(shell find ./toplevels -iname '*.py')))
IP_REPO = ../vivado/ip_repo/ip

# Function definitions {{{
# get version for this top level
ip_ver = $(shell python3 -B top_level.py --ip_ver $1)
# get the output folder's name fot this top level
to_ip_folder = $1_$(subst .,_,$(call ip_ver,$1))
# get the output path for the vhd file of this top level
to_ip_path = $(IP_REPO)/$(call to_ip_folder,$1)/src/$1.vhd
# }}}

$(info $(IPS))
$(info $(foreach ip,$(IPS),$(call to_ip_folder,$(ip))))

define BUILD_TEMPLATE
$(call to_ip_path,$1): Makefile ./toplevels/$1.py
	echo $$@ '->' 'python3 -B top_level.py' $1
endef

echo:
	@echo $(IPS)
	python3 -B ./toplevels/simple_gpio.py

test:
	pytest-3

simulate: clean_simulation
	@for f in *_sim.py; do echo "Running $$f"; python $$f; done

build: 
	echo $@ 'aze' $<

$(foreach ip,$(IPS),$(eval $(call BUILD_TEMPLATE,$(ip))))

clean: clean_simulation clean_vhd clean_pyc

clean_simulation:
	@echo "Cleaning simulation files..."
	@rm *.vcd* 2> /dev/null || true

clean_vhd:
	@echo "Cleaning vhd files..."
	@rm *.vhd 2> /dev/null || true

clean_pyc:
	@echo "Cleaning pyc files..."
	@rm *.pyc 2> /dev/null || true
	@rm -rf __pycache__ 2> /dev/null || true

# vim: foldmethod=marker
