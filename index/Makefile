run1:
	python script.py karenina_utf.html karenina.html_index synonims_utf.txt
run:
	python script.py karenina_utf1.html karenina.html_index synonims_utf.txt

run_mkindex1:
	python mkindex.py karenina_utf.html karenina.html_index

run_mkindex:
	python mkindex.py karenina_utf1.html karenina.html_index

run_search1:
	python search.py karenina_utf.html karenina.html_index synonims_utf.txt

run_search:
	python search.py karenina_utf1.html karenina.html_index synonims_utf.txt

clean:
	find . -name \*~ -delete
	find . -name \*.backup -delete

	find $(CDIR) -name \*~ -delete
	find $(CDIR) -name \*.backup -delete

