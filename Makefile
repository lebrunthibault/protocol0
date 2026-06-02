detector:
	@cd src/detector && poetry run detector
.PHONY: detector

install:
	@cd src/script && make install_script
.PHONY: install
