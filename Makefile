run:
	python script.py karenina_utf.html karenina.html_index
clean:
	find . -name \*~ -delete
	find . -name \*.backup -delete

	find $(CDIR) -name \*~ -delete
	find $(CDIR) -name \*.backup -delete

