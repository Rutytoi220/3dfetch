CC ?= cc
CFLAGS ?= -O2
PREFIX ?= /usr/local
LDFLAGS ?=
LDLIBS = -lm
VERSION := $(shell cat VERSION)
CODENAME ?= Overclocked ASCII

UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)
ifeq ($(UNAME_S),Darwin)
  LDLIBS += -framework IOKit -framework CoreFoundation
endif

fetch: fetch.c
	$(CC) $(CFLAGS) $(LDFLAGS) -DFETCH_VERSION='"$(VERSION)"' -DFETCH_CODENAME='"$(CODENAME)"' -DFETCH_ARCH='"$(UNAME_M)"' -DFETCH_OS='"$(UNAME_S)"' -o $@ $< $(LDLIBS)

install: fetch
	install -d $(DESTDIR)$(PREFIX)/bin
	install -m 755 fetch $(DESTDIR)$(PREFIX)/bin/fetch
	install -m 755 fetch $(DESTDIR)$(PREFIX)/bin/3dfetch

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/fetch $(DESTDIR)$(PREFIX)/bin/3dfetch

clean:
	rm -f fetch tests/shared

tests/shared: tests/shared.c fetch.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $< $(LDLIBS)

test: fetch tests/shared
	./tests/shared
	python3 tests/posix.py

.PHONY: install uninstall clean test
