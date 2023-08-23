output_files = build/wpress.html

.PHONY: all public

all: build public $(output_files)

build:
	mkdir -p build

public:
	cp -r public/* build

build/%.html: src/%.md
	cat $< | python3 -m markdown -x fenced_code -x codehilite | cat src/header.html - src/footer.html > $@

clean:
	rm -r build
