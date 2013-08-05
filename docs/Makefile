SOURCES=g-sorcery gs-elpa gs-ctan
MANS=$(SOURCES:=.8)

RST2MAN=rst2man.py

all: ${MANS}

%.8: %.8.rst
	$(RST2MAN) $< $@
