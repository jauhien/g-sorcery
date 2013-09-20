HTML_SOURCES=developer_instructions
HTML_DOCS=$(HTML_SOURCES:=.html)

MAN_SOURCES=g-sorcery g-sorcery.cfg gs-elpa gs-pypi gs-ctan
MANS=$(MAN_SOURCES:=.8)

RST2HTML=rst2html.py
RST2MAN=rst2man.py

all: ${MANS} ${HTML_DOCS}

%.8: %.8.rst
	$(RST2MAN) $< $@

%.html: %.rst
	$(RST2HTML) $< $@
